"""
New hierarchical hook accessor system for intuitive decorator-based hook registration.

Provides decorator-based hook registration with hierarchical organization:
- agent.hooks.streaming.*
- agent.hooks.tool.*  
- agent.hooks.context.*
"""

import logging
from typing import Callable, Optional, Any, TYPE_CHECKING
from functools import wraps
from abc import ABC, abstractmethod

from .execution import ToolExecutionHooks, HookType

if TYPE_CHECKING:
    from ..base import Agent

logger = logging.getLogger(__name__)


class HookAccessorBase(ABC):
    """
    Base class for hook accessor categories providing common decorator functionality.
    
    Handles agent reference management and provides consistent decorator registration
    patterns across all hook categories.
    """
    
    def __init__(self, agent: Optional['Agent'] = None):
        """
        Initialize base hook accessor.
        
        Args:
            agent: Agent instance for hook registration (can be set later)
        """
        self._agent: Optional['Agent'] = agent
        
    def set_agent(self, agent: 'Agent') -> None:
        """Set agent reference for hook registration."""
        self._agent = agent
        
    @property
    def agent(self) -> Optional['Agent']:
        """Get current agent reference."""
        return self._agent
        
    def _register_hook(self, hook_type: HookType, hook_function: Callable) -> Callable:
        """
        Register hook with agent's hook system.
        
        Args:
            hook_type: Type of hook to register
            hook_function: Hook function to register
            
        Returns:
            Original hook function (for decorator chaining)
            
        Raises:
            RuntimeError: If no agent is set
        """
        if self._agent is None:
            raise RuntimeError("No agent set - hook accessor must be attached to an agent")
            
        # Get agent's tool execution hooks system
        if hasattr(self._agent, '_hooks_instance'):
            hook_system = self._agent._hooks_instance
        else:
            raise RuntimeError("Agent does not have a hook system initialized")
            
        # Register the hook
        hook_system.register_hook(hook_type, hook_function)
        logger.debug(f"Registered {hook_type.value} hook: {hook_function.__name__}")
        
        return hook_function
        
    def _create_decorator(self, hook_type: HookType) -> Callable:
        """
        Create a decorator function for the given hook type.
        
        Args:
            hook_type: Type of hook to create decorator for
            
        Returns:
            Decorator function
        """
        def decorator(func: Callable) -> Callable:
            """Decorator that registers the function as a hook."""
            return self._register_hook(hook_type, func)
            
        return decorator


class StreamingHooks(HookAccessorBase):
    """
    Streaming-related hook decorators.
    
    Provides decorators for streaming chunk processing and tool call detection.
    Hook functions receive StreamExecContext with chunk-specific fields.
    """
    
    @property
    def tool_detection(self) -> Callable:
        """Decorator for tool call detection in streaming - receives StreamExecContext."""
        return self._create_decorator(HookType.ON_TOOL_CALL_DETECTED)
        
    @property
    def chunk(self) -> Callable:
        """Decorator for streaming chunk processing - receives StreamExecContext."""
        return self._create_decorator(HookType.ON_STREAMING_CHUNK)
        
    @property
    def on_response_complete(self) -> Callable:
        """Decorator for streaming response completion - receives StreamExecContext (placeholder for future)."""
        # Note: This hook type doesn't exist yet, but we can add it later
        # For now, map to existing streaming chunk hook
        return self._create_decorator(HookType.ON_STREAMING_CHUNK)
    
    # Enhanced chunk type awareness hooks for unified streaming plan
    
    @property
    def on_content(self) -> Callable:
        """Decorator for content chunks - receives StreamExecContext."""
        return self._create_decorator(HookType.ON_CONTENT_CHUNK)
        
    @property
    def on_tool_start(self) -> Callable:
        """Decorator for tool start chunks - receives StreamExecContext."""
        return self._create_decorator(HookType.ON_TOOL_START_CHUNK)
        
    @property
    def on_tool_delta(self) -> Callable:
        """Decorator for tool delta chunks - receives StreamExecContext."""
        return self._create_decorator(HookType.ON_TOOL_DELTA_CHUNK)
        
    @property
    def on_tool_complete(self) -> Callable:
        """Decorator for tool complete chunks - receives StreamExecContext."""
        return self._create_decorator(HookType.ON_TOOL_COMPLETE_CHUNK)
        
    @property
    def on_tool_result(self) -> Callable:
        """Decorator for tool result chunks - receives StreamExecContext."""
        return self._create_decorator(HookType.ON_TOOL_RESULT_CHUNK)


