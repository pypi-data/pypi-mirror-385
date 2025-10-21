"""
Context Management Package

Exports the main PACT Context class and core PACT components
for convenient imports like:

from egregore.core.context_management import (
    Context,
    PACTCore,
    TextContent,
    MessageTurn,
)
"""

# Use PACT implementations
from .pact.context import Context
from .pact.components.core import (
    PACTCore,
    PactRoot,
    SystemHeader,
    MessageTurn,
    MessageContainer,
    TextContent,
)

__all__ = [
    "Context",
    "PACTCore",
    "PactRoot",
    "SystemHeader",
    "MessageTurn",
    "MessageContainer",
    "TextContent",
]
