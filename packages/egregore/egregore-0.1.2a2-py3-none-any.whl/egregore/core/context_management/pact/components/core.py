# from optparse import Option  # Unused import
from pydantic import BaseModel, Field, PrivateAttr, ConfigDict, computed_field
from typing import ClassVar, Optional, List, Dict, Any, Union, Set, TYPE_CHECKING
from datetime import datetime
from ..data_structures.core_offset_array import CoreOffsetArray
from ..data_structures.coordinates import Coordinates
from ..data_structures.depth_array import DepthArray
import time
# from pydantic import Field, validator  # Unused import - validator is deprecated
import os
import hashlib
# RenderOptions removed - not needed in PACT architecture
import re
import warnings
if TYPE_CHECKING:
    from ..context.base import Context

# Filter out Pydantic field shadowing warnings for XMLComponent inheritance
warnings.filterwarnings("ignore", message="Field name .* shadows an attribute in parent.*", category=UserWarning)
# Filter out Pydantic serialization warnings for polymorphic content types
warnings.filterwarnings("ignore", message=".*PydanticSerializationUnexpectedValue.*", category=UserWarning)

def generate_hash_id(node_type: str = "", parent_id: str = "") -> str:
    base = f"{parent_id}:{node_type}:{time.time_ns()}:{os.urandom(4).hex()}"

    return hashlib.sha1(base.encode()).hexdigest()[:12]




class Metadata(BaseModel):
    created_at: datetime = Field(default_factory=datetime.now)
    message_cycle: int = 0
    priority: int = 0
    active: bool = True
    source: str = "core"
    aux: Dict[str, str] = Field(
        default_factory=dict
    )  # auxiliary metadata non canonical

    # Episode injection fields for in_view computation (private attributes)
    props: Dict[str, str] = Field(default_factory=dict)
    _current_cycle: Optional[int] = PrivateAttr(default=None)
    _component: Optional["PACTCore"] = PrivateAttr(default=None)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {Coordinates: lambda v: v.serialize()}

    # PACT interoperability fields for provider content
    role: Optional[str] = None  # "user" | "assistant" | "tool" | "system" | "other"
    kind: Optional[str] = None  # "text" | "call" | "result" | "image" | "summary"

    # PACT coordinate system integration
    coordinates: Coordinates = Field(
        default_factory=Coordinates
    )  # Universal PACT coordinates
    born_cycle: int = 0  # Creation cycle tracking

    # Render lifecycle fields (for dynamic component positioning)
    render_lifecycle_stages: Optional[List[Any]] = None  # List[Pos] - stages to move through
    render_current_stage_index: int = 0  # Current stage in lifecycle
    render_cycle_behavior: Optional[Union[bool, int]] = None  # Cycling: False, True, or N cycles
    render_cycles_completed: int = 0  # Number of complete cycles finished

    # PACT required metadata fields
    def __init__(self, **kwargs):
        aux = {
            k: v
            for k, v in kwargs.items()
            if k
            not in [
                "id",
                "created_at",
                "message_cycle",
                "priority",
                "active",
                "source",
                "role",

            ]
        }

        super().__init__(**kwargs)
        self.aux.update(aux)

    creation_index: int = 0

    def set_input_tokens(self, count: int):
        """Set input token count in aux metadata"""
        self.aux["input_tokens"] = str(count)

    def get_input_tokens(self) -> Optional[int]:
        """Get input token count from aux metadata"""
        return (
            int(self.aux.get("input_tokens", 0)) if "input_tokens" in self.aux else None
        )

    @property
    def created_at_ns(self) -> int:
        """Convert created_at to nanoseconds for PACT compliance"""
        return int(self.created_at.timestamp() * 1_000_000_000)

    @property
    def created_at_iso(self) -> str:
        """Convert created_at to ISO format for PACT compliance"""
        return self.created_at.isoformat()

