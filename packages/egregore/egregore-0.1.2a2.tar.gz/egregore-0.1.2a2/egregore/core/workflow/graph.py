"""
Graph-Based Execution System

This module provides the graph infrastructure for workflow execution,
enabling proper router detection for nested decisions and parallel execution.

Architecture:
- Graph: Complete representation of workflow execution structure
- GraphNode: Individual nodes with parent-child relationships
- GraphEdge: Connections between nodes with execution semantics
- Subgraph: Branch structures for Decisions and Parallels
- GraphBuilder: Constructs graphs from workflow chains
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, get_type_hints, get_origin, get_args
from enum import Enum
import typing


class NodeTypeEnum(str, Enum):
    """Types of nodes in the execution graph."""
    NODE = "node"
    DECISION = "decision"
    SEQUENCE = "sequence"
    PARALLEL = "parallel"


class EdgeTypeEnum(str, Enum):
    """Types of edges connecting nodes.

    Note: Loops are implicit through node reuse in the graph topology.
    When a branch references an existing node, the graph becomes cyclic.
    No special LOOP edge type is needed - the controller detects cycles
    through node revisitation tracking.
    """
    SEQUENTIAL = "sequential"  # Linear next_node connection
    BRANCH = "branch"  # Decision branch based on condition
    PARALLEL = "parallel"  # Parallel execution branch


class ExecutionModeEnum(str, Enum):
    """Execution modes for subgraphs."""
    SEQUENTIAL = "sequential"  # Decision branches execute sequentially
    PARALLEL = "parallel"  # Parallel branches execute concurrently
    CONCURRENT = "concurrent"  # Future: distributed concurrent execution


@dataclass
class GraphNode:
    """Represents a node in the execution graph.

    Tracks node identity, type, relationships, and router status.
    """
    id: str  # Unique identifier (typically node.guid)
    node_instance: Any  # Reference to actual BaseNode instance
    node_type: NodeTypeEnum  # Type of node
    parent: Optional['GraphNode'] = None  # Parent node in graph hierarchy
    children: List['GraphNode'] = field(default_factory=list)  # Child nodes
    is_router: bool = False  # True if this node is a router for a decision
    canonical_name: Optional[str] = None  # For aliased nodes, the original name
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional metadata

    def __hash__(self):
        """Make GraphNode hashable for use in sets/dicts."""
        return hash(self.id)

    def __eq__(self, other):
        """GraphNode equality based on ID."""
        if not isinstance(other, GraphNode):
            return False
        return self.id == other.id


@dataclass
class GraphEdge:
    """Represents a connection between nodes in the graph.

    Tracks edge type, conditions, and execution semantics.
    """
    from_node: GraphNode  # Source node
    to_node: GraphNode  # Target node
    edge_type: EdgeTypeEnum  # Type of connection
    condition: Optional[Any] = None  # For branch edges, the condition/pattern
    can_execute_parallel: bool = False  # True for parallel edges
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional metadata


@dataclass
class Subgraph:
    """Represents a branch subgraph for Decisions or Parallels.

    Each Decision branch or Parallel branch has its own subgraph with
    independent execution context and router mappings.
    """
    pattern: str  # Condition that triggers this branch (or parallel index)
    root_node: GraphNode  # First node in the subgraph
    nodes: List[GraphNode] = field(default_factory=list)  # All nodes in subgraph
    edges: List[GraphEdge] = field(default_factory=list)  # Edges within subgraph
    terminal_node: Optional[GraphNode] = None  # Last node in subgraph
    execution_mode: ExecutionModeEnum = ExecutionModeEnum.SEQUENTIAL
    parent_graph_node: Optional[GraphNode] = None  # Link back to Decision/Parallel node
    router_node: Optional[GraphNode] = None  # Router for this branch (if applicable)
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional metadata


class Graph:
    """Complete representation of workflow execution graph.

    Stores all nodes, edges, and subgraphs with methods for querying
    structure, finding routers, and navigating execution paths.
    """

    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}  # node_id -> GraphNode
        self.edges: List[GraphEdge] = []  # All edges in graph
        self.root_node: Optional[GraphNode] = None  # Entry point
        self.decision_subgraphs: Dict[str, List[Subgraph]] = {}  # decision_id -> subgraphs
        self.parallel_subgraphs: Dict[str, List[Subgraph]] = {}  # parallel_id -> subgraphs
        self.router_mappings: Dict[str, str] = {}  # decision_id -> router_node_id

    def add_node(self, node_instance: Any, node_type: NodeTypeEnum,
                 parent: Optional[GraphNode] = None, is_router: bool = False,
                 canonical_name: Optional[str] = None) -> GraphNode:
        """Add a node to the graph.

        Args:
            node_instance: The actual BaseNode instance
            node_type: Type of node (node, decision, sequence, parallel)
            parent: Parent GraphNode in hierarchy
            is_router: Whether this node is a router
            canonical_name: Original name if this is an aliased node

        Returns:
            Created GraphNode
        """
        node_id = self._get_node_id(node_instance)

        # Check if node already exists (node reuse scenario)
        if node_id in self.nodes:
            return self.nodes[node_id]

        graph_node = GraphNode(
            id=node_id,
            node_instance=node_instance,
            node_type=node_type,
            parent=parent,
            is_router=is_router,
            canonical_name=canonical_name
        )

        self.nodes[node_id] = graph_node

        # Set as root if first node
        if self.root_node is None:
            self.root_node = graph_node

        # Update parent's children
        if parent:
            parent.children.append(graph_node)

        return graph_node

    def add_edge(self, from_node: GraphNode, to_node: GraphNode,
                 edge_type: EdgeTypeEnum, condition: Optional[Any] = None,
                 can_execute_parallel: bool = False) -> GraphEdge:
        """Add an edge between two nodes.

        Args:
            from_node: Source GraphNode
            to_node: Target GraphNode
            edge_type: Type of edge
            condition: Optional condition for branch edges
            can_execute_parallel: Whether edge supports parallel execution

        Returns:
            Created GraphEdge
        """
        edge = GraphEdge(
            from_node=from_node,
            to_node=to_node,
            edge_type=edge_type,
            condition=condition,
            can_execute_parallel=can_execute_parallel
        )

        self.edges.append(edge)
        return edge

    def add_subgraph(self, parent_node: GraphNode, pattern: str,
                     subgraph: Subgraph):
        """Add a subgraph for a Decision or Parallel node.

        Args:
            parent_node: The Decision or Parallel GraphNode
            pattern: The condition/pattern for this branch
            subgraph: The Subgraph object
        """
        if parent_node.node_type == NodeTypeEnum.DECISION:
            if parent_node.id not in self.decision_subgraphs:
                self.decision_subgraphs[parent_node.id] = []
            self.decision_subgraphs[parent_node.id].append(subgraph)
        elif parent_node.node_type == NodeTypeEnum.PARALLEL:
            if parent_node.id not in self.parallel_subgraphs:
                self.parallel_subgraphs[parent_node.id] = []
            self.parallel_subgraphs[parent_node.id].append(subgraph)

    def mark_router(self, router_node: GraphNode, decision_node: GraphNode):
        """Mark a node as router for a specific decision.

        Args:
            router_node: The node that acts as router
            decision_node: The decision node that will use this router
        """
        router_node.is_router = True
        self.router_mappings[decision_node.id] = router_node.id

    def get_router_for_decision(self, decision_node: GraphNode) -> Optional[GraphNode]:
        """Get the router node for a specific decision.

        Args:
            decision_node: The Decision GraphNode

        Returns:
            Router GraphNode or None if not found
        """
        router_id = self.router_mappings.get(decision_node.id)
        if router_id:
            return self.nodes.get(router_id)
        return None

    def get_decision_for_router(self, router_node: GraphNode) -> Optional[GraphNode]:
        """Get the decision node that uses this router (reverse lookup).

        Args:
            router_node: The router GraphNode

        Returns:
            Decision GraphNode or None if not found
        """
        # Reverse lookup in router_mappings
        for decision_id, router_id in self.router_mappings.items():
            if router_id == router_node.id:
                return self.nodes.get(decision_id)
        return None

    def get_subgraphs(self, node: GraphNode) -> List[Subgraph]:
        """Get all subgraphs for a Decision or Parallel node.

        Args:
            node: The Decision or Parallel GraphNode

        Returns:
            List of Subgraph objects
        """
        if node.node_type == NodeTypeEnum.DECISION:
            return self.decision_subgraphs.get(node.id, [])
        elif node.node_type == NodeTypeEnum.PARALLEL:
            return self.parallel_subgraphs.get(node.id, [])
        return []

    def get_parent_decision(self, node: GraphNode) -> Optional[GraphNode]:
        """Get the parent Decision node for a given node.

        Walks up parent chain to find nearest Decision node.

        Args:
            node: The GraphNode to start from

        Returns:
            Parent Decision GraphNode or None
        """
        current = node.parent
        while current:
            if current.node_type == NodeTypeEnum.DECISION:
                return current
            current = current.parent
        return None

    def get_execution_path(self, from_node: GraphNode,
                          to_node: GraphNode) -> List[GraphNode]:
        """Get the execution path from one node to another.

        Uses BFS to find shortest path through graph edges.

        Args:
            from_node: Starting GraphNode
            to_node: Target GraphNode

        Returns:
            List of GraphNodes representing the path
        """
        if from_node == to_node:
            return [from_node]

        # BFS to find path
        queue = [(from_node, [from_node])]
        visited: Set[str] = {from_node.id}

        while queue:
            current, path = queue.pop(0)

            # Find edges from current node
            for edge in self.edges:
                if edge.from_node == current and edge.to_node.id not in visited:
                    new_path = path + [edge.to_node]

                    if edge.to_node == to_node:
                        return new_path

                    visited.add(edge.to_node.id)
                    queue.append((edge.to_node, new_path))

        return []  # No path found

    def find_node_by_instance(self, node_instance: Any) -> Optional[GraphNode]:
        """Find GraphNode by its node_instance reference.

        Args:
            node_instance: The BaseNode instance to find

        Returns:
            GraphNode or None if not found
        """
        node_id = self._get_node_id(node_instance)
        return self.nodes.get(node_id)

    def _get_node_id(self, node_instance: Any) -> str:
        """Get unique ID for a node instance.

        Uses guid if available, otherwise falls back to id().

        Args:
            node_instance: The BaseNode instance

        Returns:
            Unique string identifier
        """
        if hasattr(node_instance, 'guid'):
            return str(node_instance.guid)
        return str(id(node_instance))

    def get_next_nodes(self, current_node: GraphNode) -> List[GraphNode]:
        """Get next nodes from current node by following edges.

        Args:
            current_node: Current GraphNode

        Returns:
            List of next GraphNodes (usually 1, but can be multiple for branches)
        """
        next_nodes = []
        for edge in self.edges:
            if edge.from_node == current_node:
                next_nodes.append(edge.to_node)
        return next_nodes

    def get_outgoing_edges(self, current_node: GraphNode) -> List[GraphEdge]:
        """Get all outgoing edges from a node.

        Args:
            current_node: Current GraphNode

        Returns:
            List of GraphEdge objects originating from this node
        """
        outgoing = []
        for edge in self.edges:
            if edge.from_node == current_node:
                outgoing.append(edge)
        return outgoing

    def get_incoming_edges(self, target_node: GraphNode) -> List[GraphEdge]:
        """Get all incoming edges to a node.

        Args:
            target_node: Target GraphNode

        Returns:
            List of GraphEdge objects pointing to this node
        """
        incoming = []
        for edge in self.edges:
            if edge.to_node == target_node:
                incoming.append(edge)
        return incoming

    def get_execution_order(self) -> List[GraphNode]:
        """Get topological execution order starting from root.

        Returns:
            List of GraphNodes in execution order
        """
        if not self.root_node:
            return []

        visited = set()
        order = []

        def visit(node: GraphNode):
            if node.id in visited:
                return
            visited.add(node.id)
            order.append(node)

            # Visit children in edge order
            for next_node in self.get_next_nodes(node):
                visit(next_node)

        visit(self.root_node)
        return order

    def __repr__(self) -> str:
        """String representation of graph."""
        node_count = len(self.nodes)
        edge_count = len(self.edges)
        decision_count = len(self.decision_subgraphs)
        parallel_count = len(self.parallel_subgraphs)

        return (f"Graph(nodes={node_count}, edges={edge_count}, "
                f"decisions={decision_count}, parallels={parallel_count})")


class GraphBuilder:
    """Constructs execution graph from workflow chains.

    Walks through node chains using next_node pointers, identifies
    Decisions and Parallels, creates subgraphs for branches, and
    marks router nodes.
    """

    def __init__(self):
        self.graph = Graph()
        self.current_parent: Optional[GraphNode] = None
        self.decision_stack: List[GraphNode] = []  # Track nested Decisions
        self.parallel_stack: List[GraphNode] = []  # Track nested Parallels
        self.visited_nodes: Set[str] = set()  # Track processed nodes
        self.canonical_name_map: Dict[str, GraphNode] = {}  # Track nodes by canonical_name for reuse

    def build_from_sequence(self, sequence: Any) -> Graph:
        """Build graph from a Sequence's ChainSpec.

        Entry point for graph construction. Works with ChainSpec
        (the serializable workflow specification) to build the graph.

        Args:
            sequence: The Sequence instance with _chain_spec attribute

        Returns:
            Complete Graph object
        """
        if not hasattr(sequence, '_chain_spec') or sequence._chain_spec is None:
            return self.graph

        # Build graph from ChainSpec
        return self._build_from_chain_spec(sequence._chain_spec)

    def _build_from_chain_spec(self, chain_spec: Any) -> Graph:
        """Build graph from a ChainSpec.

        Processes NodeSpec list and edges to construct graph structure.

        Args:
            chain_spec: ChainSpec object with nodes and edges

        Returns:
            Complete Graph object
        """
        if not hasattr(chain_spec, 'nodes') or not chain_spec.nodes:
            return self.graph

        # Create GraphNodes for each NodeSpec
        node_map = {}  # Map from spec index to GraphNode

        for idx, node_spec in enumerate(chain_spec.nodes):
            # Determine node type
            node_type = self._get_node_type_from_spec(node_spec)

            # Check if router
            is_router = getattr(node_spec, 'is_router', False)

            # Get canonical name
            canonical_name = getattr(node_spec, 'canonical_name', None)

            # Create new GraphNode for each NodeSpec (no reuse in main sequence)
            # Each NodeSpec has unique spec_id → each gets unique GraphNode
            # Node reuse ONLY happens in decision branches (see _process_branch_from_chain_builder)
            graph_node = GraphNode(
                id=node_spec.spec_id,
                node_instance=node_spec,  # Store spec, not instance
                node_type=node_type,
                is_router=is_router,
                canonical_name=canonical_name
            )

            # Extract return type information for router detection
            self._store_return_type_info(graph_node, node_spec)

            self.graph.nodes[node_spec.spec_id] = graph_node
            node_map[idx] = graph_node

            # Track by ALIAS_NAME for explicit loop detection
            # Only aliased nodes can be referenced to create loops
            alias_name = getattr(node_spec, 'alias_name', None)
            if alias_name:
                self.canonical_name_map[alias_name] = graph_node

            # Set root if first node
            if self.graph.root_node is None:
                self.graph.root_node = graph_node

        # Create edges
        for source_idx, target_idx in chain_spec.edges:
            source_node = node_map.get(source_idx)
            target_node = node_map.get(target_idx)

            if source_node and target_node:
                self.graph.add_edge(
                    source_node,
                    target_node,
                    EdgeTypeEnum.SEQUENTIAL
                )

                # Set parent relationship
                if target_node.parent is None:
                    target_node.parent = source_node
                    source_node.children.append(target_node)

        # Process Decisions and Parallels for subgraphs
        for idx, node_spec in enumerate(chain_spec.nodes):
            graph_node = node_map[idx]

            if graph_node.node_type == NodeTypeEnum.DECISION:
                self._process_decision_from_spec(node_spec, graph_node, node_map)
            elif graph_node.node_type == NodeTypeEnum.PARALLEL:
                self._process_parallel_from_spec(node_spec, graph_node, node_map)

        # Validate decision patterns against Literal return types
        self._validate_decision_patterns()

        return self.graph

    def _node_produces_data(self, graph_node: GraphNode) -> bool:
        """Check if a node produces data (vs routing/orchestrating).

        Property-based check: looks for _produces_data attribute on node instance.

        Args:
            graph_node: The GraphNode to check

        Returns:
            True if node produces data, False if it's control flow
        """
        node_instance = graph_node.node_instance

        # Check for _produces_data property
        # For NodeSpecs (lazy construction), check _node_type_ref
        if hasattr(node_instance, '_node_type_ref') and node_instance._node_type_ref:
            source_node = node_instance._node_type_ref
            return getattr(source_node, '_produces_data', True)

        # For instantiated nodes, check directly
        return getattr(node_instance, '_produces_data', True)

    def _find_router_node(self, decision_node: GraphNode) -> Optional[GraphNode]:
        """Find the router node for a decision by walking up parent chain.

        Simple algorithm:
        1. Start from decision's parent (the criteria provider)
        2. Walk up the parent chain, skipping control flow nodes
        3. First data-producing node is the router

        The criteria provider is the node that feeds routing criteria to the decision.
        For nested decisions, each decision has its own router (the node that feeds it criteria).

        Args:
            decision_node: The Decision GraphNode

        Returns:
            Router GraphNode or None if no data-producing parent found
        """
        if not decision_node.parent:
            return None

        # Start from decision's parent and walk up until we find a data-producing node
        current = decision_node.parent

        while current:
            if self._node_produces_data(current):
                # Found a data-producing node - this is the router
                return current

            current = current.parent

        # No data-producing parent found - fall back to decision's immediate parent
        return decision_node.parent

    def _process_chain(self, start_node: Any, parent: Optional[GraphNode] = None) -> Optional[GraphNode]:
        """Process a chain of nodes, creating graph structure.

        Walks through next_node pointers, handling regular nodes,
        Decisions, Parallels, and Sequences.

        Args:
            start_node: First node in chain
            parent: Parent GraphNode in hierarchy

        Returns:
            Last GraphNode in chain or None
        """
        if start_node is None:
            return None

        current_node = start_node
        last_graph_node = None
        prev_graph_node = None

        max_steps = 1000  # Safety limit
        step_count = 0

        while current_node is not None and step_count < max_steps:
            node_id = self.graph._get_node_id(current_node)

            # Check if we've already processed this node
            if node_id in self.visited_nodes:
                # Node reuse - already in graph
                graph_node = self.graph.nodes.get(node_id)
                if graph_node and prev_graph_node:
                    # Add edge from previous to this reused node
                    self.graph.add_edge(prev_graph_node, graph_node,
                                      EdgeTypeEnum.SEQUENTIAL)
                break

            self.visited_nodes.add(node_id)

            # Determine node type
            node_type = self._get_node_type(current_node)

            # Check if this is a router (has _is_router flag)
            is_router = getattr(current_node, '_is_router', False)

            # Get canonical name for aliased nodes
            canonical_name = getattr(current_node, 'canonical_name', None)

            # Create graph node
            graph_node = self.graph.add_node(
                node_instance=current_node,
                node_type=node_type,
                parent=parent if parent else self.current_parent,
                is_router=is_router,
                canonical_name=canonical_name
            )

            # Add edge from previous node
            if prev_graph_node:
                self.graph.add_edge(prev_graph_node, graph_node,
                                  EdgeTypeEnum.SEQUENTIAL)

            # Process based on node type
            if node_type == NodeTypeEnum.DECISION:
                self._process_decision(current_node, graph_node)
            elif node_type == NodeTypeEnum.PARALLEL:
                self._process_parallel(current_node, graph_node)
            elif node_type == NodeTypeEnum.SEQUENCE:
                self._process_sequence(current_node, graph_node)

            # Move to next node
            prev_graph_node = graph_node
            last_graph_node = graph_node
            current_node = getattr(current_node, 'next_node', None)
            step_count += 1

        return last_graph_node

    def _process_decision(self, decision_instance: Any, graph_node: GraphNode):
        """Process a Decision node and its branches.

        Creates subgraphs for each pattern branch and marks routers.

        Args:
            decision_instance: The Decision instance
            graph_node: The Decision's GraphNode
        """
        # Mark router: Find the first REGULAR node in parent chain
        # Skip Decision/Parallel/Sequence nodes as they don't produce data.
        # The immediate parent provides criteria, but we need the data provider.
        router_node = self._find_router_node(graph_node)
        if router_node and not router_node.is_router:
            self.graph.mark_router(router_node, graph_node)

        # Process each pattern branch
        if not hasattr(decision_instance, 'patterns'):
            return

        self.decision_stack.append(graph_node)

        for pattern in decision_instance.patterns:
            if not hasattr(pattern, 'target_node'):
                continue

            # Get branch chain (ChainBuilder or node instance)
            branch_chain = pattern.target_node

            # Create subgraph for this branch
            subgraph = self._process_branch_chain(
                branch_chain,
                graph_node,
                str(pattern)  # Pattern representation
            )

            if subgraph:
                self.graph.add_subgraph(graph_node, str(pattern), subgraph)

        self.decision_stack.pop()

    def _process_parallel(self, parallel_instance: Any, graph_node: GraphNode):
        """Process a Parallel node and its branches.

        Creates subgraphs for each parallel branch.

        Args:
            parallel_instance: The ParallelNode instance
            graph_node: The Parallel's GraphNode
        """
        if not hasattr(parallel_instance, 'parallel_nodes'):
            return

        self.parallel_stack.append(graph_node)

        for idx, parallel_node in enumerate(parallel_instance.parallel_nodes):
            # Create subgraph for this parallel branch
            subgraph = self._process_branch_chain(
                parallel_node,
                graph_node,
                f"parallel_{idx}"  # Pattern is parallel index
            )

            if subgraph:
                subgraph.execution_mode = ExecutionModeEnum.PARALLEL
                self.graph.add_subgraph(graph_node, f"parallel_{idx}", subgraph)

        self.parallel_stack.pop()

    def _process_sequence(self, sequence_instance: Any, graph_node: GraphNode):
        """Process a nested Sequence.

        Recursively builds subgraph for the sequence's chain.

        Args:
            sequence_instance: The Sequence instance
            graph_node: The Sequence's GraphNode
        """
        if not hasattr(sequence_instance, 'start'):
            return

        # Process the sequence's internal chain
        self._process_chain(sequence_instance.start, parent=graph_node)

    def _process_branch_chain(self, branch_start: Any, parent_node: GraphNode,
                             pattern: str) -> Optional[Subgraph]:
        """Process a branch chain (Decision/Parallel branch).

        Creates subgraph structure with nodes, edges, and terminal node.

        Args:
            branch_start: First node in branch (ChainBuilder or instance)
            parent_node: Parent Decision/Parallel GraphNode
            pattern: Pattern/condition for this branch

        Returns:
            Subgraph object or None
        """
        from egregore.core.workflow.chain_builder import ChainBuilder

        # If ChainBuilder, we need to walk its node_sequence
        if isinstance(branch_start, ChainBuilder):
            if not branch_start.node_sequence:
                return None
            actual_start = branch_start.node_sequence[0]
        else:
            actual_start = branch_start

        # Create subgraph
        subgraph = Subgraph(
            pattern=pattern,
            root_node=None,  # Will be set below
            parent_graph_node=parent_node
        )

        # Save current parent
        saved_parent = self.current_parent
        self.current_parent = parent_node

        # Process branch chain
        first_graph_node = None
        last_graph_node = None
        current_node = actual_start

        max_steps = 100
        step_count = 0

        while current_node is not None and step_count < max_steps:
            node_id = self.graph._get_node_id(current_node)

            # Skip if already processed (node reuse)
            if node_id in self.visited_nodes:
                graph_node = self.graph.nodes.get(node_id)
                if graph_node:
                    if first_graph_node is None:
                        first_graph_node = graph_node
                    last_graph_node = graph_node
                    subgraph.nodes.append(graph_node)
                break

            self.visited_nodes.add(node_id)

            node_type = self._get_node_type(current_node)
            is_router = getattr(current_node, '_is_router', False)
            canonical_name = getattr(current_node, 'canonical_name', None)

            graph_node = self.graph.add_node(
                node_instance=current_node,
                node_type=node_type,
                parent=parent_node,
                is_router=is_router,
                canonical_name=canonical_name
            )

            if first_graph_node is None:
                first_graph_node = graph_node
                subgraph.root_node = graph_node

            if last_graph_node:
                edge = self.graph.add_edge(last_graph_node, graph_node,
                                         EdgeTypeEnum.SEQUENTIAL)
                subgraph.edges.append(edge)

            subgraph.nodes.append(graph_node)

            # Recursively process nested structures
            if node_type == NodeTypeEnum.DECISION:
                self._process_decision(current_node, graph_node)
            elif node_type == NodeTypeEnum.PARALLEL:
                self._process_parallel(current_node, graph_node)
            elif node_type == NodeTypeEnum.SEQUENCE:
                self._process_sequence(current_node, graph_node)

            last_graph_node = graph_node
            current_node = getattr(current_node, 'next_node', None)
            step_count += 1

        subgraph.terminal_node = last_graph_node

        # Restore parent
        self.current_parent = saved_parent

        return subgraph if subgraph.root_node else None

    def _get_node_type(self, node_instance: Any) -> NodeTypeEnum:
        """Determine the type of a node instance.

        Args:
            node_instance: The node to classify

        Returns:
            NodeTypeEnum value
        """
        class_name = node_instance.__class__.__name__

        if 'Decision' in class_name:
            return NodeTypeEnum.DECISION
        elif 'Parallel' in class_name:
            return NodeTypeEnum.PARALLEL
        elif 'Sequence' in class_name:
            return NodeTypeEnum.SEQUENCE
        else:
            return NodeTypeEnum.NODE

    def _get_node_type_from_spec(self, node_spec: Any) -> NodeTypeEnum:
        """Determine node type from NodeSpec.

        Args:
            node_spec: NodeSpec object

        Returns:
            NodeTypeEnum value
        """
        # Check class name
        class_name = getattr(node_spec, 'node_type_class', '')

        if 'Decision' in class_name:
            return NodeTypeEnum.DECISION
        elif 'Parallel' in class_name:
            return NodeTypeEnum.PARALLEL
        elif 'Sequence' in class_name:
            return NodeTypeEnum.SEQUENCE
        else:
            return NodeTypeEnum.NODE

    def _process_decision_from_spec(self, node_spec: Any, graph_node: GraphNode,
                                    node_map: Dict[int, GraphNode]):
        """Process Decision node from NodeSpec.

        Instantiates Decision to access patterns and build subgraphs for branches.

        Args:
            node_spec: NodeSpec for the Decision
            graph_node: GraphNode for the Decision
            node_map: Map from spec index to GraphNode
        """
        # Mark router: Find the first REGULAR node in parent chain
        # Skip Decision/Parallel/Sequence nodes as they don't produce data.
        router_node = self._find_router_node(graph_node)
        if router_node:
            self.graph.mark_router(router_node, graph_node)

        # Get Decision instance - it's stored in _node_type_ref
        if not hasattr(node_spec, '_node_type_ref') or node_spec._node_type_ref is None:
            return

        decision_instance = node_spec._node_type_ref

        # Check if it has patterns (Decision nodes)
        if not hasattr(decision_instance, 'patterns'):
            return

        # Extract max_iter configuration from Decision
        max_iter = getattr(decision_instance, 'max_iter', None)
        raise_on_max_iter = getattr(decision_instance, 'raise_on_max_iter', False)

        # Take snapshot of nodes BEFORE processing ANY branches
        # This prevents sibling branches from reusing each other's nodes
        pre_decision_node_ids = set(self.graph.nodes.keys())

        # Process each pattern branch as a subgraph
        from egregore.core.workflow.chain_builder import ChainBuilder

        for pattern in decision_instance.patterns:
            if not hasattr(pattern, 'target_node'):
                continue

            branch_chain = pattern.target_node

            # If branch is a ChainBuilder, expand it into subgraph
            if isinstance(branch_chain, ChainBuilder):
                # Build subgraph from this ChainBuilder
                subgraph = self._process_branch_from_chain_builder(
                    branch_chain,
                    graph_node,
                    str(pattern),  # Pattern representation
                    pattern,  # Pass pattern object for DefaultPattern detection
                    pre_decision_node_ids  # Pass snapshot for sibling isolation
                )

                if subgraph:
                    # Store Decision's max_iter configuration in subgraph metadata
                    subgraph.metadata['max_iter'] = max_iter
                    subgraph.metadata['raise_on_max_iter'] = raise_on_max_iter
                    # Check if this is the default pattern (represented by "_")
                    from egregore.core.workflow.nodes.decision.patterns import DefaultPattern
                    subgraph.metadata['is_default_pattern'] = isinstance(pattern, DefaultPattern)

                    self.graph.add_subgraph(graph_node, str(pattern), subgraph)

    def _process_branch_from_chain_builder(self, chain_builder, parent_node: GraphNode,
                                          pattern: str, pattern_obj: Any = None,
                                          pre_decision_node_ids: Optional[Set[str]] = None) -> Optional[Subgraph]:
        """Build subgraph from a ChainBuilder (Decision branch).

        Args:
            chain_builder: ChainBuilder for the branch
            parent_node: Parent Decision GraphNode
            pattern: Pattern/condition for this branch
            pattern_obj: Pattern object (for checking if DefaultPattern)
            pre_decision_node_ids: Snapshot of node IDs before processing ANY branches (for sibling isolation)

        Returns:
            Subgraph object or None
        """
        from egregore.core.workflow.chain_builder import ChainBuilder
        from egregore.core.workflow.nodes.decision.patterns import DefaultPattern

        # Convert ChainBuilder to ChainSpec
        chain_spec = chain_builder.to_spec()

        if not chain_spec.nodes:
            return None

        # Create subgraph
        subgraph = Subgraph(
            pattern=pattern,
            root_node=None,  # Will be set below
            parent_graph_node=parent_node
        )

        # Set metadata early so edge creation can use it
        if pattern_obj and isinstance(pattern_obj, DefaultPattern):
            subgraph.metadata['is_default_pattern'] = True

        # Build nodes in subgraph
        branch_node_map = {}  # Local map for this branch
        branch_created_nodes = set()  # Track nodes created in THIS branch

        # Use the pre-decision snapshot if provided (prevents sibling reuse)
        # Otherwise take a snapshot now (for backwards compatibility)
        pre_branch_node_ids = pre_decision_node_ids if pre_decision_node_ids is not None else set(self.graph.nodes.keys())

        for idx, node_spec in enumerate(chain_spec.nodes):
            node_type = self._get_node_type_from_spec(node_spec)
            is_router = getattr(node_spec, 'is_router', False)
            canonical_name = getattr(node_spec, 'canonical_name', None)

            # NODE REUSE DETECTION: Reuse nodes that reference the same NodeType.node class
            #
            # Key principle: When a node appears multiple times in a workflow,
            # check if we've already seen this exact node class. If yes, reuse it.
            #
            # Example: start >> check >> decision('loop' >> process >> check)
            # Both 'check' nodes have the same _node_type_ref.node class,
            # so the second 'check' reuses the first one's GraphNode.
            # This creates a natural loop through the explicit edge.
            #
            # Aliased nodes get explicit names for convenience:
            # - state.get('check_alias') retrieves specific aliased instance
            # - Explicit loops: 'continue' >> node.alias('loop_start')
            #
            # EXCEPTION: Control flow nodes (Decision, Parallel, Sequence) are NEVER reused.
            graph_node = None
            alias_name = getattr(node_spec, 'alias_name', None)

            # Get the node class to check for reuse
            node_class = None
            if hasattr(node_spec, '_node_type_ref') and node_spec._node_type_ref:
                # _node_type_ref is a NodeType instance, get its .node attribute
                if hasattr(node_spec._node_type_ref, 'node'):
                    node_class = node_spec._node_type_ref.node
                else:
                    # Fallback: might be an instance already
                    node_class = node_spec._node_type_ref.__class__

            # Check if we should reuse an existing node
            can_reuse = False
            if node_type not in [NodeTypeEnum.DECISION, NodeTypeEnum.PARALLEL, NodeTypeEnum.SEQUENCE]:
                if alias_name and alias_name in self.canonical_name_map:
                    # Explicit alias - reuse the aliased node
                    graph_node = self.canonical_name_map[alias_name]
                    can_reuse = True
                elif node_class:
                    # Check if this node class already exists and is reusable
                    #
                    # SIMPLIFIED REUSE RULES:
                    # 1. Same node class? → Reuse it (from main sequence or ancestor branches)
                    # 2. EXCEPTION: Don't reuse from THIS branch (already created above)
                    # 3. EXCEPTION: Don't reuse nodes created by SIBLING branches
                    #
                    # This is simpler and correct: if you reference the same NodeType,
                    # you get the same GraphNode, creating natural loops through explicit edges.
                    for existing_id in list(self.graph.nodes.keys()):
                        existing_node = self.graph.nodes[existing_id]

                        # Skip nodes created in THIS branch (avoid intra-branch reuse)
                        if existing_node.id in branch_created_nodes:
                            continue

                        # Skip nodes created by SIBLING branches (not in pre-branch set)
                        # Only reuse nodes that existed BEFORE we started building branches
                        if existing_node.id not in pre_branch_node_ids:
                            continue

                        # Check if same node class
                        existing_spec = existing_node.node_instance
                        if hasattr(existing_spec, '_node_type_ref') and existing_spec._node_type_ref:
                            # Get the existing node's class
                            existing_class = None
                            if hasattr(existing_spec._node_type_ref, 'node'):
                                existing_class = existing_spec._node_type_ref.node
                            else:
                                existing_class = existing_spec._node_type_ref.__class__

                            if existing_class == node_class:
                                # PARALLEL BRANCH VALIDATION:
                                # Parallel branches MUST NOT escape to nodes outside the parallel
                                # (i.e., can't loop back to nodes before the parallel node)
                                #
                                # Walk up ancestor chain to find any Parallel nodes
                                # If we're inside a parallel branch (at any nesting level),
                                # check if the reused node exists before that parallel
                                parallel_ancestor = None
                                current = parent_node
                                while current:
                                    if current.node_type == NodeTypeEnum.PARALLEL:
                                        parallel_ancestor = current
                                        break
                                    current = current.parent

                                if parallel_ancestor:
                                    # We're inside a parallel branch - check if node escapes
                                    # Walk up from parallel node to root, collecting forbidden nodes
                                    forbidden_nodes = set()
                                    current = parallel_ancestor.parent
                                    while current:
                                        forbidden_nodes.add(current.id)
                                        current = current.parent

                                    if existing_node.id in forbidden_nodes:
                                        # Node exists before parallel - this is an escape!
                                        node_name = canonical_name or getattr(node_spec, 'node_name', 'unknown')
                                        parallel_name = parallel_ancestor.canonical_name or parallel_ancestor.id
                                        raise ValueError(
                                            f"Parallel branch escape detected!\n"
                                            f"  Parallel node: '{parallel_name}'\n"
                                            f"  Branch pattern: '{pattern}'\n"
                                            f"  Attempted to loop back to: '{node_name}'\n\n"
                                            f"ERROR: Parallel branches CANNOT loop back to nodes outside the parallel.\n"
                                            f"This would break parallel execution isolation.\n\n"
                                            f"Parallel branches can ONLY:\n"
                                            f"  1. Loop within the same branch (reuse nodes created in THIS branch)\n"
                                            f"  2. Terminate normally without looping back\n\n"
                                            f"If you need loops, use a Decision node instead of Parallel."
                                        )

                                # Same node class - reuse it
                                graph_node = existing_node
                                can_reuse = True
                                break

            if not can_reuse:
                # Create new GraphNode
                graph_node = GraphNode(
                    id=node_spec.spec_id,
                    node_instance=node_spec,
                    node_type=node_type,
                    parent=parent_node,
                    is_router=is_router,
                    canonical_name=canonical_name
                )

                # Extract return type information for router detection
                self._store_return_type_info(graph_node, node_spec)

                # Add to main graph
                self.graph.nodes[node_spec.spec_id] = graph_node

                # Track by ALIAS_NAME for explicit loop detection
                if alias_name:
                    self.canonical_name_map[alias_name] = graph_node

                # Track that this node was created in THIS branch
                branch_created_nodes.add(graph_node.id)

            branch_node_map[idx] = graph_node
            subgraph.nodes.append(graph_node)

            if subgraph.root_node is None:
                subgraph.root_node = graph_node

        # Create edges in subgraph
        for source_idx, target_idx in chain_spec.edges:
            source_node = branch_node_map.get(source_idx)
            target_node = branch_node_map.get(target_idx)

            if source_node and target_node:
                edge = self.graph.add_edge(
                    source_node,
                    target_node,
                    EdgeTypeEnum.SEQUENTIAL
                )
                subgraph.edges.append(edge)

                # Set parent relationships ONLY for newly created nodes (in branch_created_nodes)
                # CRITICAL: Don't overwrite parent for REUSED nodes - this creates parent cycles!
                # Example bug: decision.parent=router, handler.parent=decision, router.parent=handler → infinite loop
                if target_node.id in branch_created_nodes:
                    if target_node.parent is None or target_node.parent == parent_node:
                        target_node.parent = source_node
                        if target_node not in source_node.children:
                            source_node.children.append(target_node)

        # Set terminal node
        if subgraph.nodes:
            subgraph.terminal_node = subgraph.nodes[-1]

        # Recursively process nested Decisions in this branch
        for idx, node_spec in enumerate(chain_spec.nodes):
            graph_node = branch_node_map[idx]

            if graph_node.node_type == NodeTypeEnum.DECISION:
                self._process_decision_from_spec(node_spec, graph_node, branch_node_map)

        return subgraph

    def _process_parallel_from_spec(self, node_spec: Any, graph_node: GraphNode,
                                    node_map: Dict[int, GraphNode]):
        """Process Parallel node from NodeSpec.

        Builds subgraphs for each parallel branch to enable graph analysis,
        escape validation, and execution planning.

        Args:
            node_spec: NodeSpec for the Parallel
            graph_node: GraphNode for the Parallel
            node_map: Map from spec index to GraphNode
        """
        # Get Parallel instance from spec
        if not hasattr(node_spec, '_node_type_ref') or node_spec._node_type_ref is None:
            return

        parallel_instance = node_spec._node_type_ref

        # Check if it has parallel_branches (deferred architecture)
        if not hasattr(parallel_instance, 'parallel_branches'):
            return

        # Process each parallel branch as a subgraph
        from egregore.core.workflow.chain_builder import ChainBuilder

        for idx, branch_builder in enumerate(parallel_instance.parallel_branches):
            if not isinstance(branch_builder, ChainBuilder):
                continue

            # Build subgraph from this ChainBuilder
            # Use a dummy pattern name based on index
            pattern = f"parallel_{idx}"

            # Build the branch subgraph
            subgraph = self._process_branch_from_chain_builder(
                branch_builder,
                graph_node,
                pattern,
                pattern_obj=None,  # Parallel has no pattern objects
                pre_decision_node_ids=set(self.graph.nodes.keys())  # Snapshot for isolation
            )

            if subgraph:
                # Mark as parallel execution mode
                subgraph.execution_mode = ExecutionModeEnum.PARALLEL
                self.graph.add_subgraph(graph_node, pattern, subgraph)

    def _extract_literal_return_values(self, graph_node: GraphNode) -> Optional[List[Any]]:
        """Extract possible return values from return type hint.

        Supports:
        - Literal['a', 'b', 'c'] - returns exact list of values
        - bool - returns [True, False]
        - Other types - returns None (can't enumerate, requires default pattern)

        Args:
            graph_node: GraphNode to check

        Returns:
            List of possible return values if we can enumerate them, None otherwise
        """
        node_spec = graph_node.node_instance

        # Try to get the NodeType or original function
        if hasattr(node_spec, '_node_type_ref') and node_spec._node_type_ref:
            node_type = node_spec._node_type_ref

            # Get the exec function (original function before wrapping)
            if hasattr(node_type, 'exec'):
                try:
                    hints = get_type_hints(node_type.exec)

                    if 'return' in hints:
                        return_type = hints['return']

                        # Check if it's a Literal type
                        origin = get_origin(return_type)
                        if origin is typing.Literal:
                            # Extract literal values
                            args = get_args(return_type)
                            return list(args)

                        # Check if it's bool
                        if return_type is bool:
                            return [True, False]

                        # For Union types, extract possible values
                        if origin is typing.Union:
                            # Handle Optional (Union[X, None])
                            args = get_args(return_type)
                            # If it contains Literal types, extract those
                            literals = []
                            for arg in args:
                                if get_origin(arg) is typing.Literal:
                                    literals.extend(get_args(arg))
                            if literals:
                                return literals

                except Exception:
                    # Type hints might not be available or might fail
                    pass

        return None

    def _store_return_type_info(self, graph_node: GraphNode, node_spec: Any):
        """Extract and store return type information in GraphNode metadata.

        This is used by the execution controller to distinguish between:
        - Classifiers: Return Literal types (routing decisions) → restore INPUT
        - Transformers: Return regular types (data transformation) → restore OUTPUT

        Type hints are extracted during ChainBuilder.to_spec() and stored in
        NodeSpec.metadata. This method simply copies them to GraphNode.metadata.

        Args:
            graph_node: GraphNode to store metadata on
            node_spec: NodeSpec that may contain type hint metadata
        """
        # Copy type hint metadata from NodeSpec to GraphNode
        if hasattr(node_spec, 'metadata') and node_spec.metadata:
            if 'is_literal_return' in node_spec.metadata:
                graph_node.metadata['is_literal_return'] = node_spec.metadata['is_literal_return']

            if 'literal_values' in node_spec.metadata:
                graph_node.metadata['literal_values'] = node_spec.metadata['literal_values']

            if 'same_input_output_type' in node_spec.metadata:
                graph_node.metadata['same_input_output_type'] = node_spec.metadata['same_input_output_type']

    def _find_decision_for_node(self, graph_node: GraphNode) -> Optional[GraphNode]:
        """Find which decision will handle this node's output.

        Looks for the first decision in the node's children/outgoing edges.

        Args:
            graph_node: GraphNode whose output we're tracking

        Returns:
            Decision GraphNode that will receive this node's output, or None
        """
        # Check outgoing edges
        for edge in self.graph.get_outgoing_edges(graph_node):
            if edge.to_node.node_type == NodeTypeEnum.DECISION:
                return edge.to_node

            # Recursively check the next node
            # (e.g., node >> intermediate >> decision)
            next_decision = self._find_decision_for_node(edge.to_node)
            if next_decision:
                return next_decision

        return None

    def _validate_decision_patterns(self):
        """Validate that all decisions have patterns for possible return values.

        Checks nodes with Literal return type hints and verifies that any decision
        receiving their output has patterns (or a default '_' pattern) for all possible values.

        Raises:
            ValueError: If a decision is missing patterns for possible return values
        """
        from egregore.core.workflow.nodes.decision.patterns import DefaultPattern

        # Check all nodes in the graph
        for node_id, graph_node in self.graph.nodes.items():
            # Skip control flow nodes
            if graph_node.node_type in [NodeTypeEnum.DECISION, NodeTypeEnum.PARALLEL, NodeTypeEnum.SEQUENCE]:
                continue

            # Try to extract Literal return values
            possible_values = self._extract_literal_return_values(graph_node)

            if possible_values is None:
                # No Literal type hint - skip validation
                continue

            # Find which decision will handle this node's output
            decision_node = self._find_decision_for_node(graph_node)

            if decision_node is None:
                # Node doesn't feed into a decision - skip validation
                continue

            # Get decision patterns
            node_spec = decision_node.node_instance
            if not hasattr(node_spec, '_node_type_ref') or node_spec._node_type_ref is None:
                continue

            decision_instance = node_spec._node_type_ref
            if not hasattr(decision_instance, 'patterns'):
                continue

            # Extract pattern coverage
            pattern_values = set()
            has_default = False
            has_type_match = False

            from egregore.core.workflow.nodes.decision.patterns import (
                ValuePattern, ClassPattern, RangePattern, ListPattern, DefaultPattern
            )

            for pattern in decision_instance.patterns:
                if isinstance(pattern, DefaultPattern):
                    has_default = True
                    # Default pattern covers all values
                    break

                elif isinstance(pattern, ValuePattern):
                    # Exact value match
                    pattern_values.add(pattern.value)

                elif isinstance(pattern, ClassPattern):
                    # Type pattern - check if it matches the return type
                    # e.g., ClassPattern(str) covers ALL strings, even Literal['a', 'b']
                    if possible_values:
                        # Check if all possible values are instances of this type
                        if all(isinstance(val, pattern.class_type) for val in possible_values):
                            has_type_match = True
                            break

                elif isinstance(pattern, ListPattern):
                    # List pattern covers specific values
                    pattern_values.update(pattern.values)

                elif isinstance(pattern, RangePattern):
                    # Range pattern covers integers in range
                    # Add all values in range to covered set
                    try:
                        pattern_values.update(pattern.range_obj)
                    except:
                        pass

            # If there's a default pattern or type match, all values are covered
            if has_default or has_type_match:
                continue

            # Check if all possible values are covered
            missing_values = []
            for value in possible_values:
                if value not in pattern_values:
                    missing_values.append(value)

            if missing_values:
                # Get node name for error message
                node_name = graph_node.canonical_name or node_id
                decision_name = decision_node.canonical_name or decision_node.id

                # Format missing values for error message
                missing_str = ', '.join(f"'{v}'" for v in missing_values)
                available_str = ', '.join(f"'{v}'" for v in pattern_values)

                raise ValueError(
                    f"Decision pattern coverage error:\n"
                    f"  Node '{node_name}' can return: {{{', '.join(repr(v) for v in possible_values)}}}\n"
                    f"  Decision node handling this output has patterns for: {{{available_str}}}\n"
                    f"  Missing patterns for: {{{missing_str}}}\n\n"
                    f"To fix this, either:\n"
                    f"  1. Add patterns for missing values: {missing_str}\n"
                    f"  2. Add a default pattern using: '_ >> handler'\n"
                    f"  3. Update the return type hint to only include handled values"
                )