class ToolHooks(HookAccessorBase):
    """
    Tool execution hook decorators.
    
    Provides decorators for tool execution lifecycle events.
    Hook functions receive ToolExecContext with tool-specific fields.
    """
    
    @property
    def pre_call(self) -> Callable:
        """Decorator for before individual tool call - receives ToolExecContext."""
        return self._create_decorator(HookType.BEFORE_TOOL_CALL)
        
    @property
    def post_call(self) -> Callable:
        """Decorator for after individual tool call - receives ToolExecContext."""
        return self._create_decorator(HookType.AFTER_TOOL_CALL)
        
    @property
    def on_error(self) -> Callable:
        """Decorator for tool execution errors - receives ToolExecContext."""
        return self._create_decorator(HookType.ON_TOOL_ERROR)
        
    @property
    def pre_exec(self) -> Callable:
        """Decorator for before tool execution batch - receives ToolExecContext."""
        return self._create_decorator(HookType.BEFORE_TOOL_EXECUTION)
        
    @property
    def post_exec(self) -> Callable:
        """Decorator for after tool execution batch - receives ToolExecContext."""
        return self._create_decorator(HookType.AFTER_TOOL_EXECUTION)
    
    # Enhanced async coordination hooks for ToolTaskLoop
    
    @property
    def on_async_start(self) -> Callable:
        """Decorator for when async tool execution starts - receives ToolExecContext."""
        return self._create_decorator(HookType.ON_TOOL_TASK_STARTED)
        
    @property  
    def on_async_complete(self) -> Callable:
        """Decorator for when async tool execution completes - receives ToolExecContext."""
        return self._create_decorator(HookType.ON_TOOL_TASK_COMPLETED)
        
    @property
    def on_async_failed(self) -> Callable:
        """Decorator for when async tool execution fails - receives ToolExecContext."""
        return self._create_decorator(HookType.ON_TOOL_TASK_FAILED)

    @property
    def intercept(self) -> Callable:
        """Decorator for call interception - receives ToolExecContext.

        Dual-phase hook for validation and result modification:
        - PRE-execution: context.tool_result is None (validation, blocking)
        - POST-execution: context.tool_result exists (enhancement, modification)
        """
        return self._create_decorator(HookType.CALL_INTERCEPT)


class ContextHooks(HookAccessorBase):
    """
    Context operation hook decorators for meaningful context changes.
    
    Hook functions receive ContextExecContext with direct context access:
    - context: Full Context object for direct operations
    - operation_type: Type of context operation being performed
    
    Available hooks:
    - on_add: When components are added to context
    - on_dispatch: When context notifications/updates are sent  
    - on_update: When context is updated (future)
    - on_scaffold_op: When scaffold operations complete
    - on_error: When context operations fail
    """
    
    @property
    def on_add(self) -> Callable:
        """Decorator for context component additions - receives ContextExecContext."""
        return self._create_decorator(HookType.CONTEXT_ADD)
        
    @property
    def on_dispatch(self) -> Callable:
        """Decorator for context notifications/updates - receives ContextExecContext."""
        return self._create_decorator(HookType.CONTEXT_DISPATCH)
        
    @property
    def on_update(self) -> Callable:
        """Decorator for context updates - receives ContextExecContext (future feature)."""
        return self._create_decorator(HookType.CONTEXT_UPDATE)
    
    @property
    def on_scaffold_op(self) -> Callable:
        """Decorator for scaffold operations completion - receives ContextExecContext."""
        return self._create_decorator(HookType.ON_SCAFFOLD_OPERATION_COMPLETED)
        
    @property
    def on_error(self) -> Callable:
        """Decorator for context processing errors - receives ContextExecContext."""
        return self._create_decorator(HookType.ON_TOOL_ERROR)
    
    @property
    def before_change(self) -> Callable:
        """Decorator for before any context change (insert/update/delete) - receives ContextExecContext."""
        return self._create_decorator(HookType.CONTEXT_BEFORE_CHANGE)
        
    @property
    def after_change(self) -> Callable:
        """Decorator for after any context change (insert/update/delete) - receives ContextExecContext."""
        return self._create_decorator(HookType.CONTEXT_AFTER_CHANGE)
    
    def listen(self, selector: str, event: str) -> Callable:
        """
        Enhanced listener with selector syntax and event timing.
        
        Args:
            selector: CSS-like selector for targeting specific components
                     - ".scaffold_notification" (type)
                     - "#user_files" (key) 
                     - "[ttl=0]" (attribute)
                     - "(d0,*)" (position pattern)
            event: Event timing - "before" | "after"
        
        Returns:
            Decorator function for the hook
        """
        # Create dynamic hook type from selector and event
        hook_type_name = f"context_{event}_{selector.replace('.', 'type_').replace('#', 'key_').replace('[', 'attr_').replace(']', '').replace('(', 'pos_').replace(')', '').replace(',', '_').replace('*', 'any')}"
        
        # For now, map to existing hooks based on event timing
        if event == "before":
            return self._create_decorator(HookType.CONTEXT_BEFORE_CHANGE)
        elif event == "after":
            return self._create_decorator(HookType.CONTEXT_AFTER_CHANGE)
        else:
            raise ValueError(f"Invalid event type: {event}. Must be 'before' or 'after'")


