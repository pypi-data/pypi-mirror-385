"""
Agent system for Egregore V2.

Provides V2 agent implementation with backward compatibility to V1 patterns.
"""

from .base import Agent
from .base.config import AgentConfig
from .base.controller import AgentController
from .hooks import ToolExecutionHooks, ToolHooks, StreamingHooks, ContextHooks
from .message_scheduler import MessageScheduler

__all__ = [
    "Agent",
    "AgentConfig", 
    "AgentController",
    "ToolExecutionHooks",
    "ToolHooks",
    "StreamingHooks",
    "ContextHooks",
    "MessageScheduler"
]