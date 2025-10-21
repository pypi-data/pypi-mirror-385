"""
ToolExecutionHooks system for managing tool execution lifecycle hooks.

Provides comprehensive hook management for tool execution with support for
before/after/error hooks, streaming chunk processing, and injection patterns.
"""

import logging
from typing import Dict, List, Callable, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import inspect
import asyncio

from ..utils import build_hook_kwargs, SyncHookStrategy, AsyncHookStrategy
from .execution_contexts import BaseExecContext, ToolExecContext, StreamExecContext, ScaffoldExecContext, OperationExecContext, ContextExecContext, MessageExecContext, ContextFactory

logger = logging.getLogger(__name__)


class HookType(Enum):
    """Types of execution hooks."""
    # Existing tool hooks
    BEFORE_TOOL_EXECUTION = "before_tool_execution"
    AFTER_TOOL_EXECUTION = "after_tool_execution"
    ON_TOOL_ERROR = "on_tool_error"
    BEFORE_TOOL_CALL = "before_tool_call"
    AFTER_TOOL_CALL = "after_tool_call"
    ON_STREAMING_CHUNK = "on_streaming_chunk"
    ON_TOOL_CALL_DETECTED = "on_tool_call_detected"
    CALL_INTERCEPT = "call_intercept"  # NEW: Single hook for input validation and output modification
    
    # NEW: Context operation hooks
    CONTEXT_ADD = "context_add"
    CONTEXT_DISPATCH = "context_dispatch"
    CONTEXT_UPDATE = "context_update"
    
    # NEW: Context lifecycle hooks for reactive scaffold rendering
    CONTEXT_BEFORE_CHANGE = "context_before_change"
    CONTEXT_AFTER_CHANGE = "context_after_change"
    
    # NEW: Message editing hooks
    MESSAGE_USER_INPUT = "message_user_input"        # Edit user message before provider
    MESSAGE_PROVIDER_RESPONSE = "message_provider_response"  # Edit provider response after seal
    MESSAGE_ERROR = "message_error"
    
    # NEW: ToolTaskLoop coordination hooks (from unified streaming plan)
    ON_TOOL_TASK_STARTED = "on_tool_task_started"
    ON_TOOL_TASK_COMPLETED = "on_tool_task_completed"
    ON_TOOL_TASK_FAILED = "on_tool_task_failed" 
    ON_SCAFFOLD_OPERATION_COMPLETED = "on_scaffold_operation_completed"
    ON_SCAFFOLD_STATE_CHANGE = "on_scaffold_state_change"
    
    # NEW: Enhanced streaming hooks for chunk type awareness
    ON_CONTENT_CHUNK = "on_content_chunk"
    ON_TOOL_START_CHUNK = "on_tool_start_chunk"
    ON_TOOL_DELTA_CHUNK = "on_tool_delta_chunk"
    ON_TOOL_COMPLETE_CHUNK = "on_tool_complete_chunk"
    ON_TOOL_RESULT_CHUNK = "on_tool_result_chunk"


@dataclass
class InjectionRule:
    """Rule for parameter injection during tool execution."""
    tool_name: Optional[str]  # None means apply to all tools
    parameter_name: str
    injection_function: Callable[..., Any]
    condition: Optional[Callable[..., bool]] = None  # Optional condition check


