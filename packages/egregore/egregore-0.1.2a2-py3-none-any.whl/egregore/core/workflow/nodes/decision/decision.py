"""
Decision Node with Pattern Matching

This module provides the main Decision class and helper functions
for creating sophisticated pattern-based decision nodes.
"""

from typing import Any, List, Optional, Union
import inspect
from egregore.core.workflow.nodes.node import Node, NodeMapper
from egregore.core.workflow.nodes.base import BaseNode
from egregore.core.workflow.nodes.node_types import NodeType
from .patterns import (
    Pattern, ValuePattern, ClassPattern, InstancePattern,
    PredicatePattern, DefaultPattern, RangePattern, ListPattern, DictPattern
)
from egregore.core.workflow.exceptions import MaxIterationsExceededError, InvalidPatternError


class Decision(Node):
    """Decision node with sophisticated pattern matching capabilities
    
    Supports:
    - Value matching: 'hello' >> handler
    - Type matching: str >> handler, int >> handler
    - Instance patterns: HTTPResponse(status_code=200) >> handler
    - Lambda predicates: lambda x: x > 0 >> handler
    - Default cases: _ >> handler
    - Loop control: max_iter parameter
    - Range matching: range(1, 10) >> handler
    - List matching: [1, 2, 3] >> handler
    - Dict patterns: {'status': 'ok'} >> handler
    """
    
    def __init__(self, *patterns, max_iter: Optional[int] = None, name: Optional[str] = None, raise_on_max_iter: bool = False):
        """Initialize decision node

        Args:
            *patterns: Pattern objects or condition >> node mappings
            max_iter: Maximum loop re-entry iterations before terminating or raising error
            name: Optional name for the decision node
            raise_on_max_iter: If True, raises MaxIterationsExceededError when max_iter is reached.
                              If False, terminates gracefully by returning current result.

        Raises:
            ValueError: If fewer than 2 patterns are provided
        """
        super().__init__(label=name or "Decision")

        # Decision is a control flow node - it routes but doesn't produce data
        self._produces_data = False

        self.max_iter = max_iter
        self.raise_on_max_iter = raise_on_max_iter
        self.iteration_count = 0
        self.last_selected_node = None  # Track last selected target node
        self.patterns: List[Pattern] = []

        # Process input patterns
        self._process_patterns(patterns)

        # VALIDATION: Decision nodes must have at least 2 paths
        if len(self.patterns) < 2:
            raise ValueError(
                f"Decision node must have at least 2 patterns, got {len(self.patterns)}. "
                f"Decisions require multiple routing options to function correctly."
            )

        # Sort patterns by priority (lower number = higher priority)
        self.patterns.sort(key=lambda p: p.priority)

        # Update name with pattern info
        if not name:
            pattern_summary = self._create_pattern_summary()
            self.name = f"Decision({pattern_summary})"

        # Backwards compatibility attributes
        self._iteration_count = 0

    @property
    def maps(self):
        """Backwards compatibility: convert patterns to old NodeMapper-style maps"""
        # Convert patterns to NodeMapper-like objects for old code
        class _LegacyMapper:
            def __init__(self, condition, node):
                self.condition = condition
                self.node = node

        legacy_maps = []
        for pattern in self.patterns:
            # Extract condition representation from pattern
            if isinstance(pattern, ValuePattern):
                condition = pattern.value
            elif isinstance(pattern, ClassPattern):
                condition = pattern.class_type
            elif isinstance(pattern, DefaultPattern):
                condition = "_"
            else:
                condition = str(pattern)

            legacy_maps.append(_LegacyMapper(condition, pattern.target_node))

        return legacy_maps

    def _process_patterns(self, patterns):
        """Process input patterns and convert to Pattern objects"""
        # Track which nodes are used in patterns to detect duplicates
        used_nodes = {}  # node id -> pattern index

        for pattern_input in patterns:
            if isinstance(pattern_input, Pattern):
                # Already a Pattern object
                new_pattern = pattern_input
            elif isinstance(pattern_input, NodeMapper):
                # Convert NodeMapper to appropriate Pattern
                new_pattern = self._convert_nodemapper_to_pattern(pattern_input)
            elif hasattr(pattern_input, '__rshift__'):
                # This might be a lambda or other callable that supports >>
                # We'll handle it in the next workflow iteration
                raise InvalidPatternError(pattern_input, "Lambda patterns must use >> operator (lambda x: condition >> handler)")
            else:
                raise InvalidPatternError(pattern_input, "must be a Pattern object or NodeMapper")

            # Check if this pattern's target node is already used by another pattern
            if hasattr(new_pattern, 'target_node') and new_pattern.target_node:
                node_id = id(new_pattern.target_node)
                if node_id in used_nodes:
                    # Node is reused - create an automatic alias
                    import uuid
                    is_explicit_alias = getattr(new_pattern.target_node, '_is_alias', False)
                    if not is_explicit_alias:
                        alias_name = f"{new_pattern.target_node.name}_pattern_reuse_{uuid.uuid4().hex[:8]}"
                        new_pattern.target_node = new_pattern.target_node.alias(alias_name)
                else:
                    # Track this node as used
                    used_nodes[node_id] = len(self.patterns)

            self.patterns.append(new_pattern)
    
    def _convert_nodemapper_to_pattern(self, node_mapper: NodeMapper) -> Pattern:
        """Convert NodeMapper to appropriate Pattern type

        IMPORTANT: Stores ChainBuilder as-is without instantiation.
        Instantiation happens at execution time when pattern matches.
        """
        condition = node_mapper.condition

        # NodeMapper now always has _chain_builder (fully deferred architecture)
        # Store it as-is - DON'T instantiate yet!
        target_node = node_mapper._chain_builder

        # Determine pattern type based on condition
        if condition == "_":
            return DefaultPattern(target_node)
        elif isinstance(condition, type):
            return ClassPattern(condition, target_node)
        elif isinstance(condition, range):
            return RangePattern(condition, target_node)
        elif isinstance(condition, (list, tuple)):
            return ListPattern(condition, target_node)
        elif isinstance(condition, dict):
            return DictPattern(condition, target_node)
        elif callable(condition) and not isinstance(condition, type):
            return PredicatePattern(condition, target_node)  # type: ignore[arg-type]
        elif hasattr(condition, '__class__') and hasattr(condition, '__dict__'):
            # Instance pattern (object with attributes)
            return InstancePattern(condition, target_node)
        else:
            # Default to value pattern
            return ValuePattern(condition, target_node)
    
    def _resolve_target_node(self, node):
        """Resolve NodeType or ChainBuilder to actual node instance"""
        from egregore.core.workflow.chain_builder import ChainBuilder

        if isinstance(node, NodeType):
            return node.node_instance
        elif isinstance(node, ChainBuilder):
            # Instantiate ChainBuilder to get the chain start node
            chain_spec = node.to_spec()
            chain_start = chain_spec.instantiate_chain()
            return chain_start
        return node
    
    def _create_pattern_summary(self) -> str:
        """Create a summary string of patterns for naming"""
        if not self.patterns:
            return "no_patterns"
        
        summaries = []
        for pattern in self.patterns[:3]:  # Show first 3 patterns
            if isinstance(pattern, ValuePattern):
                summaries.append(repr(pattern.value))
            elif isinstance(pattern, ClassPattern):
                summaries.append(pattern.class_type.__name__)
            elif isinstance(pattern, DefaultPattern):
                summaries.append("_")
            else:
                summaries.append(pattern.__class__.__name__.replace('Pattern', ''))
        
        if len(self.patterns) > 3:
            summaries.append("...")
        
        return ", ".join(summaries)
    
    def execute(self, *args, **kwargs):
        """Execute decision - pattern matching ONLY.

        NEW ARCHITECTURE (graph-driven):
        Decision's ONLY job is to:
        1. Get routing criteria from previous node (router output)
        2. Match pattern against criteria
        3. Set next_node to matched branch root
        4. Return router INPUT (original data) for branch to consume

        The GraphExecutionController handles all execution flow, including loops.
        """
        # Get matching criteria from previous node (criteria provider / router)
        criteria = self.state.get_previous_output()

        # Match patterns against criteria
        matched_pattern = None
        for pattern in self.patterns:
            try:
                if pattern.matches(criteria, self.state):
                    matched_pattern = pattern
                    break
            except Exception:
                continue

        if not matched_pattern:
            # No pattern matched
            self.next_node = None
            return criteria

        # Get the branch root node from graph
        if hasattr(self, '_graph') and self._graph and hasattr(self, '_graph_node'):
            subgraphs = self._graph.get_subgraphs(self._graph_node)

            # Find subgraph for matched pattern
            pattern_str = str(matched_pattern)
            for sg in subgraphs:
                if sg.pattern == pattern_str:
                    # Set next_node to branch root
                    # Controller will execute from there
                    self.next_node = self._get_node_instance_for_graph_node(sg.root_node)
                    break

        # If no graph, fall back to instantiating branch directly
        if not self.next_node:
            from egregore.core.workflow.chain_builder import ChainBuilder
            branch_chain = matched_pattern.target_node

            if isinstance(branch_chain, ChainBuilder):
                chain_spec = branch_chain.to_spec()
                self.next_node = chain_spec.instantiate_chain()

                # CRITICAL: Propagate graph references to instantiated branch
                # This ensures nested decisions can use graph for routing
                if hasattr(self, '_graph') and self._graph:
                    self._propagate_graph_to_chain(self.next_node, self._graph)
            else:
                self.next_node = branch_chain
                # Propagate graph reference to single node
                if hasattr(self, '_graph') and self._graph:
                    self.next_node._graph = self._graph

        # Decision nodes are control flow only - pass through input unchanged.
        # Router data restoration is handled by GraphExecutionController.
        return criteria

    def _propagate_graph_to_chain(self, start_node, graph):
        """Propagate graph reference to all nodes in a chain.

        Handles nested Decisions by recursively propagating to their branches.

        Args:
            start_node: First node in chain
            graph: Graph reference to propagate
        """
        current = start_node
        visited = set()

        while current and id(current) not in visited:
            visited.add(id(current))
            current._graph = graph

            # Try to find corresponding GraphNode for this instance
            # We match by node name since we don't have spec_id
            for graph_node in graph.nodes.values():
                node_spec = graph_node.node_instance
                if hasattr(node_spec, 'node_name') and hasattr(current, 'name'):
                    if node_spec.node_name == current.name:
                        current._graph_node = graph_node
                        break

            # Special handling for nested Decisions: propagate to their branch chains
            # This ensures nested decisions can use graph for routing
            if isinstance(current, Decision):
                # Propagate to each pattern's target chain
                from egregore.core.workflow.chain_builder import ChainBuilder
                for pattern in current.patterns:
                    target = pattern.target_node
                    # If target is a ChainBuilder, we'll handle it when the decision executes
                    # If target is already a node instance, propagate now
                    if not isinstance(target, ChainBuilder) and hasattr(target, '_graph'):
                        self._propagate_graph_to_chain(target, graph)

            # Move to next in chain
            if hasattr(current, 'next_node') and current.next_node:
                current = current.next_node
            else:
                break

    def _get_node_instance_for_graph_node(self, graph_node):
        """Get or instantiate a node from a GraphNode.

        Args:
            graph_node: GraphNode to instantiate

        Returns:
            Node instance
        """
        node_spec = graph_node.node_instance

        # If it's a NodeSpec, instantiate it
        if hasattr(node_spec, 'instantiate'):
            instance = node_spec.instantiate()
            # Propagate graph references
            if hasattr(self, '_graph'):
                instance._graph = self._graph
                instance._graph_node = graph_node
            return instance

        # Already an instance
        return node_spec

    def add_pattern(self, pattern: Union[Pattern, NodeMapper]):
        """Add a new pattern to the decision
        
        Args:
            pattern: Pattern object or NodeMapper to add
        """
        if isinstance(pattern, Pattern):
            self.patterns.append(pattern)
        elif isinstance(pattern, NodeMapper):
            self.patterns.append(self._convert_nodemapper_to_pattern(pattern))
        else:
            raise InvalidPatternError(pattern, "must be a Pattern object or NodeMapper")
        
        # Re-sort patterns by priority
        self.patterns.sort(key=lambda p: p.priority)
    
    def remove_pattern(self, pattern_or_index: Union[Pattern, int]):
        """Remove a pattern from the decision
        
        Args:
            pattern_or_index: Pattern object to remove or index
        """
        if isinstance(pattern_or_index, int):
            if 0 <= pattern_or_index < len(self.patterns):
                self.patterns.pop(pattern_or_index)
        else:
            try:
                self.patterns.remove(pattern_or_index)
            except ValueError:
                pass  # Pattern not found
    
    def get_pattern_info(self) -> List[dict]:
        """Get information about all patterns
        
        Returns:
            List of dictionaries with pattern information
        """
        return [
            {
                'type': pattern.__class__.__name__,
                'priority': pattern.priority,
                'target_node': getattr(pattern.target_node, 'name', str(pattern.target_node)),
                'repr': repr(pattern)
            }
            for pattern in self.patterns
        ]
    
    def __repr__(self) -> str:
        pattern_count = len(self.patterns)
        max_iter_info = f", max_iter={self.max_iter}" if self.max_iter else ""
        return f"Decision({pattern_count} patterns{max_iter_info})"