class PACTCore(BaseModel):
    """
    Base class for all PACT components - contains shared PACT fields.
    """
    id: str = Field(default_factory=lambda: generate_hash_id())
    type: ClassVar[str] = "pact_node"
    ttl: Optional[int] = Field(default=None, description="Lifetime in episodes")
    cad: Optional[int] = Field(default=None, description="Cadence (realization rhythm)")
    created_at_ns: int = Field(default_factory=lambda: int(time.time_ns()))
    creation_index: int = 0
    key: Optional[str] = Field(default=None, description="Stable sibling-unique handle")
    tags: List[str] = Field(default_factory=list, description="Free-form tags")
    metadata: Metadata = Field(default_factory=Metadata)
    placement: Optional[Any] = Field(default=None, description="Static placement using Pos selector (optional)")
    _context_ref: Optional["Context"] = PrivateAttr(default=None)
    _parent_coordinates: Optional[Coordinates] = PrivateAttr(default=None)
    _current_episode: int = PrivateAttr(default=0)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def model_dump(self, **kwargs) -> Dict[str, Any]:
        """
        Override to add PACT v0.1 canonical fields to all components.
        This cascades automatically to all subclasses.
        """
        from datetime import datetime

        # Get base Pydantic fields
        data = super().model_dump(**kwargs)

        # Remove internal/private fields that shouldn't be serialized at all
        internal_fields = ["coordinates", "parent_coordinates"]
        for field in internal_fields:
            data.pop(field, None)

        # Add PACT v0.1 canonical fields
        data["type"] = self.type  # ClassVar type field - engine-specific identifier

        # Map engine types to PACT canonical structural regions (with ^ prefix)
        # Per PACT spec: ^sys, ^seq, ^ah are structural regions
        # Root is just "root" without prefix
        # All other types are engine-defined and stay as-is
        structural_regions = {
            "root": "root",
            "pact_root": "root",
            "system_header": "^sys",
            # message_turn varies by depth - handled below
        }

        # Get nodeType - structural regions get ^ prefix, others stay engine-defined
        node_type = structural_regions.get(self.type, self.type)

        # Special handling for MessageTurn - becomes ^ah or part of ^seq based on depth
        if self.type == "message_turn" and hasattr(self, 'depth'):
            node_type = "^ah" if self.depth == 0 else "message_turn"
            # Note: historical turns (depth > 0) are inside ^seq region, not ^seq themselves

        data["nodeType"] = node_type

        data["parent_id"] = getattr(self, '_parent_id', None)
        data["offset"] = getattr(self, '_offset', 0)
        data["priority"] = getattr(self.metadata, 'priority', 0)
        data["cycle"] = getattr(self.metadata, 'born_cycle', getattr(self, '_current_episode', 0))
        data["created_at_iso"] = datetime.fromtimestamp(self.created_at_ns / 1e9).isoformat()

        # Determine component_type based on content structure
        if hasattr(self, 'content'):
            content = getattr(self, 'content', None)
            if isinstance(content, str) or content is None:
                component_type = "content"  # Leaf node
            else:
                component_type = "container"  # Has children
        else:
            component_type = "content"  # Default to content

        # Set component_type (will be moved to org)
        data["component_type"] = component_type

        # Set base_block if not already set (component class type)
        if "base_block" not in data:
            if hasattr(self, 'base_block'):
                data["base_block"] = self.base_block
            else:
                # Infer from class hierarchy
                class_names = [cls.__name__ for cls in self.__class__.__mro__]
                if "XMLComponent" in class_names:
                    data["base_block"] = "xml_component"
                elif "BaseContextScaffold" in class_names:
                    data["base_block"] = "scaffold"
                else:
                    data["base_block"] = "component"

        # Move custom/org fields to org namespace (non-canonical PACT fields)
        # NOTE: 'role' is CANONICAL on Turn containers per PACT spec §3.2, so it stays at root
        # Only truly non-canonical fields go to org namespace
        org_fields = ["text", "source", "metadata", "component_type", "base_block",
                      "scaffold_state", "scaffold_id_data"]
        org_data = {}

        # Canonical PACT fields that should NOT go to org namespace
        # Also includes internal/private fields that shouldn't be serialized
        canonical_fields = {
            "id", "nodeType", "parent_id", "offset", "ttl", "priority", "cycle",
            "created_at_ns", "created_at_iso", "creation_index", "role", "content",
            "children", "type", "content_hash", "cad", "created_at", "born_cycle",
            "coordinates", "parent_coordinates"  # Internal positioning data
        }

        for field in org_fields:
            if field in data:
                value = data.pop(field)
                # If metadata is a dict, filter out canonical fields before merging
                if field == "metadata" and isinstance(value, dict):
                    # Only include non-canonical fields from metadata
                    filtered_metadata = {k: v for k, v in value.items() if k not in canonical_fields}

                    # Flatten aux contents directly into org_data
                    if 'aux' in filtered_metadata and isinstance(filtered_metadata['aux'], dict):
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.info(f"[model_dump] Flattening aux for {self.type}: keys={list(filtered_metadata['aux'].keys())}")
                        org_data.update(filtered_metadata['aux'])
                        filtered_metadata.pop('aux')  # Remove aux container

                    # Keep props nested
                    if 'props' in filtered_metadata and isinstance(filtered_metadata['props'], dict):
                        org_data['props'] = filtered_metadata['props']
                        filtered_metadata.pop('props')  # Don't merge props

                    # Merge remaining metadata fields
                    org_data.update(filtered_metadata)
                else:
                    org_data[field] = value

        # Store content string in org.text if it exists (for content nodes)
        if "content" in data and isinstance(data.get("content"), str):
            content_str = data["content"]
            if content_str:  # Only add if non-empty
                org_data["text"] = content_str
                # Keep content field at root as it's canonical for leaf nodes

        if org_data:
            import logging
            logger = logging.getLogger(__name__)
            if self.type == "internal_notes":
                logger.info(f"[model_dump] Setting org for {self.type}: keys={list(org_data.keys())}")
            data["org"] = org_data

        # Handle children for container nodes
        # Containers have CoreOffsetArray as content, which should become children array
        # Leaf nodes have string content, which stays as-is
        if "content" in data and not isinstance(data["content"], str):
            # This is a container - convert CoreOffsetArray to children array
            content_obj = getattr(self, 'content', None)
            if content_obj is not None and hasattr(content_obj, '__iter__'):
                try:
                    children = []
                    for child in content_obj:
                        if hasattr(child, 'model_dump'):
                            child_data = child.model_dump()
                            # DEBUG: Check scaffold org data
                            if hasattr(child, 'type') and child.type == "internal_notes":
                                import logging
                                logger = logging.getLogger(__name__)
                                org_keys = list(child_data.get('org', {}).keys())
                                logger.info(f"[model_dump children] Scaffold child org keys: {org_keys}")
                                if 'scaffold_state' in child_data.get('org', {}):
                                    logger.info(f"[model_dump children] ✅ scaffold_state IS in child org")
                                else:
                                    logger.warning(f"[model_dump children] ⚠️ scaffold_state NOT in child org")
                            children.append(child_data)
                    data["children"] = children
                    # Remove the content field - containers don't serialize CoreOffsetArray
                    del data["content"]
                except:
                    pass

        return data

    def _get_context(self) -> Optional["Context"]:
        """Get root Context via reference"""
        return self._context_ref if self._context_ref is not None else None
    _offset: int = PrivateAttr(default=0)
    
    @property
    def current_episode(self) -> int:
        """Episode property for automatic propagation - available to all PACT components."""
        return self._current_episode

    @current_episode.setter  
    def current_episode(self, value: int):
        """Simplified episode setter with automatic child propagation."""
        self._current_episode = value
        
        # Handle my own temporal logic if I have it
        if hasattr(self, '_handle_cycle_change_simplified'):
            try:
                method = getattr(self, '_handle_cycle_change_simplified')
                if callable(method):
                    method(value)
            except (AttributeError, TypeError):
                pass  # Silent fallback if method call fails
        
        # Propagate to children if I'm a container and have content attribute
        if hasattr(self, 'content') and not isinstance(getattr(self, 'content', None), str):
            content = getattr(self, 'content')
            if content is not None and hasattr(content, '__iter__'):
                for child in content:
                    if hasattr(child, 'current_episode'):
                        child.current_episode = value

    def render_lifecycle(
        self,
        stages: List[Any],  # List['Pos']
        cycle: Union[bool, int] = False
    ) -> 'PACTCore':
        """
        Define positional lifecycle for this component across conversation turns.

        Components move through stages based on TTL expiry. When TTL expires at one stage,
        the component automatically transitions to the next stage position with new TTL.

        Args:
            stages: List of Pos objects defining lifecycle journey
                   Each Pos specifies position and TTL for that stage
            cycle: Cycling behavior:
                   False = No cycling (default) - component removed after last stage
                   True = Infinite cycling through all stages
                   int = Cycle N times then remove

        Returns:
            Self for method chaining

        Example:
            component.render_lifecycle([
                Pos("d0, 1", ttl=2),     # Active context for 2 turns
                Pos("d-1, 1", ttl=5),    # System context for 5 turns
                Pos("d2, 1")             # Archive permanently
            ])
        """
        if not stages:
            raise ValueError("render_lifecycle requires at least one stage")

        # Store lifecycle configuration in metadata
        self.metadata.render_lifecycle_stages = stages
        self.metadata.render_current_stage_index = 0
        self.metadata.render_cycle_behavior = cycle
        self.metadata.render_cycles_completed = 0

        # Apply first stage's TTL and cadence to component
        first_stage = stages[0]
        if hasattr(first_stage, 'ttl') and first_stage.ttl is not None:
            self.ttl = first_stage.ttl
        if hasattr(first_stage, 'cadence') and first_stage.cadence is not None:
            self.cad = first_stage.cadence

        return self



