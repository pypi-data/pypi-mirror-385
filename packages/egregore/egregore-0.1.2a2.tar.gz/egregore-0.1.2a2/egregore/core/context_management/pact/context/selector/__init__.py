"""
Lark-based PACT Selector

Public entrypoints:
- parse(selector: str) -> ast.SelectorUnion
- select(context: Context, selector: str | ast.SelectorUnion) -> list[ContextComponent]
"""

from . import ast as ast
from .parser import LarkPACTParser
from .engine import LarkPACTSelector


def parse(selector: str) -> ast.SelectorUnion:
    return LarkPACTParser().parse(selector)


def select(context, selector):
    return LarkPACTSelector().select(context, selector)


__all__ = [
    "ast",
    "LarkPACTParser",
    "LarkPACTSelector",
    "parse",
    "select",
]

