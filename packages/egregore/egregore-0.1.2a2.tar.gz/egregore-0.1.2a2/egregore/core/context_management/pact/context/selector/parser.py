"""
Lark-based parser for PACT selectors.

Parses a selector string into AST dataclasses defined in ast.py.
"""

from __future__ import annotations

from typing import List, Optional, Union

from lark import Lark, Transformer, v_args, Token, Tree

from .ast import (
    Attribute,
    Behavior,
    Pseudo,
    SimpleSelector,
    Combinator,
    DepthScope,
    Selector,
    SelectorUnion,
)


GRAMMAR = r"""
start: selector_union

selector_union: selector ("," selector)*   -> union

?selector: chain

# Chain of selector elements
chain: simple (combinator simple)*

combinator: "??" within?   -> deep_recursive
          | "?" within?    -> deep_single
          | ">"            -> child
          | "~"            -> descendant

within: "within" "(" INT ")"

simple: spatial? (temporal_range | temporal)? position? control* (core | tag* attr_block* behavior_block* pseudo*)?

spatial: "^" SPATIAL

temporal: "@" TEMP

# Temporal range forms using two temporal tokens: @tA..@tB
temporal_range: temporal ".." temporal   -> t_range

# Position can contain multiple coordinates
position: "(" position_body ")"
position_body: coord_item ("," coord_item)*      -> position_list
              | group_item ("," group_item)+      -> position_groups
group_item: "(" coord_item ("," coord_item)* ")"
coord_item: coordinate

# Coordinate vector: depth (or depth range) + optional index-or-range dims
coordinate: depth_spec ("," idx_or_range)*

# Depth specification: single depth or depth range
depth_spec: "d" SIGNED_INT ".." "d" wildcard  -> depth_range
          | "d" SIGNED_INT ".." "d" SIGNED_INT  -> depth_range
          | "d" SIGNED_INT                      -> depth_single

# Index atoms and ranges for last-dimension addressing
idx_or_range: idx_atom ".." idx_atom   -> idx_range
            | idx_atom
idx_atom: SIGNED_INT | IDXNAME | SIGNED_IDXNAME

core: wildcard
     | id
     | type id? tag* attr_block* behavior_block* pseudo*

type: "." NAME (":" NAME)*

id: "#" (QSTRING | IDNAME | NAME)

tag: "+" NAME

attr_block: "{" [attr (","? attr)*] "}"
attr: NAME OP (QSTRING | NUMBER | BOOL | NAME)

# Controls
control: "@limit=" INT   -> limit
       | "@offset=" INT  -> offset
       | "@mode=" NAME   -> mode

behavior_block: "[" behavior_items "]"
behavior_items: behavior (","? behavior)*
behavior: BEH_NAME OP (NUMBER | QSTRING | NAME) -> behavior_cmp
        | BEH_NAME                             -> behavior_flag

pseudo: ":" NAME "(" pseudo_args ")"  -> pseudo_fn
      | ":" NAME                    -> pseudo_name
pseudo_args: /[^)]+/

wildcard: "*"

SPATIAL: "sys"|"ah"|"seq"

TEMP: /t(?:0|-\d+|\*)/  // t0 valid in ranges, t-N for historical, t* for wildcard

BEH_NAME: "ttl"|"cad"|"cadence"|"ephemeral"|"sticky"
BOOL: "true"|"false"

IDXNAME: "min"|"max"|"all"|"first"|"last"
SIGNED_IDXNAME: /[+-](?:min|max|all|first|last)/

NAME: /[a-zA-Z_][a-zA-Z0-9_]*/
IDNAME: /[a-zA-Z0-9_-]+/
OP: ">="|"<="|"!="|"="|">"|"<"|"~="
QSTRING: /'[^']*'|"[^"\\]*"/
NUMBER: /-?\d+(?:\.\d+)?/
SIGNED_INT: /-?\d+/

%import common.WS
%import common.INT
%ignore WS
"""


