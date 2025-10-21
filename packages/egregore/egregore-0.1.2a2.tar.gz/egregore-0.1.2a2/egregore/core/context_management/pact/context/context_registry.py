"""
ContextRegistry - Centralized registry management for Context components.

Handles all O(1) lookups and coordinate tracking for the PACT tree structure.
"""

from typing import Dict, Tuple, Set, Optional, Union, List
from dataclasses import dataclass
from ..components.core import PACTCore
from ..data_structures.coordinates import Coordinates


@dataclass
class CadenceComponentInfo:
    """Information needed to rehydrate a cadence component."""
    component_id: str
    original_coordinates: str  # PACT selector like "(d0,1,0)" - coordinates where component was originally
    born_cycle: int
    ttl: int
    cadence: int
    component_data: dict  # Serialized component for reconstruction
    
    def get_parent_coordinates(self) -> str:
        """Extract parent coordinates from original coordinates.
        Example: "(d0,1,2)" -> "(d0,1)" 
        """
        # Remove the last offset to get parent coordinates
        coords = self.original_coordinates.strip("()")
        if "," in coords:
            parts = coords.split(",")
            return "(" + ",".join(parts[:-1]) + ")"
        return coords  # Root level component
    
    def get_relative_offset(self) -> int:
        """Extract the relative offset within parent.
        Example: "(d0,1,2)" -> 2
        """
        coords = self.original_coordinates.strip("()")
        if "," in coords:
            parts = coords.split(",")
            return int(parts[-1])
        return 0


