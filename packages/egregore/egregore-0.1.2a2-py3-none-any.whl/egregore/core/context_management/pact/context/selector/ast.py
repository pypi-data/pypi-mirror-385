"""
AST structures for the Lark-based PACT selector parser.

This module defines simple, typed dataclasses that represent a parsed
selector. It is intentionally provider-agnostic and does not depend on
egregore internals; migration can adapt this AST to any execution engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Union


@dataclass
class Attribute:
    name: str
    operator: str
    value: Union[str, int, float, None]


@dataclass
class Behavior:
    name: str
    operator: Optional[str] = None
    value: Union[str, int, float, None] = None


@dataclass
class Pseudo:
    name: str
    args: List[Union[str, int]] = field(default_factory=list)


@dataclass
class SimpleSelector:
    # Spatial/temporal/position modifiers
    spatial: Optional[str] = None           # ^sys, ^ah, ^seq
    temporal: Optional[str] = None          # @t0, @t-1, @history, @t*
    temporal_range: Optional[tuple[str, int, int]] = None  # (kind, start, end) where kind == 't'
    depth_position: Optional[List[int]] = None  # (d-1), (d0, 1, 2)
    depth_position_set: Optional[List[List[int]]] = None  # ((d1,0),(d2,0))
    depth_scope: Optional['DepthScope'] = None  # (d1..d5) or (d1..d*) within position

    # Core selector components
    type_name: Optional[str] = None         # .block
    type_tags: List[str] = field(default_factory=list)  # .block:summary:note
    tags: List[str] = field(default_factory=list)       # +urgent +beta
    id_selector: Optional[str] = None       # #abc123
    attributes: List[Attribute] = field(default_factory=list)  # {role='user'}
    behaviors: List[Behavior] = field(default_factory=list)    # [ttl=2], [ephemeral]
    pseudos: List[Pseudo] = field(default_factory=list)        # :pre, :depth(>=1)
    wildcard: bool = False                                     # * (match any)


@dataclass
class Controls:
    limit: Optional[int] = None
    offset: Optional[int] = None
    mode: Optional[str] = None  # 'all' | 'latest' (others reserved)


@dataclass
class Combinator:
    kind: str  # '??' (recursive), '?' (single), '>' (child)
    within: Optional[int] = None  # within(N) scope limit for deep search


@dataclass
class DepthScope:
    start: int
    end: Optional[Union[int, str]] = None  # '*' allowed for open-ended


@dataclass
class Selector:
    """A selector is a left-to-right chain of simple selectors connected by combinators."""
    head: SimpleSelector
    chain: List[tuple[Combinator, SimpleSelector]] = field(default_factory=list)
    scope: Optional[DepthScope] = None
    controls: Optional[Controls] = None


@dataclass
class SelectorUnion:
    """Represents a union of selectors separated by commas."""
    selectors: List[Selector]


__all__ = [
    "Attribute",
    "Behavior",
    "Pseudo",
    "SimpleSelector",
    "Combinator",
    "DepthScope",
    "Selector",
    "SelectorUnion",
    "Controls",
]