class PACTNode(PACTCore):
    """
    Canonical PACT block specification - v0.1 compliant.
    Pure data type with all required PACT fields inherited from PACTCore.
    """

    # NODE-SPECIFIC PACT FIELDS
    content: Union[str, CoreOffsetArray[PACTCore]] = Field(default="")

    # Private attributes
    _parent_id: Optional[str] = PrivateAttr(default=None)
    _context_ref: Optional["Context"] = PrivateAttr(default=None)
    _is_dynamic: bool = PrivateAttr(default=False)
    _parent: Optional["PACTCore"] = PrivateAttr(default=None)

    def __init__(self, context: Optional["Context"] = None, **kwargs):
        parent_id = kwargs.pop('parent_id', None)

        if kwargs.get("ttl") is not None:
            self._is_dynamic = True
        # Don't force type into kwargs - let Pydantic handle it from class definition or passed kwargs
        # This allows ContextHook to use _hook_type property without conflicts
        super().__init__(**kwargs)

        # Set context reference first
        self._context_ref = context

        # Register component in context registry
        if context is not None:
            context._registry.register_component(self)

        # Then set parent_id (this will call _update_coordinates)
        if parent_id:
            self._parent_id = parent_id
            if context is not None:
                self._parent = context.get_component_by_id(parent_id)



    @property
    def parent_id(self) -> Optional[str]:
        """Get parent component ID."""
        return self._parent_id

    @parent_id.setter
    def parent_id(self, value: Optional[str]) -> None:
        """Set parent component ID and inject context reference from parent."""
        self._parent_id = value
        
        # Update parent reference when parent_id is set
        if value and self._context_ref:
            self._parent = self._context_ref.get_component_by_id(value)
        else:
            self._parent = None
            
        self._update_coordinates()
        



    def _update_coordinates(self) -> None:
        """Update coordinates based on parent coordinates and offset."""
        if self.parent_id:
            assert self._context_ref is not None
            parent = self._context_ref.get_component_by_id(self.parent_id)
            if parent:
                # Use metadata.coordinates if the computed property isn't available
                parent_coords = getattr(parent, 'coordinates', parent.metadata.coordinates)
                # Create new Coordinates object with parent coords + offset
                if isinstance(parent_coords, Coordinates):
                    self._coordinates = list(parent_coords.coords) + [self.offset]
                else:
                    self._coordinates = list(parent_coords) + [self.offset]
            else:
                self._coordinates = [self.offset]
        else:
            self._coordinates = [self.offset]

    @computed_field
    @property
    def offset(self) -> int:
        """Dynamic offset calculation based on position in parent container."""
        return self._offset
    
    @offset.setter
    def offset(self, value: int) -> None:
        """Setter for offset - computed field allows setting for initialization."""
        self._offset = value
    
    @computed_field
    @property
    def coordinates(self) -> Coordinates:
        """
        Computed coordinates based on parent coordinates + self.offset.
        
        Matrix-based coordinate system: [*parent.coordinates, self.offset]
        - Root components have no parent_id → empty coordinates
        - Child components: parent.coordinates + [self.offset]
        
        Returns:
            Computed Coordinates object (excluded from serialization)
        """
        if not self.parent_id:
            return Coordinates()  # Root has empty coordinates
        
        # For components with parents, we need the parent's coordinates
        # Use cached parent coordinates if available
        if (
            hasattr(self, "_parent_coordinates")
            and self._parent_coordinates is not None
        ):
            return Coordinates(*self._parent_coordinates.coords, self.offset)
        
        # Special case: Depth-level components (SystemHeader, MessageTurn)
        # These are directly assigned to DepthArray and need depth-based coordinates
        if self._context_ref is not None:
            context = self._context_ref
            if context and hasattr(context, "content") and hasattr(context.content, "_depths"):
                # Find this component's depth in the DepthArray
                for depth in range(-1, 100):  # Reasonable range
                    try:
                        depths_array = getattr(context.content, '_depths', None)
                        if depths_array is not None and depth + 1 < len(depths_array) and depths_array[depth + 1] is self:  # depth+1 for array indexing
                            return Coordinates(depth)
                    except (KeyError, IndexError):
                        continue
        
        # Fallback to just offset
        return Coordinates(self.offset)

    def _handle_cycle_change_simplified(self, new_cycle: int) -> None:
        """
        Simplified cycle change handling - separate expiry and rehydration.
        """
        print(f"[TTL DEBUG] _handle_cycle_change_simplified called for {self.id}, ttl={self.ttl}, cad={getattr(self, 'cad', None)}")
        # Only process if I have temporal properties
        if self.ttl is None and getattr(self, 'cad', None) is None:
            print(f"[TTL DEBUG] Skipping - no temporal properties")
            return
        
        # Check for rehydration FIRST (before expiry removes component from tree)
        should_rehydrate = False
        if getattr(self, 'cad', None) is not None:
            cycles_since_birth = new_cycle - getattr(self.metadata, 'born_cycle', 0)
            if cycles_since_birth > 0 and self.cad is not None and cycles_since_birth % self.cad == 0:
                should_rehydrate = True
        
        # Simple expiry check
        if self.ttl is not None:
            age = new_cycle - getattr(self.metadata, 'born_cycle', 0)
            if age >= self.ttl and getattr(self.metadata, 'active', True):
                try:
                    # ✨ NEW: Check for lifecycle stage transition
                    if self.metadata.render_lifecycle_stages:
                        self._handle_lifecycle_transition(new_cycle)
                        return

                    # Check if this is a protected position (d0,0,0 core content)
                    if self._is_protected_position():
                        # For protected positions, just clear content but preserve structure
                        if hasattr(self, 'content'):
                            if isinstance(self.content, str):
                                self.content = ""
                            elif hasattr(self.content, '__iter__') and hasattr(self.content, 'clear'):
                                # Type guard: ensure it's a container-like object before calling clear
                                if not isinstance(self.content, str):
                                    container = self.content
                                    # Clear container by removing all items
                                    if hasattr(container, 'get_offsets') and hasattr(container, 'remove'):
                                        offsets = container.get_offsets().copy()  # Copy to avoid modification during iteration
                                        for offset in offsets:
                                            try:
                                                container.remove(offset)
                                            except Exception:
                                                pass  # Silent fallback for removal failures
                        return

                    # Save rehydration info BEFORE deletion
                    saved_offset = self.offset if should_rehydrate else None
                    saved_parent_id = self.parent_id if should_rehydrate else None
                    saved_context_ref = self._context_ref if should_rehydrate else None

                    # Complete deletion - use parent reference to remove this component
                    if hasattr(self, '_parent') and self._parent is not None:
                        parent = self._parent
                        if hasattr(parent, 'content') and not isinstance(getattr(parent, 'content', None), str):
                            container = getattr(parent, 'content')
                            if container is not None and hasattr(container, 'remove'):
                                try:
                                    container.remove(self.offset)
                                except Exception as e:
                                    pass  # Silent fallback for removal failures

                    # NOW rehydrate if needed (after old component is deleted)
                    if should_rehydrate and saved_offset is not None and saved_parent_id and saved_context_ref:
                        self._rehydrate_component(saved_context_ref, saved_parent_id, saved_offset, new_cycle)

                    return
                except Exception:
                    # Silent fallback - TTL deletion failed
                    pass
    
    def _is_protected_position(self) -> bool:
        """
        Check if this component is at a protected position (d0,0,0 core content).
        Protected positions preserve structure during TTL expiry by only clearing content.
        """
        try:
            if not self._context_ref or not self.parent_id:
                return False
            
            # Get parent to understand our position in the hierarchy
            parent = self._context_ref.get_component_by_id(self.parent_id)
            if not parent:
                return False
            
            # Check if we're core content (offset 0) in a MessageContainer at d0,0
            if (hasattr(parent, 'offset') and hasattr(parent, 'parent_id') and 
                getattr(parent, 'parent_id', None) and getattr(parent, 'offset', None) == 0):
                parent_id = getattr(parent, 'parent_id')
                grandparent = self._context_ref.get_component_by_id(parent_id) if parent_id else None
                if (grandparent and hasattr(grandparent, 'depth') and 
                    getattr(grandparent, 'depth', None) == 0 and 
                    getattr(grandparent, 'offset', None) == 0):
                    # This is d0,0,0 core content - protect structure
                    return self.offset == 0
            
            return False
        except Exception:
            # If we can't determine, be conservative and don't protect
            return False
    
    def _rehydrate_component(self, context_ref, parent_id: str, offset: int, new_cycle: int) -> None:
        """Rehydrate this component at the saved position after deletion."""
        try:
            parent = context_ref.get_component_by_id(parent_id)

            if parent and hasattr(parent, 'content') and not isinstance(getattr(parent, 'content', None), str):
                container = getattr(parent, 'content')
                if container is not None and hasattr(container, 'insert'):
                    # Create a new copy of this component with fresh metadata
                    new_component = self.model_copy(deep=True)

                    # Update metadata for rehydration
                    import time
                    from datetime import datetime
                    new_component.created_at_ns = time.time_ns()
                    new_component.metadata.created_at = datetime.fromtimestamp(time.time())
                    new_component.metadata.born_cycle = new_cycle
                    new_component.metadata.active = True

                    # Set context reference and parent
                    new_component._context_ref = context_ref
                    new_component.parent_id = parent_id

                    # Insert at the saved offset (no shifting issues since old is deleted)
                    container.insert(offset, new_component)
        except Exception:
            # Silent fallback - rehydration failed
            pass

    def _handle_lifecycle_transition(self, new_cycle: int) -> None:
        """
        Handle transition to next lifecycle stage.

        Called when TTL expires and component has render_lifecycle_stages configured.
        Moves component to next stage position or handles cycling/removal.
        """
        print(f"[LIFECYCLE DEBUG] _handle_lifecycle_transition called for component {self.id}, new_cycle={new_cycle}")
        stages = self.metadata.render_lifecycle_stages
        if not stages:
            # No lifecycle configured - fallback to normal deletion
            print(f"[LIFECYCLE DEBUG] No stages, removing from parent")
            self._remove_from_parent()
            return

        current_idx = self.metadata.render_current_stage_index
        cycle_behavior = self.metadata.render_cycle_behavior
        print(f"[LIFECYCLE DEBUG] Current stage: {current_idx}/{len(stages)}, stages: {stages}")

        # Calculate next stage index
        next_idx = current_idx + 1

        # Handle cycling when we've completed all stages
        if next_idx >= len(stages):
            # We've completed one full cycle through all stages
            self.metadata.render_cycles_completed += 1

            if cycle_behavior is True:
                # Infinite cycling - restart from stage 0
                next_idx = 0
            elif isinstance(cycle_behavior, int) and cycle_behavior > 0:
                # Check if we've completed the required number of cycles
                if self.metadata.render_cycles_completed < cycle_behavior:
                    # More cycles remaining - restart from stage 0
                    next_idx = 0
                else:
                    # Cycle limit reached - remove component
                    self._remove_from_parent()
                    return
            else:
                # No cycling - remove component
                self._remove_from_parent()
                return

        # Get next stage
        next_stage = stages[next_idx]

        # Remove from current position
        self._remove_from_parent()

        # Update component for next stage
        self.metadata.render_current_stage_index = next_idx
        self.metadata.born_cycle = new_cycle
        self.ttl = next_stage.ttl if hasattr(next_stage, 'ttl') else None
        if hasattr(next_stage, 'cadence') and next_stage.cadence is not None:
            self.cad = next_stage.cadence

        # Re-insert at new position
        if self._context_ref:
            try:
                # Extract just the coordinate part from Pos (without behavior brackets)
                if hasattr(next_stage, '_coordinate_str') and next_stage._coordinate_str:
                    # Use the raw coordinate string (no behaviors)
                    selector = f"({next_stage._coordinate_str})"
                elif hasattr(next_stage, 'selector'):
                    # Fallback: use full selector (parser will strip behaviors)
                    selector = next_stage.selector
                else:
                    selector = str(next_stage)

                print(f"[LIFECYCLE DEBUG] Re-inserting component at selector: {selector}")
                print(f"[LIFECYCLE DEBUG] _context_ref type: {type(self._context_ref)}")
                print(f"[LIFECYCLE DEBUG] Component content: {self.content}")
                result = self._context_ref.pact_insert(selector, self)
                print(f"[LIFECYCLE DEBUG] Re-insertion result: {result}")

                # Verify it's actually there
                try:
                    sys_header = self._context_ref.select("d-1")
                    print(f"[LIFECYCLE DEBUG] System header after insert: {sys_header}")
                    if sys_header:
                        print(f"[LIFECYCLE DEBUG] System header children: {list(sys_header[0].content) if hasattr(sys_header[0], 'content') else 'no content'}")
                except Exception as e:
                    print(f"[LIFECYCLE DEBUG] Error checking system header: {e}")
            except Exception as e:
                # Transition failed - component is already removed
                print(f"[LIFECYCLE DEBUG] Re-insertion failed: {e}")
                pass

    def _parse_pos_selector(self, selector: str) -> tuple:
        """
        Parse Pos selector to extract depth/position coordinates.

        Args:
            selector: PACT selector string like "(d0, 1)" or "d-1, 2"

        Returns:
            Tuple of (depth, position)

        Raises:
            ValueError: If selector cannot be parsed
        """
        import re

        # Handle parenthesized format: "(d0, 1)" or "(d-1, 2)"
        match = re.search(r'\(d(-?\d+),\s*(\d+)\)', selector)
        if match:
            depth = int(match.group(1))
            position = int(match.group(2))
            return (depth, position)

        # Handle non-parenthesized format: "d0, 1" or "d-1, 2"
        match = re.search(r'd(-?\d+),\s*(\d+)', selector)
        if match:
            depth = int(match.group(1))
            position = int(match.group(2))
            return (depth, position)

        raise ValueError(f"Cannot parse position from selector: {selector}")

    def _remove_from_parent(self) -> None:
        """
        Remove this component from its parent container.

        Used during lifecycle transitions and TTL expiry.
        """
        try:
            if hasattr(self, '_parent') and self._parent is not None:
                parent = self._parent
                if hasattr(parent, 'content') and not isinstance(getattr(parent, 'content', None), str):
                    container = getattr(parent, 'content')
                    if container is not None and hasattr(container, 'remove'):
                        container.remove(self.offset)
        except Exception:
            # Silent fallback - removal failed
            pass





