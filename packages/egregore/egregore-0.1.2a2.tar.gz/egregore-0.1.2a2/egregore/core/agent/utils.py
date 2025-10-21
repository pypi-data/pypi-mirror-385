"""
Agent utility functions for V2 architecture.

Provides shared utilities to eliminate code duplication and optimize performance
across the agent module while maintaining full backward compatibility.
"""

import logging
import inspect
import functools
import asyncio
from typing import Dict, Any, List, Optional, Union, Tuple, TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from .tool_execution_hooks import HookContext
    from .agent_controller import ExecutionState

# Module-level logger instance
logger = logging.getLogger(__name__)


def build_hook_kwargs(context: "HookContext", signature: inspect.Signature) -> Dict[str, Any]:
    """
    Shared parameter mapping logic for hook execution.
    
    Maps HookContext attributes to function parameters based on signature inspection.
    Extracted from tool_execution_hooks.py to eliminate code duplication.
    
    Args:
        context: Hook execution context with available data
        signature: Function signature for parameter mapping
        
    Returns:
        Dict mapping parameter names to context values
        
    Example:
        >>> def my_hook(agent_id: str, tool_name: str): pass
        >>> signature = inspect.signature(my_hook)
        >>> context = HookContext(agent_id="agent1", tool_name="test_tool")
        >>> kwargs = build_hook_kwargs(context, signature)
        >>> # kwargs = {"agent_id": "agent1", "tool_name": "test_tool"}
    """
    kwargs = {}
    
    # Map context attributes to hook parameters based on signature
    if 'context' in signature.parameters:
        kwargs['context'] = context
    if 'agent_id' in signature.parameters:
        kwargs['agent_id'] = context.agent_id
    if 'execution_id' in signature.parameters:
        kwargs['execution_id'] = context.execution_id
    if 'tool_name' in signature.parameters:
        kwargs['tool_name'] = context.tool_name
    if 'tool_params' in signature.parameters:
        kwargs['tool_params'] = context.tool_params
    if 'tool_result' in signature.parameters:
        kwargs['tool_result'] = context.tool_result
    if 'error' in signature.parameters:
        kwargs['error'] = context.error
    if 'chunk_data' in signature.parameters:
        kwargs['chunk_data'] = context.chunk_data
    if 'metadata' in signature.parameters:
        kwargs['metadata'] = context.metadata
        
    return kwargs


def validate_execution_state(
    current_state: "ExecutionState", 
    allowed_states: List["ExecutionState"], 
    context: str = ""
) -> None:
    """
    Shared state validation with clear error messages.
    
    Extracted from agent_controller.py to eliminate duplicate validation logic.
    Provides consistent error messages and state transition guidance.
    
    Args:
        current_state: Current execution state
        allowed_states: List of allowed states for the operation
        context: Optional context description for error messages
        
    Raises:
        RuntimeError: If current_state not in allowed_states
        
    Example:
        >>> validate_execution_state(
        ...     ExecutionState.PROCESSING, 
        ...     [ExecutionState.IDLE], 
        ...     "starting execution"
        ... )
        RuntimeError: Cannot perform starting execution: Agent in PROCESSING state, expected one of: [IDLE]
    """
    if current_state not in allowed_states:
        # Build allowed states string
        if len(allowed_states) == 1:
            allowed_str = allowed_states[0].value
        else:
            allowed_str = f"one of: [{', '.join(state.value for state in allowed_states)}]"
        
        # Build error message with optional context
        if context:
            message = f"Cannot perform {context}: Agent in {current_state.value} state, expected {allowed_str}"
        else:
            message = f"Invalid state transition: Agent in {current_state.value} state, expected {allowed_str}"
            
        raise RuntimeError(message)


def prepare_execution_context(
    scheduler,
    context,
    execution_id: str,
    context_history=None,
    *inputs
) -> Dict[str, Any]:
    """
    Shared context preparation for agent call methods.

    Extracted from agent.py call/acall/stream methods to eliminate duplicate
    context building logic. Handles message scheduling, snapshot creation,
    and thread rendering consistently.

    Args:
        scheduler: Message scheduler instance
        context: Context management instance
        execution_id: Unique execution identifier
        context_history: Optional context history for snapshot creation
        *inputs: Variable inputs to process

    Returns:
        Standardized context dictionary with scheduled messages and metadata

    Example:
        >>> context_dict = prepare_execution_context(scheduler, ctx, "exec-123", hist, "user input")
        >>> # Returns: {"provider_thread": ..., "snapshot_id": ..., "inputs": ...}
    """
    _ensure_scaffolds_rendered(context)

    # Add user inputs to context before rendering
    if inputs:
        # Convert all inputs to strings and concatenate with space
        user_message = " ".join(str(i) for i in inputs if i is not None)
        if user_message:  # Only add if non-empty after filtering None
            context.add_user(user_message)

    snapshot_id = None
    if context_history is not None:
        # Unwrap ContextController to get actual Context object
        actual_context = context._context if hasattr(context, '_context') else context
        snapshot_id = context_history.create_snapshot(
            context=actual_context,
            trigger="before_provider_call",
            execution_id=execution_id
        )

    provider_thread = scheduler.render()

    return {
        "provider_thread": provider_thread,
        "snapshot_id": snapshot_id,
        "execution_id": execution_id,
        "inputs": list(inputs)
    }