class MessageHooks(HookAccessorBase):
    """
    Message editing hook decorators for user input and provider responses.
    
    Hook functions receive MessageExecContext that can modify message_content:
    - message_content: Editable message content
    - context: Full context access for audit trails
    - message_type: "user_input" or "provider_response" 
    """
    
    @property
    def on_user_msg(self) -> Callable:
        """Decorator for user message editing before provider - receives MessageExecContext."""
        return self._create_decorator(HookType.MESSAGE_USER_INPUT)
        
    @property
    def on_provider_msg(self) -> Callable:
        """Decorator for provider message editing after seal (final response only) - receives MessageExecContext."""
        return self._create_decorator(HookType.MESSAGE_PROVIDER_RESPONSE)
        
    @property
    def on_error(self) -> Callable:
        """Decorator for message processing errors - receives MessageExecContext."""
        return self._create_decorator(HookType.MESSAGE_ERROR)


class OperationHooks(HookAccessorBase):
    """
    Universal operation hook decorators for both regular tools and scaffold operations.
    
    Provides decorators for hooks that need to handle both ToolDeclaration and 
    ScaffoldOpDeclaration operations through OperationExecContext. These hooks
    receive OperationExecContext which includes type detection and metadata access.
    
    Hook functions receive OperationExecContext with:
    - context.is_scaffold_operation: bool indicating if this is a scaffold operation
    - context.scaffold_metadata: dict with scaffold metadata if scaffold operation
    - context.tool_declaration: the original ToolDeclaration or ScaffoldOpDeclaration
    - context.tool_name: tool name (available for both types)
    - context.tool_params: tool parameters (available for both types)
    
    Example usage:
        @agent.hooks.operation.before
        def universal_pre_hook(context: OperationExecContext):
            if context.is_scaffold_operation:
                metadata = context.scaffold_metadata
                print(f"Scaffold {metadata['scaffold_type']} operation: {metadata['operation_name']}")
            else:
                print(f"Regular tool: {context.tool_name}")
    """
    
    @property
    def before(self) -> Callable:
        """Decorator for before any operation (tool or scaffold) - receives OperationExecContext."""
        return self._create_decorator(HookType.BEFORE_TOOL_EXECUTION)
        
    @property
    def after(self) -> Callable:
        """Decorator for after any operation (tool or scaffold) - receives OperationExecContext."""
        return self._create_decorator(HookType.AFTER_TOOL_EXECUTION)
        
    @property
    def on_error(self) -> Callable:
        """Decorator for operation errors (tool or scaffold) - receives OperationExecContext."""
        return self._create_decorator(HookType.ON_TOOL_ERROR)

    @property
    def intercept(self) -> Callable:
        """Decorator for call interception (both tools and scaffolds) - receives OperationExecContext.

        Dual-phase hook for validation and result modification:
        - PRE-execution: context.tool_result is None (validation, blocking)
        - POST-execution: context.tool_result exists (enhancement, modification)

        Use context.is_scaffold_operation to distinguish between tool and scaffold calls.
        """
        return self._create_decorator(HookType.CALL_INTERCEPT)


class ScaffoldHooks(HookAccessorBase):
    """
    Scaffold operation hook decorators.
    
    Provides decorators for scaffold operations.
    Hook functions receive ScaffoldExecContext with scaffold-specific fields.
    """
    
    @property
    def pre(self) -> Callable:
        """Decorator for before scaffold operations - receives ScaffoldExecContext."""
        return self._create_decorator(HookType.BEFORE_TOOL_EXECUTION)
        
    @property
    def post(self) -> Callable:
        """Decorator for after scaffold operations - receives ScaffoldExecContext."""
        return self._create_decorator(HookType.AFTER_TOOL_EXECUTION)
        
    @property
    def on_error(self) -> Callable:
        """Decorator for scaffold lifecycle errors - receives ScaffoldExecContext."""
        return self._create_decorator(HookType.ON_TOOL_ERROR)
        
    @property
    def on_state_change(self) -> Callable:
        """Decorator for scaffold state changes - receives ScaffoldExecContext."""
        return self._create_decorator(HookType.ON_SCAFFOLD_STATE_CHANGE)


class HookAccessor:
    """
    Main hook accessor coordinator providing hierarchical hook access.
    
    Exposes streaming, tool, context, and operation hook categories through properties.
    """
    
    def __init__(self, agent: Optional['Agent'] = None):
        """
        Initialize hook accessor with optional agent reference.
        
        Args:
            agent: Agent instance for hook registration
        """
        self._agent = agent
        self._streaming = StreamingHooks(agent)
        self._tool = ToolHooks(agent)
        self._context = ContextHooks(agent)
        self._operation = OperationHooks(agent)
        
    def set_agent(self, agent: 'Agent') -> None:
        """Set agent reference for all hook categories."""
        self._agent = agent
        self._streaming.set_agent(agent)
        self._tool.set_agent(agent)
        self._context.set_agent(agent)
        self._operation.set_agent(agent)
        
    @property
    def streaming(self) -> StreamingHooks:
        """Access streaming-related hooks."""
        return self._streaming
        
    @property
    def tool(self) -> ToolHooks:
        """Access tool execution hooks."""
        return self._tool
        
    @property
    def context(self) -> ContextHooks:
        """Access context/message lifecycle hooks."""
        return self._context
        
    @property
    def operation(self) -> OperationHooks:
        """Access universal operation hooks that work with both tools and scaffold operations."""
        return self._operation