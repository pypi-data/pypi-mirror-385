"""
Agent Hook System

Hook system for tool execution and streaming in agents.
"""

from .execution import ToolExecutionHooks
from .accessors import HookAccessorBase, ToolHooks, StreamingHooks, ContextHooks, HookAccessor
from .execution_contexts import (
    BaseExecContext, ToolExecContext, StreamExecContext, 
    ScaffoldExecContext, ContextExecContext, ContextFactory
)

__all__ = [
    'ToolExecutionHooks',
    'HookAccessorBase',
    'ToolHooks', 
    'StreamingHooks',
    'ContextHooks',
    'HookAccessor',
    # Execution Contexts
    'BaseExecContext',
    'ToolExecContext',
    'StreamExecContext', 
    'ScaffoldExecContext',
    'ContextExecContext',
    'ContextFactory',
]