"""
Core data types for V2 Context Scaffolds.

Provides ScaffoldState with change tracking and state management capabilities
for scaffold implementations.
"""

import hashlib
import json
from typing import Any, Dict, Optional, Set, Union, ClassVar
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

# Import change tracking infrastructure
from .change_tracking import (
    ChangeTrackingList,
    ChangeTrackingDict, 
    ChangeTrackingSet,
    ChangeTrackingProxy
)


class StateChangeSource(Enum):
    """
    Enum defining the source of scaffold state changes.
    
    Used for automatic source detection in bidirectional scaffolds
    to determine if changes originated from agent/LLM actions or
    external user/system actions.
    """
    AGENT = "agent"        # Agent/LLM initiated changes (tool calls)
    EXTERNAL = "external"  # Human/external system changes (direct calls)


class StateOperatorResult:
    """
    Standard result type for all scaffold operations.
    
    Provides consistent success/failure reporting with optional metadata
    for all scaffold operations in the V2 system.
    """
    
    def __init__(self, message: str, success: bool = True, metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize scaffold operation result.
        
        Args:
            message: Human-readable message describing the operation result
            success: Whether the operation succeeded
            metadata: Optional metadata about the operation
        """
        self.message = message
        self.success = success
        self.metadata = metadata or {}
    
    def __repr__(self) -> str:
        """String representation of the result."""
        status = "SUCCESS" if self.success else "FAILURE"
        return f"StateOperatorResult({status}: {self.message})"
    
    def __bool__(self) -> bool:
        """Boolean conversion returns success status."""
        return self.success


class ScaffoldState(BaseModel):
    """
    Base state class for scaffolds with automatic change detection.
    
    Provides hash-based change tracking to determine when scaffold content
    needs to be re-rendered or when state has been modified.
    
    Configuration Options:
        - tracking_enabled: Global enable/disable for automatic tracking
        - tracking_excluded_fields: Set of field names to exclude from tracking
        - tracking_excluded_types: Set of types to exclude from tracking
    """
    
    model_config = ConfigDict(
        # Allow arbitrary fields for flexible state storage
        extra="allow"
    )
    
    # Built-in type mappings for automatic change tracking
    _trackable_types: ClassVar[Dict[type, type]] = {
        list: ChangeTrackingList,
        dict: ChangeTrackingDict,
        set: ChangeTrackingSet,
    }
    
    # Configuration fields
    tracking_enabled: bool = True
    tracking_excluded_fields: Set[str] = Field(default_factory=set)
    tracking_excluded_types: Set[type] = Field(default_factory=set)
    
    def __init__(self, **data):
        super().__init__(**data)
        # Initialize tracking fields after calling super().__init__
        self.__dict__['_last_hash'] = None
        self.__dict__['_changed_keys'] = set()
        self.__dict__['_dirty'] = False
        self.__dict__['_last_modified'] = datetime.now()
        self.__dict__['_scaffold_ref'] = None  # Will be set by BaseContextScaffold
        
        # CRITICAL: Wrap existing field values with change tracking
        # This handles the case where fields are set during Pydantic initialization
        self._wrap_existing_fields()
    
    def __setattr__(self, key: str, value: Any) -> None:
        """
        Override setattr to track changes and detect source automatically.
        
        This method implements the core bidirectional scaffold functionality:
        - Tracks changes to state fields
        - Automatically detects if change is from AGENT or EXTERNAL source
        - Triggers scaffold state change handlers when appropriate
        """
        # Handle internal fields normally
        if key.startswith('_'):
            self.__dict__[key] = value
            return
        
        # Auto-wrap value with change tracking if applicable
        value = self._auto_track(value, key)
        
        # Check if this is actually a change
        old_value = getattr(self, key, None)
        if old_value != value:
            # ✨ AUTOMATIC SOURCE DETECTION - Core ergonomic DX!
            source = self._detect_change_source()
            
            # Get scaffold reference and trigger state change if available
            scaffold = getattr(self, '_scaffold_ref', None)
            if scaffold:
                old_state = scaffold.get_state_dict() if hasattr(scaffold, 'get_state_dict') else {}
                
                # PRE hook - call pre_state_change with pending changes
                pending_changes = {key: value}
                metadata = {
                    'changes': {key: value},
                    'detection': 'automatic',
                    'timestamp': datetime.now()
                }
                
                # Call pre_state_change hook if available
                if hasattr(scaffold, 'pre_state_change'):
                    pre_result = scaffold.pre_state_change(old_state, pending_changes, source, metadata)
                    
                    # If pre hook returns False, abort the change
                    if pre_result is False:
                        return
                    
                    # If pre hook returns a dict, use it as modified pending changes
                    if isinstance(pre_result, dict):
                        # Update the value with modifications from pre hook
                        if key in pre_result:
                            value = pre_result[key]
                            # Re-wrap with change tracking in case pre hook changed the value
                            value = self._auto_track(value, key)
                
                # Apply the change
                super().__setattr__(key, value)
                
                # Get new state after change
                new_state = scaffold.get_state_dict() if hasattr(scaffold, 'get_state_dict') else {}
                
                # POST hook - call post_state_change with old and new state
                # Use reentrancy guard to prevent infinite recursion
                if hasattr(scaffold, 'post_state_change') and not getattr(scaffold, '_in_state_change_hook', False):
                    try:
                        scaffold._in_state_change_hook = True
                        scaffold.post_state_change(old_state, new_state, source, metadata)
                    finally:
                        scaffold._in_state_change_hook = False
                
                # Update tracking fields
                if '_changed_keys' not in self.__dict__:
                    self.__dict__['_changed_keys'] = set()
                self.__dict__['_changed_keys'].add(key)
                self.__dict__['_dirty'] = True
                self.__dict__['_last_modified'] = datetime.now()
                return
            
            # Fallback: no scaffold reference, just track changes
            if '_changed_keys' not in self.__dict__:
                self.__dict__['_changed_keys'] = set()
            self.__dict__['_changed_keys'].add(key)
            self.__dict__['_dirty'] = True
            self.__dict__['_last_modified'] = datetime.now()
        
        super().__setattr__(key, value)
    
    def _auto_track(self, value: Any, field_name: str, recursive: bool = True) -> Any:
        """
        Automatically wrap values with change tracking if applicable.
        
        Args:
            value: The value being assigned to a field
            field_name: The name of the field being assigned
            recursive: Whether to recursively track nested objects
            
        Returns:
            Either the original value or a change-tracking wrapped version
        """
        # Check if tracking is enabled globally
        if not getattr(self, 'tracking_enabled', True):
            return value
        
        # Check if this field is explicitly excluded or is a configuration field
        excluded_fields = getattr(self, 'tracking_excluded_fields', set())
        config_fields = {'tracking_enabled', 'tracking_excluded_fields', 'tracking_excluded_types'}
        if field_name in excluded_fields or field_name in config_fields:
            return value
        
        # Check if this value's type is excluded
        excluded_types = getattr(self, 'tracking_excluded_types', set())
        if type(value) in excluded_types or any(isinstance(value, exc_type) for exc_type in excluded_types):
            return value
        
        # Check built-in trackable types first
        for base_type, tracking_type in self._trackable_types.items():
            if isinstance(value, base_type) and not isinstance(value, tracking_type):
                wrapped = tracking_type(value, self, field_name)
                
                # If recursive tracking enabled, track nested objects
                if recursive:
                    wrapped = self._track_nested_objects(wrapped, field_name, None)
                
                return wrapped
        
        # For custom objects, wrap with ChangeTrackingProxy
        # Skip simple types, already-wrapped objects, and callables
        if (not isinstance(value, (str, int, float, bool, type(None))) and
            not isinstance(value, (ChangeTrackingList, ChangeTrackingDict, ChangeTrackingSet, ChangeTrackingProxy)) and
            not callable(value) and
            hasattr(value, '__dict__')):  # Has attributes that can be modified
            wrapped = ChangeTrackingProxy(value, self, field_name)
            
            # If recursive tracking enabled, track nested objects
            if recursive:
                wrapped = self._track_nested_objects(wrapped, field_name, None)
            
            return wrapped
        
        # Return original value if not trackable
        return value
    
    def _wrap_existing_fields(self) -> None:
        """
        Wrap existing field values with change tracking.
        
        This method is called after Pydantic initialization to ensure that
        any fields that were set during __init__ get properly wrapped with
        change tracking.
        """
        # Skip if tracking is disabled
        if not getattr(self, 'tracking_enabled', True):
            return
        
        # Get all fields that were set during initialization
        for field_name in self.__dict__:
            # Skip private fields and configuration fields
            if field_name.startswith('_'):
                continue
            
            excluded_fields = getattr(self, 'tracking_excluded_fields', set())
            config_fields = {'tracking_enabled', 'tracking_excluded_fields', 'tracking_excluded_types'}
            if field_name in excluded_fields or field_name in config_fields:
                continue
            
            # Get the current value
            current_value = self.__dict__[field_name]
            
            # Skip callable methods (they shouldn't be tracked)
            if callable(current_value):
                continue
            
            # Check if it needs wrapping
            wrapped_value = self._auto_track(current_value, field_name, recursive=True)
            
            # If wrapping changed the value, update it directly in __dict__
            # to avoid triggering __setattr__ (which would mark it as changed)
            if wrapped_value is not current_value:
                self.__dict__[field_name] = wrapped_value
    
    def _track_nested_objects(self, wrapped_obj: Any, parent_field_name: str, _visited: Optional[Set[int]] = None) -> Any:
        """
        Recursively track nested objects within a wrapped object.
        
        Args:
            wrapped_obj: The already-wrapped parent object
            parent_field_name: Name of the parent field
            _visited: Set of object ids to prevent circular references
            
        Returns:
            The same wrapped object (modifications are done in-place)
        """
        # Initialize visited set for circular reference detection
        if _visited is None:
            _visited = set()
        
        # Get the actual object to check for circular references
        actual_obj = wrapped_obj._wrapped if hasattr(wrapped_obj, '_wrapped') else wrapped_obj
        obj_id = id(actual_obj)
        
        # Check for circular references
        if obj_id in _visited:
            return wrapped_obj  # Skip processing to avoid infinite recursion
        
        # Add to visited set
        _visited.add(obj_id)
        try:
            # Handle different types of wrapped objects
            if isinstance(wrapped_obj, ChangeTrackingDict):
                # Track nested objects in dictionary values
                for key, value in list(wrapped_obj.items()):
                    nested_field_name = f"{parent_field_name}.{key}"
                    tracked_value = self._auto_track_with_visited(value, nested_field_name, _visited)
                    if tracked_value is not value:  # Only replace if actually wrapped
                        wrapped_obj[key] = tracked_value
            
            elif isinstance(wrapped_obj, ChangeTrackingList):
                # Track nested objects in list items
                for i, value in enumerate(list(wrapped_obj)):
                    nested_field_name = f"{parent_field_name}[{i}]"
                    tracked_value = self._auto_track_with_visited(value, nested_field_name, _visited)
                    if tracked_value is not value:  # Only replace if actually wrapped
                        wrapped_obj[i] = tracked_value
            
            elif isinstance(wrapped_obj, ChangeTrackingSet):
                # Sets are trickier since we can't modify items in place
                # We need to replace the entire set content
                original_items = list(wrapped_obj)
                tracked_items = []
                any_changed = False
                
                for i, value in enumerate(original_items):
                    nested_field_name = f"{parent_field_name}[{i}]"
                    tracked_value = self._auto_track_with_visited(value, nested_field_name, _visited)
                    tracked_items.append(tracked_value)
                    if tracked_value is not value:
                        any_changed = True
                
                if any_changed:
                    wrapped_obj.clear()
                    wrapped_obj.update(tracked_items)
            
            elif isinstance(wrapped_obj, ChangeTrackingProxy):
                # Track nested objects in proxy attributes
                # We need to be careful not to trigger infinite recursion
                wrapped = wrapped_obj._wrapped
                if hasattr(wrapped, '__dict__'):
                    for attr_name, value in vars(wrapped).items():
                        # Skip callable attributes (methods) to avoid wrapping issues
                        if callable(value):
                            continue
                        
                        # Skip PACTCore immutable attributes to prevent errors
                        if hasattr(wrapped, '__class__'):
                            # Check if this is a PACTCore or subclass
                            from ..context_management.pact.components.core import PACTCore
                            if isinstance(wrapped, PACTCore):
                                # Skip metadata and other immutable fields
                                if attr_name in ['metadata'] or (hasattr(wrapped, '_immutable_fields') and attr_name in wrapped._immutable_fields):
                                    continue
                        
                        nested_field_name = f"{parent_field_name}.{attr_name}"
                        tracked_value = self._auto_track_with_visited(value, nested_field_name, _visited)
                        if tracked_value is not value:  # Only replace if actually wrapped
                            setattr(wrapped, attr_name, tracked_value)
        
        finally:
            # Remove from visited set when done processing
            _visited.discard(obj_id)
        
        return wrapped_obj
    
    def _auto_track_with_visited(self, value: Any, field_name: str, visited: Set[int]) -> Any:
        """
        Auto-track with circular reference detection.
        
        Args:
            value: The value to track
            field_name: Name of the field
            visited: Set of visited object IDs
            
        Returns:
            Tracked or original value
        """
        # Check for circular reference at the value level
        if hasattr(value, '__dict__'):
            value_id = id(value)
            if value_id in visited:
                return value  # Skip to prevent circular reference
        
        # Use normal auto-tracking but pass visited set for nested tracking
        tracked = self._auto_track(value, field_name, recursive=False)  # Don't recurse here
        
        # If something was wrapped, then do nested tracking with visited set
        if tracked is not value:
            tracked = self._track_nested_objects(tracked, field_name, visited)
        
        return tracked
    
    def configure_tracking(self, 
                          enabled: Optional[bool] = None,
                          excluded_fields: Optional[Set[str]] = None,
                          excluded_types: Optional[Set[type]] = None) -> None:
        """
        Configure tracking behavior for this state instance.
        
        Args:
            enabled: Whether to enable automatic tracking globally
            excluded_fields: Set of field names to exclude from tracking
            excluded_types: Set of types to exclude from tracking
        """
        if enabled is not None:
            self.tracking_enabled = enabled
        
        if excluded_fields is not None:
            # Validate field names
            for field in excluded_fields:
                if not isinstance(field, str):
                    raise TypeError(f"Excluded field names must be strings, got {type(field).__name__}")
            self.tracking_excluded_fields = excluded_fields
        
        if excluded_types is not None:
            # Validate types
            for exc_type in excluded_types:
                if not isinstance(exc_type, type):
                    raise TypeError(f"Excluded types must be types, got {type(exc_type).__name__}")
            self.tracking_excluded_types = excluded_types
    
    def exclude_field(self, field_name: str) -> None:
        """
        Add a field to the exclusion list.
        
        Args:
            field_name: Name of field to exclude from tracking
        """
        if not isinstance(field_name, str):
            raise TypeError(f"Field name must be a string, got {type(field_name).__name__}")
        
        if not hasattr(self, 'tracking_excluded_fields'):
            self.tracking_excluded_fields = set()
        self.tracking_excluded_fields.add(field_name)
    
    def include_field(self, field_name: str) -> None:
        """
        Remove a field from the exclusion list.
        
        Args:
            field_name: Name of field to include in tracking
        """
        if hasattr(self, 'tracking_excluded_fields') and field_name in self.tracking_excluded_fields:
            self.tracking_excluded_fields.remove(field_name)
    
    def exclude_type(self, exc_type: type) -> None:
        """
        Add a type to the exclusion list.
        
        Args:
            exc_type: Type to exclude from tracking
        """
        if not isinstance(exc_type, type):
            raise TypeError(f"Excluded type must be a type, got {type(exc_type).__name__}")
        
        if not hasattr(self, 'tracking_excluded_types'):
            self.tracking_excluded_types = set()
        self.tracking_excluded_types.add(exc_type)
    
    def include_type(self, exc_type: type) -> None:
        """
        Remove a type from the exclusion list.
        
        Args:
            exc_type: Type to include in tracking
        """
        if hasattr(self, 'tracking_excluded_types') and exc_type in self.tracking_excluded_types:
            self.tracking_excluded_types.remove(exc_type)
    
    def get_tracking_config(self) -> Dict[str, Any]:
        """
        Get current tracking configuration.
        
        Returns:
            Dictionary with current tracking configuration
        """
        return {
            'enabled': getattr(self, 'tracking_enabled', True),
            'excluded_fields': getattr(self, 'tracking_excluded_fields', set()).copy(),
            'excluded_types': getattr(self, 'tracking_excluded_types', set()).copy(),
            'registered_types': list(self._trackable_types.keys())
        }
    
    def _detect_change_source(self) -> 'StateChangeSource':
        """
        Automatically detect if change is from tool execution or external call.
        
        Returns:
            StateChangeSource.AGENT if called during tool execution
            StateChangeSource.EXTERNAL if called externally
        """
        scaffold = getattr(self, '_scaffold_ref', None)
        if scaffold and hasattr(scaffold, '_agent') and scaffold._agent:
            # Check if agent is currently executing tools
            if hasattr(scaffold._agent, 'controller') and scaffold._agent.controller:
                if hasattr(scaffold._agent.controller, 'is_tool_executing') and scaffold._agent.controller.is_tool_executing:
                    return StateChangeSource.AGENT  # LLM tool call
        return StateChangeSource.EXTERNAL  # Direct user/external call
    
    def compute_hash(self) -> str:
        """
        Compute hash of current state for change detection.
        
        Returns:
            String hash of the current state
        """
        # Use Pydantic's model_dump to get all field values, excluding private fields
        state_data = self.model_dump(exclude={'_last_hash', '_changed_keys', '_dirty', '_last_modified'})
        
        # Convert to JSON string for consistent hashing
        try:
            json_str = json.dumps(state_data, sort_keys=True, default=str)
            return hashlib.sha256(json_str.encode()).hexdigest()
        except (TypeError, ValueError) as e:
            # Fallback for non-JSON-serializable data
            fallback_str = str(sorted(state_data.items()))
            return hashlib.sha256(fallback_str.encode()).hexdigest()
    
    def has_changed(self, update_hash: bool = True) -> bool:
        """
        Check if state has changed since last check.
        
        Args:
            update_hash: Whether to update the stored hash after checking
            
        Returns:
            True if state has changed, False otherwise
        """
        current_hash = self.compute_hash()
        last_hash = self.__dict__.get('_last_hash')
        
        # First run - no previous hash to compare
        if last_hash is None:
            if update_hash:
                self.__dict__['_last_hash'] = current_hash
                self.__dict__['_dirty'] = False
                if '_changed_keys' in self.__dict__:
                    self.__dict__['_changed_keys'].clear()
            return True
        
        # Compare with stored hash
        changed = current_hash != last_hash
        
        if update_hash and changed:
            self.__dict__['_last_hash'] = current_hash
            self.__dict__['_dirty'] = False
            if '_changed_keys' in self.__dict__:
                self.__dict__['_changed_keys'].clear()
        
        return changed
    
    def mark_changed(self, *keys: str) -> None:
        """
        Manually mark specific keys as changed and trigger state change flow.
        
        Args:
            *keys: Keys to mark as changed
        """
        if '_changed_keys' not in self.__dict__:
            self.__dict__['_changed_keys'] = set()
        
        # Store old state before marking changes
        old_state = self.get_state_dict()
        
        # Mark the changes
        self.__dict__['_changed_keys'].update(keys)
        self.__dict__['_dirty'] = True
        self.__dict__['_last_modified'] = datetime.now()
        # Force hash update on next check
        self.__dict__['_last_hash'] = None
        
        # Trigger state change flow if scaffold reference exists
        scaffold = getattr(self, '_scaffold_ref', None)
        if scaffold:
            new_state = self.get_state_dict()
            source = self._detect_change_source()
            
            metadata = {
                'changes': {key: getattr(self, key, None) for key in keys},
                'detection': 'mark_changed',
                'timestamp': datetime.now()
            }
            
            # Only call POST hook - no PRE hook since there are no pending changes to validate
            # Use reentrancy guard to prevent infinite recursion
            if hasattr(scaffold, 'post_state_change') and not getattr(scaffold, '_in_state_change_hook', False):
                try:
                    scaffold._in_state_change_hook = True
                    scaffold.post_state_change(old_state, new_state, source, metadata)
                finally:
                    scaffold._in_state_change_hook = False
    
    def get_changed_keys(self) -> Set[str]:
        """
        Get set of keys that have changed since last check.
        
        Returns:
            Set of changed key names
        """
        return self.__dict__.get('_changed_keys', set()).copy()
    
    def clear_changes(self) -> None:
        """Clear change tracking state."""
        if '_changed_keys' in self.__dict__:
            self.__dict__['_changed_keys'].clear()
        self.__dict__['_dirty'] = False
        self.__dict__['_last_hash'] = self.compute_hash()
        self.__dict__['_last_modified'] = datetime.now()
    
    def get_last_modified(self) -> Optional[datetime]:
        """
        Get timestamp of last modification.
        
        Returns:
            DateTime of last modification or None if never modified
        """
        return self.__dict__.get('_last_modified')
    
    def update_state(self, **updates: Any) -> None:
        """
        Update multiple state fields at once.
        
        Args:
            **updates: Key-value pairs to update
        """
        for key, value in updates.items():
            setattr(self, key, value)
    
    def _batch_update(self, updates: Dict[str, Any]) -> bool:
        """
        Apply multiple state changes atomically without triggering per-field hooks.
        
        This method is used internally to avoid N+1 hook execution when updating
        multiple fields at once. It preserves change tracking wrappers and only
        triggers hooks once at the batch level.
        
        Args:
            updates: Dictionary of field updates to apply
            
        Returns:
            True if any changes were made, False if no changes occurred
        """
        if not updates:
            return False
        
        # Check which fields will actually change
        changes_to_apply = {}
        for key, new_value in updates.items():
            # Skip internal fields
            if key.startswith('_'):
                continue
                
            # Auto-wrap value with change tracking if applicable
            wrapped_value = self._auto_track(new_value, key)
            
            # Check if this is actually a change
            old_value = getattr(self, key, None)
            if old_value != wrapped_value:
                changes_to_apply[key] = wrapped_value
        
        # If no actual changes, return False
        if not changes_to_apply:
            return False
        
        # Apply all changes directly to __dict__ to bypass __setattr__ hooks
        for key, value in changes_to_apply.items():
            # Use Pydantic's direct setting to maintain model consistency
            super(ScaffoldState, self).__setattr__(key, value)
        
        # Update tracking fields once for all changes
        if '_changed_keys' not in self.__dict__:
            self.__dict__['_changed_keys'] = set()
        self.__dict__['_changed_keys'].update(changes_to_apply.keys())
        self.__dict__['_dirty'] = True
        self.__dict__['_last_modified'] = datetime.now()
        self.__dict__['_last_hash'] = None  # Force hash update on next check
        
        return True
    
    def get_state_dict(self) -> Dict[str, Any]:
        """
        Get current state as dictionary (excluding private fields).
        
        Returns:
            Dictionary of current state
        """
        return self.model_dump(exclude={'_last_hash', '_changed_keys', '_dirty', '_last_modified'})
    
    def reset_to_state(self, state_dict: Dict[str, Any]) -> None:
        """
        Reset state to provided dictionary.
        
        Args:
            state_dict: Dictionary to reset state to
        """
        # Get current field names from the model
        current_fields = set(self.model_dump().keys())
        
        # Clear current fields that aren't private
        for field_name in current_fields:
            if hasattr(self, field_name):
                delattr(self, field_name)
        
        # Set new state
        for key, value in state_dict.items():
            setattr(self, key, value)
    
    @classmethod
    def register_trackable_type(cls, base_type: type, tracking_type: type) -> None:
        """
        Register custom type for automatic change tracking.
        
        This allows users to register their own classes to be automatically
        wrapped with custom change tracking implementations.
        
        Args:
            base_type: The base type to track (e.g., CustomCollection)
            tracking_type: The tracking wrapper type (e.g., ChangeTrackingCustomCollection)
            
        Raises:
            TypeError: If base_type is not a type or tracking_type doesn't inherit from ChangeNotifier
            ValueError: If base_type is already registered
            
        Example:
            ```python
            class CustomCollection:
                def __init__(self):
                    self.items = []
                
                def add_item(self, item):
                    self.items.append(item)
            
            class ChangeTrackingCustomCollection(ChangeNotifier, CustomCollection):
                def __init__(self, original, state_ref, field_name):
                    ChangeNotifier.__init__(self, state_ref, field_name)
                    CustomCollection.__init__(self)
                    # Copy data from original
                    self.items = list(original.items)
                
                def add_item(self, item):
                    super().add_item(item)
                    self._notify_change()
            
            # Register the type
            ScaffoldState.register_trackable_type(CustomCollection, ChangeTrackingCustomCollection)
            
            # Now CustomCollection instances will be automatically tracked
            state = MyState()
            state.collection = CustomCollection()  # Automatically wrapped
            state.collection.add_item("test")      # Triggers change detection
            ```
        """
        # Validate parameters
        if not isinstance(base_type, type):
            raise TypeError(f"base_type must be a type, got {type(base_type).__name__}")
        
        if not isinstance(tracking_type, type):
            raise TypeError(f"tracking_type must be a type, got {type(tracking_type).__name__}")
        
        # Check if tracking_type inherits from ChangeNotifier
        from .change_tracking import ChangeNotifier
        if not issubclass(tracking_type, ChangeNotifier):
            raise TypeError(f"tracking_type must inherit from ChangeNotifier")
        
        # Check if already registered
        if base_type in cls._trackable_types:
            current_type = cls._trackable_types[base_type]
            if current_type is not tracking_type:
                raise ValueError(f"Type {base_type.__name__} already registered with {current_type.__name__}")
        
        # Register the type
        cls._trackable_types[base_type] = tracking_type
    
    @classmethod
    def unregister_trackable_type(cls, base_type: type) -> bool:
        """
        Unregister a custom trackable type.
        
        Args:
            base_type: The base type to unregister
            
        Returns:
            True if the type was registered and removed, False if not found
            
        Example:
            ```python
            # Remove custom registration
            was_registered = ScaffoldState.unregister_trackable_type(CustomCollection)
            ```
        """
        if not isinstance(base_type, type):
            raise TypeError(f"base_type must be a type, got {type(base_type).__name__}")
        
        # Don't allow unregistering built-in types
        builtin_types = {list, dict, set}
        if base_type in builtin_types:
            raise ValueError(f"Cannot unregister built-in type {base_type.__name__}")
        
        return cls._trackable_types.pop(base_type, None) is not None
    
    @classmethod
    def get_trackable_types(cls) -> Dict[type, type]:
        """
        Get a copy of all registered trackable types.
        
        Returns:
            Dictionary mapping base types to their tracking implementations
            
        Example:
            ```python
            types = ScaffoldState.get_trackable_types()
            print(f"Registered types: {list(types.keys())}")
            ```
        """
        return cls._trackable_types.copy()
    
    @classmethod
    def is_type_trackable(cls, obj_type: type) -> bool:
        """
        Check if a type is registered for automatic tracking.
        
        Args:
            obj_type: The type to check
            
        Returns:
            True if the type is registered for automatic tracking
            
        Example:
            ```python
            if ScaffoldState.is_type_trackable(CustomCollection):
                print("CustomCollection will be automatically tracked")
            ```
        """
        return obj_type in cls._trackable_types