class ToolExecutionHooks:
    """
    Manages hooks for tool execution lifecycle events.
    
    Supports registration of hooks for various tool execution events,
    parameter injection patterns, and streaming chunk processing.
    """
    
    def __init__(self):
        """Initialize the hook system."""
        self._hooks: Dict[HookType, List[Callable]] = {
            hook_type: [] for hook_type in HookType
        }
        self._injection_rules: List[InjectionRule] = []
        self._hook_enabled: Dict[HookType, bool] = {
            hook_type: True for hook_type in HookType
        }
        
        # Hook execution strategies
        self._sync_strategy = SyncHookStrategy()
        self._async_strategy = AsyncHookStrategy()
        
        logger.debug("ToolExecutionHooks initialized")
    
    # Hook Registration
    
    def register_hook(self, hook_type: HookType, hook_function: Callable) -> None:
        """
        Register a hook function for a specific hook type.
        
        Args:
            hook_type: Type of hook to register
            hook_function: Function to call for this hook
        """
        if not callable(hook_function):
            raise ValueError("Hook function must be callable")
        
        self._hooks[hook_type].append(hook_function)
        logger.debug(f"Registered {hook_type.value} hook: {hook_function.__name__}")
    
    def register_before_tool_execution(self, hook: Callable) -> None:
        """Register hook to execute before tool execution starts."""
        self.register_hook(HookType.BEFORE_TOOL_EXECUTION, hook)
    
    def register_after_tool_execution(self, hook: Callable) -> None:
        """Register hook to execute after tool execution completes."""
        self.register_hook(HookType.AFTER_TOOL_EXECUTION, hook)
    
    def register_tool_error_hook(self, hook: Callable) -> None:
        """Register hook to execute when tool execution errors occur."""
        self.register_hook(HookType.ON_TOOL_ERROR, hook)
    
    def register_before_tool_call(self, hook: Callable) -> None:
        """Register hook to execute before individual tool call."""
        self.register_hook(HookType.BEFORE_TOOL_CALL, hook)
    
    def register_after_tool_call(self, hook: Callable) -> None:
        """Register hook to execute after individual tool call."""
        self.register_hook(HookType.AFTER_TOOL_CALL, hook)
    
    def register_streaming_chunk_hook(self, hook: Callable) -> None:
        """Register hook to process streaming chunks."""
        self.register_hook(HookType.ON_STREAMING_CHUNK, hook)
    
    def register_tool_call_detected_hook(self, hook: Callable) -> None:
        """Register hook to execute when tool call is detected in streaming."""
        self.register_hook(HookType.ON_TOOL_CALL_DETECTED, hook)
    
    # Streaming Chunk Processing
    
    def process_stream_chunk(self, chunk: Any, context: Any) -> Any:
        """
        Process streaming chunk through registered hooks (sync version).
        
        Args:
            chunk: Stream chunk to process
            context: Context for chunk processing
            
        Returns:
            Processed chunk
        """
        if not self._hooks[HookType.ON_STREAMING_CHUNK]:
            return chunk
        
        hook_context = ContextFactory.create_stream_context(
            agent_id=getattr(context, 'agent_id', 'unknown'),
            chunk_data=chunk,
            agent=getattr(context, 'agent', None),
            chunk_type="content"
        )
        
        processed_chunk = chunk
        for hook in self._hooks[HookType.ON_STREAMING_CHUNK]:
            try:
                # Call hook with chunk and context
                result = hook(processed_chunk, context)
                if result is not None:
                    processed_chunk = result
            except Exception as e:
                logger.warning(f"Streaming hook failed: {e}")
                continue
        
        return processed_chunk
    
    async def aprocess_stream_chunk(self, chunk: Any, context: Any) -> Any:
        """
        Process streaming chunk through registered hooks (async version).
        
        Args:
            chunk: Stream chunk to process
            context: Context for chunk processing
            
        Returns:
            Processed chunk
        """
        if not self._hooks[HookType.ON_STREAMING_CHUNK]:
            return chunk
        
        hook_context = ContextFactory.create_stream_context(
            agent_id=getattr(context, 'agent_id', 'unknown'),
            chunk_data=chunk,
            agent=getattr(context, 'agent', None),
            chunk_type="content"
        )
        
        processed_chunk = chunk
        for hook in self._hooks[HookType.ON_STREAMING_CHUNK]:
            try:
                # Check if hook is async
                if inspect.iscoroutinefunction(hook):
                    result = await hook(processed_chunk, context)
                else:
                    result = hook(processed_chunk, context)
                    
                if result is not None:
                    processed_chunk = result
            except Exception as e:
                logger.warning(f"Async streaming hook failed: {e}")
                continue
        
        return processed_chunk
    
    # Enhanced streaming hook methods for unified streaming plan
    
    async def process_content_chunk_async(self, chunk: Any, context: Any) -> Any:
        """Process content chunks with chunk type awareness."""
        return await self._process_chunk_by_type(HookType.ON_CONTENT_CHUNK, chunk, context)
    
    async def process_tool_chunk_async(self, chunk: Any, context: Any) -> Any:
        """Process tool-related chunks (start, delta, complete)."""
        chunk_type = getattr(chunk, 'chunk_type', 'content')
        
        if chunk_type == "tool_start":
            return await self._process_chunk_by_type(HookType.ON_TOOL_START_CHUNK, chunk, context)
        elif chunk_type == "tool_delta":
            return await self._process_chunk_by_type(HookType.ON_TOOL_DELTA_CHUNK, chunk, context)
        elif chunk_type == "tool_complete":
            return await self._process_chunk_by_type(HookType.ON_TOOL_COMPLETE_CHUNK, chunk, context)
        else:
            return chunk
    
    async def process_tool_result_chunk_async(self, chunk: Any, context: Any) -> Any:
        """Process tool result chunks."""
        return await self._process_chunk_by_type(HookType.ON_TOOL_RESULT_CHUNK, chunk, context)
    
    async def process_stream_chunk_async(self, chunk: Any, context: Any) -> Any:
        """Fallback for generic chunk processing."""
        return await self._process_chunk_by_type(HookType.ON_STREAMING_CHUNK, chunk, context)
    
    async def _process_chunk_by_type(self, hook_type: HookType, chunk: Any, context: Any) -> Any:
        """Generic chunk processing for specific hook types."""
        if not self._hooks[hook_type]:
            return chunk
        
        chunk_type = getattr(chunk, 'chunk_type', 'content')
        hook_context = ContextFactory.create_stream_context(
            agent_id=getattr(context, 'agent_id', 'unknown'),
            chunk_data=chunk,
            agent=getattr(context, 'agent', None),
            chunk_type=chunk_type
        )
        
        processed_chunk = chunk
        for hook in self._hooks[hook_type]:
            try:
                if inspect.iscoroutinefunction(hook):
                    result = await hook(hook_context)
                else:
                    result = hook(hook_context)
                    
                if result is not None:
                    processed_chunk = result
            except Exception as e:
                logger.warning(f"Enhanced chunk hook failed for {hook_type.value}: {e}")
                continue
        
        return processed_chunk
    
    # Message Editing Hooks
    
    def execute_message_editing_hook(self, hook_type: HookType, message_content: Any, 
                                    context: Any = None) -> tuple[Any, bool]:
        """
        Execute message editing hooks that can modify message content.
        
        Args:
            hook_type: Type of message hook (MESSAGE_USER_INPUT or MESSAGE_PROVIDER_RESPONSE)
            message_content: Message content to potentially edit
            context: Additional context for the hook
            
        Returns:
            tuple: (potentially_modified_content, was_modified)
        """
        if hook_type not in self._hooks:
            return message_content, False
        
        hooks = self._hooks.get(hook_type, [])
        if not hooks:
            return message_content, False
        
        modified_content = message_content
        was_modified = False
        
        for hook_function in hooks:
            try:
                # Create specialized context for message editing
                if hook_type == HookType.MESSAGE_USER_INPUT:
                    exec_context = ContextFactory.create_user_message_context(
                        message_content=modified_content,
                        context=context,
                        agent_id=getattr(context, 'agent_id', 'unknown') if context else 'unknown'
                    )
                else:  # MESSAGE_PROVIDER_RESPONSE
                    exec_context = ContextFactory.create_provider_message_context(
                        message_content=modified_content,
                        context=context,
                        agent_id=getattr(context, 'agent_id', 'unknown') if context else 'unknown',
                        is_final_response=getattr(context, 'is_final_response', True) if context else True
                    )
                
                # Execute hook - hook can modify exec_context.message_content
                result = hook_function(exec_context)
                
                # Check if content was modified
                if hasattr(exec_context, 'message_content') and exec_context.message_content != modified_content:
                    modified_content = exec_context.message_content
                    was_modified = True
                    
            except Exception as e:
                logger.error(f"Message editing hook failed: {e}")

                # Phase 5: Fire MESSAGE_ERROR hook
                from .execution_contexts import ContextFactory
                error_context = ContextFactory.create_message_error_context(
                    message_content=modified_content,
                    context=exec_context.context if hasattr(exec_context, 'context') else None,
                    error=e,
                    message_type=message_type,
                    agent_id=getattr(exec_context, 'agent_id', 'unknown')
                )
                self.execute_hooks(HookType.MESSAGE_ERROR, error_context)

                # Re-raise exception after firing hook
                raise
        
        return modified_content, was_modified
    
    # Hook Execution
    
    def execute_hooks(self, hook_type: HookType, context: Union[BaseExecContext, ToolExecContext, StreamExecContext, ScaffoldExecContext, OperationExecContext, ContextExecContext, MessageExecContext]) -> None:
        """
        Execute all hooks of a specific type using strategy pattern.
        
        Args:
            hook_type: Type of hooks to execute
            context: Context information for the hooks
        """
        if not self._hook_enabled.get(hook_type, True):
            return
        
        hooks = self._hooks.get(hook_type, [])
        if not hooks:
            return
        
        try:
            self._sync_strategy.execute_hooks(hooks, context)
        except Exception as e:
            # If this isn't already an error hook, execute error hooks
            if hook_type != HookType.ON_TOOL_ERROR:
                error_context = self._create_error_context(context, e, hook_type)
                self.execute_hooks(HookType.ON_TOOL_ERROR, error_context)
            # Re-raise the exception to propagate it up the call stack
            raise
    
    async def execute_hooks_async(self, hook_type: HookType, context: Union[BaseExecContext, ToolExecContext, StreamExecContext, ScaffoldExecContext, OperationExecContext, ContextExecContext, MessageExecContext]) -> None:
        """
        Execute hooks asynchronously using strategy pattern.
        
        Args:
            hook_type: Type of hooks to execute
            context: Context information for the hooks
        """
        if not self._hook_enabled.get(hook_type, True):
            return
        
        hooks = self._hooks.get(hook_type, [])
        if not hooks:
            return
        
        try:
            await self._async_strategy.execute_hooks_async(hooks, context)
        except Exception as e:
            # If this isn't already an error hook, execute error hooks
            if hook_type != HookType.ON_TOOL_ERROR:
                error_context = self._create_error_context(context, e, hook_type)
                await self.execute_hooks_async(HookType.ON_TOOL_ERROR, error_context)
            # Re-raise the exception to propagate it up the call stack
            raise
    
    # Note: Hook execution now handled by strategy classes
    # _execute_single_hook and _execute_single_hook_async methods removed
    # in favor of strategy pattern implementation
    
    def _create_error_context(self, original_context: Union[BaseExecContext, ToolExecContext, StreamExecContext, ScaffoldExecContext, OperationExecContext, ContextExecContext, MessageExecContext], error: Exception, hook_type: HookType) -> Union[BaseExecContext, ToolExecContext, StreamExecContext, ScaffoldExecContext, OperationExecContext, ContextExecContext, MessageExecContext]:
        """Create error context of the same type as original context."""
        error_metadata = {
            "original_hook_type": hook_type.value,
            "failed_hook": getattr(error, '__hook_name__', 'unknown')
        }
        
        # Create error context matching the original context type
        if isinstance(original_context, ToolExecContext):
            return ToolExecContext(
                agent_id=original_context.agent_id,
                execution_id=original_context.execution_id,
                agent=original_context.agent,
                tool_name=original_context.tool_name,
                tool_params=original_context.tool_params,
                error=error,
                metadata=error_metadata
            )
        elif isinstance(original_context, ScaffoldExecContext):
            return ScaffoldExecContext(
                agent_id=original_context.agent_id,
                execution_id=original_context.execution_id,
                agent=original_context.agent,
                scaffold_type=original_context.scaffold_type,
                scaffold_id=original_context.scaffold_id,
                operation_name=original_context.operation_name,
                error=error,
                metadata=error_metadata
            )
        elif isinstance(original_context, StreamExecContext):
            return StreamExecContext(
                agent_id=original_context.agent_id,
                execution_id=original_context.execution_id,
                agent=original_context.agent,
                chunk_data=original_context.chunk_data,
                chunk_type=original_context.chunk_type,
                error=error,
                metadata=error_metadata
            )
        elif isinstance(original_context, OperationExecContext):
            return OperationExecContext(
                agent_id=original_context.agent_id,
                execution_id=original_context.execution_id,
                agent=original_context.agent,
                tool_declaration=original_context.tool_declaration,
                tool_name=original_context.tool_name,
                tool_params=original_context.tool_params,
                error=error,
                metadata=error_metadata
            )
        elif isinstance(original_context, ContextExecContext):
            return ContextExecContext(
                agent_id=original_context.agent_id,
                execution_id=original_context.execution_id,
                agent=original_context.agent,
                context=original_context.context,
                operation_type=original_context.operation_type,
                error=error,
                metadata=error_metadata
            )
        elif isinstance(original_context, MessageExecContext):
            return MessageExecContext(
                agent_id=original_context.agent_id,
                execution_id=original_context.execution_id,
                agent=original_context.agent,
                message_content=original_context.message_content,
                message_type=original_context.message_type,
                message_id=original_context.message_id,
                context=original_context.context,
                is_final_response=original_context.is_final_response,
                content_length=original_context.content_length,
                error=error,
                metadata=error_metadata
            )
        else:
            # Fallback to base context for unknown types
            return BaseExecContext(
                agent_id=original_context.agent_id,
                execution_id=original_context.execution_id,
                agent=original_context.agent,
                error=error,
                metadata=error_metadata
            )
    
    # Parameter Injection System
    
    def add_injection_rule(self, 
                          parameter_name: str,
                          injection_function: Callable[..., Any],
                          tool_name: Optional[str] = None,
                          condition: Optional[Callable[..., bool]] = None) -> None:
        """
        Add parameter injection rule.
        
        Args:
            parameter_name: Name of parameter to inject
            injection_function: Function that generates the parameter value
            tool_name: Specific tool name (None for all tools)
            condition: Optional condition function to check before injection
        """
        rule = InjectionRule(
            tool_name=tool_name,
            parameter_name=parameter_name,
            injection_function=injection_function,
            condition=condition
        )
        self._injection_rules.append(rule)
        logger.debug(f"Added injection rule for parameter '{parameter_name}' on tool '{tool_name or 'all'}'")
    
    def apply_injection_patterns(self, 
                                tool_name: str, 
                                tool_params: Dict[str, Any],
                                context: Union[BaseExecContext, ToolExecContext, StreamExecContext, ScaffoldExecContext, OperationExecContext]) -> Dict[str, Any]:
        """
        Apply injection patterns to tool parameters.
        
        Args:
            tool_name: Name of the tool being called
            tool_params: Current tool parameters
            context: Hook context for injection functions
            
        Returns:
            Modified tool parameters with injections applied
        """
        modified_params = tool_params.copy()
        
        for rule in self._injection_rules:
            # Check if rule applies to this tool
            if rule.tool_name is not None and rule.tool_name != tool_name:
                continue
            
            # Check condition if specified
            if rule.condition and not rule.condition(tool_name=tool_name, 
                                                   tool_params=tool_params, 
                                                   context=context):
                continue
            
            try:
                # Generate injected value
                injected_value = rule.injection_function(
                    tool_name=tool_name,
                    tool_params=tool_params,
                    context=context
                )
                modified_params[rule.parameter_name] = injected_value
                logger.debug(f"Injected parameter '{rule.parameter_name}' for tool '{tool_name}'")
                
            except Exception as e:
                logger.error(f"Injection rule failed for parameter '{rule.parameter_name}': {e}")
        
        return modified_params
    
    # Hook Management
    
    def enable_hook_type(self, hook_type: HookType) -> None:
        """Enable hooks of a specific type."""
        self._hook_enabled[hook_type] = True
        logger.debug(f"Enabled {hook_type.value} hooks")
    
    def disable_hook_type(self, hook_type: HookType) -> None:
        """Disable hooks of a specific type."""
        self._hook_enabled[hook_type] = False
        logger.debug(f"Disabled {hook_type.value} hooks")
    
    def clear_hooks(self, hook_type: Optional[HookType] = None) -> None:
        """
        Clear hooks.
        
        Args:
            hook_type: Specific hook type to clear, or None to clear all
        """
        if hook_type is None:
            for hook_list in self._hooks.values():
                hook_list.clear()
            logger.debug("Cleared all hooks")
        else:
            self._hooks[hook_type].clear()
            logger.debug(f"Cleared {hook_type.value} hooks")
    
    def clear_injection_rules(self, tool_name: Optional[str] = None) -> None:
        """
        Clear injection rules.
        
        Args:
            tool_name: Clear rules for specific tool, or None for all
        """
        if tool_name is None:
            self._injection_rules.clear()
            logger.debug("Cleared all injection rules")
        else:
            self._injection_rules = [
                rule for rule in self._injection_rules 
                if rule.tool_name != tool_name
            ]
            logger.debug(f"Cleared injection rules for tool '{tool_name}'")
    
    # Status and Information
    
    def get_hook_counts(self) -> Dict[str, int]:
        """Get count of registered hooks by type."""
        return {
            hook_type.value: len(hooks) 
            for hook_type, hooks in self._hooks.items()
        }
    
    def get_injection_rule_count(self) -> int:
        """Get count of registered injection rules."""
        return len(self._injection_rules)
    
    def is_hook_type_enabled(self, hook_type: HookType) -> bool:
        """Check if a hook type is enabled."""
        return self._hook_enabled.get(hook_type, True)
    
    def __repr__(self) -> str:
        """String representation."""
        hook_counts = self.get_hook_counts()
        total_hooks = sum(hook_counts.values())
        return f"ToolExecutionHooks(hooks={total_hooks}, injection_rules={len(self._injection_rules)})"