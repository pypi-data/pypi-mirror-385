"""
Egregore Core 

This module contains the core architecture for Egregore that makes
advanced features feel native rather than bolted-on.

Key principles:
- Clear layer separation: Agent → ContextBuilder → Provider → Native API
- Rich internal types that translate to simple provider types
- Centralized context management and message lifecycle
- No provider knowledge of Egregore-specific concepts

Architecture:
- message_types: Core and native message type definitions
- context_builder: Translation and context management layer
"""
from egregore.core.agent.base import Agent
from egregore.core import context_scaffolds


# Import modules as they become available

# from egregore.corev2.message_types import (
#     # Core types (what providers see)
#     SystemMessage,
#     UserMessage, 
#     AssistantMessage,
#     
#     # Native types (internal Egregore types)
#     # TODO: Add as we build them
# )

# from egregore.corev2.context_builder import (
#     ContextBuilder,
#     # TODO: Add as we build them
# )

__all__ = [
    "Agent",
    "context_scaffolds",
]