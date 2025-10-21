"""
PactContextUpdateHandler - Our own update logic for PACT operations.

Provides append and replace modes using Lark-based selector targeting and
coordinate-based placement, while preserving core PACT behaviors and
registry semantics.
"""

from __future__ import annotations

from typing import Any, List, Tuple, Union, cast

from egregore.core.context_management.pact.context.base import Context, UpdateResult
from egregore.core.context_management.pact.context.position import Pos
from egregore.core.context_management.pact.components.core import (
    PACTCore as ContextComponent,
    TextContent as TextContextComponent,
    MessageTurn as MessageTurnComponent,
    MessageContainer,
    MessageTurn as MessageTurnComponent,
)
from egregore.core.context_management.pact.components.core import MessageTurn as ActiveMessageComponent


class PactContextUpdateHandler:
    def __init__(self, context: Context) -> None:
        self.context = context

    def update(
        self,
        pos_or_selector: Union[Pos, str, None] = None,
        *,
        component: ContextComponent | None = None,
        mode: str = "replace",
        content: str | None = None,
        **_kwargs: Any,
    ) -> UpdateResult:
        try:
            if pos_or_selector is None and component is None and content is None:
                return UpdateResult(success=True, warnings=["No-op update"])

            # Convert string component to TextContextComponent
            if isinstance(component, str):
                component = TextContextComponent(content=component)
            elif component is None and content is not None and mode in ("append", "replace"):
                component = TextContextComponent(content=content)

            if component is None:
                return UpdateResult(success=False, errors=["Component required for update"])

            if mode not in ("append", "replace"):
                return UpdateResult(success=False, errors=[f"Invalid mode: {mode}"])

            if isinstance(pos_or_selector, str):
                sel = pos_or_selector
            elif isinstance(pos_or_selector, Pos):
                sel = pos_or_selector.selector
            else:
                sel = "(d0)"  # default to active message core

            if mode == "append":
                return self._update_append_mode(sel, component)
            else:
                return self._update_replace_mode(sel, component)

        except Exception as e:
            import traceback
            return UpdateResult(success=False, errors=[f"Update failed: {e}", f"Traceback: {traceback.format_exc()}"])

    # --- append ---

    def _update_append_mode(self, selector_str: str, component: ContextComponent) -> UpdateResult:
        # Assign creation metadata
        _assign_creation_index(self.context, component)
        current_cycle = getattr(self.context, 'current_episode', 0)
        component.metadata.born_cycle = current_cycle

        # Resolve target container and requested position
        target_container, requested_position = self._resolve_append_target(selector_str)

        # Inject context reference first (needed for parent_id assignment)
        if hasattr(component, '_inject_context_ref'):
            component._inject_context_ref(self.context)
        component._context_ref = self.context

        # Parent linkage
        component.parent_id = getattr(target_container, 'id', None)

        # Find available position with container rules
        actual_position = self._find_available_position_with_container_rules(target_container, requested_position)

        # Insert using CoreOffsetArray stack push
        content = getattr(target_container, 'content', None)
        if content is None or not hasattr(content, 'insert'):
            return UpdateResult(success=False, errors=[f"Target container {type(target_container)} does not support stack push insertion"])
        # CoreOffsetArray.insert performs stack-push semantics
        content.insert(actual_position, component)

        # Inject context reference
        if hasattr(component, '_inject_context_ref'):
            component._inject_context_ref(self.context)

        # Register
        self.context._registry.register_component(component)

        return UpdateResult(
            success=True,
            updated_components=[component],
            warnings=[f"Component appended at position {actual_position} (requested {requested_position})"],
        )

    def _resolve_append_target(self, selector_str: str) -> Tuple[ContextComponent, int]:
        # Coordinate selectors
        if selector_str.startswith('(') and ')' in selector_str:
            coords = self._parse_coordinates(selector_str.strip('()'))
            if len(coords) == 1:
                depth = coords[0]
                depth_comp = self._get_component_by_depth(depth)
                if depth == 0:
                    message_turn = cast(MessageTurnComponent, depth_comp)
                    mc = message_turn.content[0]  # MessageContainer is always at offset 0
                    return mc, 0
                return depth_comp, 0
            if len(coords) == 2:
                depth, requested_position = coords
                depth_comp = self._get_component_by_depth(depth)
                # (dN,0) is the MessageContainer for message depths; redirect append into it
                if requested_position == 0 and depth >= 0:
                    if depth == 0:
                        # Append to active's MessageContainer core area
                        message_turn = cast(MessageTurnComponent, depth_comp)
                        mc = message_turn.content[0]  # MessageContainer is always at offset 0
                        return mc, 0
                    return depth_comp, 0
                # Ensure canvas exists for message depths when appending at pos>0
                if requested_position > 0 and depth >= 0:
                    self._ensure_canvas_exists(depth_comp)
                return depth_comp, requested_position
            # 3+ dims: navigate through container path
            current = self._get_component_by_depth(coords[0])
            for idx in coords[1:-1]:
                cont_any = getattr(current, 'content', None)
                if cont_any is not None and hasattr(cont_any, '__contains__') and idx in cast(Any, cont_any):
                    current = cast(Any, cont_any)[idx]
                else:
                    raise ValueError(f"Parent coordinate path doesn't exist: {coords[:-1]}")
            return current, coords[-1]

        # Non-coordinate: use Lark selector to identify a container target
        try:
            from ..context.selector.parser import LarkPACTParser
            from ..context.selector.engine import LarkPACTSelector
            parser = LarkPACTParser()
            ast = parser.parse(selector_str)
            engine = LarkPACTSelector()
            candidates = engine.select(self.context, ast)
            if candidates:
                # Prefer containers with content; otherwise use parent container
                for c in candidates:
                    if hasattr(c, 'content') and not isinstance(getattr(c, 'content'), str):
                        return c, 0
                target = candidates[0]
                parent_id = getattr(target, 'parent_id', None)
                parent = self.context.get_component_by_id(parent_id) if parent_id else None
                if parent and hasattr(parent, 'content'):
                    return parent, 0
        except Exception:
            pass
        # Default to active message container
        message_turn = cast(MessageTurnComponent, self.context.content[0])
        return message_turn.content[0], 0

    def _find_available_position_with_container_rules(self, target_container: ContextComponent, requested_position: int) -> int:
        content = getattr(target_container, 'content', None)
        if content is None or not hasattr(content, 'get_offsets'):
            return requested_position
        offsets = list(content.get_offsets())
        if 0 not in offsets:
            return 0
        # Positive requests: find first available >= requested
        if requested_position >= 0:
            pos = requested_position
            while pos in offsets:
                pos += 1
            return pos
        # Negative requests: find first available <= requested
        pos = requested_position
        while pos in offsets:
            pos -= 1
        return pos

    # --- replace ---

    def _update_replace_mode(self, selector_str: str, component: ContextComponent) -> UpdateResult:
        # Assign creation metadata
        _assign_creation_index(self.context, component)
        current_cycle = getattr(self.context, 'current_episode', 0)
        component.metadata.born_cycle = current_cycle

        # Keep original selector for error messages
        original_selector = selector_str
        
        # Resolve target parent container and exact position to replace
        target_parent, exact_position, old_component = self._resolve_replace_target(selector_str)

        # Validate against replacing structural components
        if old_component is not None:
            if isinstance(old_component, MessageContainer) and original_selector in ["(d0,0)", "d0,0"]:
                return UpdateResult(
                    success=False, 
                    errors=["Cannot replace structural MessageContainer at d0,0 - this would break the PACT structure"]
                )
            if isinstance(old_component, (ActiveMessageComponent, MessageTurnComponent)):
                return UpdateResult(
                    success=False,
                    errors=[f"Cannot replace structural component {type(old_component).__name__} - this would break the PACT structure"]
                )

        # Remove from current parent if different
        current_parent_id = getattr(component, 'parent_id', None)
        if current_parent_id and current_parent_id != getattr(target_parent, 'id', None):
            self._remove_from_current_parent(component, current_parent_id)

        # Replace at exact position using direct container operations (remove + insert)
        cont_any = getattr(target_parent, 'content', None)
        if cont_any is None:
            return UpdateResult(success=False, errors=[f"Target {type(target_parent).__name__} has no content"])
        # Remove existing slot content if present
        try:
            if hasattr(cont_any, 'remove'):
                cont_any.remove(exact_position)
            elif hasattr(cont_any, '__delitem__'):
                del cast(Any, cont_any)[exact_position]
        except Exception:
            # If removal fails (e.g., non-existent), continue; insert will validate
            pass
        # Insert new component at the same position
        if not hasattr(cont_any, 'insert'):
            return UpdateResult(success=False, errors=[f"Target {type(target_parent).__name__} content does not support insertion"])
        cont_any.insert(exact_position, component)

        # Inject context reference first (needed for parent_id assignment)
        if hasattr(component, '_inject_context_ref'):
            component._inject_context_ref(self.context)
        component._context_ref = self.context
        
        # Update parent reference and register
        component.parent_id = getattr(target_parent, 'id', None)
        try:
            self.context._registry.register_component(component)
        except Exception:
            pass

        # Return success without aggressive unregister to avoid cascading issues
        return UpdateResult(success=True, updated_components=[component], warnings=[f"Component replaced at position {exact_position}"])

    def _resolve_replace_target(self, selector_str: str) -> Tuple[ContextComponent, int, ContextComponent | None]:
        # Handle bare coordinate format like "d0,0" by adding parentheses
        if selector_str.startswith('d') and ',' in selector_str and not selector_str.startswith('('):
            selector_str = f"({selector_str})"
            
        # Coordinates
        if selector_str.startswith('(') and ')' in selector_str:
            coords = self._parse_coordinates(selector_str.strip('()'))
            if len(coords) == 1:
                depth = coords[0]
                parent = self._get_component_by_depth(depth)
                # Replace requires a specific position; default to 0 if exists
                cont_any = getattr(parent, 'content', None)
                if cont_any is None or not hasattr(cont_any, '__contains__'):
                    raise ValueError(f"Target {type(parent).__name__} has no content")
                pos = 0
                if pos not in cast(Any, cont_any):
                    raise ValueError(f"Position {pos} does not exist in {type(parent).__name__}.content")
                old = cast(Any, cont_any)[pos]
                return parent, pos, old
            if len(coords) == 2:
                depth, pos = coords
                parent = self._get_component_by_depth(depth)
                cont_any = getattr(parent, 'content', None)
                if cont_any is None or not hasattr(cont_any, '__contains__') or pos not in cast(Any, cont_any):
                    raise ValueError(f"Position {pos} does not exist in {type(parent).__name__}.content")
                old = cast(Any, cont_any)[pos]
                return parent, pos, old
            # 3+ dims: navigate to parent and final pos
            parent = self._get_component_by_depth(coords[0])
            for idx in coords[1:-1]:
                cont_any = getattr(parent, 'content', None)
                if cont_any is not None and hasattr(cont_any, '__contains__') and idx in cast(Any, cont_any):
                    parent = cast(Any, cont_any)[idx]
                else:
                    raise ValueError(f"Parent coordinate path doesn't exist: {coords[:-1]}")
            final = coords[-1]
            cont_any = getattr(parent, 'content', None)
            if cont_any is None or not hasattr(cont_any, '__contains__') or final not in cast(Any, cont_any):
                raise ValueError(f"Position {final} does not exist in {type(parent).__name__}.content")
            old = cast(Any, cont_any)[final]
            return parent, final, old

        # Non-coordinate: use Lark to resolve a target node and replace at its parent
        from ..context.selector.parser import LarkPACTParser
        from ..context.selector.engine import LarkPACTSelector
        parser = LarkPACTParser()
        ast = parser.parse(selector_str)
        engine = LarkPACTSelector()
        candidates = engine.select(self.context, ast)
        if not candidates:
            raise ValueError("No targets found for replace")
        target = candidates[0]
        parent_id = getattr(target, 'parent_id', None)
        parent = self.context.get_component_by_id(parent_id) if parent_id else None
        if parent is None or not hasattr(parent, 'content'):
            raise ValueError("Cannot resolve parent container for replace")
        # Find offset of target under parent
        found_pos = None
        cont_any = getattr(parent, 'content', None)
        if cont_any is not None and hasattr(cont_any, '__iter__'):
            for off in cast(Any, cont_any):
                try:
                    if cast(Any, cont_any)[off] is target:
                        found_pos = off
                        break
                except Exception:
                    continue
        if found_pos is None:
            raise ValueError("Unable to locate target position for replace")
        old = cast(Any, cont_any)[found_pos]
        return parent, found_pos, old

    # --- utilities ---

    def _parse_coordinates(self, coord_str: str) -> List[int]:
        if not coord_str.startswith('d'):
            raise ValueError(f"Coordinate must start with 'd': {coord_str}")
        s = coord_str[1:]
        if ',' in s:
            return [int(p.strip()) for p in s.split(',')]
        return [int(s)]

    def _get_component_by_depth(self, depth: int) -> ContextComponent:
        try:
            return self.context.content[depth]
        except (KeyError, ValueError):
            if depth >= 1:
                mt = MessageTurnComponent()
                mt.parent_id = self.context.id
                mt.metadata.ensure_id(mt, node_type="seg", parent_id=self.context.id)
                cast(Any, self.context.content).insert_depth(depth, mt)
                self.context._registry.register_component(mt)
                return mt
            raise ValueError(f"Invalid or uninitialized PACT depth: {depth}")

    def _ensure_canvas_exists(self, depth_component: ContextComponent) -> None:
        cont_any = getattr(depth_component, 'content', None)
        if cont_any is not None and hasattr(cont_any, '__contains__') and 0 in cast(Any, cont_any):
            return
        empty_container = MessageContainer()
        empty_container.parent_id = depth_component.id
        empty_container.metadata.ensure_id(empty_container, node_type="cont", parent_id=depth_component.id)
        empty_text = TextContextComponent(content="")
        empty_text.parent_id = empty_container.id
        # Initialize cores via insert
        empty_container.content.insert(0, empty_text)
        cast(Any, depth_component.content).insert(0, empty_container)
        self.context._registry.register_component(empty_container)
        self.context._registry.register_component(empty_text)

    def _remove_from_current_parent(self, component: ContextComponent, current_parent_id: str) -> None:
        current_parent = self.context.get_component_by_id(current_parent_id)
        if current_parent and hasattr(current_parent, 'content'):
            cont_any = getattr(current_parent, 'content', None)
            if cont_any is not None and hasattr(cont_any, '__iter__'):
                for off in cast(Any, cont_any):
                    try:
                        if cast(Any, cont_any)[off] is component:
                            del cast(Any, cont_any)[off]
                            break
                    except Exception:
                        continue

    def _cascade_unregister_descendants(self, component_id: str) -> None:
        component = self.context.get_component_by_id(component_id)
        if not component:
            self.context._registry.unregister_component(component_id)
            return
        descendant_ids: List[str] = []
        self._collect_descendant_ids(component, descendant_ids)
        for cid in descendant_ids:
            self.context._registry.unregister_component(cid)

    def _collect_descendant_ids(self, component: ContextComponent, acc: List[str]) -> None:
        acc.append(getattr(component, 'id', ''))
        if hasattr(component, 'content'):
            cont_any = getattr(component, 'content', None)
            if cont_any is not None and hasattr(cont_any, '__iter__'):
                for off in cast(Any, cont_any):
                    try:
                        child = cast(Any, cont_any)[off]
                        if hasattr(child, 'id'):
                            self._collect_descendant_ids(child, acc)
                    except Exception:
                        continue


def _assign_creation_index(context: Context, component: ContextComponent) -> None:
    if hasattr(component, 'creation_index') and hasattr(context, 'get_next_creation_index'):
        component.creation_index = context.get_next_creation_index()