class PactRoot(PACTCore):
    """
    PACT root container with CoreOffsetArray content.
    """

    type: ClassVar[str] = "root"
    content: Optional[DepthArray] = Field(default=None) 

class PactCore(PACTNode):
    _depth: Optional[int] = PrivateAttr(default=None)
    @computed_field
    @property
    def depth(self) -> int:
        """Compute depth by looking up parent using get_component_by_id."""
        # Container components store their own depth
        if self._depth is not None:
            return self._depth

        # Content components inherit from parent
        if self.parent_id:
            context = self._context_ref
            if context:
                # During context initialization, avoid circular lookups
                if not hasattr(context, '_initialized') or not context._initialized:
                    return 0
                try:
                    parent = context.get_component_by_id(self.parent_id)
                    return getattr(parent, 'depth', 0) if parent else 0
                except:
                    pass
        return 0

class PACTSegment(PACTCore):
    type: ClassVar[str] = "pact_segment"
    depth: int = 0
    content: CoreOffsetArray[PACTNode] = Field(default_factory=CoreOffsetArray)

class PACTContainer(PactCore):
    content: CoreOffsetArray[PACTNode] = Field(default_factory=CoreOffsetArray)


class MessageTurn(PACTSegment):
    role: Optional[str] = Field(default="user")
    type: ClassVar[str] = "message_turn"
    depth: int = 0
    

    def __init__(self, context:"Context", **kwargs):
        kwargs['context_ref'] = context
        if context:
            kwargs['parent_id'] = context.id  # MessageTurn's parent is the context
        else:
            kwargs['parent_id'] = None
        super().__init__(**kwargs)
        self._context_ref = context
        self.content.core = MessageContainer(context=context, parent_id=self.id)