def _ensure_scaffolds_rendered(context) -> None:
    """
    Ensure all XML scaffolds are rendered before provider calls.
    
    Traverses the context tree to find all BaseXMLScaffold instances and calls
    their _ensure_rendered() method to ensure scaffolds show current state 
    when their content is accessed by the LLM.
    
    Args:
        context: Context instance containing the context tree
    """
    try:
        # Import here to avoid circular dependency
        from ..context_scaffolds.xml_base import BaseXMLScaffold
        
        def traverse_and_ensure_rendered(component):
            """Recursively traverse context tree and ensure scaffolds are rendered."""
            if isinstance(component, BaseXMLScaffold):
                if hasattr(component, '_ensure_rendered'):
                    component._ensure_rendered()
            
            # Traverse children if component has list content
            if hasattr(component, 'content') and isinstance(component.content, list):
                for child in component.content:
                    if hasattr(child, 'content'):  # Is a ContextComponent
                        traverse_and_ensure_rendered(child)
        
        # Start traversal from context root
        if hasattr(context, 'system_header'):
            traverse_and_ensure_rendered(context.system_header)
        if hasattr(context, 'conversation_history'):
            traverse_and_ensure_rendered(context.conversation_history)
        if hasattr(context, 'active_message'):
            traverse_and_ensure_rendered(context.active_message)
            
    except Exception as e:
        # Log warning but don't fail the provider call
        logger.warning(f"Failed to ensure scaffolds rendered: {e}")


