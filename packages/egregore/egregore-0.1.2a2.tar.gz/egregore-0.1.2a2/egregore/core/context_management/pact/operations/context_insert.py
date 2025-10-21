"""
PactContextInsertHandler - Our own insertion logic for PACT operations.

Implements a subset of the core ContextInsertHandler behaviors with a clean
implementation that doesn't route through ContextOperations. The goal is to
provide a separate, explicit insert path for pact API usage.

Supported behaviors:
- Input validation: string or ContextComponent; empty strings blocked
- String auto-converted to TextContextComponent
- Selectors: coordinate "(d...)" with 1-3+ elements, "#key", ".type"
- d0 invariant: d0,1+ requires d0,0,0
- (dN,0) MessageContainer wrapping; (d0,0) pushes active→depth1 first
- Auto-create conversation depth (d>=1) MessageTurnComponent as needed
- Offset selection by CoreOffsetArray.get_offsets() → max+1 when appending
- Multi-position tuple of Pos supported via cloning
"""

from __future__ import annotations

from typing import Any, List, Tuple, Union, cast

# Import real types — no Any aliasing
from egregore.core.context_management.pact.components.core import (
    PACTCore, 
    PACTNode, 
    PactCore,
    TextContent,
    MessageTurn,
    MessageContainer,
)
from egregore.core.context_management.pact.context.base import Context, UpdateResult
from egregore.core.context_management.pact.context.position import Pos
from egregore.core.context_management.pact.data_structures.core_offset_array import CoreOffsetArray