class MessageContainer(PACTContainer):
    type: ClassVar[str] = "message_container"

    def __init__(self, context: Optional["Context"] = None, **kwargs):
        kwargs['context_ref'] = context
        super().__init__(**kwargs)
        
        # Register this MessageContainer in the context registry
        if context is not None:
            context._registry.register_component(self)
        
        # Core Offset Layout Rule: Create default content at offset 0 (the "core")
        # Note: Default content creation moved to post-init to avoid forward reference issues

class SystemHeader(PACTCore):
    type: ClassVar[str] = "system_header"
    depth: int = -1
    content: CoreOffsetArray[PACTNode] = Field(default_factory=CoreOffsetArray)
    
    def __init__(self, context: Optional["Context"] = None, **kwargs):
        kwargs['context_ref'] = context
        if context:
            kwargs['parent_id'] = context.id  # SystemHeader's parent is the context
        else:
            kwargs['parent_id'] = None
        super().__init__(**kwargs)


class PACTContent(PACTNode):
    type: ClassVar[str] = "pact_content"
    content: str = ""
    
    def __init__(self, context: Optional["Context"] = None, **kwargs):
        # PACTContent components have string content, not CoreOffsetArray
        # So we need to handle the initialization differently than PACTNode
        super().__init__(context=context, **kwargs)