# Convenience functions and syntax sugar

def decision(*patterns, max_iter: Optional[int] = None, name: Optional[str] = None, raise_on_max_iter: bool = False) -> Decision:
    """Create a decision node with pattern matching

    Args:
        *patterns: Patterns to match against (condition >> node pairs)
        max_iter: Maximum loop re-entry iterations before terminating or raising error
        name: Optional name for the decision node
        raise_on_max_iter: If True, raises exception when max_iter is reached.
                          If False (default), terminates gracefully by returning current result.

    Returns:
        Decision instance

    Examples:
        decision(
            str >> string_handler,
            int >> number_handler,
            HTTPResponse(status_code=200) >> success_handler,
            lambda x: x > 100 >> big_value_handler,
            _ >> default_handler,
            max_iter=3
    """
    return Decision(*patterns, max_iter=max_iter, name=name, raise_on_max_iter=raise_on_max_iter)


class DefaultMarker:
    """Marker class for default patterns"""
    
    def __rshift__(self, target_node):
        """Support _ >> node syntax"""
        from egregore.core.workflow.nodes.node import NodeType
        if isinstance(target_node, NodeType):
            target_node = target_node.node_instance
        return DefaultPattern(target_node)
    
    def __repr__(self):
        return "_"


# Global default marker instance
_ = DefaultMarker()


# Type pattern creation helper - we can't modify built-in types directly
# Instead, we'll provide wrapper functions and document the syntax

def create_type_pattern(type_class: type, target_node):
    """Create a ClassPattern for a type - use this instead of type >> node"""
    from egregore.core.workflow.nodes.node_types import NodeType
    if isinstance(target_node, NodeType):
        target_node = target_node.node_instance
    return ClassPattern(type_class, target_node)

def create_range_pattern(range_obj: range, target_node):
    """Create a RangePattern - use this instead of range >> node"""
    from egregore.core.workflow.nodes.node_types import NodeType
    if isinstance(target_node, NodeType):
        target_node = target_node.node_instance
    return RangePattern(range_obj, target_node)

# Note: For type matching, users should use:
# decision(
#     create_type_pattern(str, handler),  # Instead of str >> handler
#     "value" >> handler,                 # Direct values still work with >>
#     _ >> default_handler
# )

# NOTE: Old basic decision() function removed - see line 231 for enhanced version
