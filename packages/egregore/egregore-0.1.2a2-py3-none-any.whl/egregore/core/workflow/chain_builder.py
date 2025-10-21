"""Chain builder for deferred workflow instantiation.

This module provides the core infrastructure for building workflow chains
without creating node instances. Instead, it captures the chain structure
as metadata that can be serialized and instantiated later.

This enables:
- Distributed execution (send specs to different VMs/pods)
- Workflow serialization and checkpointing
- Retry logic and fault tolerance
- Resource scheduling and optimization
"""

from typing import List, Tuple, Optional, Dict, Any, TYPE_CHECKING
from dataclasses import dataclass, field
import uuid

if TYPE_CHECKING:
    from egregore.core.workflow.nodes.node_types import NodeType
    from egregore.core.workflow.nodes.base import BaseNode


@dataclass
class NodeSpec:
    """Serializable specification of a single workflow node.

    This captures everything needed to instantiate a node on any machine:
    - Node type (class reference)
    - Node name (user-facing name from @node('name'))
    - Canonical name (original name from decorator)
    - Alias name (if this is an aliased node)
    - Metadata (any additional configuration)

    Attributes:
        node_type_class: Fully qualified class name (e.g., "mymodule.MyNode_abc123")
        node_name: User-facing name from @node('name') decorator
        canonical_name: Original name before any aliasing
        alias_name: Explicit alias name if .alias() was called
        is_router: Whether this node is a router (feeds decision criteria to Decision)
        metadata: Additional configuration data
        spec_id: Unique identifier for this spec (for graph edges)
        _node_type_ref: Internal reference to NodeType for in-memory instantiation (not serialized)
    """
    node_type_class: str
    node_name: str
    canonical_name: str
    alias_name: Optional[str] = None
    is_router: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    spec_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    _node_type_ref: Optional[Any] = field(default=None, repr=False, compare=False)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for JSON/network transport."""
        return {
            'node_type_class': self.node_type_class,
            'node_name': self.node_name,
            'canonical_name': self.canonical_name,
            'alias_name': self.alias_name,
            'is_router': self.is_router,
            'metadata': self.metadata,
            'spec_id': self.spec_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NodeSpec':
        """Deserialize from dictionary."""
        return cls(
            node_type_class=data['node_type_class'],
            node_name=data['node_name'],
            canonical_name=data['canonical_name'],
            alias_name=data.get('alias_name'),
            is_router=data.get('is_router', False),
            metadata=data.get('metadata', {}),
            spec_id=data.get('spec_id', str(uuid.uuid4())),
        )

    def instantiate(self) -> 'BaseNode':
        """Instantiate a fresh node instance from this spec.

        This is called at execution time (not build time) to create
        the actual node instance that will execute.

        Returns:
            Fresh BaseNode instance with properties from this spec
        """
        # Prefer in-memory reference for dynamically created nodes
        if self._node_type_ref is not None:
            # Check if it's a NodeType or a BaseNode instance
            if hasattr(self._node_type_ref, 'node_instance'):
                # It's a NodeType - get fresh instance
                instance = self._node_type_ref.node_instance
            else:
                # It's a BaseNode instance (Decision, etc.) - return as-is
                # These are already instantiated and stateful
                instance = self._node_type_ref
        else:
            # Fallback to module import for persistent classes
            import importlib

            # Parse the fully qualified class name
            module_path, class_name = self.node_type_class.rsplit('.', 1)

            # Dynamically import the module and get the class
            module = importlib.import_module(module_path)
            node_class = getattr(module, class_name)

            # Create fresh instance
            instance = node_class()

        # Set names from spec (only for fresh instances, not pre-existing ones)
        if hasattr(self._node_type_ref, 'node_instance'):
            instance.name = self.node_name
            instance.canonical_name = self.canonical_name
            if self.alias_name:
                instance.alias_name = self.alias_name

            # Set router flag
            instance._is_router = self.is_router

            # Apply any metadata
            for key, value in self.metadata.items():
                setattr(instance, key, value)
        else:
            # Pre-existing BaseNode instance - still need to set router flag
            # This is critical for nested decisions where routers are re-instantiated
            instance._is_router = self.is_router

        return instance


@dataclass
class SequenceSpec(NodeSpec):
    """Specification for a nested Sequence node.

    Preserves encapsulation - the nested sequence is treated as
    a logical unit with its own internal ChainSpec.

    This enables the Lego composability pattern where sequences can be
    composed like any other node while preserving their internal structure.

    Attributes:
        sub_chain_spec: The nested sequence's internal ChainSpec
        (inherits all NodeSpec fields: node_type_class, node_name, etc.)
    """
    sub_chain_spec: 'ChainSpec' = field(default_factory=lambda: None)  # Will be set after ChainSpec is defined

    def __post_init__(self):
        """Initialize sub_chain_spec after ChainSpec is available."""
        if self.sub_chain_spec is None:
            self.sub_chain_spec = ChainSpec()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary including nested ChainSpec."""
        base_dict = super().to_dict()
        base_dict['sub_chain_spec'] = self.sub_chain_spec.to_dict()
        return base_dict

    def instantiate(self) -> 'BaseNode':
        """Instantiate the nested Sequence with its internal structure.

        Returns:
            Fresh Sequence instance with internal ChainSpec preserved
        """
        # Import here to avoid circular dependencies
        from egregore.core.workflow.sequence import Sequence

        # Create Sequence with ChainBuilder that converts to this sub_chain_spec
        # We'll need to create the sequence with the sub_chain_spec directly
        sequence = Sequence.__new__(Sequence)

        # Initialize basic attributes from BaseNode that __new__ skips
        import uuid
        sequence.guid = str(uuid.uuid4())
        sequence.next_node = None
        sequence._first_node = sequence
        sequence._prev_shift = None
        sequence._chain_start = None

        # Set name attributes
        sequence.name = self.node_name
        sequence.canonical_name = self.canonical_name
        sequence.alias_name = self.alias_name if self.alias_name else None

        # Store the ChainSpec for later instantiation
        sequence._chain_spec = self.sub_chain_spec

        # Initialize other required Sequence attributes
        from datetime import datetime
        from egregore.core.workflow.state import SharedState
        from egregore.core.workflow.nodes.registry import NodeRegistry
        from egregore.core.workflow.sequence.controller import WorkflowController

        sequence.state = SharedState(instance_name=sequence.name)
        sequence.state.workflow = sequence
        sequence.max_steps = 1000
        sequence.workflow_id = str(uuid.uuid4())
        sequence.created_at = datetime.now()
        sequence._local_node_registry = NodeRegistry()
        sequence._template_chain = None  # Not used in ChainSpec mode
        sequence.start = None  # Will be set by execute()
        sequence.controller = WorkflowController(sequence)
        sequence._hooks_proxy = None

        # Initialize graph attributes
        sequence._graph = None
        sequence._graph_built = False
        sequence._owns_state = False  # Nested Sequence shares parent's state

        # Register with node registry
        from egregore.core.workflow.nodes.base import _get_active_registry
        registry = _get_active_registry()
        registry.register_node(sequence)

        return sequence