class ContentComponent(PACTContent):
    """ContextComponent for content that can be rendered"""
    type: ClassVar[str] = "content"
    description: ClassVar[str] = "Content"
    content: str = ""



class TextContent(ContentComponent):
    """ContextComponent for plain text content or History"""
    type: ClassVar[str] = "text_content"
    description: ClassVar[str] = "Text content"
    content: str = ""
    # Optional mount hint used by AgentContextManager before scheduling
    _mount_position: Optional[str] = None
    
    class Config:
        validate_assignment = True  # Enable validation on assignment
    


class ImagetContent(ContentComponent):
    """ContextComponent for Image input or History"""
    type: ClassVar[str] = "image_content"
    description: ClassVar[str] = "Image content"
    content: str = ""
    
    def render(self, options: Optional[Any] = None) -> str:
        """Render image component with markdown image syntax"""
        content = self.content.strip() if self.content else ""
        if not content:
            return ""
        
        # Check if it's a URL or description
        if content.startswith(('http://', 'https://', 'file://', 'data:')):
            formatted = f"![Image]({content})"
        else:
            formatted = f"🖼️ [Image: {content}]"
        
        if options is not None and hasattr(options, 'show_component_types') and options.show_component_types:
            formatted += f" *[{self.type}]*"
        
        return formatted


class AudioContent(ContentComponent):
    """ContextComponent for Audio input"""
    type: ClassVar[str] = "audio_content"
    description: ClassVar[str] = "Audio content"
    content: str = ""
    
    def render(self, options: Optional[Any] = None) -> str:
        """Render audio component with emoji and description"""
        content = self.content.strip() if self.content else ""
        if not content:
            return ""
        
        # Check if it's a URL or description  
        if content.startswith(('http://', 'https://', 'file://', 'data:')):
            formatted = f"🎵 [Audio]({content})"
        else:
            formatted = f"🎵 [Audio: {content}]"
        
        if options is not None and hasattr(options, 'show_component_types') and options.show_component_types:
            formatted += f" *[{self.type}]*"
        
        return formatted