class ContextRegistry:
    """
    Centralized registry for all Context component tracking and management.
    
    Provides O(1) lookups for:
    - Coordinate-based navigation
    - Parent-child relationships
    - Component properties (keys, types, tags)
    - Dynamic component tracking (TTL/cadence)
    """
    
    def __init__(self):
        # Core registries for O(1) component tracking and management
        # NOTE: _parent_registry and _coordinate_registry removed - now using computed coordinates
        # and direct component.parent_id access for better consistency and simplicity
        self._children_count_registry: Dict[str, int] = {}  # component_id → children count (deprecated with CoreOffsetArray)
        self._dynamic_components: Set[str] = set()  # component_ids with non-default ttl/cadence
        self._cadence_registry: Dict[str, 'CadenceComponentInfo'] = {}  # component_id → rehydration info for cadence components
        
        # Helper property registries for fast lookups
        self._key_registry: Dict[str, str] = {}  # key → component_id
        self._type_registry: Dict[str, Set[str]] = {}  # type → set of component_ids
        self._tag_registry: Dict[str, Set[str]] = {}  # tag → set of component_ids
        self._tool_pairs_registry: Dict[str, Tuple[str, str]] = {}  # tool_call_id → (call_id, result_id)
        self._tool_executions: Dict[str, List[str]] = {}  # tool_name → [tool_call_ids in execution order]
        self._node_registry: Dict[str, PACTCore] = {}  # parent_id → component
    
    # === Core Registry Operations ===
    
    def register_component(self, component: PACTCore, coords: Union[Coordinates, Tuple[int, ...], None] = None) -> None:
        """
        Register component in all relevant registries.
        
        Args:
            component: Component to register
            coords: Coordinate path for the component (Coordinates or tuple) - optional since coordinates are now computed
        """
        # NOTE: coords parameter kept for backward compatibility but not used
        # Coordinates are now computed via component.coordinates property
        # Parent relationships are stored directly in component.parent_id
        
        self._node_registry[component.id] = component
        # Helper property registries
        if hasattr(component, 'key') and component.key:
            self._key_registry[component.key] = component.id
        
        # Register component type
        component_type = getattr(component, 'component_type', None) or getattr(component, 'type', None)
        if component_type:
            if component_type not in self._type_registry:
                self._type_registry[component_type] = set()
            self._type_registry[component_type].add(component.id)
        
        # Register tags from direct .tags attribute OR metadata.props['tags']
        tags_to_register = set()
        if hasattr(component, 'tags') and component.tags:
            if isinstance(component.tags, (list, tuple, set)):
                tags_to_register.update(str(t) for t in component.tags)
            elif isinstance(component.tags, str):
                tags_to_register.add(component.tags)

        # Also check metadata.props['tags']
        if hasattr(component, 'metadata') and hasattr(component.metadata, 'props'):
            t = component.metadata.props.get('tags')
            if isinstance(t, list):
                tags_to_register.update(str(x) for x in t)
            elif isinstance(t, str):
                # Split on commas/space
                import re
                for part in re.split(r'[\s,]+', t.strip()):
                    if part:
                        tags_to_register.add(part)

        for tag in tags_to_register:
            if tag not in self._tag_registry:
                self._tag_registry[tag] = set()
            self._tag_registry[tag].add(component.id)
        
        # Dynamic component tracking
        if (hasattr(component, 'ttl') and component.ttl is not None) or \
           (hasattr(component, 'cad') and component.cad != 1):
            self._dynamic_components.add(component.id)
        
        # Cadence component rehydration tracking
        # Register if component has both TTL (expires) and cadence (reappears)
        # This includes sticky components (ttl=1, cad=1) which expire and reappear each turn
        if (hasattr(component, 'cad') and component.cad and component.cad >= 1 and
            hasattr(component, 'ttl') and component.ttl is not None):
            # Convert coordinates to PACT selector string if provided
            if coords is not None:
                coord_str = str(coords)
                # Register for cadence rehydration if we have valid coordinates
                self.register_cadence_component(component, coord_str)
    
    def unregister_component(self, component_id: str) -> None:
        """
        Remove component from all registries.
        
        Args:
            component_id: Component ID to unregister
        """
        # Remove from core registries (coordinate/parent registries removed)
        self._children_count_registry.pop(component_id, None)
        self._dynamic_components.discard(component_id)
        self.unregister_cadence_component(component_id)
        
        # Remove from helper registries (need to find by value)
        # Key registry (direct lookup)
        key_to_remove = None
        for key, cid in self._key_registry.items():
            if cid == component_id:
                key_to_remove = key
                break
        if key_to_remove:
            self._key_registry.pop(key_to_remove)
        
        # Type registry (remove from sets)
        for component_set in self._type_registry.values():
            component_set.discard(component_id)
        
        # Tag registry (remove from sets)
        for component_set in self._tag_registry.values():
            component_set.discard(component_id)
        
        # Tool pairs registry (remove by call_id or result_id)
        tool_id_to_remove = None
        for tool_id, (call_id, result_id) in self._tool_pairs_registry.items():
            if call_id == component_id or result_id == component_id:
                tool_id_to_remove = tool_id
                break
        if tool_id_to_remove:
            self._tool_pairs_registry.pop(tool_id_to_remove)
    
    # === Coordinate and Parent-Child Registries (REMOVED) ===
    # These deprecated methods have been completely removed to force migration to:
    # - component.coordinates property for computed coordinates  
    # - component.parent_id property for parent relationships
    # - Direct traversal using CoreOffsetArray for coordinate lookup
    
    
    
    
    # === Parent-Child Registry (REMOVED) ===
    # Parent relationships are now stored directly in component.parent_id
    
    
    
    # === Children Count Registry ===
    
    def get_children_count(self, component_id: str) -> int:
        """Get number of children for a component (O(1) lookup)."""
        return self._children_count_registry.get(component_id, 0)
    
    def update_children_count(self, parent_id: str, delta: int) -> None:
        """Update children count for a parent component."""
        current_count = self._children_count_registry.get(parent_id, 0)
        new_count = max(0, current_count + delta)
        self._children_count_registry[parent_id] = new_count
    
    def set_children_count(self, component_id: str, count: int) -> None:
        """Set children count directly."""
        self._children_count_registry[component_id] = count
    
    def is_empty_container(self, component_id: str) -> bool:
        """O(1) empty container check using children count registry."""
        return self._children_count_registry.get(component_id, 0) == 0
    
    # === Property Lookups ===
    
    def find_by_key(self, key: str) -> Optional[str]:
        """O(1) key lookup: find component ID by key."""
        return self._key_registry.get(key)
    
    def find_by_type(self, type_name: str) -> Set[str]:
        """O(1) type lookup: find component IDs by type."""
        return self._type_registry.get(type_name, set()).copy()
    
    def find_by_tag(self, tag: str) -> Set[str]:
        """O(1) tag lookup: find component IDs by tag."""
        return self._tag_registry.get(tag, set()).copy()
    
    # === Dynamic Component Tracking ===
    
    def get_dynamic_components(self) -> Set[str]:
        """Return component IDs with non-default TTL/cadence for MessageScheduler."""
        return self._dynamic_components.copy()
    
    def register_dynamic_component(self, component_id: str) -> None:
        """Add component to dynamic tracking."""
        self._dynamic_components.add(component_id)
    
    def unregister_dynamic_component(self, component_id: str) -> None:
        """Remove component from dynamic tracking."""
        self._dynamic_components.discard(component_id)
    
    def is_dynamic_component(self, component_id: str) -> bool:
        """Check if component is tracked for temporal processing."""
        return component_id in self._dynamic_components
    
    def get_dynamic_component_count(self) -> int:
        """Get count of components requiring temporal processing."""
        return len(self._dynamic_components)
    
    # === Cadence Component Rehydration Registry ===
    
    def register_cadence_component(self, component: PACTCore, coordinates: str) -> None:
        """Register a component with cadence for rehydration tracking."""
        if not hasattr(component, 'cad') or not component.cad:
            return  # Must have cadence to be tracked
        if not hasattr(component, 'ttl') or component.ttl is None:
            return  # Only track components that expire (have TTL)
            
        cadence_info = CadenceComponentInfo(
            component_id=component.id,
            original_coordinates=coordinates,
            born_cycle=getattr(component.metadata, 'born_cycle', 0) if hasattr(component, 'metadata') else 0,
            ttl=component.ttl,
            cadence=component.cad,
            component_data=component.model_dump()  # Serialize for reconstruction
        )
        
        self._cadence_registry[component.id] = cadence_info
        
        # Invariant: Component with cadence registration must not have invalid position
        # This prevents rehydration attempts at non-existent coordinates
        if coordinates in ["", "()", "(d)", "(d0)", "(,)"]:
            raise ValueError(f"Invalid coordinates '{coordinates}' for cadence component {component.id}")
    
    def unregister_cadence_component(self, component_id: str) -> None:
        """Remove component from cadence tracking."""
        self._cadence_registry.pop(component_id, None)
    
    def get_cadence_components(self) -> Dict[str, CadenceComponentInfo]:
        """Return all components tracked for cadence rehydration."""
        return self._cadence_registry.copy()
    
    def get_components_for_rehydration(self, current_cycle: int) -> List[CadenceComponentInfo]:
        """Get components that should be rehydrated at the current cycle."""
        components_to_rehydrate = []
        
        for cadence_info in self._cadence_registry.values():
            # Calculate when this component should reappear
            # Component expires at: born_cycle + ttl
            # Component reappears at: born_cycle + cadence, born_cycle + 2*cadence, etc.
            
            cycles_since_birth = current_cycle - cadence_info.born_cycle
            if cycles_since_birth > 0 and cycles_since_birth % cadence_info.cadence == 0:
                # This is a rehydration cycle for this component
                # But make sure it's not currently active (hasn't expired yet)
                expires_at = cadence_info.born_cycle + cadence_info.ttl
                if current_cycle >= expires_at:
                    components_to_rehydrate.append(cadence_info)
        
        return components_to_rehydrate
    
    def is_cadence_component(self, component_id: str) -> bool:
        """Check if component is tracked for cadence rehydration."""
        return component_id in self._cadence_registry
    
    def get_cadence_component_count(self) -> int:
        """Get count of components tracked for cadence rehydration."""
        return len(self._cadence_registry)
    
    # === Tool Pairs Registry ===

    def register_tool_call(self, tool_call_id: str, call_id: str, tool_name: str) -> None:
        """Phase 1: Register tool call component (partial registration).

        Called automatically when ToolCall component is inserted into context.
        """
        # Store partial pair (result_id will be added later)
        self._tool_pairs_registry[tool_call_id] = (call_id, None)

        # Track execution order immediately when call is registered
        if tool_name not in self._tool_executions:
            self._tool_executions[tool_name] = []

        # Only add to executions if not already present (idempotent)
        if tool_call_id not in self._tool_executions[tool_name]:
            self._tool_executions[tool_name].append(tool_call_id)

    def complete_tool_pair(self, tool_call_id: str, result_id: str) -> None:
        """Phase 2: Complete tool pair by adding result component.

        Called automatically when ToolResult component is inserted into context.
        """
        if tool_call_id in self._tool_pairs_registry:
            call_id, _ = self._tool_pairs_registry[tool_call_id]
            # Complete the pair with result_id
            self._tool_pairs_registry[tool_call_id] = (call_id, result_id)

    def register_tool_pair(self, tool_call_id: str, call_id: str, result_id: str, tool_name: str) -> None:
        """Legacy: Register complete tool pair in one call.

        Prefer using register_tool_call() + complete_tool_pair() for automatic registration.
        """
        self._tool_pairs_registry[tool_call_id] = (call_id, result_id)

        # Track execution order per tool
        if tool_name not in self._tool_executions:
            self._tool_executions[tool_name] = []

        # Only add if not already present
        if tool_call_id not in self._tool_executions[tool_name]:
            self._tool_executions[tool_name].append(tool_call_id)

    def get_tool_pair(self, tool_call_id: str) -> Optional[Tuple[str, str]]:
        """Get tool call/result pair by tool call ID."""
        pair = self._tool_pairs_registry.get(tool_call_id)
        print(f"[GET_TOOL_PAIR DEBUG] Requested: {tool_call_id}, Found: {pair}")
        print(f"[GET_TOOL_PAIR DEBUG] All pairs in registry: {self._tool_pairs_registry}")
        return pair

    def unregister_tool_pair(self, tool_call_id: str) -> None:
        """Remove tool pair from registry after deletion."""
        print(f"[UNREGISTER DEBUG] unregister_tool_pair called for {tool_call_id}")
        print(f"[UNREGISTER DEBUG] In pairs registry? {tool_call_id in self._tool_pairs_registry}")
        print(f"[UNREGISTER DEBUG] Pairs registry keys: {list(self._tool_pairs_registry.keys())}")
        if tool_call_id in self._tool_pairs_registry:
            # Remove from pairs registry
            del self._tool_pairs_registry[tool_call_id]
            print(f"[UNREGISTER DEBUG] Removed from pairs registry")

            # Remove from executions tracking
            print(f"[UNREGISTER DEBUG] Executions before: {dict(self._tool_executions)}")
            print(f"[UNREGISTER DEBUG] Registry ID: {id(self._tool_executions)}")
            print(f"[UNREGISTER DEBUG] Looking for tool_call_id: '{tool_call_id}'")
            for tool_name, call_ids in self._tool_executions.items():
                print(f"[UNREGISTER DEBUG] Checking tool '{tool_name}', call_ids={call_ids}")
                print(f"[UNREGISTER DEBUG] Is tool_call_id in list? {tool_call_id in call_ids}")
                if tool_call_id in call_ids:
                    print(f"[UNREGISTER DEBUG] Found in '{tool_name}', removing...")
                    print(f"[UNREGISTER DEBUG] List before remove: {call_ids}, ID: {id(call_ids)}")
                    call_ids.remove(tool_call_id)
                    print(f"[UNREGISTER DEBUG] List after remove: {call_ids}, ID: {id(call_ids)}")
                    print(f"[UNREGISTER DEBUG] Registry list now: {self._tool_executions[tool_name]}, ID: {id(self._tool_executions[tool_name])}")
                    break
            print(f"[UNREGISTER DEBUG] Executions after: {dict(self._tool_executions)}")
        else:
            print(f"[UNREGISTER DEBUG] NOT in pairs registry, skipping removal from executions")
    
    # === Utility Methods ===
    
    def clear_all(self) -> None:
        """Clear all registries - use with caution."""
        # NOTE: _parent_registry and _coordinate_registry removed
        self._children_count_registry.clear()
        self._dynamic_components.clear()
        self._cadence_registry.clear()
        self._key_registry.clear()
        self._type_registry.clear()
        self._tag_registry.clear()
        self._tool_pairs_registry.clear()
        self._tool_executions.clear()
    
    def get_registry_stats(self) -> Dict[str, int]:
        """Get statistics about registry usage."""
        return {
            # NOTE: total_components and parent_relationships removed (computed coordinates)
            "keyed_components": len(self._key_registry),
            "dynamic_components": len(self._dynamic_components),
            "cadence_components": len(self._cadence_registry),
            "types_tracked": len(self._type_registry),
            "tags_tracked": len(self._tag_registry),
            "tool_pairs": len(self._tool_pairs_registry),
            "children_counts_tracked": len(self._children_count_registry)  # deprecated
        }
    