def _unquote(s: str) -> str:
    if len(s) >= 2 and ((s[0] == s[-1] == '"') or (s[0] == s[-1] == "'")):
        return s[1:-1]
    return s


def _num(token: Union[str, Token]) -> Union[int, float, str]:
    s = str(token)
    try:
        if "." in s:
            return float(s)
        return int(s)
    except ValueError:
        return s


@v_args(inline=True)
class _ToAST(Transformer):
    def union(self, first: Selector, *rest) -> SelectorUnion:
        selectors = [first]
        selectors += list(rest)
        return SelectorUnion(selectors)

    def child(self) -> Combinator:
        return Combinator(kind=">")

    def descendant(self, *args) -> Combinator:
        return Combinator(kind=" ")

    def deep_single(self, *args) -> Combinator:
        within = None
        if args and isinstance(args[0], int):
            within = args[0]
        return Combinator(kind="?", within=within)

    def deep_recursive(self, *args) -> Combinator:
        within = None
        if args and isinstance(args[0], int):
            within = args[0]
        return Combinator(kind="??", within=within)

    def within(self, _kw: Token, _lp: Token, n: Token, _rp: Token) -> int:
        return int(n)

    def t_range(self, *args):
        # Accept either (t1, '..', t2) or just (t1, t2) depending on Lark inlining
        if len(args) == 3:
            t1, _dots, t2 = args
        elif len(args) == 2:
            t1, t2 = args
        else:
            # Fallback: return an invalid neutral range to avoid crash
            return ("t", 0, 0)
        # t1/t2 come from temporal() which returns str like 't-1' or 'c5'
        def _parse(t: str) -> tuple[str, int]:
            t = str(t)
            if t.startswith('@'):
                t = t[1:]
            kind = t[0]
            value = int(t[1:])
            return kind, value
        k1, v1 = _parse(t1)
        k2, v2 = _parse(t2)
        # For now, assume both kinds are the same; engine validates further
        kind = k1 if k1 == k2 else k1
        return (kind, v1, v2)

    def spatial(self, *items) -> str:
        # items: ["^", SPATIAL]
        for it in items:
            if isinstance(it, Token) and it.type == "SPATIAL":
                return str(it)
        return ""

    def temporal(self, *items) -> str:
        # items: ["@", Token(TEMP, "t-1")]
        # Return "@t-1" with @ prefix included
        for it in items:
            if isinstance(it, Token) and it.type == "TEMP":
                return "@" + str(it)  # Keep @ as part of the value
        return ""

    def position(self, body):
        # Wrap to distinguish from attribute/behavior lists in simple()
        return ("POSITION", body)

    def position_list(self, first, *rest):
        items = [first] + list(rest)
        if len(items) == 1 and isinstance(items[0], list):
            return items[0]
        return items

    def group_item(self, *items):
        # items come from coord_item parsing; flatten to a coordinate vector
        coords: List[object] = []
        for it in items:
            if isinstance(it, list):
                for v in it:
                    # Preserve range tokens and named markers
                    if isinstance(v, tuple) and len(v) == 3 and v[0] == 'IDX_RANGE':
                        coords.append(v)
                    elif isinstance(v, str):
                        coords.append(v)
                    else:
                        try:
                            coords.append(int(str(v)))
                        except Exception:
                            coords.append(v)
            elif isinstance(it, DepthScope):
                # Depth range - mark it for expansion by engine
                coords.append(('DEPTH_RANGE', it.start, it.end))
            else:
                # Unknown type - try to convert
                try:
                    coords.append(int(str(it)))
                except Exception:
                    pass
        return coords

    def position_groups(self, first_group, *other_groups):
        groups = [first_group]
        groups += list(other_groups)
        return groups

    def depth_single(self, depth_tok: Token) -> int:
        """Transform single depth 'd42' -> 42"""
        return int(str(depth_tok))

    def depth_range(self, *args) -> DepthScope:
        """Transform depth range 'd0..d2' or 'd0..d*' -> DepthScope"""
        # args: (start_tok, end_val) where end_val is either int or "*"
        start = int(str(args[0]))
        if len(args) > 1:
            end_val = args[1]
            # Check if wildcard (either "*" string or Token)
            end_str = str(end_val)
            if end_str == "*":
                return DepthScope(start=start, end="*")
            # Otherwise it's a number
            try:
                return DepthScope(start=start, end=int(end_str))
            except (ValueError, TypeError):
                # Fallback for unexpected format
                return DepthScope(start=start, end="*")
        # Single argument - shouldn't happen with new grammar
        return DepthScope(start=start, end=start)

    def coordinate(self, depth_spec, *rest) -> List[object]:
        # depth_spec is either int (from depth_single) or DepthScope (from depth_range)
        # rest contains optional index/range dims (only last dim may be a range)
        vals: List[object] = []

        # Handle depth specification (single or range)
        if isinstance(depth_spec, DepthScope):
            # Depth range - mark it for expansion by engine
            vals.append(('DEPTH_RANGE', depth_spec.start, depth_spec.end))
        else:
            # Single depth
            vals.append(depth_spec)

        # Handle remaining dimensions
        for it in rest:
            # idx_range returns a tuple marker; tokens for idx_atom arrive as Tokens
            if isinstance(it, tuple) and len(it) == 3 and it[0] == 'IDX_RANGE':
                # ('IDX_RANGE', start, end) — keep tokens as-is for engine validation
                vals.append(('IDX_RANGE', it[1], it[2]))
            elif isinstance(it, Token):
                if it.type == 'SIGNED_INT':
                    vals.append(int(str(it)))
                elif it.type == 'IDXNAME':
                    name = str(it).lower()
                    if name == 'all':
                        # Expand 'all' to an implicit min..max range marker
                        vals.append(('IDX_RANGE', 'min', 'max'))
                    elif name in {'first', 'last'}:
                        vals.append('min' if name == 'first' else 'max')
                    else:
                        vals.append(name)
            else:
                vals.append(it)
        return vals

    def coord_item(self, item):
        # Unwrap coordinate or range result
        return item

    def idx_range(self, a, b):
        def _coerce(x):
            from lark import Token as _Tok
            if isinstance(x, _Tok):
                if x.type == 'SIGNED_INT':
                    return int(str(x))
                if x.type == 'IDXNAME':
                    s = str(x).lower()
                    if s == 'first':
                        return 'min'
                    if s == 'last':
                        return 'max'
                    return s
                if x.type == 'SIGNED_IDXNAME':
                    s = str(x).lower()
                    sign = s[0]
                    base = s[1:]
                    if base == 'all':
                        return 'all'
                    if base in {'first', 'last'}:
                        # interpret sign to pick edge
                        return 'min' if sign == '-' else 'max'
                    if base in {'min', 'max'}:
                        return base
                    return base
            return x
        return ('IDX_RANGE', _coerce(a), _coerce(b))

    def idx_atom(self, x):
        # Coerce idx atom to int or name token
        if isinstance(x, Token):
            if x.type == 'SIGNED_INT':
                return int(str(x))
            if x.type == 'IDXNAME':
                s = str(x).lower()
                if s == 'first':
                    return 'min'
                if s == 'last':
                    return 'max'
                return s
            if x.type == 'SIGNED_IDXNAME':
                s = str(x).lower()
                sign = s[0]
                base = s[1:]
                if base == 'all':
                    return 'all'
                if base in {'first', 'last'}:
                    return 'min' if sign == '-' else 'max'
                if base in {'min', 'max'}:
                    return base
                return base
        return x

    def idx_or_range(self, item):
        # Pass through single atom directly
        return item

    # ---- controls ----
    def control(self, *args):
        # Aggregated via simple(); individual mappers below return dicts
        return {}

    def limit(self, *_args):
        # _args: [Token('@limit='), INT]
        return {"limit": int(str(_args[-1]))}

    def offset(self, *_args):
        return {"offset": int(str(_args[-1]))}

    def mode(self, *_args):
        return {"mode": str(_args[-1])}

    def wildcard(self, *args) -> SimpleSelector:
        return SimpleSelector(wildcard=True)

    def type(self, *items) -> tuple[str, List[str]]:
        type_name = None
        type_tags: List[str] = []
        for it in items:
            if isinstance(it, Token) and it.type == "NAME":
                if type_name is None:
                    type_name = str(it)
                else:
                    type_tags.append(str(it))
        return type_name or "", type_tags

    def id(self, *items) -> tuple[str, str]:
        for it in items:
            if isinstance(it, Token):
                if it.type == "QSTRING":
                    return ("id", _unquote(str(it)))
                if it.type in {"IDNAME", "NAME"}:
                    return ("id", str(it))
        return ("id", "")

    def tag(self, name: Token) -> tuple[str, str]:
        return ("tag", str(name))

    def attr(self, name: Token, op: Token, value: Token) -> Attribute:
        v = str(value)
        if isinstance(value, Token):
            if value.type == "QSTRING":
                v = _unquote(v)
            elif value.type == "NUMBER":
                v = _num(v)
            elif value.type == "BOOL":
                v = True if str(value) == "true" else False
            elif value.type == "NAME":
                lv = str(value).lower()
                if lv in {"true", "false"}:
                    v = True if lv == "true" else False
        return Attribute(name=str(name), operator=str(op), value=v)

    def attr_block(self, *items) -> List[Attribute]:
        # items may include punctuation tokens; only keep Attribute
        return [i for i in items if isinstance(i, Attribute)]

    def behavior_cmp(self, name: Token, op: Token, num: Token) -> Behavior:
        return Behavior(name=str(name), operator=str(op), value=_num(num))

    def behavior_flag(self, name: Token) -> Behavior:
        return Behavior(name=str(name))

    def behavior_items(self, first: Behavior, *rest) -> List[Behavior]:
        items = [first]
        items += [b for b in rest if isinstance(b, Behavior)]
        return items

    def behavior_block(self, items: List[Behavior]) -> List[Behavior]:
        return items

    def pseudo_fn(self, name: Token, args: Token) -> Pseudo:
        raw = str(args).strip()
        # Split by comma or whitespace, keep comparisons and ranges as-is
        parts: List[str] = []
        if raw:
            for part in raw.replace(",", " ").split():
                parts.append(part.strip())
        return Pseudo(name=str(name), args=parts)

    def pseudo_name(self, name: Token) -> Pseudo:
        return Pseudo(name=str(name))

    def pseudo(self, item: Union[Pseudo, Tree]) -> Pseudo:
        from lark import Tree
        from .ast import Pseudo
        if isinstance(item, Tree):
            return Pseudo(name=str(item.data))
        return item  # already built by pseudo_fn/pseudo_name

    def core(self, *bits) -> SimpleSelector:
        # bits may include: wildcard(SimpleSelector), (type,tags) tuple, id, attr list, behavior list, pseudo
        # If wildcard was emitted, return it directly.
        if bits and isinstance(bits[0], SimpleSelector) and bits[0].wildcard:
            return bits[0]

        type_name: Optional[str] = None
        type_tags: List[str] = []
        id_selector: Optional[str] = None
        attrs: List[Attribute] = []
        behaviors: List[Behavior] = []
        pseudos: List[Pseudo] = []
        tags: List[str] = []

        for b in bits:
            # Distinguish between (type, tags) and ("id", value)/("tag", value)
            if isinstance(b, tuple) and len(b) == 2 and isinstance(b[1], list):
                # (type, [tags...]) from type rule
                type_name, type_tags = b
            elif isinstance(b, tuple) and len(b) == 2:
                kind, val = b
                if kind == "id":
                    id_selector = val
                elif kind == "tag":
                    tags.append(val)
            elif isinstance(b, list):
                if all(isinstance(x, Attribute) for x in b):
                    attrs.extend(b)  # attribute block
                elif all(isinstance(x, Behavior) for x in b):
                    behaviors.extend(b)  # behavior block
            elif isinstance(b, Pseudo):
                pseudos.append(b)

        return SimpleSelector(
            type_name=type_name,
            type_tags=type_tags,
            id_selector=id_selector,
            attributes=attrs,
            behaviors=behaviors,
            pseudos=pseudos,
            tags=tags,
        )

    def simple(self, *parts) -> SimpleSelector:
        # parts may contain: spatial(str), temporal(str), position(List[int]), core(SimpleSelector)
        spatial = None
        temporal = None
        temporal_range = None
        depth_position: Optional[List[int]] = None
        depth_position_set: Optional[List[List[int]]] = None
        depth_scope: Optional[DepthScope] = None
        core = SimpleSelector()
        controls = {}
        extra_tags: List[str] = []
        extra_attrs: List[Attribute] = []
        extra_behaviors: List[Behavior] = []
        extra_pseudos: List[Pseudo] = []

        for p in parts:
            if isinstance(p, str):
                # Could be spatial or temporal; spatial appears before temporal in grammar
                if spatial is None and p in {"sys", "ah", "seq"}:
                    spatial = p
                else:
                    temporal = p
            elif isinstance(p, tuple) and len(p) == 2 and p[0] == "POSITION":
                body = p[1]
                if isinstance(body, list) and body:
                    # Could be a position set: list of coord_item(s)
                    # Normalize to either a single depth_position or a set (list of vectors)
                    if all(not isinstance(x, list) for x in body):
                        # Single vector (may contain range tokens)
                        depth_position = body  # type: ignore[assignment]
                    else:
                        positions: List[List[object]] = []
                        for item in body:
                            if isinstance(item, list):
                                vec: List[object] = []
                                for v in item:
                                    if isinstance(v, tuple) and len(v) == 3 and v[0] == 'IDX_RANGE':
                                        vec.append(v)
                                    elif isinstance(v, str):
                                        vec.append(v)
                                    else:
                                        try:
                                            vec.append(int(str(v)))
                                        except Exception:
                                            vec.append(v)
                                positions.append(vec)
                            elif isinstance(item, DepthScope):
                                depth_scope = item
                        if positions:
                            depth_position_set = positions
            elif isinstance(p, tuple) and len(p) == 3 and p[0] in {"t", "c"}:
                temporal_range = p
            elif isinstance(p, dict):
                controls.update(p)
            elif isinstance(p, SimpleSelector):
                core = p
            elif isinstance(p, tuple) and len(p) == 2:
                kind, val = p
                if kind == 'tag':
                    extra_tags.append(val)
            elif isinstance(p, list):
                if all(isinstance(x, Attribute) for x in p):
                    extra_attrs.extend(p)
                elif all(isinstance(x, Behavior) for x in p):
                    extra_behaviors.extend(p)
            elif isinstance(p, Pseudo):
                extra_pseudos.append(p)

        core.spatial = spatial
        core.temporal = temporal
        core.temporal_range = temporal_range
        core.depth_position = depth_position
        core.depth_position_set = depth_position_set
        core.depth_scope = depth_scope
        if extra_tags:
            core.tags = list(core.tags or []) + extra_tags
        if extra_attrs:
            core.attributes = list(core.attributes or []) + extra_attrs
        if extra_behaviors:
            core.behaviors = list(core.behaviors or []) + extra_behaviors
        if extra_pseudos:
            core.pseudos = list(core.pseudos or []) + extra_pseudos
        # stash controls on a temporary field (will be moved to Selector at chain)
        if controls:
            core._controls = controls  # type: ignore[attr-defined]
        return core

    def chain(self, *parts) -> Selector:
        # parts may start with an optional DepthScope, followed by head SimpleSelector, then (Combinator, SimpleSelector)*
        idx = 0
        scope: Optional[DepthScope] = None
        if parts and isinstance(parts[0], DepthScope):
            scope = parts[0]
            idx = 1
        head = parts[idx]
        idx += 1
        chain_items: List[tuple[Combinator, SimpleSelector]] = []
        while idx < len(parts):
            comb = parts[idx]
            nxt = parts[idx + 1] if idx + 1 < len(parts) else None
            if isinstance(comb, Combinator) and isinstance(nxt, SimpleSelector):
                chain_items.append((comb, nxt))
            idx += 2
        # extract selector-level controls from any simple in the chain (last wins)
        controls = None
        cdict: dict | None = None
        for part in [head] + [s for pair in chain_items for s in pair[1:2]]:
            if hasattr(part, '_controls'):
                cdict = dict(getattr(part, '_controls') or {})
                delattr(part, '_controls')
        if cdict:
            from .ast import Controls as _Controls
            controls = _Controls(
                limit=cdict.get('limit'),
                offset=cdict.get('offset'),
                mode=cdict.get('mode'),
            )
        return Selector(head=head, chain=chain_items, scope=scope, controls=controls)

    def selector(self, sel: Selector) -> Selector:
        return sel

    def selector_union(self, u: Union[SelectorUnion, Selector]) -> SelectorUnion:
        if isinstance(u, SelectorUnion):
            return u
        return SelectorUnion([u])