class DocumentContent(ContentComponent):
    """ContextComponent for Document input or History"""
    type: ClassVar[str] = "document_content"
    description: ClassVar[str] = "Document content"
    content: str = ""
    
    def render(self, options: Optional[Any] = None) -> str:
        """Render document component with emoji and description"""
        content = self.content.strip() if self.content else ""
        if not content:
            return ""
        
        # Check if it's a URL or description  
        if content.startswith(('http://', 'https://', 'file://', 'data:')):
            formatted = f"📄 [Document]({content})"
        else:
            formatted = f"📄 [Document: {content}]"
        
        if options is not None and hasattr(options, 'show_component_types') and options.show_component_types:
            formatted += f" *[{self.type}]*"
        
        return formatted


class VideoContent(ContentComponent):
    """ContextComponent for Video input or History"""
    type: ClassVar[str] = "video_content"
    description: ClassVar[str] = "Video content"
    content: str = ""
    
    def render(self, options: Optional[Any] = None) -> str:
        """Render video component with emoji and description"""
        content = self.content.strip() if self.content else ""
        if not content:
            return ""
        
        # Check if it's a URL or description  
        if content.startswith(('http://', 'https://', 'file://', 'data:')):
            formatted = f"🎥 [Video]({content})"
        else:
            formatted = f"🎥 [Video: {content}]"
        
        if options is not None and hasattr(options, 'show_component_types') and options.show_component_types:
            formatted += f" *[{self.type}]*"
        
        return formatted



class ContextHook(PACTNode):
    """Context hook component that allows dynamic type assignment for declarative templates"""

    # Define type as a Pydantic field so it can be passed dynamically
    type: str = Field(default="hook")

    def __repr__(self) -> str:
        content_preview = str(self.content)[:50] if self.content else ""
        return f"ContextHook(type='{self.type}', content='{content_preview}...')"


class XMLAttributeAccessor:
    """Accessor class for XML attributes with dict-like interface"""
    
    def __init__(self, attributes: dict):
        self._attributes = attributes
    
    def __getitem__(self, key: str) -> Any:
        return self._attributes[key]
    
    def __contains__(self, key: str) -> bool:
        return key in self._attributes
    
    def get(self, key: str, default: Any = None) -> Any:
        return self._attributes.get(key, default)
    
    def keys(self):
        return self._attributes.keys()
    
    def values(self):
        return self._attributes.values()
    
    def items(self):
        return self._attributes.items()
    
    def __setitem__(self, key: str, value: Any) -> None:
        self._attributes[key] = value
    
    def __delitem__(self, key: str) -> None:
        del self._attributes[key]
    
    def update(self, other: dict) -> None:
        self._attributes.update(other)
    
    def __repr__(self) -> str:
        return f"XMLAttributeAccessor({self._attributes})"


