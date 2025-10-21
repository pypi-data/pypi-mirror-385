"""
Registry and access management for V2 Context Scaffolds.

Provides SystemInterface for scaffold registration/management,
ScaffoldAccessor for dynamic attribute access, and ScaffoldProxy
for operation exposure.
"""

import logging
from typing import Dict, Any, Optional, List, Type, Union, Callable
from collections import defaultdict

logger = logging.getLogger(__name__)

# Import will be done at runtime to avoid circular imports
# from ..context_management.scaffolds import BaseContextScaffold
# from ..context_management.context import Context


class SystemInterface:
    """
    Core scaffold registry and lifecycle management.
    
    Manages scaffold registration, storage, retrieval, and lifecycle
    for the V2 scaffold system.
    """
    
    def __init__(self):
        """Initialize the system interface."""
        self._scaffolds: Dict[str, Any] = {}  # scaffold_name -> BaseContextScaffold
        self._scaffold_metadata: Dict[str, Dict[str, Any]] = {}
        self._scaffold_positions: Dict[str, str] = {}
        self._scaffold_lifecycle_hooks: Dict[str, List[Callable]] = defaultdict(list)
        
        logger.debug("SystemInterface initialized")
    
    def add_scaffold(
        self, 
        name: str, 
        scaffold: Any,  # BaseContextScaffold
        position: str = "system",
        depth: int = 0,
        **metadata
    ) -> None:
        """
        Add a scaffold to the registry.
        
        Args:
            name: Unique name for the scaffold
            scaffold: BaseContextScaffold instance
            position: Mount position ("system", "active", "history")
            depth: Depth for positioning
            **metadata: Additional metadata
        """
        if name in self._scaffolds:
            logger.warning(f"Replacing existing scaffold '{name}'")
            self.remove_scaffold(name)
        
        # Store scaffold and metadata
        self._scaffolds[name] = scaffold
        self._scaffold_positions[name] = position
        self._scaffold_metadata[name] = {
            'name': name,
            'type': type(scaffold).__name__,
            'position': position,
            'depth': depth,
            'registered_at': None,  # Could add timestamp
            **metadata
        }
        
        # Set depth on scaffold if supported
        if hasattr(scaffold, 'depth'):
            scaffold.depth = depth
        
        # Trigger registration hooks
        self._trigger_lifecycle_hooks('register', name, scaffold)
        
        logger.info(f"Registered scaffold '{name}' at position '{position}' with depth {depth}")
    
    def get_scaffold(self, name: str) -> Optional[Any]:
        """
        Get scaffold by name.
        
        Args:
            name: Scaffold name
            
        Returns:
            BaseContextScaffold instance or None
        """
        return self._scaffolds.get(name)
    
    def remove_scaffold(self, name: str) -> Optional[Any]:
        """
        Remove scaffold from registry.
        
        Args:
            name: Scaffold name to remove
            
        Returns:
            Removed scaffold or None if not found
        """
        if name not in self._scaffolds:
            logger.warning(f"Scaffold '{name}' not found for removal")
            return None
        
        scaffold = self._scaffolds.pop(name)
        self._scaffold_positions.pop(name, None)
        self._scaffold_metadata.pop(name, None)
        
        # Trigger removal hooks
        self._trigger_lifecycle_hooks('remove', name, scaffold)
        
        logger.info(f"Removed scaffold '{name}'")
        return scaffold
    
    def list_scaffolds(self) -> List[str]:
        """Get list of registered scaffold names."""
        return list(self._scaffolds.keys())
    
    def get_scaffolds_by_position(self, position: str) -> Dict[str, Any]:
        """
        Get all scaffolds at a specific position.
        
        Args:
            position: Position to filter by
            
        Returns:
            Dictionary of scaffold_name -> scaffold
        """
        return {
            name: scaffold 
            for name, scaffold in self._scaffolds.items()
            if self._scaffold_positions.get(name) == position
        }
    
    def get_scaffold_metadata(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a scaffold.
        
        Args:
            name: Scaffold name
            
        Returns:
            Metadata dictionary or None
        """
        return self._scaffold_metadata.get(name)
    
    def get_all_metadata(self) -> Dict[str, Dict[str, Any]]:
        """Get metadata for all scaffolds."""
        return self._scaffold_metadata.copy()
    
    def update_scaffold_position(self, name: str, new_position: str) -> bool:
        """
        Update scaffold position.
        
        Args:
            name: Scaffold name
            new_position: New position
            
        Returns:
            True if updated successfully
        """
        if name not in self._scaffolds:
            logger.error(f"Cannot update position for scaffold '{name}': not found")
            return False
        
        old_position = self._scaffold_positions.get(name)
        self._scaffold_positions[name] = new_position
        
        # Update metadata
        if name in self._scaffold_metadata:
            self._scaffold_metadata[name]['position'] = new_position
        
        logger.info(f"Updated scaffold '{name}' position from '{old_position}' to '{new_position}'")
        return True
    
    def clear_all_scaffolds(self) -> int:
        """
        Clear all scaffolds.
        
        Returns:
            Number of scaffolds cleared
        """
        count = len(self._scaffolds)
        
        # Trigger removal hooks for all scaffolds
        for name, scaffold in self._scaffolds.items():
            self._trigger_lifecycle_hooks('remove', name, scaffold)
        
        self._scaffolds.clear()
        self._scaffold_positions.clear()
        self._scaffold_metadata.clear()
        
        logger.info(f"Cleared all {count} scaffolds")
        return count
    
    def add_lifecycle_hook(self, event: str, hook: Callable) -> None:
        """
        Add lifecycle hook for scaffold events.
        
        Args:
            event: Event name ('register', 'remove', etc.)
            hook: Callable to execute on event
        """
        self._scaffold_lifecycle_hooks[event].append(hook)
        logger.debug(f"Added lifecycle hook for '{event}' event")
    
    def _trigger_lifecycle_hooks(self, event: str, scaffold_name: str, scaffold: Any) -> None:
        """Trigger lifecycle hooks for an event."""
        hooks = self._scaffold_lifecycle_hooks.get(event, [])
        for hook in hooks:
            try:
                hook(scaffold_name, scaffold)
            except Exception as e:
                logger.error(f"Error in lifecycle hook for '{event}': {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get system interface status.
        
        Returns:
            Status dictionary
        """
        position_counts = defaultdict(int)
        for position in self._scaffold_positions.values():
            position_counts[position] += 1
        
        return {
            "total_scaffolds": len(self._scaffolds),
            "scaffolds": list(self._scaffolds.keys()),
            "position_distribution": dict(position_counts),
            "scaffold_types": {
                name: meta.get('type') 
                for name, meta in self._scaffold_metadata.items()
            }
        }
    
    def __len__(self) -> int:
        """Get number of registered scaffolds."""
        return len(self._scaffolds)
    
    def __contains__(self, name: str) -> bool:
        """Check if scaffold exists."""
        return name in self._scaffolds
    
    def __iter__(self):
        """Iterate over scaffold names."""
        return iter(self._scaffolds.keys())


class ScaffoldProxy:
    """
    Proxy for scaffold operations with state access and change detection.
    
    Provides clean access to scaffold operations and state management
    while maintaining the scaffold's change detection capabilities.
    """
    
    def __init__(self, scaffold: Any, name: str):
        """
        Initialize scaffold proxy.
        
        Args:
            scaffold: BaseContextScaffold instance
            name: Scaffold name for logging/identification
        """
        self._scaffold = scaffold
        self._name = name
        self._operation_cache = {}
        
        # Expose scaffold state operators
        self._expose_state_operators()
        
        logger.debug(f"ScaffoldProxy created for '{name}'")
    
    def _expose_state_operators(self) -> None:
        """Expose state management operators as proxy methods."""
        # Import here to avoid circular imports
        from .decorators import get_scaffold_operations
        
        # Get all scaffold operations
        operations = get_scaffold_operations(self._scaffold)
        
        for op_name, metadata in operations.items():
            # Create bound method for each operation
            bound_method = self._create_bound_operation(op_name, metadata)
            setattr(self, op_name, bound_method)
            self._operation_cache[op_name] = metadata
        
        # Add on_change support if needed
        if hasattr(self._scaffold, 'state'):
            self.on_change = self._create_change_decorator()
    
    def _create_bound_operation(self, op_name: str, metadata) -> Callable:
        """
        Create a bound operation method for the proxy.
        
        Args:
            op_name: Operation name
            metadata: ScaffoldOperationMetadata
            
        Returns:
            Bound method for the operation
        """
        original_method = getattr(self._scaffold, metadata.original_func.__name__)
        
        def bound_operation(*args, **kwargs):
            logger.debug(f"Executing scaffold operation '{self._name}.{op_name}'")
            try:
                result = original_method(*args, **kwargs)
                logger.debug(f"Scaffold operation '{self._name}.{op_name}' completed successfully")
                return result
            except Exception as e:
                logger.error(f"Error in scaffold operation '{self._name}.{op_name}': {e}")
                raise
        
        # Copy metadata for introspection
        bound_operation._scaffold_operation_metadata = metadata
        bound_operation._is_scaffold_operation = True
        bound_operation.__name__ = op_name
        bound_operation.__doc__ = metadata.description
        
        return bound_operation
    
    def _create_change_decorator(self) -> Callable:
        """
        Create on_change decorator for state change detection.
        
        Returns:
            Decorator function for change detection
        """
        def on_change(callback: Callable) -> Callable:
            """
            Decorator for registering change callbacks.
            
            Args:
                callback: Function to call when state changes
                
            Returns:
                Original callback function
            """
            # Store callback for later use (could be enhanced)
            if not hasattr(self._scaffold, '_change_callbacks'):
                self._scaffold._change_callbacks = []
            self._scaffold._change_callbacks.append(callback)
            
            logger.debug(f"Registered change callback for scaffold '{self._name}'")
            return callback
        
        return on_change
    
    @property
    def state(self) -> Any:
        """Access scaffold state directly."""
        if hasattr(self._scaffold, 'state'):
            return self._scaffold.state
        return None
    
    def get_operations(self) -> Dict[str, Any]:
        """Get all available operations."""
        return self._operation_cache.copy()
    
    def has_operation(self, op_name: str) -> bool:
        """Check if operation exists."""
        return op_name in self._operation_cache
    
    def __getattr__(self, name: str) -> Any:
        """
        Fallback attribute access to the underlying scaffold.
        
        Args:
            name: Attribute name
            
        Returns:
            Attribute value from scaffold
        """
        if name.startswith('_'):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        
        # Delegate to the scaffold
        if hasattr(self._scaffold, name):
            return getattr(self._scaffold, name)
        
        raise AttributeError(f"Scaffold '{self._name}' has no attribute '{name}'")
    
    def __repr__(self) -> str:
        """String representation."""
        return f"ScaffoldProxy(name='{self._name}', operations={len(self._operation_cache)})"


class ScaffoldAccessor:
    """
    Simple accessor for scaffold instances by normalized tag name.
    
    Provides direct access to scaffold instances and their operations
    without management overhead. Just accesses what was passed to the agent.
    
    Usage:
        agent.scaffolds.task_manager.state  # Access scaffold's state
        agent.scaffolds.task_manager.some_operation()  # Call scaffold operation
    """
    
    def __init__(self, scaffold_instances: List[Any]):
        """
        Initialize with scaffold instances.
        
        Args:
            scaffold_instances: List of scaffold instances from agent config
        """
        self._scaffolds = scaffold_instances or []
        self._scaffold_map = {}
        
        # Build map of normalized names to scaffold instances using type property
        for scaffold in self._scaffolds:
            if hasattr(scaffold, 'type') and scaffold.type:
                # Normalize the type (lowercase, replace spaces/hyphens with underscores)
                normalized_type = self._normalize_name(scaffold.type)
                self._scaffold_map[normalized_type] = scaffold
            else:
                # Fallback to class name if no type attribute
                class_name = self._normalize_name(scaffold.__class__.__name__)
                self._scaffold_map[class_name] = scaffold
        
        logger.debug(f"ScaffoldAccessor initialized with {len(self._scaffolds)} scaffolds: {list(self._scaffold_map.keys())}")
    
    def _normalize_name(self, name: str) -> str:
        """
        Normalize scaffold type for attribute access.
        
        Args:
            name: Original scaffold type
            
        Returns:
            Normalized type (lowercase, underscores)
        """
        return name.lower().replace(' ', '_').replace('-', '_')
    
    def __getattr__(self, name: str) -> Any:
        """
        Get scaffold by normalized name.
        
        Args:
            name: Normalized scaffold name
            
        Returns:
            Scaffold instance
            
        Raises:
            AttributeError: If scaffold not found
        """
        if name.startswith('_'):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        
        if name in self._scaffold_map:
            return self._scaffold_map[name]
        
        available_names = list(self._scaffold_map.keys())
        raise AttributeError(f"Scaffold '{name}' not found. Available scaffolds: {available_names}")
    
    def __len__(self) -> int:
        """Get number of scaffold instances."""
        return len(self._scaffolds)
    
    def __iter__(self):
        """Iterate over scaffold instances."""
        return iter(self._scaffolds)
    
    def __bool__(self) -> bool:
        """Check if any scaffolds exist."""
        return len(self._scaffolds) > 0
    
    def list_scaffold_names(self) -> List[str]:
        """Get list of normalized scaffold names."""
        return list(self._scaffold_map.keys())
    
    def __repr__(self) -> str:
        """String representation."""
        names = list(self._scaffold_map.keys())
        return f"ScaffoldAccessor({len(self._scaffolds)} scaffolds: {names})"