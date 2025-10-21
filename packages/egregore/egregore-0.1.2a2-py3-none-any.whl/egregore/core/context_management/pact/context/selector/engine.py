"""
Execution engine for the Lark-based PACT selector AST.

This engine operates directly on the current Context tree implementation
in egregore.core.context_management and returns matching components.
"""

from __future__ import annotations

from typing import Iterable, List, Optional, Set, Union
import re
import logging

logger = logging.getLogger(__name__)

# Use PACT Context and Components
from ..base import Context
from ...components.core import PACTCore
# Constants moved to PACT constants
from ...constants import (
    SELECTOR_TYPE_MAPPING,
    LEGACY_TYPE_ALIASES,
)

from .ast import (
    Attribute,
    Behavior,
    Pseudo,
    SimpleSelector,
    Combinator,
    Selector,
    SelectorUnion,
)

# Build a set of all known component type strings from canonical mapping
_ALL_COMPONENT_TYPES: set[str] = set()
for _v in SELECTOR_TYPE_MAPPING.values():
    _ALL_COMPONENT_TYPES.update(_v)


class LarkPACTSelector:
    """
    Execute parsed selectors on a Context.

    This engine implements a straightforward traversal+filter pipeline:
    - Determine the starting region (spatial, position)
    - Filter candidates by type/id/attributes/behaviors/pseudos
    - Apply combinators to expand to children/descendants and filter again
    """

    def select(self, context: Context, selector_ast: Union[SelectorUnion, Selector, SimpleSelector, str]) -> List[PACTCore]:
        # Allow passing a raw string by importing the parser lazily
        if isinstance(selector_ast, str):
            from .parser import LarkPACTParser  # lazy to avoid import cycle
            selector_ast = LarkPACTParser().parse(selector_ast)

        if isinstance(selector_ast, SelectorUnion):
            seen: Set[str] = set()
            out: List[PACTCore] = []
            for s in selector_ast.selectors:
                res = self._select_single(context, s)
                if getattr(s, 'controls', None):
                    res = self._apply_controls(res, s.controls)
                for comp in res:
                    cid = getattr(comp, "id", None)
                    if cid and cid not in seen:
                        out.append(comp)
                        seen.add(cid)
            return out
        elif isinstance(selector_ast, Selector):
            results = self._select_single(context, selector_ast)
            if selector_ast.controls:
                results = self._apply_controls(results, selector_ast.controls)
            return results
        elif isinstance(selector_ast, SimpleSelector):
            return self._apply_simple(context, [context], selector_ast)
        else:
            return []

    # ----- selection pipeline -----

    def _select_single(self, context: Context, selector: Selector) -> List[PACTCore]:
        # Temporal union handling for @history and @t*
        head_temporal = getattr(selector.head, 'temporal', None)
        head_tr = getattr(selector.head, 'temporal_range', None)
        if head_tr is not None:
            kind, start, end = head_tr
            return self._execute_temporal_range(context, selector, kind, start, end)
        if head_temporal in {"history", "hist"}:
            # Union across history only (exclude current)
            cleared_head = SimpleSelector(
                spatial=selector.head.spatial,
                temporal=None,
                depth_position=selector.head.depth_position,
                depth_position_set=selector.head.depth_position_set,
                depth_scope=selector.head.depth_scope,
                type_name=selector.head.type_name,
                type_tags=list(selector.head.type_tags or []),
                tags=list(selector.head.tags or []),
                id_selector=selector.head.id_selector,
                attributes=list(selector.head.attributes or []),
                behaviors=list(selector.head.behaviors or []),
                pseudos=list(selector.head.pseudos or []),
                wildcard=selector.head.wildcard,
            )
            sel = Selector(head=cleared_head, chain=list(selector.chain), scope=selector.scope)

            results: List[PACTCore] = []
            seen: Set[str] = set()

            hist = None
            try:
                if hasattr(context, 'context_manager') and context.context_manager is not None:
                    hist = getattr(context.context_manager, 'context_history', None)
            except Exception:
                hist = None

            if hist is not None and hasattr(hist, 'snapshots'):
                try:
                    count = len(hist.snapshots)
                except Exception:
                    count = 0
                for offset in range(1, count + 1):
                    try:
                        snap_ctx = hist.get_snapshot_by_offset(offset)
                    except Exception:
                        snap_ctx = None
                    if snap_ctx is None:
                        continue
                    for comp in self._select_single(snap_ctx, sel):
                        cid = getattr(comp, 'id', None)
                        if cid and cid not in seen:
                            seen.add(cid)
                            results.append(comp)
            return results

        if head_temporal == "t*":
            # Build selector without temporal on head
            cleared_head = SimpleSelector(
                spatial=selector.head.spatial,
                temporal=None,
                depth_position=selector.head.depth_position,
                depth_position_set=selector.head.depth_position_set,
                depth_scope=selector.head.depth_scope,
                type_name=selector.head.type_name,
                type_tags=list(selector.head.type_tags or []),
                tags=list(selector.head.tags or []),
                id_selector=selector.head.id_selector,
                attributes=list(selector.head.attributes or []),
                behaviors=list(selector.head.behaviors or []),
                pseudos=list(selector.head.pseudos or []),
                wildcard=selector.head.wildcard,
            )
            sel = Selector(head=cleared_head, chain=list(selector.chain), scope=selector.scope)

            results: List[PACTCore] = []
            seen: Set[str] = set()

            # Include current context for @t*
            if head_temporal == "t*":
                for comp in self._select_single(context, sel):
                    cid = getattr(comp, 'id', None)
                    if cid and cid not in seen:
                        seen.add(cid)
                        results.append(comp)

            # Iterate history if available
            hist = None
            try:
                if hasattr(context, 'context_manager') and context.context_manager is not None:
                    hist = getattr(context.context_manager, 'context_history', None)
            except Exception:
                hist = None

            if hist is not None and hasattr(hist, 'snapshots'):
                try:
                    count = len(hist.snapshots)
                except Exception:
                    count = 0
                for offset in range(1, count + 1):
                    try:
                        snap_ctx = hist.get_snapshot_by_offset(offset)
                    except Exception:
                        snap_ctx = None
                    if snap_ctx is None:
                        continue
                    for comp in self._select_single(snap_ctx, sel):
                        cid = getattr(comp, 'id', None)
                        if cid and cid not in seen:
                            seen.add(cid)
                            results.append(comp)
            # If no history, just return current selection (for @t*) or empty for @history
            return results

        # Resolve single-snapshot temporal addressing on head into a chain root
        chain_root: Context = context
        if head_temporal and head_temporal not in {"history", "t*"}:
            snap = None
            if head_temporal.startswith('t'):
                snap = f"@{head_temporal}"
            # cycle tokens removed (@cN no longer supported)
            if snap:
                try:
                    chain_root = context._resolve_snapshot(snap)
                except Exception:
                    chain_root = context

        # Start from spatial/position head (expand from chain root)
        candidates: List[PACTCore] = self._apply_simple(chain_root, [chain_root], selector.head, expand_descendants=True)

        # Traverse chain
        for comb, simple in selector.chain:
            next_candidates: List[PACTCore] = []
            search_roots: List[PACTCore] = []

            for cand in candidates:
                if comb.kind == ">":
                    search_roots.extend(self._get_direct_children(cand))
                elif comb.kind == "?":
                    # single-hop deep search (direct children)
                    search_roots.extend(self._get_direct_children(cand))
                else:  # "??" recursive deep search
                    search_roots.extend(self._get_all_descendants(cand, limit=comb.within))

            # Apply next simple selector to the collected roots
            next_candidates = self._apply_simple(chain_root, search_roots, simple, expand_descendants=False)
            candidates = next_candidates

        # Apply optional chain scope filter (e.g., d1..d*)
        if selector.scope is not None and candidates:
            candidates = self._filter_by_chain_scope(chain_root, candidates, selector.scope)

        return candidates

    def _apply_controls(self, nodes: List[PACTCore], controls) -> List[PACTCore]:
        mode = getattr(controls, 'mode', None)
        if mode:
            m = mode.lower()
            if m not in {'all', 'latest'}:
                raise ValueError(f"Unknown mode '{mode}'. Expected 'all' or 'latest'.")
        if mode and mode.lower() == 'latest':
            seen = set()
            out = []
            for n in nodes:
                key = self._semantic_key(n)
                if key not in seen:
                    seen.add(key)
                    out.append(n)
            nodes = out
        offset = getattr(controls, 'offset', None) or 0
        limit = getattr(controls, 'limit', None)
        if offset:
            nodes = nodes[offset:]
        if limit is not None:
            nodes = nodes[:limit]
        return nodes

    def _semantic_key(self, n: PACTCore) -> str:
        if hasattr(n, 'key') and getattr(n, 'key'):
            return f"key:{getattr(n,'key')}"
        try:
            if hasattr(n, 'metadata') and hasattr(n.metadata, 'props') and n.metadata.props.get('key'):
                return f"key:{n.metadata.props.get('key')}"
        except Exception:
            pass
        return f"id:{getattr(n,'id', '')}"

    def _execute_temporal_range(self, context: Context, selector: Selector, kind: str, start: int, end: int) -> List[PACTCore]:
        cleared_head = SimpleSelector(
            spatial=selector.head.spatial,
            temporal=None,
            temporal_range=None,
            depth_position=selector.head.depth_position,
            depth_position_set=selector.head.depth_position_set,
            depth_scope=selector.head.depth_scope,
            type_name=selector.head.type_name,
            type_tags=list(selector.head.type_tags or []),
            tags=list(selector.head.tags or []),
            id_selector=selector.head.id_selector,
            attributes=list(selector.head.attributes or []),
            behaviors=list(selector.head.behaviors or []),
            pseudos=list(selector.head.pseudos or []),
            wildcard=selector.head.wildcard,
        )
        # Don't pass controls through - they will be applied at the top level after temporal range execution completes
        # Filter out spurious empty chain elements that may be created by control parsing bugs
        filtered_chain = []
        for comb, simple in selector.chain:
            # Keep chain element if it has any meaningful content
            if (simple.depth_position or simple.depth_position_set or simple.type_name or
                simple.tags or simple.id_selector or simple.attributes or simple.behaviors or
                simple.pseudos or simple.wildcard or simple.spatial):
                filtered_chain.append((comb, simple))
        sel = Selector(head=cleared_head, chain=filtered_chain, scope=selector.scope, controls=None)
        results: List[PACTCore] = []
        seen: Set[str] = set()

        if kind == 't':
            step = 1 if end >= start else -1
            for tval in range(start, end + step, step):
                if tval == 0:
                    snap_ctx = context
                else:
                    try:
                        snap_ctx = context._resolve_snapshot(f"@t{tval}")
                    except Exception:
                        snap_ctx = None
                if snap_ctx is None:
                    continue
                for comp in self._select_single(snap_ctx, sel):
                    cid = getattr(comp, 'id', None)
                    if cid and cid not in seen:
                        seen.add(cid)
                        results.append(comp)
            return results

        # unsupported kind (cycles removed)
        return []

    def _apply_simple(self, context: Context, bases: List[PACTCore], simple: SimpleSelector, *, expand_descendants: bool) -> List[PACTCore]:
        # Temporal snapshot resolution (@t-1, @cN, history)
        if simple.temporal:
            # Map tokens to Context._resolve_snapshot format
            token = simple.temporal
            snap = None
            if token in {"history", "hist"}:
                # @history union handled at _select_single; ignore here
                snap = None
            elif token.startswith("@t") or token.startswith("t"):
                # Token may already have @ prefix from parser
                snap = token if token.startswith("@") else f"@{token}"
            # cycle tokens removed (@cN no longer supported)
            if snap:
                try:
                    resolved_context = context._resolve_snapshot(snap)
                    context = resolved_context
                    bases = [context]
                except Exception as e:
                    # Temporal resolution failed - continue with current context
                    pass

        # Spatial base narrowing
        bases = self._apply_spatial(context, bases, simple)

        # Depth position navigation (single or set) with coordinate range expansion
        # CRITICAL: Resolve depth/position BEFORE prefilter so registry filtering respects depth boundaries
        if simple.depth_position:
            bases = self._resolve_positions_to_components(context, simple.depth_position)
        elif simple.depth_position_set:
            new_bases: List[PACTCore] = []
            for coords in simple.depth_position_set:
                comps = self._resolve_positions_to_components(context, coords)
                if comps:
                    new_bases.extend(comps)
            bases = new_bases
        elif simple.depth_scope is not None:
            # Navigate to each depth in the scope without additional indices
            new_bases: List[PACTCore] = []
            # Determine end of range (resolve '*')
            start = simple.depth_scope.start
            end = simple.depth_scope.end
            if end == "*":
                try:
                    max_depth = context._depths.get_max_depth()
                except Exception:
                    max_depth = start
                end_val = max_depth if isinstance(max_depth, int) else start
            else:
                end_val = end if isinstance(end, int) else start
            step = 1 if end_val >= start else -1
            for d in range(start, end_val + step, step):
                target = self._navigate_position(context, [d])
                if target is not None:
                    new_bases.append(target)
            bases = new_bases

        # Registry fast-path prefilter for common selectors (AFTER depth resolution)
        pre = self._prefilter_with_registry(context, bases, simple, expand_descendants)
        if pre is not None:
            return pre

        # Decide candidate expansion strategy
        candidates: List[PACTCore]
        has_criteria = (
            simple.wildcard or simple.type_name or simple.id_selector or
            (simple.attributes and len(simple.attributes) > 0) or
            (simple.behaviors and len(simple.behaviors) > 0) or
            (simple.pseudos and len(simple.pseudos) > 0) or
            (simple.tags and len(simple.tags) > 0)
        )

        if expand_descendants:
            # First head: allow full-tree expansion from bases
            if simple.wildcard:
                cands: List[PACTCore] = []
                for b in bases:
                    cands.extend(self._get_all_descendants(b))
                    if b not in cands:
                        cands.append(b)
                candidates = cands
            elif has_criteria:
                cands = []
                for b in bases:
                    cands.append(b)
                    cands.extend(self._get_all_descendants(b))
                candidates = cands
            else:
                # No criteria: keep bases only (e.g., '^ah' before a combinator)
                candidates = list(bases)
        else:
            # In chained steps: never auto-expand; use current scope and filter
            candidates = list(bases)

        # If type_name is non-canonical (e.g., .summary), treat as nodeType sugar
        tn = simple.type_name
        if tn and (tn not in SELECTOR_TYPE_MAPPING and not _ALL_COMPONENT_TYPES.__contains__(tn)):
            # Convert to attribute filter and clear type_name
            derived_attr = Attribute(name="nodeType", operator="=", value=tn)
            simple = SimpleSelector(
                spatial=simple.spatial,
                temporal=simple.temporal,
                depth_position=simple.depth_position,
                type_name=None,
                type_tags=list(simple.type_tags or []),
                id_selector=simple.id_selector,
                attributes=list(simple.attributes) + [derived_attr],
                behaviors=list(simple.behaviors),
                pseudos=list(simple.pseudos),
                wildcard=simple.wildcard,
            )

        # Filters
        candidates = self._filter_by_type(candidates, simple.type_name)
        candidates = self._filter_by_id(candidates, simple.id_selector)
        # Type sugar: .block:tag -> [nodeType='tag']
        derived_attrs = [Attribute(name="nodeType", operator="=", value=tag) for tag in (simple.type_tags or [])]
        combined_attrs = list(simple.attributes) + derived_attrs
        # Tag anchors (+tag)
        candidates = self._filter_by_tags(candidates, simple.tags)
        candidates = self._filter_by_attributes(candidates, combined_attrs)
        candidates = self._filter_by_behaviors(candidates, simple.behaviors)
        candidates = self._filter_by_pseudos(context, candidates, simple.pseudos)

        return candidates

    def _prefilter_with_registry(self, context: Context, bases: List[PACTCore], simple: SimpleSelector, expand_descendants: bool) -> Optional[List[PACTCore]]:
        """Use ContextRegistry indexes to prefilter candidates for common cases.

        Only applied when expanding from the full context (root) or a known
        depth root; otherwise falls back to traversal. Preserves canonical
        ordering and enforces subtree constraints when spatial bases are used.
        """
        try:
            # Must be head-of-chain scan
            if not expand_descendants:
                return None
            # Establish base roots for subtree restriction
            base_roots: List[PACTCore] = []
            if bases:
                base_roots = list(bases)
            else:
                base_roots = [context]

            reg = getattr(context, '_registry', None)
            if reg is None:
                return None

            candidate_ids: Optional[Set[str]] = None

            # Key fast-path (#key)
            if simple.id_selector:
                cid = reg.find_by_key(simple.id_selector)
                comps: List[PACTCore] = []
                if cid:
                    c = context.get_component_by_id(cid)
                    if c is not None and self._within_bases(context, c, base_roots):
                        comps = [c]
                return comps

            # Type fast-path
            if simple.type_name:
                tn = LEGACY_TYPE_ALIASES.get(simple.type_name, simple.type_name)
                ids = set(reg.find_by_type(tn))
                # If canonical type, also include mapped underlying types
                mapped = SELECTOR_TYPE_MAPPING.get(tn)
                if mapped:
                    for mt in mapped:
                        ids |= set(reg.find_by_type(mt))
                if ids:
                    candidate_ids = ids

            # Tags prefilter
            if getattr(simple, 'tags', None):
                for tag in (simple.tags or []):
                    tag_ids = reg.find_by_tag(tag)
                    if candidate_ids is None:
                        candidate_ids = set(tag_ids)
                    else:
                        candidate_ids &= set(tag_ids)
                    if not candidate_ids:
                        return []

            # Attribute prefilter: nodeType and role equality
            nt_values: List[str] = []
            role_values: List[str] = []
            for a in (simple.attributes or []):
                if a.name == 'nodeType' and a.operator == '=' and isinstance(a.value, (str,)):
                    nt_values.append(str(a.value))
                if a.name == 'role' and a.operator == '=' and isinstance(a.value, (str,)):
                    role_values.append(str(a.value))
            for nt in nt_values:
                nt_ids = reg.find_by_node_type(nt)
                if candidate_ids is None:
                    candidate_ids = set(nt_ids)
                else:
                    candidate_ids &= set(nt_ids)
                if not candidate_ids:
                    return []
            for rv in role_values:
                rv_ids = reg.find_by_role(rv)
                if candidate_ids is None:
                    candidate_ids = set(rv_ids)
                else:
                    candidate_ids &= set(rv_ids)
                if not candidate_ids:
                    return []

            # Behavior prefilter: ttl/cad equality
            ttl_eq: List[int] = []
            cad_eq: List[int] = []
            for b in (simple.behaviors or []):
                if b.name in {'ttl'} and b.operator == '=' and isinstance(b.value, (int, float)):
                    ttl_eq.append(int(b.value))
                if b.name in {'cad', 'cadence'} and b.operator == '=' and isinstance(b.value, (int, float)):
                    cad_eq.append(int(b.value))
                if b.name == 'ephemeral' and not b.operator:
                    ttl_eq.append(1)
                if b.name == 'sticky' and not b.operator:
                    ttl_eq.append(1)
                    cad_eq.append(1)
            for tv in ttl_eq:
                t_ids = reg.find_by_ttl(tv)
                if candidate_ids is None:
                    candidate_ids = set(t_ids)
                else:
                    candidate_ids &= set(t_ids)
                if not candidate_ids:
                    return []
            for cv in cad_eq:
                c_ids = reg.find_by_cad(cv)
                if candidate_ids is None:
                    candidate_ids = set(c_ids)
                else:
                    candidate_ids &= set(c_ids)
                if not candidate_ids:
                    return []

            if candidate_ids is None:
                return None  # no registry-based narrowing possible

            # Materialize components and enforce base subtree restriction
            comps: List[PACTCore] = []
            for cid in candidate_ids:
                c = context.get_component_by_id(cid)
                if c is None:
                    continue
                if self._within_bases(context, c, base_roots):
                    comps.append(c)
            # Canonical order
            comps = self._canonical_order_components(comps)
            return comps
        except Exception:
            return None

    def _within_bases(self, context: Context, node: PACTCore, bases: List[PACTCore]) -> bool:
        # If any base is the whole context, always passes
        if any(b is context for b in bases):
            return True
        for b in bases:
            try:
                if self._in_subtree(b, node):
                    return True
            except Exception:
                continue
        return False

    def _canonical_order_components(self, nodes: List[PACTCore]) -> List[PACTCore]:
        def key(n):
            off = getattr(n, 'offset', 0)
            created_at_ns = 0
            creation_index = 0
            cid = ''
            try:
                if hasattr(n, 'metadata'):
                    created_at_ns = getattr(n.metadata, 'created_at_ns', 0)
                    creation_index = getattr(n.metadata, 'creation_index', 0)
                    cid = getattr(n.metadata, 'id', '')
            except Exception:
                pass
            return (off, created_at_ns, creation_index, cid)
        return sorted(nodes, key=key)

    # ----- spatial/position -----

    def _apply_spatial(self, context: Context, bases: List[PACTCore], simple: SimpleSelector) -> List[PACTCore]:
        if not simple.spatial:
            return bases
        if simple.spatial == "sys":
            return [context.system_header]
        elif simple.spatial == "ah":
            return [context.active_message]
        elif simple.spatial == "seq":
            # Treat sequence as the whole context; downstream type filters will scope
            return [context]
        return bases

    def _navigate_position(self, context: Context, coords: List[int]) -> Optional[PACTCore]:
        # coords: [depth, idx1, idx2, ...]
        if not coords:
            return None
        depth = coords[0]
        try:
            if depth == -1:
                current: PACTCore = context.system_header
            elif depth == 0:
                current = context.active_message
            elif depth >= 1:
                # DepthArray provides index access by depth for conversation segments
                current = context.conversation_history[depth]
            else:
                return None
        except Exception:
            return None

        # Traverse child indexes if provided
        for index in coords[1:]:
            children = self._get_direct_children(current)
            if 0 <= index < len(children):
                current = children[index]
            else:
                return None
        return current

    # ----- traversal helpers -----

    def _get_direct_children(self, component: PACTCore) -> List[PACTCore]:
        if hasattr(component, "content"):
            content = getattr(component, "content")
            # DepthArray/CoreOffsetArray expose traversal helpers
            if hasattr(content, "get_all_items"):
                try:
                    return list(content.get_all_items())
                except Exception:
                    pass
            if isinstance(content, list):
                return list(content)
        # metadata children as fallback
        if hasattr(component, "metadata") and hasattr(component.metadata, "children"):
            try:
                return list(component.metadata.children)
            except Exception:
                return []
        return []

    def _resolve_positions_to_components(self, context: Context, coords: List[object]) -> List[PACTCore]:
        out: List[PACTCore] = []
        vectors = self._expand_coordinate_vector(context, coords)
        for vec in vectors:
            target = self._navigate_position(context, vec)
            if target is not None:
                out.append(target)
        return out

    def _expand_coordinate_vector(self, context: Context, coords: List[object]) -> List[List[int]]:
        if not coords:
            return []
        # Handle DEPTH_RANGE tuple at start
        if isinstance(coords[0], tuple) and len(coords[0]) == 3 and coords[0][0] == 'DEPTH_RANGE':
            start, end = coords[0][1], coords[0][2]
            # Resolve end depth (could be "*" for wildcard)
            max_depth = context.content.max_depth if hasattr(context, 'content') else 0
            end_depth = max_depth if end == "*" else end
            # Expand to multiple coordinates
            results = []
            for d in range(start, end_depth + 1):
                expanded_coords = [d] + list(coords[1:])
                results.extend(self._expand_coordinate_vector(context, expanded_coords))
            return results
        # Copy and analyze
        if not isinstance(coords[0], int):
            return []
        depth = coords[0]
        # Find last dim
        if len(coords) == 1:
            return [coords]  # depth only
        prefix_dims: List[int] = []
        for i, d in enumerate(coords):
            if i == 0:
                prefix_dims.append(d)
                continue
            if i < len(coords) - 1:
                if not isinstance(d, int):
                    raise ValueError("Offset range tokens are only allowed in the last coordinate dimension")
                prefix_dims.append(d)
            else:
                last = d
                parent = self._navigate_position(context, prefix_dims)
                if parent is None:
                    return []
                offsets: List[int] = []
                try:
                    if hasattr(parent, 'content') and hasattr(parent.content, 'get_offsets'):
                        offsets = list(parent.content.get_offsets())
                except Exception:
                    offsets = []
                if not offsets:
                    return []
                lo = min(offsets)
                hi = max(offsets)
                def coerce(v):
                    if isinstance(v, str):
                        v = v.lower()
                        if v in ('first','min'):
                            return lo
                        if v in ('last','max'):
                            return hi
                        if v == 'all':
                            return (lo, hi)
                    return int(v)
                expanded: List[List[int]] = []
                if isinstance(last, tuple) and len(last) == 3 and last[0] == 'IDX_RANGE':
                    a, b = last[1], last[2]
                    if isinstance(a, str) and a.lower() == 'all' or isinstance(b, str) and b.lower() == 'all':
                        raise ValueError("'all' not valid inside a range; use 'all' alone or min/max")
                    sa = coerce(a)
                    sb = coerce(b)
                    start, end = (sa, sb) if sa <= sb else (sb, sa)
                    for k in sorted(off for off in offsets if start <= off <= end):
                        expanded.append(prefix_dims + [k])
                elif isinstance(last, str):
                    token = last.lower()
                    if token == 'all':
                        for k in sorted(offsets):
                            expanded.append(prefix_dims + [k])
                    elif token in ('min','first','max','last'):
                        k = coerce(token)
                        if k in offsets:
                            expanded.append(prefix_dims + [k])
                elif isinstance(last, int):
                    if last in offsets:
                        expanded.append(prefix_dims + [last])
                else:
                    return []
                return expanded
        # Fallback single vector if no last token/range
        if all(isinstance(x, int) for x in coords):
            return [coords]  # type: ignore
        return []

    def _navigate_position(self, context: Context, coords: List[int]) -> Optional[PACTCore]:
        # coords: [depth, idx1, idx2, ...]
        if not coords:
            return None
        depth = coords[0]
        try:
            if depth == -1:
                current: PACTCore = context.system_header
            elif depth == 0:
                current = context.active_message
            elif depth >= 1:
                # Use DepthArray indexing by depth
                current = context.conversation_history[depth]
            else:
                return None
        except Exception:
            return None

        # Traverse child indexes if provided
        for index in coords[1:]:
            if hasattr(current, 'content') and hasattr(current.content, '__contains__') and hasattr(current.content, '__getitem__'):
                try:
                    if index in current.content:
                        current = current.content[index]
                    else:
                        return None
                except Exception:
                    return None
            else:
                children = self._get_direct_children(current)
                if 0 <= index < len(children):
                    current = children[index]
                else:
                    return None
        return current

    def _get_all_descendants(self, component: PACTCore, limit: Optional[int] = None) -> List[PACTCore]:
        # Determine if we're starting from a MessageTurn to enforce depth boundaries
        from ...components.core import MessageTurn
        starting_depth = None
        if isinstance(component, MessageTurn):
            starting_depth = getattr(component, 'depth', None)

        results: List[PACTCore] = []
        frontier: List[tuple[PACTCore, int]] = [(component, 0)]
        while frontier:
            node, depth = frontier.pop(0)
            children = self._get_direct_children(node)
            for child in children:
                # DEPTH BOUNDARY CHECK: Stop traversal at MessageTurns with different depths
                if isinstance(child, MessageTurn) and starting_depth is not None:
                    child_depth = getattr(child, 'depth', None)
                    if child_depth is not None and child_depth != starting_depth:
                        continue  # Don't traverse into MessageTurns at different depths

                results.append(child)
                if limit is None or depth + 1 < limit:
                    frontier.append((child, depth + 1))
        return results

    # ----- filters -----

    def _filter_by_type(self, nodes: List[PACTCore], type_name: Optional[str]) -> List[PACTCore]:
        if not type_name:
            return nodes

        tn = LEGACY_TYPE_ALIASES.get(type_name, type_name)
        mapped = SELECTOR_TYPE_MAPPING.get(tn)

        out: List[PACTCore] = []
        for n in nodes:
            comp_type = getattr(n, "type", None)
            if not comp_type:
                continue
            if mapped is not None:
                if comp_type in mapped:
                    out.append(n)
            else:
                if comp_type == tn:
                    out.append(n)
        return out

    def _filter_by_id(self, nodes: List[PACTCore], id_selector: Optional[str]) -> List[PACTCore]:
        """
        PACT semantics: #key targets a semantic key, not component IDs.
        Matches against component.key or metadata.props['key'] when present.
        """
        if not id_selector:
            return nodes
        out: List[PACTCore] = []
        for n in nodes:
            # direct component key field
            if hasattr(n, "key") and getattr(n, "key") == id_selector:
                out.append(n)
                continue
            # metadata.props key
            if hasattr(n, "metadata") and hasattr(n.metadata, "props"):
                if n.metadata.props.get("key") == id_selector:
                    out.append(n)
                    continue
        return out

    def _get_attr_value(self, n: PACTCore, name: str):
        if name == "nodeType":
            # First check metadata.kind (legacy support for nodeType)
            if hasattr(n, "metadata"):
                md = getattr(n, "metadata")
                kind_val = getattr(md, "kind", None)
                if kind_val is not None:
                    return kind_val
            # Fallback to component's type field (PACT-compliant)
            # type is a ClassVar on component classes
            return getattr(n, "type", None)
        if hasattr(n, name):
            return getattr(n, name)
        if hasattr(n, "metadata"):
            md = getattr(n, "metadata")
            if hasattr(md, name):
                return getattr(md, name)
            if hasattr(md, "props") and name in md.props:
                return md.props[name]
            if name == "created_at_ns":
                return md.created_at_ns
            if name == "created_at_iso":
                return md.created_at_iso
            if name == "role":
                return getattr(md, "role", None)
            if name == "kind":
                # Legacy: kind is deprecated in PACT spec, use nodeType instead
                return getattr(md, "kind", None)
        return None

    def _compare(self, actual, op: str, expected) -> bool:
        try:
            if op == "=":
                return actual == expected
            if op == "!=":
                return actual != expected
            if op == "<":
                return actual < expected
            if op == "<=":
                return actual <= expected
            if op == ">":
                return actual > expected
            if op == ">=":
                return actual >= expected
            if op == "~=":
                # Regex search on stringified actual
                try:
                    pattern = re.compile(str(expected))
                except re.error:
                    return False
                return bool(pattern.search("" if actual is None else str(actual)))
        except Exception:
            pass
        # Fallback to string compare for equality/inequality
        if op == "=":
            return str(actual) == str(expected)
        if op == "!=":
            return str(actual) != str(expected)
        return False

    def _filter_by_attributes(self, nodes: List[PACTCore], attrs: List[Attribute]) -> List[PACTCore]:
        if not attrs:
            return nodes
        out: List[PACTCore] = []
        for n in nodes:
            ok = True
            for a in attrs:
                v = self._get_attr_value(n, a.name)
                if v is None or not self._compare(v, a.operator, a.value):
                    ok = False
                    break
            if ok:
                out.append(n)
        return out

    def _filter_by_behaviors(self, nodes: List[PACTCore], behaviors: List[Behavior]) -> List[PACTCore]:
        if not behaviors:
            return nodes
        out: List[PACTCore] = []
        for n in nodes:
            ok = True
            for b in behaviors:
                if b.name in {"ttl", "cad", "cadence"}:
                    attr = "cad" if b.name == "cadence" else b.name
                    v = getattr(n, attr, None)
                    if v is None:
                        ok = False
                        break
                    if b.operator:
                        if not self._compare(v, b.operator, b.value):
                            ok = False
                            break
                elif b.name == "ephemeral":
                    ttl_val = getattr(n, "ttl", None)
                    if b.operator:
                        # Interpret truthy/falsey values
                        expect_true = str(b.value).lower() in {"1", "true", "yes"}
                        is_ephemeral = (ttl_val == 1)
                        if b.operator == "=":
                            if is_ephemeral != expect_true:
                                ok = False
                                break
                        elif b.operator == "!=":
                            if is_ephemeral == expect_true:
                                ok = False
                                break
                        else:
                            # Unsupported operator for boolean behavior
                            ok = False
                            break
                    else:
                        if ttl_val != 1:
                            ok = False
                            break
                elif b.name == "sticky":
                    ttl_val = getattr(n, "ttl", None)
                    cad_val = getattr(n, "cad", None)
                    is_sticky = (ttl_val == 1 and cad_val == 1)
                    if b.operator:
                        expect_true = str(b.value).lower() in {"1", "true", "yes"}
                        if b.operator == "=":
                            if is_sticky != expect_true:
                                ok = False
                                break
                        elif b.operator == "!=":
                            if is_sticky == expect_true:
                                ok = False
                                break
                        else:
                            ok = False
                            break
                    else:
                        if not is_sticky:
                            ok = False
                            break
                else:
                    # Unknown behavior - treat as non-match for safety
                    ok = False
                    break
            if ok:
                out.append(n)
        return out

    def _filter_by_tags(self, nodes: List[PACTCore], tags: Optional[List[str]]) -> List[PACTCore]:
        if not tags:
            return nodes
        required: Set[str] = set(tags)
        out: List[PACTCore] = []
        for n in nodes:
            found: Set[str] = set()
            # Prefer metadata.props['tags'] if present
            try:
                if hasattr(n, "metadata") and hasattr(n.metadata, "props"):
                    t = n.metadata.props.get("tags")
                    if isinstance(t, list):
                        found.update(str(x) for x in t)
                    elif isinstance(t, str):
                        # Split on commas/space
                        for part in re.split(r"[\s,]+", t.strip()):
                            if part:
                                found.add(part)
            except Exception:
                pass
            # Also support direct .tags attribute if exists
            if hasattr(n, "tags"):
                try:
                    iter_tags = getattr(n, "tags")
                    if isinstance(iter_tags, (list, tuple, set)):
                        found.update(str(x) for x in iter_tags)
                except Exception:
                    pass
            if required.issubset(found):
                out.append(n)
        return out

    def _filter_by_chain_scope(self, context: Context, nodes: List[PACTCore], scope) -> List[PACTCore]:
        start = getattr(scope, "start", None)
        end = getattr(scope, "end", None)
        if start is None:
            return nodes
        # Resolve '*' using DepthArray if needed
        if end == "*":
            try:
                max_depth = context._depths.get_max_depth()
            except Exception:
                max_depth = start
            end_val = max_depth if isinstance(max_depth, int) else start
        else:
            end_val = end if isinstance(end, int) else start
        lo, hi = (start, end_val) if start <= end_val else (end_val, start)
        out: List[PACTCore] = []
        for n in nodes:
            d = self._component_depth(context, n)
            if lo <= d <= hi:
                out.append(n)
        return out

    def _filter_by_pseudos(self, context: Context, nodes: List[PACTCore], pseudos: List[Pseudo]) -> List[PACTCore]:
        if not pseudos:
            return nodes
        res = nodes
        for p in pseudos:
            name = p.name
            if name == "pre":
                res = [n for n in res if getattr(n, "offset", 0) < 0]
            elif name == "core":
                res = [n for n in res if getattr(n, "offset", 0) == 0]
            elif name == "post":
                res = [n for n in res if getattr(n, "offset", 0) > 0]
            elif name == "first":
                res = res[:1] if res else []
            elif name == "last":
                res = res[-1:] if res else []
            elif name == "nth":
                if p.args:
                    try:
                        k = int(p.args[0]) - 1
                        res = [res[k]] if 0 <= k < len(res) else []
                    except Exception:
                        res = []
                else:
                    res = []
            elif name == "depth":
                res = self._filter_by_depth(context, res, p.args)
            # else: unknown pseudos are ignored (no-op)
        return res

    def _component_depth(self, context: Context, n: PACTCore) -> int:
        # 1) Explicit depth field
        if hasattr(n, "depth") and getattr(n, "depth") is not None:
            try:
                # Only trust depth for structural containers/segments
                t = getattr(n, 'type', None)
                if t in {"system_header", "active_message", "message_turn", "client_message", "provider_message"}:
                    return int(getattr(n, "depth"))
            except Exception:
                pass

        # 2) Region-based approximation via subtree checks
        try:
            if self._in_subtree(context.system_header, n):
                return -1
        except Exception:
            pass
        try:
            if self._in_subtree(context.active_message, n):
                return 0
        except Exception:
            pass
        # Check any historical segment → treat as depth >= 1
        try:
            for i in range(1, len(context._depths._conversation_segments) + 1):
                try:
                    seg = context._depths[i]
                except Exception:
                    continue
                if self._in_subtree(seg, n):
                    return 1
        except Exception:
            pass

        # 3) Fallback: unknown depth
        return 0

    def _in_subtree(self, root: PACTCore, target: PACTCore) -> bool:
        if root is target:
            return True
        # BFS using direct children
        queue = list(self._get_direct_children(root))
        tid = getattr(target, 'id', None)
        while queue:
            node = queue.pop(0)
            if node is target or (tid is not None and getattr(node, 'id', None) == tid):
                return True
            queue.extend(self._get_direct_children(node))
        return False

    def _matches_depth_expr(self, value: int, expr: str) -> bool:
        expr = expr.strip()
        if not expr:
            return False
        # exact int
        if expr.isdigit() or (expr.startswith("-") and expr[1:].isdigit()):
            return value == int(expr)
        # comparisons
        for op in (">=", "<=", ">", "<"):
            if expr.startswith(op):
                try:
                    num = int(expr[len(op):])
                    if op == ">=":
                        return value >= num
                    if op == "<=":
                        return value <= num
                    if op == ">":
                        return value > num
                    if op == "<":
                        return value < num
                except Exception:
                    return False
        # ranges like 1-3 or -2--1
        if "-" in expr and not expr.startswith("-"):
            try:
                a, b = expr.split("-", 1)
                return int(a) <= value <= int(b)
            except Exception:
                return False
        if expr.count("-") > 1:
            try:
                pos = expr.find("-", 1)
                a = int(expr[:pos])
                b = int(expr[pos + 1 :])
                return a <= value <= b
            except Exception:
                return False
        return False

    def _filter_by_depth(self, context: Context, nodes: List[PACTCore], exprs: List[str]) -> List[PACTCore]:
        if not exprs:
            return []
        out: List[PACTCore] = []
        for n in nodes:
            d = self._component_depth(context, n)
            for e in exprs:
                if self._matches_depth_expr(d, e):
                    out.append(n)
                    break
        return out