class XMLComponent(ContextHook):
    """XML component that renders as XML tags with dynamic type"""
    
    # Reserved parameters that should not become XML attributes
    RESERVED_PARAMS: ClassVar[Set[str]] = {
        'type', 'content', 'ttl', 'cycle', 'depth', 'offset', 'description',
        # PACT infrastructure fields that should not be treated as XML attributes
        'metadata', 'coordinates', 'placement', 'key', 'tags',
        'created_at_ns', 'creation_index', 'id', 'cad', 'parent_id'
    }
    
    # Attributes that would conflict with component methods/properties
    FORBIDDEN_ATTRS: ClassVar[Set[str]] = {
        'type', 'content', 'render', 'attrs', 'metadata', 'add_child', 
        'remove_child', 'get_parent', 'is_empty_container', 'can_cascade_cleanup',
        '__init__', '__repr__', '__str__'
    }
    
    def __init__(self, type: Optional[str] = None, **kwargs):
        """Initialize XMLComponent supporting both dynamic and declarative patterns."""
        
        # Handle declarative subclass pattern: check if 'type' is defined as a field
        if type is None:
            # Check if subclass has 'type' as an instance field by looking at annotations
            annotations = getattr(self.__class__, '__annotations__', {})
            if 'type' in annotations:
                # For Pydantic field declarations, we need to look at __fields__ or model defaults
                model_fields = getattr(self.__class__, '__fields__', {})
                if 'type' in model_fields:
                    field_info = model_fields['type']
                    if hasattr(field_info, 'default') and field_info.default is not None:
                        type = field_info.default
                    else:
                        raise ValueError("XMLComponent subclass has 'type' field but no default value")
                else:
                    # Fallback: try to get from class __dict__ (for simple assignments)
                    class_dict = {}
                    for cls in self.__class__.__mro__:
                        class_dict.update(cls.__dict__)
                    if 'type' in class_dict and isinstance(class_dict['type'], str):
                        type = class_dict['type']
                    else:
                        raise ValueError("XMLComponent subclass has 'type' field annotation but no usable default")
            else:
                raise ValueError("XMLComponent requires 'type' parameter or 'type' field declaration")
        
        # Split kwargs into XML attributes and component parameters
        xml_attrs = {}
        component_kwargs = {}
        pydantic_fields = {}
        
        for k, v in kwargs.items():
            if k in self.RESERVED_PARAMS:
                component_kwargs[k] = v
            else:
                # Check if it's a declared Pydantic field in this class or parents
                annotations = getattr(self.__class__, '__annotations__', {})
                if k in annotations:
                    pydantic_fields[k] = v  # Will be set as instance attribute
                    xml_attrs[k] = str(v) if v is not None else None  # Also add to XML attrs as string
                else:
                    xml_attrs[k] = str(v) if v is not None else None  # Pure XML attribute
        
        # Validate XML attribute names for conflicts
        self._validate_attribute_names(xml_attrs)
        
        # Initialize parent (ContextHook) with type
        if type is None:
            raise ValueError("XMLComponent requires a valid type string")
        super().__init__(type=type, **component_kwargs)
        
        # Set Pydantic field values as instance attributes
        for field_name, field_value in pydantic_fields.items():
            setattr(self, field_name, field_value)
        
        # After initialization, collect ALL declared field values for XML attributes
        # (including defaults that weren't passed as kwargs)
        annotations = getattr(self.__class__, '__annotations__', {})
        for field_name in annotations:
            if field_name not in self.RESERVED_PARAMS and hasattr(self, field_name):
                field_value = getattr(self, field_name)
                # Skip ClassVar attributes and None values
                if (field_value is not None and 
                    not isinstance(field_value, set) and  # Skip ClassVar constants like RESERVED_PARAMS
                    not field_name.isupper()):  # Skip CONSTANT_STYLE names
                    xml_attrs[field_name] = str(field_value)
        
        # Store XML attributes in PACT metadata.props
        self.metadata.props.update(xml_attrs)
    
    def _validate_attribute_names(self, xml_attrs: dict) -> None:
        """Validate XML attribute names don't conflict with component methods"""
        conflicts = set(xml_attrs.keys()) & self.FORBIDDEN_ATTRS
        if conflicts:
            raise ValueError(f"XML attributes conflict with component methods: {conflicts}")
        
        # Validate XML name syntax (basic XML name pattern)
        xml_name_pattern = re.compile(r'^[a-zA-Z_:][\w\-\.:]*$')
        
        for attr_name in xml_attrs:
            if not xml_name_pattern.match(attr_name):
                raise ValueError(f"Invalid XML attribute name: '{attr_name}'")
    
    @property
    def attrs(self) -> 'XMLAttributeAccessor':
        """Convenience accessor for XML attributes stored in metadata.props"""
        return XMLAttributeAccessor(self.metadata.props)
    
    def _escape_text(self, text: str) -> str:
        """Escape XML text content"""
        return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;'))
    
    def _escape_attribute(self, value: str) -> str:
        """Escape XML attribute value"""
        return (value
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&apos;'))
    
    def _render_attributes(self) -> str:
        """Convert Python values to XML attribute strings"""
        attr_parts = []
        
        for key, value in self.metadata.props.items():
            if value is None:
                continue  # Skip None values
            elif value is True:
                attr_parts.append(f'{key}="true"')
            elif value is False:
                attr_parts.append(f'{key}="false"')
            elif isinstance(value, (list, tuple)):
                # Join lists with spaces (common XML pattern)
                str_value = ' '.join(str(item) for item in value)
                attr_parts.append(f'{key}="{self._escape_attribute(str_value)}"')
            else:
                str_value = str(value)
                attr_parts.append(f'{key}="{self._escape_attribute(str_value)}"')
        
        return ' '.join(attr_parts)
    
    def render(self, options: Optional[Any] = None) -> str:
        """Render component as XML markup"""
        tag_name = self.type
        attr_str = self._render_attributes()
        
        # Check for empty content and use self-closing tags
        if isinstance(self.content, str):
            if not self.content.strip():
                # Self-closing tag for empty or whitespace-only content
                if attr_str:
                    return f"<{tag_name} {attr_str}/>"
                else:
                    return f"<{tag_name}/>"
        elif isinstance(self.content, list):
            if not self.content:
                # Self-closing tag for empty list
                if attr_str:
                    return f"<{tag_name} {attr_str}/>"
                else:
                    return f"<{tag_name}/>"
        
        # Build opening tag
        if attr_str:
            opening_tag = f"<{tag_name} {attr_str}>"
        else:
            opening_tag = f"<{tag_name}>"
        
        closing_tag = f"</{tag_name}>"
        
        # Handle content rendering
        if isinstance(self.content, str):
            # Escape and render string content with newlines for readability
            escaped_content = self._escape_text(self.content)
            return f"{opening_tag}\n{escaped_content}\n{closing_tag}"
        elif isinstance(self.content, list):
            # Render list content - iterate through items
            content_parts = []
            for item in self.content:
                if isinstance(item, str):
                    # String items get escaped
                    content_parts.append(self._escape_text(item))
                elif hasattr(item, 'render') and callable(getattr(item, 'render')):
                    # ContextComponent items get rendered with options
                    content_parts.append(item.render(options))  # type: ignore
                else:
                    # Other objects get converted to string and escaped
                    content_parts.append(self._escape_text(str(item)))
            
            # Join multiple components with newlines for better readability
            if len(content_parts) > 1:
                rendered_content = '\n'.join(content_parts)
            else:
                rendered_content = ''.join(content_parts)
            if rendered_content.strip():  # Only add newlines if there's actual content
                return f"{opening_tag}\n{rendered_content}\n{closing_tag}"
            else:
                return f"{opening_tag}{rendered_content}{closing_tag}"
        else:
            # Fallback for any other content types (should not occur due to Pydantic typing)
            # Convert to string and escape as safety measure
            fallback_content = self._escape_text(str(self.content))
            return f"{opening_tag}\n{fallback_content}\n{closing_tag}"
