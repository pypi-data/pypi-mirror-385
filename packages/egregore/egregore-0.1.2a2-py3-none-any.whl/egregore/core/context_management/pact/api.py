"""
PACT Facade: Single entry-point insert/update/delete under egregore.pact.

Goal:
- Provide our own API surface within the module for single-point ops.
- Ensure any newly inserted or updated nodes get registered in the
  component registry for O(1) lookups.

This facade delegates structural correctness (coordinate rules, d0
invariants, DepthArray/CoreOffsetArray behavior) to the core Context
handlers, but enforces the registry guarantee as a finalization step.
"""

from __future__ import annotations

from typing import Any, Iterable, List, Tuple, Union

# Import real types — no Any aliasing
from egregore.core.context_management.pact.components.core import PACTCore
from egregore.core.context_management.pact.context.position import Pos
from egregore.core.context_management.pact.context.base import UpdateResult


Selector = Union[str, "Pos", Tuple["Pos", ...]]


class PactFacade:
    """Facade wrapping a Context instance with single-point ops."""

    def __init__(self, context: Any):
        self.context = context

    # --- Public API ---

    def insert(self, selector: Selector, component: Union[PACTCore, str]) -> UpdateResult:
        """Insert component using pact's own inserter and register results."""
        # Use our own handler (no delegation to core Context.insert)
        from .operations.context_insert import PactContextInsertHandler
        handler = PactContextInsertHandler(self.context)
        result: UpdateResult = handler.insert(selector, component)
        if getattr(result, "success", False):
            for inserted in getattr(result, "updated_components", []) or []:
                _register_subtree(self.context, inserted)
        return result

    def update(
        self,
        selector_or_component: Union[str, PACTCore, None] = None,
        *,
        component: Union[PACTCore, None] = None,
        mode: str = "replace",
        content: Union[str, None] = None,
        **kwargs: Any,
    ) -> UpdateResult:
        """Update via pact's own handler, then guarantee registry consistency."""
        from .operations.context_update import PactContextUpdateHandler

        handler = PactContextUpdateHandler(self.context)
        result: UpdateResult = handler.update(
            pos_or_selector=selector_or_component,  # may be str or None
            component=component,
            mode=mode,
            content=content,
            **kwargs,
        )
        if getattr(result, "success", False):
            for updated in getattr(result, "updated_components", []) or []:
                _register_subtree(self.context, updated)
        return result

    def delete(self, selector: Union[str, PACTCore]) -> UpdateResult:
        """Delete via pact's own handler with PACT rules and registry cleanup."""
        from .operations.context_delete import PactContextDeleteHandler
        handler = PactContextDeleteHandler(self.context)
        result: UpdateResult = handler.delete(selector)
        return result


# --- Module-level convenience ---

def insert(context: Any, selector: Selector, component: Union[PACTCore, str]) -> UpdateResult:
    return PactFacade(context).insert(selector, component)


def update(
    context: Any,
    selector_or_component: Union[str, PACTCore, None] = None,
    *,
    component: Union[PACTCore, None] = None,
    mode: str = "replace",
    content: Union[str, None] = None,
    **kwargs: Any,
) -> UpdateResult:
    return PactFacade(context).update(
        selector_or_component, component=component, mode=mode, content=content, **kwargs
    )


def delete(context: Any, selector: Union[str, PACTCore]) -> UpdateResult:
    return PactFacade(context).delete(selector)


# --- Helpers ---

def _as_component(obj: Union[PACTCore, str]) -> PACTCore:
    if isinstance(obj, str):
        from egregore.core.context_management.pact.components.core import TextContent
        return TextContent(content=obj)
    return obj


def _register_subtree(context: Any, component: PACTCore) -> None:
    """Register component and descendants in the context registry."""
    try:
        if hasattr(context, "_registry"):
            context._registry.register_component(component)
    except Exception:
        pass

    # Recurse through typical container shapes
    content = getattr(component, "content", None)
    if content is None:
        return
    try:
        # CoreOffsetArray-like
        if hasattr(content, "__iter__") and hasattr(content, "__getitem__") and not isinstance(content, list):
            for offset in content:  # type: ignore
                try:
                    child = content[offset]
                    if _is_component(child):
                        _register_subtree(context, child)
                except Exception:
                    continue
        # List-like
        elif isinstance(content, list):
            for child in content:
                if _is_component(child):
                    _register_subtree(context, child)
    except Exception:
        pass


def _is_component(obj: Any) -> bool:
    try:
        from egregore.core.context_management.pact.components.core import PACTCore as CC
        return isinstance(obj, CC)
    except Exception:
        # Fallback: check for minimal shape
        return hasattr(obj, "id") and hasattr(obj, "metadata")


def _resolve_targets(context: Any, selector: Union[str, PACTCore]) -> List[PACTCore]:
    if isinstance(selector, str):
        try:
            res = context.select(selector)
            return list(res) if isinstance(res, Iterable) else []
        except Exception:
            return []
    else:
        return [selector]


def _collect_descendant_ids(component: Any, acc: List[str]) -> None:
    cid = getattr(component, "id", None)
    if isinstance(cid, str):
        acc.append(cid)

    content = getattr(component, "content", None)
    if content is None:
        return
    # CoreOffsetArray-like iteration
    try:
        if hasattr(content, "__iter__") and hasattr(content, "__getitem__") and not isinstance(content, list):
            for offset in content:  # type: ignore
                try:
                    child = content[offset]
                    _collect_descendant_ids(child, acc)
                except Exception:
                    continue
        elif isinstance(content, list):
            for child in content:
                _collect_descendant_ids(child, acc)
    except Exception:
        pass
