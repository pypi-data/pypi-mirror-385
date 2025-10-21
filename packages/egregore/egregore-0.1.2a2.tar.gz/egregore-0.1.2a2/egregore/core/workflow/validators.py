"""
Built-in validators for sequence validation
"""

from typing import Dict, List, Set, Deque, Optional
from collections import deque

from egregore.core.workflow.validation import (
    BaseValidator, ValidationResult, ValidationError, ValidationWarning
)
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from egregore.core.workflow.sequence.base import Sequence
    from egregore.core.workflow.nodes.base import BaseNode
class CycleDetectionValidator(BaseValidator):
    """Detects cycles in sequence graphs using DFS"""
    
    @property
    def validator_name(self) -> str:
        return "CycleDetection"
    
    def validate(self, sequence: 'Sequence') -> ValidationResult:
        """Detect cycles using DFS with color coding"""
        
        if not sequence:
            return ValidationResult(is_valid=True)
        
        try:
            graph = self._build_graph(sequence)
            cycles = self._detect_cycles(graph)
            
            errors = []
            for cycle in cycles:
                cycle_names = [getattr(node, 'name', str(node)) for node in cycle]
                cycle_path = " -> ".join(cycle_names) + f" -> {cycle_names[0]}"
                errors.append(ValidationError(
                    location=cycle[0] if cycle else None,
                    suggestion="Remove one of the connections in the cycle or add max_iter to decision nodes"
                ))
            
            
            return ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors
            )
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[ValidationError(message=f"Cycle detection failed: {e}")]
            )
    
    def _build_graph(self, sequence: 'Sequence') -> Dict['BaseNode', List['BaseNode']]:
        """Build adjacency list representation of sequence graph"""
        graph = {}
        visited = set()
        queue = deque([sequence.start])
        
        while queue:
            node = queue.popleft()
            if node in visited or node is None:
                continue
            visited.add(node)
            
            neighbors = []
            
            # Handle different node types
            if hasattr(node, 'maps') and node.maps:  # Decision node
                for map_item in node.maps:
                    if hasattr(map_item, 'node') and map_item.node:
                        neighbors.append(map_item.node)
                        if map_item.node not in visited:
                            queue.append(map_item.node)
            elif hasattr(node, 'parallel_nodes') and node.parallel_nodes:  # Parallel node
                for parallel_child in node.parallel_nodes:
                    if parallel_child:
                        neighbors.append(parallel_child)
                        if parallel_child not in visited:
                            queue.append(parallel_child)
            
            # Handle next_node connections
            if hasattr(node, 'next_node') and node.next_node:
                neighbors.append(node.next_node)
                if node.next_node not in visited:
                    queue.append(node.next_node)
            
            graph[node] = neighbors
        
        return graph
    
    def _detect_cycles(self, graph: Dict['BaseNode', List['BaseNode']]) -> List[List['BaseNode']]:
        """Detect cycles using DFS with three colors"""
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {node: WHITE for node in graph}
        parent = {node: None for node in graph}
        cycles = []
        
        def dfs(node):
            color[node] = GRAY
            
            for neighbor in graph.get(node, []):
                if color[neighbor] == WHITE:
                    parent[neighbor] = node
                    dfs(neighbor)
                elif color[neighbor] == GRAY:
                    # Found back edge - reconstruct cycle
                    cycle = []
                    current = node
                    while current != neighbor:
                        cycle.append(current)
                        current = parent[current]
                        if current is None:  # Safety check
                            break
                    cycle.append(neighbor)
                    cycles.append(cycle)
            
            color[node] = BLACK
        
        for node in graph:
            if color[node] == WHITE:
                dfs(node)
        
        return cycles