class PactContextInsertHandler:
    def __init__(self, context: Context) -> None:
        self.context = context

    # --- public API ---

    def insert(self, selector: Union[str, Pos, Tuple[Pos, ...]], component: Union[PACTCore, PactCore, str]) -> 'UpdateResult':
        from egregore.core.context_management.pact.context.base import UpdateResult

        try:
            # Validate type - raise TypeError for validation tests
            if not isinstance(component, (str,)) and not _is_component(component) and not _is_pact_component(component):
                raise TypeError(f"Component must be either a string, ContextComponent, or PACTCore, got {type(component)}")

            # Note: Empty string validation now happens in pact_insert() before conversion
            # This allows pre-made TextContent with empty content to be inserted if needed

            # Multi-position tuple of Pos objects
            if isinstance(selector, tuple):
                return self._insert_multi_position(selector, component)

            # Normalize selector to str
            sel_str = _pos_to_string(selector)

            # Multi-coordinate string selector: ((d0,1), (d-1,1))
            if sel_str.strip().startswith('((') and '),' in sel_str:
                # Parse multi-coordinate selector and convert to tuple of Pos
                return self._insert_multi_coordinate_string(sel_str, component)

            # Convert string to TextContent for PACT architecture
            if isinstance(component, str):
                from egregore.core.context_management.pact.components.core import TextContent
                component = TextContent(content=component)

            # Assign creation metadata and context reference  
            _assign_creation_index(self.context, component)
            current_cycle = getattr(self.context, 'current_episode', 0)
            component.metadata.born_cycle = current_cycle
            
            # Set context reference BEFORE setting parent_id (prevents _update_coordinates assertion)
            if hasattr(component, '_context_ref'):
                component._context_ref = self.context

            # Resolve target
            target_container, target_offset = self._resolve_insertion_target(sel_str)

            # Enforce d0 invariant
            self._validate_d0_invariant(sel_str)

            # MessageContainers should only be created by depth triggers, not direct insertion
            # Remove MessageContainer wrapping for direct insertions

            # Parent linkage - handle both old and new component types
            if hasattr(component, 'parent_id'):
                component.parent_id = getattr(target_container, 'id', None)

            # Insert via CoreOffsetArray stack push
            content = getattr(target_container, 'content', None)
            if content is None or not hasattr(content, 'insert'):
                raise ValueError(f"Target container {type(target_container)} does not support stack push insertion")
            actual_offset = content.insert(target_offset, component)

            # CRITICAL: Update component's offset to reflect actual insertion position
            if hasattr(component, 'offset'):
                component.offset = actual_offset

            # ODI is handled automatically by DepthArray when needed

            # Inject context reference for computed coordinates
            if hasattr(component, '_inject_context_ref'):
                component._inject_context_ref(self.context)
            elif hasattr(component, '_context_ref'):
                component._context_ref = self.context

            # Register with coordinates for cadence tracking
            # Pass the selector string - registry will convert it
            # Don't use component.coordinates as it may be incomplete during insertion
            self.context._registry.register_component(component, coords=sel_str)

            return UpdateResult(success=True, updated_components=[component])

        except TypeError:
            # Re-raise TypeError for validation failures
            raise
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            return UpdateResult(success=False, errors=[f"Insert failed: {e}", f"Traceback: {tb}"])

    # --- helpers ---

    def _resolve_insertion_target(self, selector_str: str) -> Tuple[PactCore, int]:
        """Resolve insertion target using Lark-based selector when possible.

        Coordinate selectors are handled explicitly for exact placement semantics.
        Other selectors are resolved via the Lark engine, and we pick the first
        container-like node (or the parent of a leaf) as the insertion target.
        """
        # 1) Coordinate selectors: "(d0,0)", "(d0,1,2)" AND "d0,0", "d0,1"
        # Strip behavior brackets first (PACT v0.1 allows behaviors like "[ttl=3]")
        coord_str = selector_str
        if '[' in coord_str:
            coord_str = coord_str[:coord_str.index('[')].strip()

        if (coord_str.startswith('(') and ')' in coord_str) or (coord_str.startswith('d') and ',' in coord_str):
            coords = self._parse_coordinates(coord_str.strip('()'))
            if len(coords) == 1:
                depth = coords[0]
                depth_comp = self._get_component_by_depth(depth)
                if depth == 0:
                    # For PACT depth 0, just use the MessageTurn directly
                    return depth_comp, _next_offset(cast(Any, depth_comp.content))
                return depth_comp, _next_offset(cast(Any, depth_comp.content))

            if len(coords) == 2:
                depth, position = coords
                # Special case: (d0,0) insertion behavior
                if depth == 0 and position == 0:
                    existing_turn = self.context.content[0]
                    existing_container = existing_turn.content[0]

                    # Check if the existing MessageContainer at d0,0 has content
                    if hasattr(existing_container, 'content') and hasattr(existing_container.content, 'get_offsets'):
                        existing_offsets = existing_container.content.get_offsets()
                        if existing_offsets and any(existing_container.content[off] for off in existing_offsets if hasattr(existing_container.content[off], 'content') and existing_container.content[off].content.strip()):
                            # Has content - create new MessageTurn and trigger ODI
                            new_turn = self.context.content.create_message_turn(depth=0)
                            self.context._registry.register_component(new_turn)
                            if hasattr(new_turn.content, 'core') and new_turn.content.core:
                                self.context._registry.register_component(new_turn.content.core)
                            message_container = new_turn.content[0]
                            return message_container, 0
                        else:
                            # No content - use existing MessageContainer
                            return existing_container, 0
                    else:
                        # No content structure - use existing MessageContainer
                        return existing_container, 0

                depth_comp = self._get_component_by_depth(depth)
                # (dN,0) for other depths - target existing MessageContainer
                if position == 0 and depth >= 0:
                    # For content insertion at (dN,0), target the content inside MessageContainer (dN,0,0)
                    # Get the MessageContainer and return it as the container with offset 0
                    if hasattr(depth_comp, 'content') and hasattr(depth_comp.content, '__getitem__'):
                        try:
                            message_container = depth_comp.content[0]  # MessageContainer at position 0
                            return message_container, 0  # Insert at offset 0 inside the container
                        except (KeyError, IndexError):
                            # If no MessageContainer exists, return depth_comp to create one
                            pass
                    return depth_comp, 0
                if position > 0 and depth >= 0:
                    self._ensure_canvas_exists(depth_comp)
                return depth_comp, position

            # 3+ coordinates: validate PACT structure rules
            depth = coords[0]
            # PACT rule: MessageContainers only exist at (dN,0), so (dN,1+) should not be accessible
            if depth >= 0 and len(coords) >= 3 and coords[1] > 0:
                raise ValueError(f"Parent coordinate path doesn't exist: {coords[:-1]}")
            
            # Navigate to parent container, validate that intermediate positions exist
            current = self._get_component_by_depth(coords[0])
            for idx in coords[1:-1]:
                cont_any = getattr(current, 'content', None)
                if cont_any is not None and hasattr(cont_any, '__contains__') and idx in cast(Any, cont_any):
                    current = cast(Any, cont_any)[idx]
                else:
                    # PACT invariant: parent coordinate path must exist before insertion
                    raise ValueError(f"Parent coordinate path doesn't exist: {coords[:-1]}")
            return current, coords[-1]

        # 2) Non-coordinate: use Lark selector engine
        try:
            from egregore.pact.selector import LarkPACTParser, LarkPACTSelector
            parser = LarkPACTParser()
            ast = parser.parse(selector_str)
            engine = LarkPACTSelector()
            candidates = engine.select(self.context, ast)
            if candidates:
                # Prefer containers (with 'content'); if leaf, use parent container
                target = None
                for c in candidates:
                    if hasattr(c, 'content') and not isinstance(getattr(c, 'content'), str):
                        target = c
                        break
                if target is None:
                    target = candidates[0]
                    parent_id = getattr(target, 'parent_id', None)
                    parent = self.context.get_component_by_id(parent_id) if parent_id else None
                    if parent and hasattr(parent, 'content'):
                        return parent, _next_offset(cast(Any, parent.content))
                    # Fallback to active message container (depth 0)
                    depth_0 = self.context.content[0]
                    return depth_0, _next_offset(cast(Any, depth_0.content))
                # Insert at end of container
                return target, _next_offset(cast(Any, target.content))
        except Exception:
            # If Lark resolution fails, fall back to active message container
            pass

        # Use PACT depth 0 as active message
        depth_0 = self.context.content[0]
        return depth_0, _next_offset(cast(Any, depth_0.content))

    def _ensure_canvas_exists(self, depth_component: PactCore) -> None:
        # MessageContainers should only be created by depth triggers, not direct insertion
        # For existing depths, the MessageContainer should already exist at position 0
        cont_any = getattr(depth_component, 'content', None)
        if cont_any is not None and hasattr(cont_any, '__contains__') and 0 in cast(Any, cont_any):
            return
        # If no canvas exists, this indicates an architectural issue
        # MessageContainers should be created when the depth is first created
        raise ValueError(f"No MessageContainer found at position 0 for depth component {type(depth_component)}. MessageContainers should be created by depth triggers, not insertion.")

    def _parse_coordinates(self, coord_str: str) -> List[int]:
        if not coord_str.startswith('d'):
            raise ValueError(f"Coordinate must start with 'd': {coord_str}")

        # Strip behavior brackets like "[ttl=3]" from valid PACT selectors
        s = coord_str[1:]  # Remove 'd' prefix
        if '[' in s:
            s = s[:s.index('[')].strip()  # Remove everything from '[' onward

        if ',' in s:
            return [int(p.strip()) for p in s.split(',')]
        return [int(s)]

    def _get_component_by_depth(self, depth: int) -> PactCore:
        try:
            return self.context.content[depth]
        except (KeyError, ValueError):
            if depth >= 1:
                from egregore.core.context_management.pact.components.core import MessageTurn
                mt = MessageTurn(context=self.context)
                self.context.content.insert(depth, mt)
                self.context._registry.register_component(mt)
                return mt
            raise ValueError(f"Invalid or uninitialized PACT depth: {depth}")

    def _validate_d0_invariant(self, selector_str: str) -> None:
        if selector_str.startswith('(') and ')' in selector_str:
            # Strip behavior brackets first (PACT v0.1 allows behaviors)
            coord_str = selector_str
            if '[' in coord_str:
                coord_str = coord_str[:coord_str.index('[')].strip()
            coords = self._parse_coordinates(coord_str.strip('()'))
            if len(coords) == 2 and coords[0] == 0 and coords[1] > 0:
                am = self.context.active_message
                if not (0 in am.content):
                    raise ValueError("PACT invariant violation: d0,0,0 must exist before inserting at d0,N")

    def _is_message_container_position(self, selector_str: str, target_offset: int) -> bool:
        if selector_str.startswith('(') and ')' in selector_str and target_offset == 0:
            coords = self._parse_coordinates(selector_str.strip('()'))
            if len(coords) == 2:
                depth, pos = coords
                # Only wrap in MessageContainer for conversation depths (depth > 0), not system depth (-1) or active depth (0)
                return depth > 0 and pos == 0
        return False

    def _wrap_in_message_container(self, component: PactCore, parent_container: PactCore) -> PactCore:
        mc = MessageContainer()
        mc.parent_id = parent_container.id
        _assign_creation_index(self.context, mc)
        current_cycle = getattr(self.context, 'current_episode', 0)
        mc.metadata.born_cycle = current_cycle
        component.parent_id = mc.id
        
        # Inject context reference into the original component BEFORE wrapping
        if hasattr(component, '_inject_context_ref'):
            component._inject_context_ref(self.context)
            
        mc.content.insert(0, component)
        self.context._registry.register_component(mc)
        self.context._registry.register_component(component)
        return mc

    def _push_active_to_depth_1_if_needed(self) -> None:
        try:
            am = self.context.active_message
            # If there is content at d0, move its MessageContainer to a new MessageTurn at d1
            if hasattr(am, 'content') and len(am.content) > 0:
                container = am.content[0]
                from egregore.core.context_management.pact.components.core import MessageTurn
                mt = MessageTurn(context=self.context)
                container.parent_id = mt.id
                mt.content.insert(0, container)
                cast(Any, am.content).remove(0)
                self.context.content.insert(1, mt)
                self.context._registry.register_component(mt)
        except Exception:
            # Non-fatal
            pass

    def _insert_multi_position(self, positions: Tuple[Pos, ...], component: Union[PACTCore, PactCore, str]) -> 'UpdateResult':
        from egregore.core.context_management.pact.context.base import UpdateResult
        if not positions:
            return UpdateResult(success=False, errors=["No positions provided for multi-position insertion"])

        if isinstance(component, str):
            component = TextContent(content=component)

        inserted = []
        errors: List[str] = []
        warnings: List[str] = []

        for i, pos in enumerate(positions):
            try:
                comp_to_insert = component if i == 0 else _clone_component(self.context, component, i)
                sel_str = _pos_to_string(pos)
                target, offset = self._resolve_insertion_target(sel_str)

                # Set context reference FIRST before setting parent_id (prevents assertion error)
                if hasattr(comp_to_insert, '_inject_context_ref'):
                    comp_to_insert._inject_context_ref(self.context)
                elif hasattr(comp_to_insert, '_context_ref'):
                    comp_to_insert._context_ref = self.context

                # Now set parent_id (triggers _update_coordinates which needs _context_ref)
                if hasattr(comp_to_insert, 'parent_id'):
                    comp_to_insert.parent_id = getattr(target, 'id', None)

                content = getattr(target, 'content', None)
                if content is None:
                    raise ValueError(f"Target container {type(target)} has no content")

                # Use insert method for proper offset handling (not __setitem__)
                if hasattr(content, 'insert'):
                    actual_offset = content.insert(offset, comp_to_insert)
                    # Update component's offset to reflect actual position
                    if hasattr(comp_to_insert, 'offset'):
                        comp_to_insert.offset = actual_offset
                else:
                    raise ValueError(f"Target container {type(target)} does not support insertion")

                self.context._registry.register_component(comp_to_insert)
                inserted.append(comp_to_insert)
            except Exception as e:
                import traceback
                tb = traceback.format_exc()
                errors.append(f"Failed to insert at position {pos}: {e}\n{tb}")

        if inserted:
            coord_list: List[Any] = []
            for c in inserted:
                coords_obj = getattr(c, 'coordinates', None)
                if coords_obj is not None and hasattr(coords_obj, 'coords'):
                    coord_list.append(coords_obj.coords)
            coords = coord_list
            warnings.append(f"Multi-position placement: {len(inserted)} locations - {coords}")

        return UpdateResult(success=len(errors) == 0, updated_components=inserted, errors=errors, warnings=warnings)

    def _insert_multi_coordinate_string(self, selector_str: str, component: Union[PACTCore, PactCore, str]) -> 'UpdateResult':
        """Parse multi-coordinate selector string and convert to tuple of Pos objects."""
        from egregore.core.context_management.pact.context.position import Pos
        from egregore.core.context_management.pact.context.base import UpdateResult

        try:
            # Remove outer parentheses: ((d0,1), (d-1,1)) -> (d0,1), (d-1,1)
            inner = selector_str.strip()[1:-1].strip()

            # Split by "), (" to get individual coordinates
            coord_strs = []
            depth = 0
            current = []
            for char in inner:
                if char == '(':
                    depth += 1
                elif char == ')':
                    depth -= 1
                    if depth == 0:
                        # End of coordinate
                        current.append(char)
                        coord_strs.append(''.join(current).strip())
                        current = []
                        continue

                if depth > 0 or (depth == 0 and char not in ','):
                    current.append(char)

            # Convert to Pos objects
            positions = tuple(Pos(coord.strip()) for coord in coord_strs if coord.strip())

            # Delegate to multi-position handler
            return self._insert_multi_position(positions, component)

        except Exception as e:
            return UpdateResult(success=False, errors=[f"Failed to parse multi-coordinate selector '{selector_str}': {e}"])


