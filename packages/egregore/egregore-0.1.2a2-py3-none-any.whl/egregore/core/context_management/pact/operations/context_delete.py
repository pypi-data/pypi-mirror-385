"""
PACT Context Delete Handler - Clean PACT-native deletion.

Handles deletion using PACT components only, no legacy architecture references.
Uses the PACT selector system and PACT component hierarchy.
"""

from __future__ import annotations

from typing import Any, List, Union

from ..components.core import PACTCore, MessageTurn, MessageContainer
from ..context.base import Context, UpdateResult


class PactContextDeleteHandler:
    """PACT-native deletion handler using only PACT components and APIs."""
    
    def __init__(self, context: Context):
        self.context = context

    def delete(self, selector: Union[str, PACTCore, List[PACTCore]]) -> UpdateResult:
        """
        Delete components using PACT-native operations.

        Args:
            selector: String selector, component, or list of components to delete

        Returns:
            UpdateResult with success status and updated components
        """
        print(f"[DELETE HANDLER] delete() called with selector: {selector}")
        try:
            # Resolve targets using PACT selector system
            if isinstance(selector, str):
                print(f"[DELETE HANDLER] Selector is string, resolving targets")
                # Validate selector for invalid depths
                if "d-2" in selector or "d-3" in selector or selector.startswith("d-") and not selector.startswith("d-1"):
                    # Extract depth from selector for better error message
                    import re
                    match = re.search(r'd(-?\d+)', selector)
                    if match:
                        depth = int(match.group(1))
                        if depth < -1:
                            return UpdateResult(success=False, errors=[f"Invalid PACT depth: {depth}. Depths must be >= -1."])

                targets = self._resolve_targets_pact(selector)
            elif isinstance(selector, PACTCore):
                targets = [selector]
            else:
                targets = list(selector)

            if not targets:
                return UpdateResult(success=True, warnings=["No targets found to delete"])

            print(f"[DELETE HANDLER] Resolved {len(targets)} targets")
            if len(targets) == 0:
                print(f"[DELETE HANDLER] No targets found - component may already be deleted")
                return UpdateResult(success=True, warnings=[f"No component found with selector: {selector}"])

            # Check for paired tool call/result deletions
            # If deleting a tool call or result, also delete its pair
            targets_with_pairs = self._expand_targets_with_pairs(targets)
            print(f"[DELETE HANDLER] After expanding pairs: {len(targets_with_pairs)} targets")

            # Perform deletions using PACT methods
            deleted_components = []
            for target in targets_with_pairs:
                try:
                    if self._delete_pact_component(target):
                        deleted_components.append(target)
                except Exception as e:
                    continue  # Skip failed deletions

            print(f"[DELETE HANDLER] Successfully deleted {len(deleted_components)} components")
            print(f"[DELETE HANDLER] Calling cleanup with {len(targets_with_pairs)} targets")

            # Clean up registry for any tool pairs that were deleted
            self._cleanup_tool_pair_registry(targets_with_pairs)

            return UpdateResult(
                success=True,
                updated_components=deleted_components
            )

        except Exception as e:
            return UpdateResult(success=False, errors=[str(e)])

    def _resolve_targets_pact(self, selector: str) -> List[PACTCore]:
        """
        Resolve targets using PACT selector system.

        Args:
            selector: PACT selector string

        Returns:
            List of PACTCore components to delete
        """
        try:
            # Normalize selector - wrap bare "d0,1" to "(d0,1)"
            normalized_selector = selector.strip()
            if normalized_selector.startswith('d') and not normalized_selector.startswith('('):
                normalized_selector = f"({normalized_selector})"

            # Use the context's PACT selector
            results = self.context.pact_select(normalized_selector)
            if isinstance(results, list):
                return results
            else:
                return []  # Handle RangeDiffLatestResult case
        except Exception:
            return []

    def _delete_pact_component(self, component: PACTCore) -> bool:
        """
        Delete a PACT component using PACT-native methods.

        Args:
            component: PACTCore component to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            # Special case: MessageTurn at depth level (stored directly in DepthArray)
            if isinstance(component, MessageTurn):
                depth = getattr(component, 'depth', None)
                if depth is not None and depth > 0:  # Don't delete system or active
                    if depth in self.context.content:
                        del self.context.content[depth]
                        return True
                return False

            # Use the component's built-in delete method if available
            if hasattr(component, 'delete') and callable(getattr(component, 'delete')):
                delete_method = getattr(component, 'delete')
                delete_method()
                return True

            # Fallback: remove from parent container
            parent_id = getattr(component, 'parent_id', None)
            if parent_id:
                parent = self.context.get_component_by_id(parent_id)
                if parent and hasattr(parent, 'content'):
                    parent_content = getattr(parent, 'content', None)
                    if parent_content and hasattr(parent_content, 'remove'):
                        offset = getattr(component, 'offset', None)
                        if offset is not None:
                            parent_content.remove(offset)

                            # Remove from node registry (critical for get_component_by_id)
                            component_id = getattr(component, 'id', None)
                            if component_id and component_id in self.context._registry._node_registry:
                                del self.context._registry._node_registry[component_id]

                            # After deletion, check if parent is now empty and should be cleaned up
                            self._cleanup_empty_containers(parent)
                            return True

            return False

        except Exception:
            return False

    def _expand_targets_with_pairs(self, targets: List[PACTCore]) -> List[PACTCore]:
        """
        Expand deletion targets to include paired tool call/result components.

        When deleting a ToolCall, automatically include its ToolResult pair.
        When deleting a ToolResult, automatically include its ToolCall pair.

        Args:
            targets: Original list of components to delete

        Returns:
            Expanded list including paired components
        """
        expanded = list(targets)  # Start with original targets
        seen_ids = {getattr(t, 'id', None) for t in targets}

        for target in targets:
            # Check if this is a tool call or result component
            tool_call_id = getattr(target, 'tool_call_id', None)
            if not tool_call_id:
                continue

            # Try registry lookup first (most common case)
            try:
                pair = self.context._registry.get_tool_pair(tool_call_id)

                if pair:
                    # Registry has the pair - use it
                    call_id, result_id = pair
                    target_id = getattr(target, 'id', None)
                    pair_id = None

                    if target_id == call_id:
                        # Deleting call, need to also delete result
                        pair_id = result_id
                    elif target_id == result_id:
                        # Deleting result, need to also delete call
                        pair_id = call_id

                    # Add the pair if not already in targets
                    if pair_id and pair_id not in seen_ids:
                        pair_component = self.context.get_component_by_id(pair_id)
                        if pair_component:
                            expanded.append(pair_component)
                            seen_ids.add(pair_id)
                else:
                    # No registry entry - fallback to selector search
                    # This handles cases where result exists but wasn't registered
                    # (old data, manual insertion, bugs)
                    target_type = type(target).__name__

                    if 'Call' in target_type:
                        # Deleting a call, search for matching result
                        results = self.context.select(f"{{tool_call_id='{tool_call_id}'}}")
                        for component in results:
                            comp_type = type(component).__name__
                            if 'Result' in comp_type and component.id not in seen_ids:
                                expanded.append(component)
                                seen_ids.add(component.id)
                                break
                    elif 'Result' in target_type:
                        # Deleting a result, search for matching call
                        calls = self.context.select(f"{{tool_call_id='{tool_call_id}'}}")
                        for component in calls:
                            comp_type = type(component).__name__
                            if 'Call' in comp_type and component.id not in seen_ids:
                                expanded.append(component)
                                seen_ids.add(component.id)
                                break

            except Exception:
                # If both registry lookup and selector search fail, continue with normal deletion
                continue

        return expanded

    def _cleanup_tool_pair_registry(self, deleted_components: List[PACTCore]) -> None:
        """
        Clean up registry entries for deleted tool call/result pairs.

        Args:
            deleted_components: List of components that were deleted
        """
        print(f"[DELETE HANDLER DEBUG] _cleanup_tool_pair_registry called with {len(deleted_components)} components")
        # Collect all tool_call_ids that were deleted
        deleted_tool_call_ids = set()

        for component in deleted_components:
            tool_call_id = getattr(component, 'tool_call_id', None)
            print(f"[DELETE HANDLER DEBUG] Component {component.id}: tool_call_id={tool_call_id}")
            if tool_call_id:
                deleted_tool_call_ids.add(tool_call_id)

        print(f"[DELETE HANDLER DEBUG] Found {len(deleted_tool_call_ids)} tool_call_ids: {deleted_tool_call_ids}")

        # Remove registry entries for deleted pairs
        for tool_call_id in deleted_tool_call_ids:
            try:
                # Use unregister_tool_pair to properly clean up both registries
                print(f"[DELETE HANDLER DEBUG] Calling unregister for tool_call_id: {tool_call_id}")
                self.context._registry.unregister_tool_pair(tool_call_id)
                print(f"[DELETE HANDLER DEBUG] Unregister complete")
            except Exception as e:
                # Silently fail registry cleanup
                print(f"[DELETE HANDLER DEBUG] Exception during unregister: {e}")
                pass

    def _cleanup_empty_containers(self, container: PACTCore) -> None:
        """
        Recursively clean up empty containers after deletion.

        If a MessageContainer or MessageTurn is empty after deletion, recursively clean up parent containers.

        Args:
            container: Container to check for cleanup
        """
        try:
            # Check if container is empty
            is_empty = False
            if hasattr(container, 'content'):
                content = getattr(container, 'content')
                # Check if content is empty (CoreOffsetArray has len)
                if hasattr(content, '__len__'):
                    is_empty = len(content) == 0

            if is_empty:
                # Container is empty, check if we should remove it
                parent_id = getattr(container, 'parent_id', None)
                if parent_id:
                    parent = self.context.get_component_by_id(parent_id)

                    # Stop cascade if parent is the Context itself
                    if parent and parent.id == self.context.id:
                        # Don't try to clean up the context
                        return

                    # If parent is a MessageTurn at a depth > 0, remove the entire depth
                    if parent and isinstance(parent, MessageTurn):
                        depth = getattr(parent, 'depth', None)
                        if depth is not None and depth > 0:  # Don't remove system or active
                            # Remove from depth array
                            if depth in self.context.content:
                                del self.context.content[depth]
                    elif parent:
                        # Otherwise, recursively clean up the parent
                        self._cleanup_empty_containers(parent)
        except Exception:
            # Silently fail cleanup, deletion already succeeded
            pass


def delete(context: Context, selector: Union[str, PACTCore]) -> UpdateResult:
    """
    Module-level delete function for PACT operations.
    
    Args:
        context: PACT Context instance
        selector: Component selector
        
    Returns:
        UpdateResult
    """
    handler = PactContextDeleteHandler(context)
    return handler.delete(selector)