class DependencyValidator(BaseValidator):
    """Validates sequence structure and node dependencies"""
    
    @property
    def validator_name(self) -> str:
        return "DependencyValidation"
    
    def validate(self, sequence: 'Sequence') -> ValidationResult:
        """Validate sequence dependencies and structure"""
        
        if not sequence:
            return ValidationResult(is_valid=True)
        
        errors = []
        warnings = []
        
        try:
            # Get all nodes in sequence
            nodes = self._get_all_nodes(sequence)
            
            for node in nodes:
                # Validate parallel node configurations
                if hasattr(node, 'parallel_nodes'):
                    errors.extend(self._validate_parallel_node(node))
                
                # Validate decision node configurations
                if hasattr(node, 'maps'):
                    errors.extend(self._validate_decision_node(node))
                
                # Check for common structural issues
                warnings.extend(self._check_structural_warnings(node))
            
            
            return ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings
            )
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[ValidationError(message=f"Dependency validation failed: {e}")]
            )
    
    def _get_all_nodes(self, sequence: 'Sequence') -> List['BaseNode']:
        """Get all nodes in the sequence"""
        nodes = []
        visited = set()
        queue = deque([sequence.start])
        
        while queue:
            node = queue.popleft()
            if node in visited or node is None:
                continue
            visited.add(node)
            nodes.append(node)
            
            # Add connected nodes to queue
            if hasattr(node, 'maps') and node.maps:
                for map_item in node.maps:
                    if hasattr(map_item, 'node') and map_item.node:
                        queue.append(map_item.node)
            
            if hasattr(node, 'parallel_nodes') and node.parallel_nodes:
                for parallel_child in node.parallel_nodes:
                    queue.append(parallel_child)
            
            if hasattr(node, 'next_node') and node.next_node:
                queue.append(node.next_node)
        
        return nodes
    
    def _validate_parallel_node(self, node: 'BaseNode') -> List[ValidationError]:
        """Validate parallel node configuration"""
        errors = []
        
        if not node.parallel_nodes:
            errors.append(ValidationError(
                location=node,
                suggestion="Add nodes to parallel execution or use a regular node"
            ))
        
        # Check for duplicate names (existing validation in ParallelNode)
        names = []
        for child in node.parallel_nodes:
            name = getattr(child, 'name', None)
            if name:
                if name in names:
                    errors.append(ValidationError(
                        location=node,
                        suggestion="Ensure all parallel nodes have unique names"
                    ))
                names.append(name)
        
        # Check concurrency limits
        if hasattr(node, 'concurrency_limit') and node.concurrency_limit is not None:
            if node.concurrency_limit <= 0:
                errors.append(ValidationError(
                    location=node,
                    suggestion="Concurrency limit must be a positive integer"
                ))
        
        return errors
    
    def _validate_decision_node(self, node: 'BaseNode') -> List[ValidationError]:
        """Validate decision node configuration"""
        errors = []
        
        if not node.maps:
            errors.append(ValidationError(
                location=node,
                suggestion="Add patterns to decision node using decision('pattern' >> handler)"
            ))
        
        return errors
    
    def _check_structural_warnings(self, node: 'BaseNode') -> List[ValidationWarning]:
        """Check for structural issues that might cause problems"""
        warnings = []
        
        # Check for nodes with no next connection and no explicit termination
        if (not hasattr(node, 'next_node') or node.next_node is None) and \
           (not hasattr(node, 'maps') or not node.maps) and \
           (not hasattr(node, 'parallel_nodes') or not node.parallel_nodes):
            warnings.append(ValidationWarning(
                message="Node appears to be a dead end with no connections",
                location=node,
                suggestion="Consider if this node should connect to another node"
            ))
        
        return warnings


class SchemaValidator(BaseValidator):
    """Validates sequence configuration and node parameters"""
    
    @property
    def validator_name(self) -> str:
        return "SchemaValidation"
    
    def validate(self, sequence: 'Sequence') -> ValidationResult:
        """Validate sequence schema and configuration"""
        
        if not sequence:
            return ValidationResult(
                is_valid=False,
                errors=[ValidationError(message="Sequence cannot be None")]
            )
        
        errors = []
        warnings = []
        
        try:
            # Basic sequence structure validation
            if not hasattr(sequence, 'start') or sequence.start is None:
                errors.append(ValidationError(
                    "Sequence has no start node",
                    suggestion="Provide a start node when creating the sequence"
                ))
            
            # Validate sequence has a meaningful structure
            if hasattr(sequence, 'start') and sequence.start:
                node_count = len(self._get_all_nodes_simple(sequence))
                if node_count == 0:
                    errors.append(ValidationError(message="Sequence contains no executable nodes"))
                elif node_count == 1:
                    warnings.append(ValidationWarning(
                        message="Sequence contains only one node",
                        suggestion="Consider if this should be a simple function call instead"
                    ))
            
            
            return ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings
            )
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[ValidationError(message=f"Schema validation failed: {e}")]
            )
    
    def _get_all_nodes_simple(self, sequence: 'Sequence') -> List['BaseNode']:
        """Simple node counting for schema validation"""
        if not sequence.start:
            return []
        
        # For now, just return the start node - full traversal is done by DependencyValidator
        return [sequence.start]