@dataclass
class ChainSpec:
    """Serializable specification of a complete workflow chain.

    This captures the entire workflow graph structure as pure data:
    - List of NodeSpec objects (the nodes)
    - List of edges (connections between nodes)
    - Metadata about the workflow itself

    Attributes:
        nodes: List of NodeSpec objects defining each node
        edges: List of (source_idx, target_idx) tuples defining connections
        metadata: Additional workflow-level configuration
        spec_id: Unique identifier for this workflow
    """
    nodes: List[NodeSpec] = field(default_factory=list)
    edges: List[Tuple[int, int]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    spec_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for JSON/network transport."""
        return {
            'nodes': [node.to_dict() for node in self.nodes],
            'edges': self.edges,
            'metadata': self.metadata,
            'spec_id': self.spec_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChainSpec':
        """Deserialize from dictionary."""
        # Deserialize nodes - check if any are SequenceSpec
        nodes = []
        for n in data['nodes']:
            if 'sub_chain_spec' in n:
                # This is a SequenceSpec
                nodes.append(SequenceSpec(
                    node_type_class=n['node_type_class'],
                    node_name=n['node_name'],
                    canonical_name=n['canonical_name'],
                    alias_name=n.get('alias_name'),
                    metadata=n.get('metadata', {}),
                    spec_id=n.get('spec_id', str(uuid.uuid4())),
                    sub_chain_spec=ChainSpec.from_dict(n['sub_chain_spec'])
                ))
            else:
                # Regular NodeSpec
                nodes.append(NodeSpec.from_dict(n))

        return cls(
            nodes=nodes,
            edges=[tuple(e) for e in data['edges']],
            metadata=data.get('metadata', {}),
            spec_id=data.get('spec_id', str(uuid.uuid4())),
        )

    def get_start_node_idx(self) -> int:
        """Find the index of the starting node (no incoming edges).

        Returns:
            Index of the start node in self.nodes

        Raises:
            ValueError: If no start node found or multiple start nodes exist
        """
        if not self.nodes:
            raise ValueError("ChainSpec has no nodes")

        # Find nodes with no incoming edges
        target_indices = {target for _, target in self.edges}
        start_indices = [i for i in range(len(self.nodes)) if i not in target_indices]

        if len(start_indices) == 0:
            raise ValueError("No start node found (all nodes have incoming edges)")
        if len(start_indices) > 1:
            raise ValueError(f"Multiple start nodes found: {start_indices}")

        return start_indices[0]

    def instantiate_node(self, idx: int) -> 'BaseNode':
        """Instantiate a specific node by index.

        Args:
            idx: Index of node in self.nodes

        Returns:
            Fresh BaseNode instance
        """
        if idx < 0 or idx >= len(self.nodes):
            raise IndexError(f"Node index {idx} out of range (have {len(self.nodes)} nodes)")

        return self.nodes[idx].instantiate()

    def instantiate_chain(self) -> 'BaseNode':
        """Instantiate the complete workflow chain.

        Creates fresh instances for all nodes and wires them together
        according to the edge specifications.

        Returns:
            The start node of the instantiated chain
        """
        if not self.nodes:
            raise ValueError("Cannot instantiate empty ChainSpec")

        # Create fresh instances for all nodes
        instances = [node.instantiate() for node in self.nodes]

        # Wire up connections based on edges
        for source_idx, target_idx in self.edges:
            source = instances[source_idx]
            target = instances[target_idx]
            source.next_node = target

        # Find and return start node
        start_idx = self.get_start_node_idx()
        return instances[start_idx]


class ChainBuilder:
    """Builder for constructing workflow chains without instantiation.

    This is the key class that replaces instance-based chain building.
    Instead of creating node instances during >> operations, it captures
    the chain structure as metadata (NodeType references and connections).

    The >> operator builds a ChainBuilder, which can then be converted to
    a serializable ChainSpec for distribution or storage.

    Attributes:
        node_types: List of NodeType wrappers (not instances!)
        edges: List of (source_idx, target_idx) connection tuples
        alias_map: Map of node_idx -> alias_name for aliased nodes
    """

    def __init__(
        self,
        node_types: Optional[List['NodeType']] = None,
        edges: Optional[List[Tuple[int, int]]] = None,
        alias_map: Optional[Dict[int, str]] = None,
    ):
        """Initialize chain builder.

        Args:
            node_types: List of NodeType wrappers (not instances)
            edges: List of (source_idx, target_idx) tuples
            alias_map: Map of node_idx -> alias_name
        """
        self.node_types: List['NodeType'] = node_types or []
        self.edges: List[Tuple[int, int]] = edges or []
        self.alias_map: Dict[int, str] = alias_map or {}

    @classmethod
    def from_single(cls, node_type: 'NodeType', alias_name: Optional[str] = None) -> 'ChainBuilder':
        """Create builder from a single NodeType.

        Args:
            node_type: NodeType wrapper
            alias_name: Optional alias name for this node

        Returns:
            ChainBuilder with single node
        """
        alias_map = {0: alias_name} if alias_name else {}
        return cls(node_types=[node_type], edges=[], alias_map=alias_map)

    @classmethod
    def from_chain(cls, left: 'ChainBuilder', right: 'ChainBuilder') -> 'ChainBuilder':
        """Create builder by chaining two builders together.

        This is called by the >> operator to build up the chain structure
        without creating any instances.

        Args:
            left: Left-hand ChainBuilder (upstream)
            right: Right-hand ChainBuilder (downstream)

        Returns:
            New ChainBuilder with combined structure
        """
        # Combine node lists
        combined_nodes = left.node_types + right.node_types

        # Offset right edges by left node count
        left_count = len(left.node_types)
        offset_right_edges = [(s + left_count, t + left_count) for s, t in right.edges]

        # Combine edges and add connection between chains
        combined_edges = left.edges + offset_right_edges

        # Find left chain end (node with no outgoing edges)
        left_sources = {s for s, _ in left.edges}
        left_end_candidates = [i for i in range(len(left.node_types)) if i not in left_sources]
        left_end = left_end_candidates[-1] if left_end_candidates else len(left.node_types) - 1

        # Find right chain start (node with no incoming edges)
        right_targets = {t for _, t in right.edges}
        right_start_candidates = [i for i in range(len(right.node_types)) if i not in right_targets]
        right_start = right_start_candidates[0] if right_start_candidates else 0

        # Add edge connecting left end to right start
        combined_edges.append((left_end, right_start + left_count))

        # Combine alias maps (offset right indices)
        combined_alias_map = left.alias_map.copy()
        for idx, alias in right.alias_map.items():
            combined_alias_map[idx + left_count] = alias

        return cls(
            node_types=combined_nodes,
            edges=combined_edges,
            alias_map=combined_alias_map,
        )

    def to_spec(self) -> ChainSpec:
        """Convert builder to serializable ChainSpec.

        This is the key step that transforms metadata into a form
        that can be serialized for network transport or storage.

        Handles both NodeType and Sequence instances in node_types list.
        Sequence instances become SequenceSpec with nested ChainSpec.

        Returns:
            ChainSpec with NodeSpec objects and edge list
        """
        from egregore.core.workflow.sequence import Sequence

        # Create NodeSpec for each NodeType, SequenceSpec for Sequence, or handle BaseNode instances
        node_specs = []
        for idx, node_type in enumerate(self.node_types):
            # Check if this is a Sequence instance (not NodeType)
            if isinstance(node_type, Sequence):
                # Create SequenceSpec for nested Sequence
                # All Sequences now have _chain_spec (no legacy _template_chain)
                if hasattr(node_type, '_chain_spec') and node_type._chain_spec:
                    sub_chain_spec = node_type._chain_spec
                else:
                    # Empty or improperly initialized Sequence - create empty ChainSpec
                    sub_chain_spec = ChainSpec()

                # Build fully qualified class name for Sequence
                fqcn = f"{node_type.__class__.__module__}.{node_type.__class__.__name__}"

                spec = SequenceSpec(
                    node_type_class=fqcn,
                    node_name=node_type.name,
                    canonical_name=node_type.name,
                    alias_name=self.alias_map.get(idx),
                    sub_chain_spec=sub_chain_spec,
                )
            elif not hasattr(node_type, 'node'):
                # This is a BaseNode instance (Decision, custom nodes, etc.), not a NodeType
                # Store it as-is with an in-memory reference
                from egregore.core.workflow.nodes.base import BaseNode

                fqcn = f"{node_type.__class__.__module__}.{node_type.__class__.__name__}"
                node_name = getattr(node_type, 'name', node_type.__class__.__name__)

                # Get router flag if present
                is_router = getattr(node_type, '_is_router', False)

                # Extract type hints for router detection (store in metadata)
                # For instantiated nodes, check if they have _source_node_type reference
                metadata = {}
                if hasattr(node_type, '_source_node_type') and node_type._source_node_type:
                    # Instance has reference to original NodeType - use its exec function
                    source_node_type = node_type._source_node_type
                    if hasattr(source_node_type, 'exec'):
                        try:
                            from typing import get_type_hints, get_origin, get_args
                            import typing
                            import inspect

                            hints = get_type_hints(source_node_type.exec)
                            if 'return' in hints:
                                return_type = hints['return']
                                origin = get_origin(return_type)

                                # Store whether this is a Literal return type (classifier)
                                metadata['is_literal_return'] = (origin is typing.Literal)

                                # If Literal, also store the possible values
                                if origin is typing.Literal:
                                    metadata['literal_values'] = list(get_args(return_type))

                                # Store input/output type info for transformer detection
                                sig = inspect.signature(source_node_type.exec)
                                input_params = {
                                    k: v for k, v in hints.items()
                                    if k != 'return' and k not in ['state', 'context', 'workflow']
                                }

                                if input_params:
                                    first_param_type = next(iter(input_params.values()))
                                    # Store whether input/output types match (transformer pattern)
                                    metadata['same_input_output_type'] = (first_param_type == return_type)
                        except Exception:
                            # Type hints might not be available or might fail
                            pass

                spec = NodeSpec(
                    node_type_class=fqcn,
                    node_name=node_name,
                    canonical_name=node_name,
                    alias_name=self.alias_map.get(idx),
                    is_router=is_router,
                    metadata=metadata,
                    _node_type_ref=node_type,  # Store instance for re-use
                )
            else:
                # Regular NodeType - existing logic
                node_class = node_type.node
                node_name = getattr(node_class, '__name__', 'UnknownNode')

                # Build fully qualified class name
                module = node_class.__module__
                class_name = node_class.__name__
                fqcn = f"{module}.{class_name}"

                # Get canonical name (original @node('name') parameter)
                # This requires NodeType to store the original name
                canonical_name = getattr(node_type, '_original_name', node_name)

                # Get alias if present
                alias_name = self.alias_map.get(idx)

                # Get router flag if present
                is_router = getattr(node_type, '_is_router', False)

                # Extract type hints for router detection (store in metadata)
                metadata = {}
                if hasattr(node_type, 'exec'):
                    try:
                        from typing import get_type_hints, get_origin, get_args
                        import typing
                        import inspect

                        hints = get_type_hints(node_type.exec)
                        if 'return' in hints:
                            return_type = hints['return']
                            origin = get_origin(return_type)

                            # Store whether this is a Literal return type (classifier)
                            metadata['is_literal_return'] = (origin is typing.Literal)

                            # If Literal, also store the possible values
                            if origin is typing.Literal:
                                metadata['literal_values'] = list(get_args(return_type))

                            # Store input/output type info for transformer detection
                            # Get first parameter type (skip 'state', 'context', 'workflow')
                            sig = inspect.signature(node_type.exec)
                            input_params = {
                                k: v for k, v in hints.items()
                                if k != 'return' and k not in ['state', 'context', 'workflow']
                            }

                            if input_params:
                                first_param_type = next(iter(input_params.values()))
                                # Store whether input/output types match (transformer pattern)
                                metadata['same_input_output_type'] = (first_param_type == return_type)
                    except Exception:
                        # Type hints might not be available or might fail
                        pass

                # Create NodeSpec with in-memory reference
                spec = NodeSpec(
                    node_type_class=fqcn,
                    node_name=canonical_name,
                    canonical_name=canonical_name,
                    alias_name=alias_name,
                    is_router=is_router,
                    metadata=metadata,
                    _node_type_ref=node_type,  # Store NodeType for in-memory instantiation
                )

            node_specs.append(spec)

        # Create ChainSpec
        return ChainSpec(
            nodes=node_specs,
            edges=self.edges,
        )

    def __rshift__(self, other) -> 'ChainBuilder':
        """Chain builder with another builder: self >> other.

        This enables the >> operator to build up chain metadata
        without creating any instances.

        Accepts ChainBuilder, NodeType, or BaseNode instances for flexibility.

        Args:
            other: Right-hand ChainBuilder, NodeType, or BaseNode instance

        Returns:
            New ChainBuilder with combined structure
        """
        from egregore.core.workflow.nodes.node_types import NodeType
        from egregore.core.workflow.nodes.base import BaseNode
        from egregore.core.workflow.nodes.decision import Decision

        # Router detection: Check if 'other' is a Decision node BEFORE converting
        # If so, mark last node in 'self' as router
        is_decision = False
        if isinstance(other, Decision):
            is_decision = True
        elif isinstance(other, BaseNode):
            # Check class name in case it's a Decision subclass
            is_decision = other.__class__.__name__ == 'Decision'
        elif isinstance(other, ChainBuilder):
            # Check if ChainBuilder contains a Decision as first node
            if other.node_types and len(other.node_types) > 0:
                first_node = other.node_types[0]
                if isinstance(first_node, Decision):
                    is_decision = True
                elif isinstance(first_node, BaseNode):
                    is_decision = first_node.__class__.__name__ == 'Decision'

        # Convert NodeType to ChainBuilder if needed (for symmetry)
        if isinstance(other, NodeType):
            other = ChainBuilder.from_single(other)
        elif isinstance(other, BaseNode):
            # BaseNode instance (Decision, Sequence, custom nodes)
            # Wrap in ChainBuilder to preserve as-is
            other = ChainBuilder(
                node_types=[other],
                edges=[],
                alias_map={}
            )
        elif not isinstance(other, ChainBuilder):
            raise TypeError(
                f"Cannot chain ChainBuilder with {type(other).__name__}. "
                f"Expected ChainBuilder, NodeType, or BaseNode."
            )

        # Mark router before combining chains
        if is_decision and self.node_types:
            # Mark last node in self as router by setting metadata
            # We'll propagate this to NodeSpec in to_spec()
            last_idx = len(self.node_types) - 1
            last_node = self.node_types[last_idx]

            # Set router flag on the NodeType or BaseNode instance
            if hasattr(last_node, 'node_instance'):
                # NodeType - set flag on the template (will be copied to instances)
                last_node._is_router = True
            elif hasattr(last_node, '_is_router'):
                # BaseNode instance - set flag directly
                last_node._is_router = True

        return ChainBuilder.from_chain(self, other)

    def __rrshift__(self, other):
        """Handle reverse right shift: other >> self.

        This is called when ChainBuilder is on the right side of >> and the
        left operand doesn't define __rshift__. Common cases:
        - str >> ChainBuilder (creates NodeMapper for decision branches)
        - bool >> ChainBuilder (creates NodeMapper for decision branches)
        - Any condition >> ChainBuilder (creates NodeMapper)

        Args:
            other: Left-hand operand (condition for decision branch)

        Returns:
            NodeMapper wrapping the condition and ChainBuilder
        """
        from egregore.core.workflow.nodes.node import NodeMapper

        # Create NodeMapper with condition and ChainBuilder target
        return NodeMapper(other, self)

    def __repr__(self) -> str:
        """String representation for debugging."""
        node_names = []
        for nt in self.node_types:
            if hasattr(nt, 'node'):
                # NodeType wrapper
                node_names.append(nt.node.__name__)
            elif hasattr(nt, 'name'):
                # BaseNode instance (Sequence, Decision, etc.)
                node_names.append(nt.name)
            else:
                node_names.append(str(type(nt).__name__))
        return f"ChainBuilder(nodes={node_names}, edges={self.edges})"
