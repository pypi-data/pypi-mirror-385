"""
ContextUpdateHandler - Clean CoreOffsetArray-based update logic.

Rewritten from scratch to work with the new PACT architecture:
- DepthArray for Context depth management
- CoreOffsetArray containers with zero-centered offsets
- Computed coordinates via component.coordinates property
- Direct parent_id relationships instead of registry lookups
- CoreOffsetArray insert operations with stack pushing
"""

from typing import Optional, Any, List, Dict, Union, Tuple, Set, TYPE_CHECKING
from dataclasses import dataclass, field
from datetime import datetime
from ..components import ContextComponent, TextContextComponent, MessageContainer
from .position import Pos
from ..data_structures.coordinates import Coordinates

# Type hints only
if TYPE_CHECKING:
    from .base import Context, UpdateResult, UpdateOperation


class ContextUpdateHandler:
    """Clean CoreOffsetArray-based update handler."""
    
    def __init__(self, context: 'Context'):
        self.context = context
    
    def update(self, 
               pos_or_selector: Optional[Union[Pos, str, ContextComponent, List[ContextComponent]]] = None, 
               component: Optional[Union[ContextComponent, str]] = None, 
               mode: Optional[str] = None,
               content: Optional[str] = None, 
               behavior: str = "queued", 
               **kwargs) -> 'UpdateResult':
        """
        Enhanced Context.update() method with CoreOffsetArray operations.
        
        Supports both new position-based modes and legacy behavior modes:
        
        New modes (using PACT coordinates):
        - update(Pos("(d0,1)"), component, mode='append') - Append with core offset layout rule
        - update(Pos("(d0,1)"), component, mode='replace') - Replace at exact position
        
        Legacy modes (backward compatibility):
        - update("#key", content="new content", behavior="queued") - Queue update operation
        
        Args:
            pos_or_selector: PACT selector (Pos, str) or legacy selector
            component: Component for position-based operations
            mode: 'append' or 'replace' for position-based operations
            content: New content to set (legacy mode)
            behavior: Execution behavior ("queued", "dispatch", "force") - legacy mode
            **kwargs: Other properties to update
        
        Returns:
            UpdateResult indicating success/failure and details
        """
        from .base import UpdateResult
        
        try:
            # Global update: no arguments = process all internal state changes
            if pos_or_selector is None and component is None and mode is None:
                return self._update_global()
            
            # Position-based modes (append/replace)
            if mode is not None:
                if mode not in ['append', 'replace']:
                    return UpdateResult(
                        success=False,
                        errors=[f"Invalid mode: {mode}. Must be 'append' or 'replace'"]
                    )
                if component is None:
                    return UpdateResult(
                        success=False,
                        errors=["Component or string content required for position-based update modes"]
                    )
                return self._update_position_based(pos_or_selector, component, mode)
            
            # Legacy mode - content updates (redirect to appropriate behavior)
            valid_behaviors = {"queued", "dispatch", "force"}
            if behavior not in valid_behaviors:
                return UpdateResult(
                    success=False,
                    errors=[f"Unknown behavior: {behavior}. Must be one of: {', '.join(valid_behaviors)}"]
                )
            
            if behavior == "queued":
                return self._update_queued(pos_or_selector, content, **kwargs)
            elif behavior == "dispatch":
                return self._update_dispatch(pos_or_selector, content, **kwargs)
            elif behavior == "force":
                return self._update_force(pos_or_selector, content, **kwargs)
            else:
                return UpdateResult(
                    success=False,
                    errors=[f"Unhandled behavior: {behavior}"]
                )
                
        except Exception as e:
            return UpdateResult(
                success=False,
                errors=[f"Update failed: {str(e)}"]
            )
    
    def _update_global(self) -> 'UpdateResult':
        """
        Global update: Process all internal state changes (cycle processing, timing).
        """
        from .base import UpdateResult
        
        try:
            # Check if we need to process this cycle (optimization)
            current_cycle = getattr(self.context, 'current_episode', 0)
            last_processed = getattr(self.context, '_last_processed_cycle', -1)
            
            if current_cycle == last_processed:
                return UpdateResult(
                    success=True,
                    warnings=[f"Cycle {current_cycle} already processed, skipping"]
                )
            
            # Process dynamic components (TTL/cadence updates)
            updated_components = []
            for component_id in self.context._registry.get_dynamic_components().copy():
                component = self.context.get_component_by_id(component_id)
                if component is not None:
                    # Update component temporal status
                    if hasattr(self.context, 'update_component_temporal_status'):
                        self.context.update_component_temporal_status(component)
                    updated_components.append(component)
            
            # Process cadence component rehydration
            rehydrated_components = []
            components_for_rehydration = self.context._registry.get_components_for_rehydration(current_cycle)
            
            for cadence_info in components_for_rehydration:
                print(f"🔄 Attempting to rehydrate {cadence_info.component_id} at {cadence_info.original_coordinates}")
                try:
                    # Recreate the component from stored data
                    component_class_name = cadence_info.component_data.get('__class__', 'TextContent')

                    # Import the appropriate component class (support both legacy and PACT)
                    from egregore.core.context_management.pact.components.core import TextContent, MessageContainer
                    component_classes = {
                        'TextContent': TextContent,
                        'TextContextComponent': TextContent,  # Legacy alias
                        'MessageContainer': MessageContainer,
                    }

                    component_class = component_classes.get(component_class_name, TextContent)
                    rehydrated_component = component_class.parse_obj(cadence_info.component_data)
                    
                    # Update component's birth cycle to current cycle (fresh lifecycle)
                    if hasattr(rehydrated_component, 'metadata'):
                        rehydrated_component.metadata.born_cycle = current_cycle
                    
                    # Insert the component back at the original coordinates
                    insert_result = self.context.insert(cadence_info.original_coordinates, rehydrated_component)
                    if insert_result.success:
                        rehydrated_components.append(rehydrated_component)
                        print(f"✅ Rehydrated {cadence_info.component_id} at {cadence_info.original_coordinates}")
                    else:
                        print(f"❌ Failed to insert rehydrated component: {insert_result.errors}")
                        
                except Exception as e:
                    # Log rehydration failure but continue processing other components
                    print(f"DEBUG: Failed to rehydrate component {cadence_info.component_id}: {e}")
            
            # Update cycle tracking
            if hasattr(self.context, '_last_processed_cycle'):
                self.context._last_processed_cycle = current_cycle
            
            # Combine warnings
            warnings = [f"Processed {len(updated_components)} dynamic components in cycle {current_cycle}"]
            if rehydrated_components:
                warnings.append(f"Rehydrated {len(rehydrated_components)} cadence components in cycle {current_cycle}")
            
            return UpdateResult(
                success=True,
                updated_components=updated_components + rehydrated_components,
                warnings=warnings
            )
            
        except Exception as e:
            return UpdateResult(
                success=False,
                errors=[f"Global update failed: {str(e)}"]
            )
    
    def _update_position_based(self, pos: Union[Pos, str], component: Union[ContextComponent, str], mode: str) -> 'UpdateResult':
        """
        Position-based update with append/replace modes using CoreOffsetArray operations.
        
        Args:
            pos: Position specification (Pos object or string)
            component: Component to insert or replace, or string to convert to TextContextComponent
            mode: 'append' (core offset layout rule) or 'replace' (exact position)
        """
        from .base import UpdateResult
        
        try:
            # Convert string to Pos if needed
            if isinstance(pos, str):
                pos = Pos(pos)
            
            # Convert string component to TextContextComponent (like insert does)
            if isinstance(component, str):
                # Block empty string updates
                if not component.strip():
                    return UpdateResult(success=False, errors=["Empty string content not allowed"])
                
                from ..components.core_components.content import TextContextComponent
                component = TextContextComponent(content=component)
                
            # Validate tool components can only be in message containers
            from ...tool_calling.context_components import ToolCall, ToolResult
            if isinstance(component, (ToolCall, ToolResult)):
                # Check if target selector is a message container position (dN,0,M)
                pos_str = str(pos)
                # Pattern should be like "d0,0" or "(d0,0)" - message container positions
                import re
                if not re.match(r'^\(?d\d*,0(?:,\d+)?\)?$', pos_str):
                    component_type = "ToolCall" if isinstance(component, ToolCall) else "ToolResult"
                    return UpdateResult(
                        success=False,
                        errors=[f"{component_type} can only be updated in MessageContainer positions (dN,0,M), not {pos}"]
                    )
            
            if mode == 'append':
                return self._update_append_mode(pos, component)
            elif mode == 'replace':
                return self._update_replace_mode(pos, component)
            else:
                return UpdateResult(
                    success=False,
                    errors=[f"Invalid mode: {mode}. Must be 'append' or 'replace'"]
                )
                
        except Exception as e:
            return UpdateResult(
                success=False,
                errors=[f"Position-based update failed: {str(e)}"]
            )
    
    def _update_append_mode(self, pos: Pos, component: ContextComponent) -> 'UpdateResult':
        """
        Append mode: Add component using core offset layout rule.
        
        Core Offset Layout Rule:
        1. If position 0 missing: Always fill position 0 first
        2. Otherwise:
           - Positive request: First available >= requested position
           - Negative request: First available <= requested position (more negative)
        """
        from .base import UpdateResult
        
        try:
            # Resolve target container and requested position
            target_container, requested_position = self._resolve_append_target(pos)
            
            # Set creation metadata
            self._assign_creation_index(component)
            current_cycle = getattr(self.context, 'current_episode', 0)
            component.metadata.born_cycle = current_cycle
            
            # Set parent relationship
            component.parent_id = target_container.id
            
            # Append using CoreOffsetArray with offset awareness
            if hasattr(target_container, 'content'):
                if hasattr(target_container.content, "append"):
                    actual_position = target_container.content.append(component, requested_position)
                else:
                    # Fallback for non-CoreOffsetArray containers
                    target_container.content[requested_position] = component
                    actual_position = requested_position
            else:
                raise ValueError(f"Target container {type(target_container)} does not support CoreOffsetArray insertion")
            
            # Inject context reference for computed coordinates
            if hasattr(component, '_inject_context_ref'):
                component._inject_context_ref(self.context)
            
            # Register in remaining registries (keys, types, tags, dynamic components)
            self.context._registry.register_component(component)
            
            return UpdateResult(
                success=True,
                updated_components=[component],
                warnings=[f"Component appended at position {actual_position} (requested {requested_position})"]
            )
                
        except Exception as e:
            return UpdateResult(
                success=False,
                errors=[f"Append mode failed: {str(e)}"]
            )
    
    def _update_replace_mode(self, pos: Pos, component: ContextComponent) -> 'UpdateResult':
        """
        Replace mode: Replace component at exact position without shifting.
        """
        from .base import UpdateResult
        
        try:
            # Check for structural component replacement attempts
            pos_str = str(pos).strip('()')
            if pos_str in ['d0,0', 'd-1,0'] or pos_str.startswith('d0,0,'):
                # These are structural components that should not be replaced
                component_name = {
                    'd0,0': 'ActiveMessageComponent (d0,0)',
                    'd-1,0': 'SystemHeaderComponent (d-1,0)'
                }.get(pos_str.split(',')[0] + ',0', f'structural component ({pos_str})')
                
                return UpdateResult(
                    success=False,
                    errors=[f"Cannot replace {component_name} - structural components are not replaceable. Use d0,0,0 to replace message content instead."]
                )
            
            # Resolve target container and exact position
            target_container, exact_position = self._resolve_replace_target(pos)
            
            # Set creation metadata
            self._assign_creation_index(component)
            current_cycle = getattr(self.context, 'current_episode', 0)
            component.metadata.born_cycle = current_cycle
            
            # Check if position exists in CoreOffsetArray
            if not hasattr(target_container, 'content'):
                return UpdateResult(
                    success=False,
                    errors=[f"Target {type(target_container).__name__} has no content"]
                )
            
            if not hasattr(target_container.content, '__contains__') or exact_position not in target_container.content:
                return UpdateResult(
                    success=False,
                    errors=[f"Position {exact_position} does not exist in {type(target_container).__name__}.content"]
                )
            
            # Remove from current parent if different
            current_parent_id = getattr(component, 'parent_id', None)
            if current_parent_id and current_parent_id != target_container.id:
                self._remove_from_current_parent(component, current_parent_id)
            
            # Get old component for cleanup
            # Get old component for cleanup (after validation, since target_container exists)
            old_component = target_container.content[exact_position]
            
            # Replace at exact position
            target_container.content[exact_position] = component
            
            # Update parent reference
            component.parent_id = target_container.id
            
            # Inject context reference for computed coordinates
            if hasattr(component, '_inject_context_ref'):
                component._inject_context_ref(self.context)
            
            # Register new component
            self.context._registry.register_component(component)
            
            # Unregister old component and cascade to descendants
            if hasattr(old_component, 'id'):
                self._cascade_unregister_descendants(old_component.id)
            
            return UpdateResult(
                success=True,
                updated_components=[component],
                warnings=[f"Component replaced at position {exact_position}"]
            )
                
        except Exception as e:
            return UpdateResult(
                success=False,
                errors=[f"Replace mode failed: {str(e)}"]
            )
    
    def _resolve_append_target(self, pos: Pos) -> Tuple[ContextComponent, int]:
        """
        Resolve append target using PACT coordinates.
        
        Returns:
            (target_container, requested_position) for append operation
        """
        selector_str = pos.selector
        
        # Handle coordinate selectors like "(d0,1)", "(d0,1,2)"
        if selector_str.startswith('(') and ')' in selector_str:
            coord_str = selector_str.strip('()')
            
            if not coord_str.startswith('d'):
                raise ValueError(f"Invalid coordinate format: {selector_str}")
            
            # Parse coordinates
            coords = self._parse_coordinates(coord_str)
            
            if len(coords) == 1:
                # Single depth: (d0) -> append to active message MessageContainer at offset 0
                depth = coords[0]
                
                # Validate depth exists
                if not self._validate_depth_exists(depth):
                    raise ValueError(f"PACT depth {depth} does not exist. Cannot append to non-existent depth.")
                
                depth_component = self._get_component_by_depth(depth)
                
                if depth == 0:  # Active message
                    # Get MessageContainer at offset 0
                    if hasattr(depth_component, 'content') and hasattr(depth_component.content, '__getitem__'):
                        message_container = depth_component.content[0]
                        return message_container, 0  # Append with position preference 0
                    raise ValueError(f"Invalid depth component structure at depth {depth}")
                else:
                    # Other depths - append directly
                    return depth_component, 0
                    
            elif len(coords) == 2:
                # Two coordinates: (d0,1) -> append to depth 0, with position preference 1
                depth, requested_position = coords
                
                # Validate depth exists
                if not self._validate_depth_exists(depth):
                    raise ValueError(f"PACT depth {depth} does not exist. Cannot append to non-existent depth.")
                
                depth_component = self._get_component_by_depth(depth)
                
                # Special case: position 0 at any depth is reserved for MessageContainer
                # Redirect (dN,0) append to append INTO the MessageContainer at (dN,0,N)
                if requested_position == 0:
                    if hasattr(depth_component, 'content') and hasattr(depth_component.content, '__getitem__'):
                        message_container = depth_component.content[0]  # MessageContainer at position 0
                        return message_container, requested_position  # Let Core Offset Layout Rule handle positioning
                    raise ValueError(f"Invalid depth component structure at depth {depth} - no MessageContainer at position 0")
                
                return depth_component, requested_position
                    
            else:
                # Three+ coordinates: (d0,1,2) -> navigate to container and append with position preference
                depth = coords[0]
                
                # Validate depth exists
                if not self._validate_depth_exists(depth):
                    raise ValueError(f"PACT depth {depth} does not exist. Cannot append to non-existent depth.")
                
                current = self._get_component_by_depth(depth)
                
                # Navigate to target container
                for coord in coords[1:-1]:
                    if hasattr(current, 'content') and hasattr(current.content, '__contains__'):
                        if coord not in current.content:
                            raise ValueError(f"Container path doesn't exist: {coords[:-1]}")
                        current = current.content[coord]
                    else:
                        raise ValueError(f"Invalid container structure at coordinate {coord}")
                
                # Append with final coordinate as position preference
                requested_position = coords[-1]
                return current, requested_position
        
        # Handle key selectors like "#key"
        elif selector_str.startswith('#'):
            key = selector_str[1:]
            component_id = self.context._registry.find_by_key(key)
            if component_id:
                target = self.context.get_component_by_id(component_id)
                if target and hasattr(target, 'content'):
                    return target, 0
            
            # Key not found - append to active message
            message_container = self.context.active_message.content[0]
            return message_container, 0
        
        # Handle type selectors like ".type"
        elif selector_str.startswith('.'):
            type_name = selector_str[1:]
            component_ids = self.context._registry.find_by_type(type_name)
            if component_ids:
                component_id = next(iter(component_ids))
                target = self.context.get_component_by_id(component_id)
                if target and hasattr(target, 'content'):
                    return target, 0
            
            # Type not found - append to active message
            message_container = self.context.active_message.content[0]
            return message_container, 0
        
        # Default: append to active message MessageContainer
        message_container = self.context.active_message.content[0]
        return message_container, 0
    
    def _resolve_replace_target(self, pos: Pos) -> Tuple[ContextComponent, int]:
        """
        Resolve replace target using PACT coordinates.
        
        Returns:
            (target_container, exact_position) for replace operation
        """
        selector_str = pos.selector
        
        # Handle coordinate selectors like "(d0,1)", "(d0,1,2)" 
        if selector_str.startswith('(') and ')' in selector_str:
            coord_str = selector_str.strip('()')
            
            if not coord_str.startswith('d'):
                raise ValueError(f"Invalid coordinate format: {selector_str}")
            
            # Parse coordinates
            coords = self._parse_coordinates(coord_str)
            
            if len(coords) < 2:
                raise ValueError(f"Replace mode requires at least depth and position: {selector_str}")
                
            if len(coords) == 2:
                # Two coordinates: (d0,1) -> replace at depth 0, position 1
                depth, position = coords
                
                # Validate depth exists
                if not self._validate_depth_exists(depth):
                    raise ValueError(f"PACT depth {depth} does not exist. Cannot replace in non-existent depth.")
                
                depth_component = self._get_component_by_depth(depth)
                return depth_component, position
                    
            else:
                # Three+ coordinates: (d0,1,2) -> navigate to parent container and replace at final position
                depth = coords[0]
                
                # Validate depth exists
                if not self._validate_depth_exists(depth):
                    raise ValueError(f"PACT depth {depth} does not exist. Cannot replace in non-existent depth.")
                
                current = self._get_component_by_depth(depth)
                
                # Navigate to parent container
                for coord in coords[1:-1]:
                    if hasattr(current, 'content') and hasattr(current.content, '__contains__'):
                        if coord not in current.content:
                            raise ValueError(f"Parent container path doesn't exist: {coords[:-1]}")
                        current = current.content[coord]
                    else:
                        raise ValueError(f"Invalid container structure at coordinate {coord}")
                
                # Replace at final coordinate
                final_position = coords[-1]
                return current, final_position
        
        else:
            raise ValueError(f"Replace mode requires coordinate format like '(d0,1)': {selector_str}")
    
    def _parse_coordinates(self, coord_str: str) -> List[int]:
        """Parse coordinate string like 'd0,1,2' into [0, 1, 2]."""
        if not coord_str.startswith('d'):
            raise ValueError(f"Coordinate must start with 'd': {coord_str}")
        
        coord_part = coord_str[1:]  # Remove 'd'
        
        if ',' in coord_part:
            parts = coord_part.split(',')
            return [int(part.strip()) for part in parts]
        else:
            return [int(coord_part)]
    
    def _get_component_by_depth(self, depth: int) -> ContextComponent:
        """Get component by PACT depth using DepthArray."""
        try:
            return self.context.content[depth]
        except (KeyError, ValueError) as e:
            raise ValueError(f"Invalid or uninitialized PACT depth: {depth}") from e
    
    def _validate_depth_exists(self, depth: int) -> bool:
        """Check if a PACT depth exists without raising an exception."""
        try:
            self.context.content[depth]
            return True
        except (KeyError, ValueError):
            return False
    
    
    
    def _assign_creation_index(self, component: ContextComponent) -> None:
        """Assign creation_index to component."""
        if hasattr(component, 'creation_index') and hasattr(self.context, 'get_next_creation_index'):
            component.creation_index = self.context.get_next_creation_index()
    
    def _remove_from_current_parent(self, component: ContextComponent, current_parent_id: str) -> None:
        """Remove component from its current parent container."""
        current_parent = self.context.get_component_by_id(current_parent_id)
        if current_parent and hasattr(current_parent, 'content'):
            # Handle CoreOffsetArray content
            if hasattr(current_parent.content, '__delitem__'):
                # Find and delete by position
                for offset in current_parent.content:
                    if current_parent.content[offset] == component:
                        del current_parent.content[offset]
                        break
    
    def _cascade_unregister_descendants(self, component_id: str) -> None:
        """
        Cascade unregister all descendants using component traversal.
        
        Since we no longer have coordinate registries, we traverse the component
        tree to find all descendants and unregister them.
        """
        # Get the component
        component = self.context.get_component_by_id(component_id)
        if not component:
            self.context._registry.unregister_component(component_id)
            return
        
        # Collect all descendant component IDs
        descendant_ids = []
        self._collect_descendant_ids(component, descendant_ids)
        
        # Unregister all descendants (including the component itself)
        for cid in descendant_ids:
            self.context._registry.unregister_component(cid)
    
    def _collect_descendant_ids(self, component: ContextComponent, descendant_ids: List[str]) -> None:
        """Recursively collect all descendant component IDs."""
        descendant_ids.append(component.id)
        
        # Traverse children if component has content that contains child components
        # (CoreOffsetArray), not string content
        if hasattr(component, 'content') and hasattr(component.content, 'get_offsets'):
            # CoreOffsetArray - iterate over offsets to get child components
            for offset in component.content.get_offsets():
                child = component.content[offset]
                if hasattr(child, 'id'):
                    self._collect_descendant_ids(child, descendant_ids)
    
    # Legacy behavior methods (backward compatibility)
    
    def _update_queued(self, selector_or_component: Union[str, ContextComponent], content: Optional[str] = None, **kwargs) -> 'UpdateResult':
        """Queue update operation for next agent call."""
        from .base import UpdateResult, UpdateOperation
        
        try:
            # Create update operation
            operation = UpdateOperation(
                selector_or_component=selector_or_component,
                content=content,
                properties=kwargs,
                timestamp=datetime.now(),
                agent_id=getattr(self.context.agent, 'agent_id', None) if self.context.agent else None
            )
            
            # Add to queue
            self.context.update_queue.add_update(operation)
            
            return UpdateResult(
                success=True,
                warnings=[f"Update queued for next agent call (queue size: {len(self.context.update_queue)})"]
            )
            
        except Exception as e:
            return UpdateResult(
                success=False,
                errors=[f"Failed to queue update: {str(e)}"]
            )
    
    def _update_dispatch(self, selector_or_component: Union[str, ContextComponent], content: Optional[str] = None, **kwargs) -> 'UpdateResult':
        """Update using dispatch engine - placeholder for Task 3.1"""
        from .base import UpdateResult
        
        return UpdateResult(
            success=False,
            errors=["Dispatch behavior not yet implemented"]
        )
    
    def _update_force(self, selector_or_component: Union[str, ContextComponent], content: Optional[str] = None, **kwargs) -> 'UpdateResult':
        """Force update with agent interruption - placeholder for Task 4.2"""
        from .base import UpdateResult
        
        return UpdateResult(
            success=False,
            errors=["Force behavior not yet implemented"]
        )