# --- module helpers ---

def _pos_to_string(pos: Union[str, Pos]) -> str:
    if isinstance(pos, str):
        # Allow bare "d0,0" to be treated as "(d0,0)"
        s = pos.strip()
        if s.startswith('('):
            return s
        if s.startswith('d'):
            return f"({s})"
        return s
    # Pos-like with .selector
    return getattr(pos, 'selector', str(pos))


def _next_offset(content) -> int:
    if not hasattr(content, 'get_offsets'):
        return 0
    offsets = content.get_offsets()
    if not offsets:
        return 0
    mx = max(offsets) if offsets else -1
    return mx + 1 if mx >= 0 else 0


def _is_component(obj: Any) -> bool:
    try:
        from egregore.core.context_management.pact.components.core import PactCore as CC
        return isinstance(obj, CC)
    except Exception:
        return hasattr(obj, 'id') and hasattr(obj, 'metadata')


def _is_pact_component(obj: Any) -> bool:
    try:
        from egregore.core.context_management.pact.components.core import PACTCore
        return isinstance(obj, PACTCore)
    except Exception:
        return hasattr(obj, 'id') and hasattr(obj, 'metadata')


def _assign_creation_index(context: Context, component: PactCore) -> None:
    if hasattr(component, 'creation_index') and hasattr(context, 'get_next_creation_index'):
        component.creation_index = context.get_next_creation_index()