def handle_agent_errors(func):
    """
    Common error handling decorator for agent methods.
    
    Provides consistent error logging and exception preservation across
    agent operations. Maintains original exception types and messages
    for backward compatibility.
    
    Args:
        func: Agent method to wrap with error handling
        
    Returns:
        Wrapped function with error handling
        
    Example:
        >>> @handle_agent_errors
        ... def call(self, *inputs):
        ...     # method implementation
        ...     pass
    """
    @functools.wraps(func)
    def sync_wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            # Try to end execution if this is a main agent method
            execution_id = getattr(self, '_current_execution_id', None)
            if execution_id and hasattr(self, 'controller'):
                try:
                    self.controller.end_execution(execution_id)
                except:
                    pass  # Don't let cleanup errors mask original error
            
            # Log error with agent context
            if hasattr(self, 'agent_id'):
                logger.error(f"Agent {self.agent_id} {func.__name__} failed: {e}")
            else:
                logger.error(f"{func.__name__} failed: {e}")
            
            # Re-raise original exception to maintain compatibility
            raise
    
    @functools.wraps(func) 
    async def async_wrapper(self, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except Exception as e:
            # Try to end execution if this is a main agent method
            execution_id = getattr(self, '_current_execution_id', None)
            if execution_id and hasattr(self, 'controller'):
                try:
                    self.controller.end_execution(execution_id)
                except:
                    pass  # Don't let cleanup errors mask original error
            
            # Log error with agent context
            if hasattr(self, 'agent_id'):
                logger.error(f"Agent {self.agent_id} {func.__name__} failed: {e}")
            else:
                logger.error(f"{func.__name__} failed: {e}")
            
            # Re-raise original exception to maintain compatibility
            raise
    
    # Return appropriate wrapper based on whether function is async
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


# Hook Execution Strategies

class HookExecutionStrategy:
    """
    Base strategy for hook execution.
    
    Provides a common interface for different hook execution approaches,
    allowing for flexible execution patterns while maintaining consistency.
    """
    
    def execute_hooks(self, hooks: List[Any], context: "HookContext") -> None:
        """
        Execute a list of hooks with the given context.
        
        Args:
            hooks: List of hook functions to execute
            context: Context information for hook execution
        """
        raise NotImplementedError("Subclasses must implement execute_hooks")
    
    def should_execute(self, hooks: List[Any]) -> bool:
        """
        Check if hooks should be executed (early bailout optimization).
        
        Args:
            hooks: List of hooks to check
            
        Returns:
            True if hooks should be executed, False to skip
        """
        return bool(hooks)


class SyncHookStrategy(HookExecutionStrategy):
    """
    Strategy for synchronous hook execution.
    
    Executes hooks sequentially in the current thread with proper error handling
    and parameter mapping using shared utilities.
    """
    
    def execute_hooks(self, hooks: List[Any], context: "HookContext") -> None:
        """Execute hooks synchronously."""
        if not self.should_execute(hooks):
            return
        
        logger.debug(f"Executing {len(hooks)} synchronous hooks")
        
        for hook in hooks:
            try:
                self._execute_single_hook(hook, context)
            except Exception as e:
                logger.error(f"Sync hook execution error in {hook.__name__}: {e}")
                raise
    
    def _execute_single_hook(self, hook: Any, context: "HookContext") -> None:
        """Execute a single synchronous hook with parameter mapping."""
        sig = inspect.signature(hook)
        kwargs = build_hook_kwargs(context, sig)
        hook(**kwargs)


class AsyncHookStrategy(HookExecutionStrategy):
    """
    Strategy for asynchronous hook execution.
    
    Executes hooks with proper async/await handling, supporting both
    sync and async hook functions with concurrent execution where appropriate.
    """
    
    async def execute_hooks_async(self, hooks: List[Any], context: "HookContext") -> None:
        """Execute hooks asynchronously."""
        if not self.should_execute(hooks):
            return
        
        logger.debug(f"Executing {len(hooks)} asynchronous hooks")
        
        tasks = []
        for hook in hooks:
            try:
                if inspect.iscoroutinefunction(hook):
                    tasks.append(self._execute_single_hook_async(hook, context))
                else:
                    # Run sync hook in executor
                    tasks.append(asyncio.get_event_loop().run_in_executor(
                        None, self._execute_single_hook_sync, hook, context
                    ))
            except Exception as e:
                logger.error(f"Async hook setup error in {hook.__name__}: {e}")
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _execute_single_hook_async(self, hook: Any, context: "HookContext") -> None:
        """Execute a single async hook with parameter mapping."""
        sig = inspect.signature(hook)
        kwargs = build_hook_kwargs(context, sig)
        await hook(**kwargs)
    
    def _execute_single_hook_sync(self, hook: Any, context: "HookContext") -> None:
        """Execute a single sync hook with parameter mapping (for executor)."""
        sig = inspect.signature(hook)
        kwargs = build_hook_kwargs(context, sig)
        hook(**kwargs)


# Memory Optimization - Object Pool for Small Objects

class SimpleObjectPool:
    """
    Simple object pool for memory optimization.
    
    Reuses objects to reduce allocation overhead for frequently created
    small objects like formatted strings and temporary data structures.
    """
    
    def __init__(self, factory_func: Callable[..., Any], max_size: int = 100):
        """
        Initialize object pool.
        
        Args:
            factory_func: Function that creates new objects
            max_size: Maximum number of objects to pool
        """
        self._factory = factory_func
        self._pool = []
        self._max_size = max_size
        self._created_count = 0
        self._reused_count = 0
    
    def get(self, *args, **kwargs):
        """
        Get an object from the pool or create new one.
        
        Args:
            *args, **kwargs: Arguments to pass to factory if creating new object
        
        Returns:
            Object from pool or newly created
        """
        if self._pool:
            obj = self._pool.pop()
            self._reused_count += 1
            return obj
        else:
            self._created_count += 1
            return self._factory(*args, **kwargs)
    
    def return_object(self, obj):
        """
        Return an object to the pool for reuse.
        
        Args:
            obj: Object to return to pool
        """
        if len(self._pool) < self._max_size:
            # Reset object to clean state if it has a reset method
            if hasattr(obj, 'reset'):
                obj.reset()
            self._pool.append(obj)
    
    def stats(self) -> Dict[str, Union[int, float]]:
        """Get pool statistics."""
        return {
            "pool_size": len(self._pool),
            "created": self._created_count,
            "reused": self._reused_count,
            "hit_rate": self._reused_count / max(1, self._created_count + self._reused_count)
        }


# Global object pools for common small objects
_string_pool = SimpleObjectPool(lambda: [], max_size=50)  # For string building
_dict_pool = SimpleObjectPool(dict, max_size=30)  # For temporary dictionaries


def get_temp_list():
    """Get a temporary list from the pool."""
    return _string_pool.get()


def return_temp_list(temp_list):
    """Return a temporary list to the pool."""
    temp_list.clear()  # Reset to clean state
    _string_pool.return_object(temp_list)


def get_temp_dict():
    """Get a temporary dictionary from the pool."""
    return _dict_pool.get()


def return_temp_dict(temp_dict):
    """Return a temporary dictionary to the pool."""
    temp_dict.clear()  # Reset to clean state
    _dict_pool.return_object(temp_dict)


def get_pool_stats() -> Dict[str, Dict[str, Union[int, float]]]:
    """Get statistics for all object pools."""
    return {
        "string_pool": _string_pool.stats(),
        "dict_pool": _dict_pool.stats()
    }