_PARSER = Lark(GRAMMAR, start="start", parser="lalr")


class LarkPACTParser:
    """Public parser API for the Lark-based PACT selector parser."""

    def __init__(self) -> None:
        self._parser = _PARSER
        self._transform = _ToAST()

    def parse(self, selector: str) -> SelectorUnion:
        selector = self._preprocess(selector)
        tree = self._parser.parse(selector)
        result = self._transform.transform(tree)
        # Unwrap Tree wrapping when transformer returns a Tree(start, [SelectorUnion])
        from lark import Tree as _Tree
        if isinstance(result, _Tree) and result.data == 'start' and result.children:
            cand = result.children[0]
            if isinstance(cand, SelectorUnion):
                return cand
        if isinstance(result, SelectorUnion):
            return result
        if isinstance(result, Selector):
            return SelectorUnion([result])
        if isinstance(result, SimpleSelector):
            return SelectorUnion([Selector(head=result, chain=[])])
        # Fallback: wrap as a single empty selector
        return SelectorUnion([Selector(head=SimpleSelector(), chain=[])])

    # ----- preprocessing helpers -----
    def _preprocess(self, s: str) -> str:
        """Normalize whitespace: convert whitespace combinators to ~ marker."""
        import re
        # First, normalize whitespace around explicit combinators
        s = re.sub(r'\s*([>?]{1,2})\s*', r'\1', s)
        # Then, replace whitespace between selector parts with ~ descendant marker
        # But NOT inside parentheses, brackets, or after commas
        # This handles: "@t0 .seg" → "@t0~.seg", but preserves "(d0, 1)"
        result = []
        depth = 0  # Track nesting level
        i = 0
        while i < len(s):
            ch = s[i]
            if ch in '([{':
                depth += 1
                result.append(ch)
            elif ch in ')]}':
                depth -= 1
                result.append(ch)
            elif ch == ',' and depth > 0:
                # Inside parentheses/brackets - preserve comma and following space
                result.append(ch)
                i += 1
                while i < len(s) and s[i].isspace():
                    result.append(s[i])
                    i += 1
                continue
            elif ch.isspace() and depth == 0:
                # Outside parentheses/brackets - check if this is a combinator space
                # Skip consecutive whitespace
                j = i
                while j < len(s) and s[j].isspace():
                    j += 1
                # Only add ~ if:
                # 1. We've already seen content (not leading whitespace)
                # 2. There's more content after the whitespace
                # 3. The next character is not a paren/bracket/tag/control (which continues same selector)
                # Note: . (dot) is removed from exclusion - it's a type selector that should work with combinators
                # Note: @ is excluded to prevent controls from creating spurious chain elements
                if result and j < len(s) and s[j] not in '([{+#@':
                    result.append('~')
                i = j
                continue
            else:
                result.append(ch)
            i += 1
        return ''.join(result)
    