def _clone_component(context: Context, component: PactCore, position_index: int) -> PactCore:
    cloned = component.model_copy(deep=True)
    from egregore.core.context_management.pact.components.core import generate_hash_id
    from egregore.core.context_management.pact.data_structures.coordinates import Coordinates
    cloned.id = generate_hash_id()
    cloned.metadata.coordinates = Coordinates()
    current_cycle = getattr(context, 'current_episode', 0)
    cloned.metadata.born_cycle = current_cycle
    if hasattr(cloned.metadata, 'aux'):
        if cloned.metadata.aux is None:
            cloned.metadata.aux = {}
        cloned.metadata.aux['multi_position_source'] = getattr(component, 'id', '')
        cloned.metadata.aux['position_index'] = str(position_index)
        cloned.metadata.aux['is_multi_position_clone'] = 'true'
    # ttl/cad copy if present
    if hasattr(component, 'ttl'):
        cloned.ttl = getattr(component, 'ttl')
    if hasattr(component, 'cad'):
        cloned.cad = getattr(component, 'cad')
    # Copy tags and key with suffix
    if hasattr(component, 'tags') and getattr(component, 'tags'):
        cloned.tags = component.tags.copy()
    if hasattr(component, 'key') and getattr(component, 'key'):
        cloned.key = f"{component.key}_pos{position_index}"
    return cloned
