"""
ToolTaskLoop - Core async execution engine for tools and scaffold operations.

Provides unified async execution engine for tools and scaffold operations with:
- Non-blocking tool execution
- Real-time progress streaming  
- External scaffold operations
- Interruption support
- Context dispatch integration
"""

import asyncio
import logging
import uuid
import json
from typing import Dict, Any, Optional, AsyncIterator, TYPE_CHECKING
from datetime import datetime
from egregore.core.context_management.pact.components.core import Metadata as ComponentMetadata

if TYPE_CHECKING:
    from .base import Agent

logger = logging.getLogger(__name__)


class ToolTaskLoop:
    """
    Unified async execution engine for tools and scaffold operations.
    
    Supports both streaming and non-streaming execution with:
    - Non-blocking tool execution
    - Real-time progress streaming  
    - External scaffold operations
    - Interruption support
    - Context dispatch integration
    """
    
    def __init__(self, agent: Optional['Agent'] = None):
        """
        Initialize ToolTaskLoop with agent reference.
        
        Args:
            agent: Agent instance for tool execution and context management
        """
        self.agent = agent
        
        # Core data structures
        self.running_tasks: Dict[str, Dict[str, Any]] = {}
        self.operation_queue: asyncio.Queue = asyncio.Queue(maxsize=100)  # Bounded to prevent memory bloat
        self.context_update_queue: asyncio.Queue = asyncio.Queue(maxsize=200)  # Bounded to prevent memory bloat
        
        # Streaming support  
        self.streaming_results: Dict[str, asyncio.Queue] = {}  # task_id -> result queue for progress streaming
        
        # Shutdown coordination
        self._shutdown_event = asyncio.Event()
        
        logger.info(f"ToolTaskLoop initialized for agent {getattr(agent, 'agent_id', 'unknown')}")
    
    
    async def execute_tool_async(self, tool_call: Any) -> str:
        """
        Execute tool asynchronously (non-streaming).
        
        Args:
            tool_call: Tool call object to execute
            
        Returns:
            task_id: Unique identifier for tracking the async operation
        """
        task_id = f"tool_{getattr(tool_call, 'id', uuid.uuid4().hex[:8])}_{uuid.uuid4().hex[:8]}"
        
        try:
            # Create task tracking record
            task_info = {
                'task_id': task_id,
                'tool_call': tool_call,
                'type': 'async',
                'started_at': datetime.now(),
                'status': 'started'
            }
            
            # Track the task
            self.running_tasks[task_id] = task_info
            
            # Emit tool started hook
            await self._emit_tool_started_hook(task_id, tool_call)
            
            # Create async task for execution
            async def async_execution():
                try:
                    # Update status
                    self.running_tasks[task_id]['status'] = 'executing'
                    
                    # Get operation for tool (placeholder - will integrate with actual tool system)
                    operation = self._get_operation_for_tool(tool_call)
                    
                    # Execute operation
                    if operation:
                        result = await self._execute_operation(operation, tool_call)
                        self.running_tasks[task_id]['result'] = result
                        self.running_tasks[task_id]['status'] = 'completed'
                    else:
                        self.running_tasks[task_id]['status'] = 'failed'
                        self.running_tasks[task_id]['error'] = "No operation found for tool"
                    
                    # Queue context update
                    await self.context_update_queue.put({
                        'status': 'completed',  # Fix: use consistent 'status' field
                        'type': 'tool_completed',
                        'task_id': task_id,
                        'tool_call': tool_call,
                        'result': self.running_tasks[task_id].get('result')
                    })
                    
                except Exception as e:
                    logger.error(f"Async tool execution failed: {e}")
                    self.running_tasks[task_id]['status'] = 'failed'
                    self.running_tasks[task_id]['error'] = str(e)
                    
                    # Queue error update
                    await self.context_update_queue.put({
                        'status': 'failed',  # Fix: use consistent 'status' field
                        'type': 'tool_failed',
                        'task_id': task_id,
                        'tool_call': tool_call,
                        'error': str(e)
                    })
            
            # Start the async task
            task = asyncio.create_task(async_execution())
            self.running_tasks[task_id]['task'] = task
            
            logger.info(f"Started async tool execution: {task_id}")
            return task_id
            
        except Exception as e:
            logger.error(f"Failed to start async tool execution: {e}")
            # Clean up on failure
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
            raise
    
    def _get_operation_for_tool(self, tool_call: Any) -> Optional[Any]:
        """
        Get operation for tool call using real ToolExecutor integration.

        Returns an async callable real_operation(**kwargs) that yields a ContextComponent
        (ToolResult/ScaffoldResult) when using ToolExecutor.execute_tool,
        or an arbitrary JSON-serializable dict if a custom operation is supplied.
        Callers should not assume a single return type; downstream normalization is expected.

        Args:
            tool_call: Tool call object with function.name and function.arguments

        Returns:
            Async operation callable that returns ContextComponent or dict, or None if no operation found
        """
        logger.info(f"_get_operation_for_tool called, tool_call type: {type(tool_call)}")
        logger.info(f"_get_operation_for_tool tool_call attributes: {dir(tool_call) if hasattr(tool_call, '__dict__') else 'no __dict__'}")

        if not self.agent or not hasattr(self.agent, 'tool_executor'):
            logger.warning("No agent or tool_executor")
            return None

        try:
            # Get tool name from call - handle both dict and object formats
            if isinstance(tool_call, dict):
                # Dict format: {'id': '...', 'function': {'name': '...', 'arguments': '...'}}
                function = tool_call.get('function', {})
                tool_name = function.get('name') if isinstance(function, dict) else None
                logger.info(f"Dict format - Got tool_name: {tool_name}")
            else:
                # Object format
                function = getattr(tool_call, 'function', None)
                tool_name = getattr(function, 'name', None) if function else None
                logger.info(f"Object format - Got tool_name: {tool_name}")

            if not tool_name:
                logger.warning(f"No tool_name found in tool_call: {tool_call}")
                return None
            
            # Use agent's tool executor to get the actual tool
            tool_executor = self.agent.tool_executor
            
            # Create async wrapper for tool execution
            # Note: ToolTaskLoop manages its own hook lifecycle, so use direct execution
            async def real_operation(**kwargs):
                try:
                    # Use existing provider translation infrastructure (DRY principle) 
                    if self.agent and hasattr(self.agent, 'provider') and hasattr(self.agent.provider, 'client') and hasattr(self.agent.provider.client, 'translator'):
                        try:
                            # Convert tool_call to the format the translator expects (OpenAI format)
                            if hasattr(tool_call, '__dict__'):
                                # Convert mock object to dict
                                tool_call_dict = {}
                                for key, value in tool_call.__dict__.items():
                                    if hasattr(value, '__dict__'):
                                        tool_call_dict[key] = value.__dict__ 
                                    else:
                                        tool_call_dict[key] = value
                            else:
                                # Already a dict or dict-like
                                tool_call_dict = dict(tool_call) if hasattr(tool_call, 'keys') else tool_call
                            
                            # Use provider's public translation method (no longer brittle private call)
                            translator = getattr(getattr(self.agent.provider, 'client', None), 'translator', None)
                            if translator and hasattr(translator, 'convert_tool_calls_to_provider_format'):
                                content_blocks = translator.convert_tool_calls_to_provider_format([tool_call_dict])
                            else:
                                # Fallback - will use manual conversion below
                                content_blocks = []
                            
                            # Extract ProviderToolCall from content blocks
                            provider_tool_call = None
                            for block in content_blocks:
                                if hasattr(block, 'tool_name'):  # It's a ProviderToolCall
                                    provider_tool_call = block
                                    break
                                    
                            if not provider_tool_call:
                                logger.warning("Provider translator failed to create ProviderToolCall, falling back")
                                raise ValueError("Translation failed")
                                
                        except Exception as e:
                            logger.warning(f"Provider translation failed: {e}, using fallback")
                            # Fall through to manual conversion below
                    
                    # Manual conversion fallback (handles both no translator and failed translation)
                    if 'provider_tool_call' not in locals() or provider_tool_call is None:
                        from egregore.core.messaging import ProviderToolCall
                        
                        # Extract tool call components properly
                        call_id = getattr(tool_call, 'id', 'unknown')
                        function = getattr(tool_call, 'function', None)
                        
                        if function:
                            function_name = getattr(function, 'name', 'unknown')
                            # Handle both string and dict arguments
                            if hasattr(function, 'arguments_dict') and function.arguments_dict:
                                parameters = function.arguments_dict
                            else:
                                try:
                                    arguments_str = getattr(function, 'arguments', '{}')
                                    parameters = json.loads(arguments_str) if arguments_str else {}
                                except:
                                    parameters = {}
                        else:
                            # Try direct attributes on tool_call
                            function_name = getattr(tool_call, 'name', 'unknown')
                            parameters = getattr(tool_call, 'parameters', {})
                        
                        provider_tool_call = ProviderToolCall(
                            tool_name=function_name,
                            tool_call_id=call_id,
                            parameters=parameters
                        )
                    
                    # Execute via tool executor with proper ProviderToolCall
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(None, tool_executor.execute_tool, provider_tool_call)
                    return result
                except Exception as e:
                    logger.error(f"Tool execution failed: {e}")
                    raise
            
            return real_operation
            
        except Exception as e:
            import traceback
            logger.error(f"Failed to get operation for tool: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    async def _execute_operation(self, operation: Any, tool_call: Any) -> Any:
        """
        Execute operation with tool call parameters.
        
        Returns the operation's raw result (ContextComponent or dict). No wrapping is 
        performed here by design. Higher-level orchestration layers (Agent or Orchestrator) 
        normalize to context components as needed.
        
        Args:
            operation: Operation callable (typically from _get_operation_for_tool)
            tool_call: Tool call object with function.name and function.arguments
            
        Returns:
            Raw operation result - ContextComponent when using ToolExecutor, dict for custom operations
        """
        try:
            # Extract parameters from tool call
            function = getattr(tool_call, 'function', None)
            if function:
                # Try to get arguments_dict first
                params = getattr(function, 'arguments_dict', {})
                if not params:
                    # Try to extract from arguments string (fallback)
                    args_str = getattr(function, 'arguments', '{}')
                    params = json.loads(args_str) if args_str else {}
            else:
                params = {}
            
            # Execute operation
            if asyncio.iscoroutinefunction(operation):
                result = await operation(**params)
            else:
                result = operation(**params)
            
            # Normalize mixed result shapes to ContextComponent ASAP when possible
            normalized_result = self._normalize_result_to_context_component(result, tool_call)
            return normalized_result
            
        except Exception as e:
            logger.error(f"Operation execution failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _normalize_result_to_context_component(self, result: Any, tool_call: Any) -> Any:
        """
        Normalize mixed result shapes to ContextComponent when possible.
        
        Args:
            result: Raw operation result (ContextComponent or dict)
            tool_call: Tool call object for context
            
        Returns:
            ContextComponent when possible, or dict for non-normalizable results
        """
        try:
            # Import here to avoid circular dependencies
            from ..context_management.pact.components.core import PACTCore as ContextComponent
            from ..tool_calling.context_components import ToolResult
            
            # If already a ContextComponent, return as-is
            if isinstance(result, ContextComponent):
                return result
            
            # If it's a dict with error structure, convert to ToolResult
            if isinstance(result, dict):
                # Extract tool information from tool_call
                tool_name = 'unknown'
                tool_call_id = 'unknown'
                
                if hasattr(tool_call, 'function') and hasattr(tool_call.function, 'name'):
                    tool_name = tool_call.function.name
                if hasattr(tool_call, 'id'):
                    tool_call_id = tool_call.id
                
                # Check if it's an error result
                if result.get('success') is False:
                    comp = ToolResult(
                        tool_name=tool_name,
                        tool_call_id=tool_call_id,
                        content=str(result.get('error', 'Unknown error')),
                        success=False,
                        error_message=str(result.get('error', 'Unknown error')),
                        offset=0  # Tools belong in message container with core content
                    )
                    # Attach metadata details safely
                    try:
                        comp.metadata.source = 'task_loop'
                        comp.metadata.created_at = datetime.now()
                        aux = getattr(comp.metadata, 'aux', {}) or {}
                        aux.update({'normalized_from': 'dict_error', 'execution_method': 'task_loop'})
                        comp.metadata.aux = aux
                    except Exception:
                        pass
                    return comp
                else:
                    # Convert successful dict result to ToolResult
                    content = str(result.get('result', result))
                    comp = ToolResult(
                        tool_name=tool_name,
                        tool_call_id=tool_call_id,
                        content=content,
                        success=True,
                        offset=0  # Tools belong in message container with core content
                    )
                    try:
                        comp.metadata.source = 'task_loop'
                        comp.metadata.created_at = datetime.now()
                        aux = getattr(comp.metadata, 'aux', {}) or {}
                        aux.update({'normalized_from': 'dict_success', 'execution_method': 'task_loop'})
                        comp.metadata.aux = aux
                    except Exception:
                        pass
                    return comp
            
            # For other types, convert to string content in ToolResult
            tool_name = 'unknown'
            tool_call_id = 'unknown'
            
            if hasattr(tool_call, 'function') and hasattr(tool_call.function, 'name'):
                tool_name = tool_call.function.name
            if hasattr(tool_call, 'id'):
                tool_call_id = tool_call.id
            
            comp = ToolResult(
                tool_name=tool_name,
                tool_call_id=tool_call_id,
                content=str(result),
                success=True,
                offset=1  # PACT positioning for post-message context
            )
            try:
                comp.metadata.source = 'task_loop'
                comp.metadata.created_at = datetime.now()
                aux = getattr(comp.metadata, 'aux', {}) or {}
                aux.update({'normalized_from': type(result).__name__, 'execution_method': 'task_loop'})
                comp.metadata.aux = aux
            except Exception:
                pass
            return comp
            
        except Exception as e:
            logger.warning(f"Failed to normalize result to ContextComponent: {e}")
            # Return original result if normalization fails
            return result
    
    async def execute_tool_streaming(self, tool_call: Any) -> AsyncIterator[Dict[str, Any]]:
        """
        Execute tool with streaming progress updates.

        Args:
            tool_call: Tool call object to execute

        Yields:
            Progress updates and final result
        """
        task_id = f"stream_{getattr(tool_call, 'id', uuid.uuid4().hex[:8])}_{uuid.uuid4().hex[:8]}"

        logger.info(f"execute_tool_streaming called for task {task_id}")

        try:
            # Create task tracking record
            task_info = {
                'task_id': task_id,
                'tool_call': tool_call,
                'type': 'streaming',
                'started_at': datetime.now(),
                'status': 'started'
            }
            
            # Track the task
            self.running_tasks[task_id] = task_info
            
            # Emit tool started hook
            await self._emit_tool_started_hook(task_id, tool_call)
            
            # Create result queue for streaming
            result_queue = asyncio.Queue(maxsize=50)  # Bounded streaming results
            self.streaming_results[task_id] = result_queue
            
            # Yield start event
            logger.info(f"Yielding start event for task {task_id}")
            yield {
                'type': 'started',
                'task_id': task_id,
                'tool': self._safe_get_tool_name(tool_call)
            }
            logger.info(f"Start event yielded for task {task_id}")
            
            # Create async task for execution with progress updates
            async def streaming_execution():
                try:
                    logger.info(f"streaming_execution started for {task_id}")
                    # Update status
                    self.running_tasks[task_id]['status'] = 'executing'

                    # Send progress update
                    await result_queue.put({
                        'type': 'progress',
                        'task_id': task_id,
                        'message': 'Starting tool execution'
                    })
                    logger.info(f"Put progress update in queue for {task_id}")

                    # Get operation for tool
                    logger.info(f"Getting operation for tool {task_id}")
                    operation = self._get_operation_for_tool(tool_call)
                    logger.info(f"Got operation for tool {task_id}: {operation is not None}")
                    
                    if operation:
                        # Send progress update  
                        await result_queue.put({
                            'type': 'progress',
                            'task_id': task_id,
                            'message': 'Executing operation'
                        })
                        
                        # Execute operation
                        result = await self._execute_operation(operation, tool_call)
                        
                        # Send result
                        await result_queue.put({
                            'type': 'result',
                            'task_id': task_id,
                            'result': result
                        })
                        
                        self.running_tasks[task_id]['result'] = result
                        self.running_tasks[task_id]['status'] = 'completed'
                    else:
                        await result_queue.put({
                            'type': 'error',
                            'task_id': task_id,
                            'error': "No operation found for tool"
                        })
                        
                        self.running_tasks[task_id]['status'] = 'failed'
                        self.running_tasks[task_id]['error'] = "No operation found for tool"
                    
                    # Signal completion with result
                    await result_queue.put({
                        'type': 'completed',
                        'task_id': task_id,
                        'result': self.running_tasks[task_id].get('result')
                    })
                    
                    # Queue context update
                    await self.context_update_queue.put({
                        'type': 'tool_streaming_completed',
                        'task_id': task_id,
                        'tool_call': tool_call,
                        'result': self.running_tasks[task_id].get('result')
                    })
                    
                except Exception as e:
                    logger.error(f"Streaming tool execution failed: {e}")
                    await result_queue.put({
                        'type': 'error',
                        'task_id': task_id,
                        'error': str(e)
                    })
                    
                    self.running_tasks[task_id]['status'] = 'failed'
                    self.running_tasks[task_id]['error'] = str(e)
                    
                    # Queue error update
                    await self.context_update_queue.put({
                        'type': 'tool_streaming_failed',
                        'task_id': task_id,
                        'tool_call': tool_call,
                        'error': str(e)
                    })
            
            # Start the async task
            task = asyncio.create_task(streaming_execution())
            self.running_tasks[task_id]['task'] = task
            
            # Stream results as they come
            try:
                while True:
                    try:
                        # Wait for result with timeout
                        result = await asyncio.wait_for(result_queue.get(), timeout=30.0)
                        yield result
                        
                        # Break on completion or error
                        if result['type'] in ['completed', 'error']:
                            break
                            
                    except asyncio.TimeoutError:
                        yield {
                            'type': 'timeout',
                            'task_id': task_id,
                            'message': 'Tool execution timed out'
                        }
                        break
                        
            finally:
                # Cleanup
                if task_id in self.streaming_results:
                    del self.streaming_results[task_id]
                
                # Cancel task if still running
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                        
                logger.info(f"Completed streaming tool execution: {task_id}")
                
        except Exception as e:
            logger.error(f"Failed to start streaming tool execution: {e}")
            # Clean up on failure
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
            if task_id in self.streaming_results:
                del self.streaming_results[task_id]
            
            yield {
                'type': 'error',
                'task_id': task_id,
                'error': str(e)
            }
    
    async def execute_scaffold_operation_async(self, scaffold_instance: Any, operation_name: str, **kwargs) -> str:
        """
        Execute scaffold operation asynchronously.
        
        Args:
            scaffold_instance: Scaffold instance to execute operation on
            operation_name: Name of the scaffold operation
            **kwargs: Operation parameters
            
        Returns:
            task_id: Unique identifier for tracking the async operation
        """
        task_id = f"scaffold_{getattr(scaffold_instance, 'type', 'unknown')}_{operation_name}_{uuid.uuid4().hex[:8]}"
        
        try:
            # Create task tracking record with scaffold metadata
            task_info = {
                'task_id': task_id,
                'scaffold_instance': scaffold_instance,
                'operation_name': operation_name,
                'operation_params': kwargs,
                'type': 'scaffold_async',
                'started_at': datetime.now(),
                'status': 'started',
                'metadata': {
                    'scaffold_type': getattr(scaffold_instance, 'type', 'unknown'),
                    'scaffold_id': getattr(scaffold_instance, 'scaffold_id', f"{getattr(scaffold_instance, 'type', 'unknown')}_{id(scaffold_instance)}"),
                    'operation_name': operation_name
                }
            }
            
            # Track the task
            self.running_tasks[task_id] = task_info
            
            # Create async task for execution
            async def async_scaffold_execution():
                try:
                    # Update status
                    self.running_tasks[task_id]['status'] = 'executing'
                    
                    # Get scaffold operation method
                    operation = getattr(scaffold_instance, operation_name, None)
                    
                    if operation and callable(operation):
                        # Execute scaffold operation
                        if asyncio.iscoroutinefunction(operation):
                            result = await operation(**kwargs)
                        else:
                            result = operation(**kwargs)
                        
                        self.running_tasks[task_id]['result'] = result
                        self.running_tasks[task_id]['status'] = 'completed'
                        
                        # Queue context update for scaffold state change
                        await self.context_update_queue.put({
                            'type': 'scaffold_operation_completed',
                            'task_id': task_id,
                            'scaffold_instance': scaffold_instance,
                            'operation_name': operation_name,
                            'result': result,
                            'metadata': task_info['metadata']
                        })
                        
                    else:
                        error_msg = f"Operation '{operation_name}' not found on scaffold"
                        self.running_tasks[task_id]['status'] = 'failed'
                        self.running_tasks[task_id]['error'] = error_msg
                        
                        # Queue error update
                        await self.context_update_queue.put({
                            'type': 'scaffold_operation_failed',
                            'task_id': task_id,
                            'scaffold_instance': scaffold_instance,
                            'operation_name': operation_name,
                            'error': error_msg,
                            'metadata': task_info['metadata']
                        })
                    
                except Exception as e:
                    logger.error(f"Async scaffold operation failed: {e}")
                    self.running_tasks[task_id]['status'] = 'failed'
                    self.running_tasks[task_id]['error'] = str(e)
                    
                    # Queue error update
                    await self.context_update_queue.put({
                        'type': 'scaffold_operation_failed',
                        'task_id': task_id,
                        'scaffold_instance': scaffold_instance,
                        'operation_name': operation_name,
                        'error': str(e),
                        'metadata': task_info['metadata']
                    })
            
            # Start the async task
            task = asyncio.create_task(async_scaffold_execution())
            self.running_tasks[task_id]['task'] = task
            
            logger.info(f"Started async scaffold operation: {task_info['metadata']['scaffold_type']}.{operation_name} ({task_id})")
            return task_id
            
        except Exception as e:
            logger.error(f"Failed to start async scaffold operation: {e}")
            # Clean up on failure
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
            raise
    
    async def start(self):
        """Start background processors for operation and context update processing."""
        logger.info("Starting ToolTaskLoop background processors...")
        
        # Start background processors
        self._operation_processor_task = asyncio.create_task(self._process_operations())
        self._context_processor_task = asyncio.create_task(self._process_context_updates())
        
        logger.info("ToolTaskLoop background processors started")
    
    def _safe_get_tool_name(self, tool_call: Any) -> str:
        """
        Safely extract tool name from tool_call using dict-style access with guards.
        
        Args:
            tool_call: Tool call object or dict
            
        Returns:
            Tool name or 'unknown' as fallback
        """
        # Use recommended pattern: dict-style access with guards
        fn = (tool_call or {}).get('function') or {}
        return fn.get('name', 'unknown')
    
    def _safe_get_tool_params(self, tool_call: Any) -> Dict[str, Any]:
        """
        Safely extract tool parameters from tool_call using dict-style access with guards.
        
        Args:
            tool_call: Tool call object or dict
            
        Returns:
            Tool parameters dict or empty dict as fallback
        """
        # Use recommended pattern: dict-style access with guards  
        fn = (tool_call or {}).get('function') or {}
        return fn.get('arguments_dict', {})

    async def await_task_completion(self, task_id: str) -> Dict[str, Any]:
        """
        Await completion of a specific task by awaiting its asyncio task.
        
        Args:
            task_id: Task ID to await completion for
            
        Returns:
            Task info with result/error after completion
            
        Raises:
            KeyError: If task_id is not found
        """
        if task_id not in self.running_tasks:
            raise KeyError(f"Task {task_id} not found in running tasks")
        
        task_info = self.running_tasks[task_id]
        
        # If task has an asyncio task, await it directly
        if 'task' in task_info:
            try:
                await task_info['task']
            except Exception as e:
                # Task may have failed, but we still return the task_info
                logger.debug(f"Task {task_id} completed with exception: {e}")
        
        # Return final task info
        return self.running_tasks[task_id]

    async def shutdown(self):
        """Graceful shutdown of background processors."""
        if self._is_shutdown:
            return
            
        logger.info("Shutting down ToolTaskLoop...")
        self._is_shutdown = True
        
        # Signal shutdown first
        self._shutdown_event.set()
        
        # Cancel background processors IMMEDIATELY before anything else
        tasks_to_cancel = []
        
        if hasattr(self, '_operation_processor_task') and self._operation_processor_task:
            if not self._operation_processor_task.done():
                self._operation_processor_task.cancel()
                tasks_to_cancel.append(self._operation_processor_task)
        
        if hasattr(self, '_context_processor_task') and self._context_processor_task:
            if not self._context_processor_task.done():
                self._context_processor_task.cancel()
                tasks_to_cancel.append(self._context_processor_task)
        
        # Wait for background tasks to be cancelled immediately
        if tasks_to_cancel:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*tasks_to_cancel, return_exceptions=True),
                    timeout=0.5
                )
            except asyncio.TimeoutError:
                pass  # Continue anyway
            except Exception:
                pass  # Ignore cancellation exceptions
        
        # Now cancel all running tool tasks
        await self.cancel_all_operations()
        
        # Clean up queues to prevent memory leaks  
        await self._cleanup_queues()
        
        # Clear task references
        if hasattr(self, '_operation_processor_task'):
            self._operation_processor_task = None
        if hasattr(self, '_context_processor_task'):
            self._context_processor_task = None
        
        logger.info("ToolTaskLoop shutdown complete")
    
    async def _cleanup_queues(self):
        """Clean up queues to prevent memory leaks."""
        try:
            # Drain operation queue
            while not self.operation_queue.empty():
                try:
                    self.operation_queue.get_nowait()
                    self.operation_queue.task_done()
                except asyncio.QueueEmpty:
                    break
            
            # Drain context update queue
            while not self.context_update_queue.empty():
                try:
                    self.context_update_queue.get_nowait()
                    self.context_update_queue.task_done()
                except asyncio.QueueEmpty:
                    break
            
            # Clean up streaming results
            for task_id, result_queue in list(self.streaming_results.items()):
                while not result_queue.empty():
                    try:
                        result_queue.get_nowait()
                        result_queue.task_done()
                    except asyncio.QueueEmpty:
                        break
                del self.streaming_results[task_id]
            
            # Clear all tracking structures
            self.running_tasks.clear()
            
            logger.debug("Queue cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during queue cleanup: {e}")
    
    async def _process_operations(self):
        """Background processor for operation queue (placeholder for future use)."""
        try:
            while not self._shutdown_event.is_set():
                try:
                    # Wait for operation with timeout
                    operation = await asyncio.wait_for(
                        self.operation_queue.get(), 
                        timeout=1.0
                    )
                    
                    # Process operation (placeholder)
                    logger.debug(f"Processing queued operation: {operation}")
                    
                except asyncio.TimeoutError:
                    # Check for shutdown periodically
                    continue
                    
        except asyncio.CancelledError:
            logger.debug("Operation processor cancelled")
        except Exception as e:
            logger.error(f"Operation processor error: {e}")
    
    async def _process_context_updates(self):
        """Background processor for context update queue."""
        try:
            while not self._shutdown_event.is_set():
                try:
                    # Wait for context update with timeout
                    update = await asyncio.wait_for(
                        self.context_update_queue.get(), 
                        timeout=1.0
                    )
                    
                    # Process context update
                    await self._handle_context_update(update)
                    
                except asyncio.TimeoutError:
                    # Check for shutdown periodically
                    continue
                    
        except asyncio.CancelledError:
            logger.debug("Context update processor cancelled")
        except Exception as e:
            logger.error(f"Context update processor error: {e}")
    
    async def _emit_tool_started_hook(self, task_id: str, tool_call: Any) -> None:
        """
        Emit ON_TOOL_TASK_STARTED hook and add to context update queue.
        
        Args:
            task_id: Task identifier
            tool_call: Tool call object
        """
        try:
            # Get tool name for hook
            tool_name = 'unknown'
            if hasattr(tool_call, 'function') and hasattr(tool_call.function, 'name'):
                tool_name = tool_call.function.name
            
            # Emit hook if agent available
            if self.agent and hasattr(self.agent, '_hooks_instance'):
                try:
                    from egregore.core.agent.hooks.execution import HookType, ToolExecContext
                    
                    # Create proper hook context
                    context = ToolExecContext(
                        agent_id=self.agent.agent_id,
                        agent=self.agent,
                        tool_name=tool_name,
                        tool_params={},  # No params yet at start time
                        metadata={'timestamp': datetime.now().isoformat(), 'task_id': task_id}
                    )
                    
                    # Execute hook through proper hooks system
                    await self.agent._hooks_instance.execute_hooks_async(
                        HookType.ON_TOOL_TASK_STARTED,
                        context
                    )
                except Exception as e:
                    logger.error(f"Failed to execute tool started hook: {e}")
            
            # Add to context update queue for UI integration
            await self.context_update_queue.put({
                'type': 'tool_started',
                'task_id': task_id,
                'tool_name': tool_name,
                'tool_call': tool_call,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Failed to emit tool started hook: {e}")
    
    async def _handle_context_update(self, update: Dict[str, Any]):
        """
        Handle context update with hook integration.
        
        Args:
            update: Context update dictionary with type and data
        """
        try:
            update_type = update.get('type', 'unknown')
            task_id = update.get('task_id')
            
            logger.debug(f"Handling context update: {update_type} for task {task_id}")
            
            # Integrate with existing hook system if agent is available
            if self.agent and hasattr(self.agent, '_hooks_instance'):
                hooks = self.agent._hooks_instance
                
                # Execute appropriate hooks based on update type
                if update_type.startswith('tool_'):
                    # Tool-related updates
                    if update_type in ['tool_completed', 'tool_streaming_completed']:
                        # Execute tool completion hooks
                        from egregore.core.agent.hooks.execution import HookType
                        from egregore.core.agent.hooks.execution_contexts import ContextFactory
                        
                        # Create hook context
                        hook_context = ContextFactory.create_tool_context(
                            agent_id=getattr(self.agent, 'agent_id', 'unknown'),
                            tool_name=self._safe_get_tool_name(update.get('tool_call')),
                            tool_params=self._safe_get_tool_params(update.get('tool_call')),
                            agent=self.agent,
                            tool_result=update.get('result'),
                            execution_id=task_id
                        )
                        
                        # Execute async completion hook
                        await hooks.execute_hooks_async(HookType.ON_TOOL_TASK_COMPLETED, hook_context)
                        
                    elif update_type in ['tool_failed', 'tool_streaming_failed']:
                        # Execute tool failure hooks
                        from egregore.core.agent.hooks.execution import HookType
                        from egregore.core.agent.hooks.execution_contexts import ContextFactory
                        
                        # Create error context
                        hook_context = ContextFactory.create_tool_context(
                            agent_id=getattr(self.agent, 'agent_id', 'unknown'),
                            tool_name=self._safe_get_tool_name(update.get('tool_call')),
                            tool_params=self._safe_get_tool_params(update.get('tool_call')),
                            agent=self.agent,
                            execution_id=task_id,
                            error=Exception(update.get('error', 'Unknown error'))
                        )
                        
                        # Execute async failure hook
                        await hooks.execute_hooks_async(HookType.ON_TOOL_TASK_FAILED, hook_context)
                
                elif update_type.startswith('scaffold_'):
                    # Scaffold-related updates
                    if update_type == 'scaffold_operation_completed':
                        # Execute scaffold completion hooks
                        from egregore.core.agent.hooks.execution import HookType
                        from egregore.core.agent.hooks.execution_contexts import ContextFactory
                        
                        # Create scaffold context
                        hook_context = ContextFactory.create_scaffold_context(
                            agent_id=getattr(self.agent, 'agent_id', 'unknown'),
                            scaffold_type=update.get('metadata', {}).get('scaffold_type', 'unknown'),
                            scaffold_id=update.get('metadata', {}).get('scaffold_id', 'unknown'),
                            operation_name=update.get('operation_name', 'unknown'),
                            agent=self.agent,
                            execution_id=task_id,
                            operation_result=update.get('result')
                        )
                        
                        # Execute scaffold operation completed hook
                        await hooks.execute_hooks_async(HookType.ON_SCAFFOLD_OPERATION_COMPLETED, hook_context)
            
            # Update agent context with real implementation
            if self.agent and hasattr(self.agent, 'context'):
                try:
                    # Create ToolResult from completed tool execution
                    if update_type == 'tool_completed':
                        from egregore.core.tool_calling.context_components import ToolResult

                        tool_call = update.get('tool_call', {})
                        result = update.get('result', {})

                        tool_result_component = ToolResult(
                            tool_name=self._safe_get_tool_name(tool_call),
                            tool_call_id=tool_call.get('id', 'unknown'),
                            content=str(result),
                            success=True,
                            offset=1  # Post-message position
                        )

                        # Add to active message context (use _context for internal Context object)
                        context = self.agent._context if hasattr(self.agent, '_context') else self.agent.context
                        # Use pact_update with append mode to trigger hooks for automatic registration
                        context.pact_update("d0,0", tool_result_component, mode="append")

                    elif update_type == 'tool_failed':
                        from egregore.core.tool_calling.context_components import ToolResult

                        tool_call = update.get('tool_call', {})
                        error = update.get('error', 'Unknown error')

                        tool_result_component = ToolResult(
                            tool_name=self._safe_get_tool_name(tool_call),
                            tool_call_id=tool_call.get('id', 'unknown'),
                            content=f"Error: {error}",
                            success=False,
                            error_message=error,
                            offset=1
                        )

                        # Add to active message context (use _context for internal Context object)
                        context = self.agent._context if hasattr(self.agent, '_context') else self.agent.context
                        # Use pact_update with append mode to trigger hooks for automatic registration
                        context.pact_update("d0,0", tool_result_component, mode="append")

                    # Create snapshot after context update (use _context for internal Context object)
                    if hasattr(self.agent, 'history') and self.agent.history:
                        context = self.agent._context if hasattr(self.agent, '_context') else self.agent.context
                        self.agent.history.create_snapshot(
                            context=context,
                            trigger=f"tool_task_loop_{update_type}",
                            execution_id=getattr(self.agent.controller, 'execution_id', None),
                            metadata={
                                'task_id': update.get('task_id'),
                                'tool_call_id': update.get('tool_call', {}).get('id'),
                                'update_type': update_type
                            }
                        )
                    
                    logger.debug(f"Updated agent context for: {update_type}")
                    
                except Exception as e:
                    logger.error(f"Error updating context for {update_type}: {e}")
            
        except Exception as e:
            logger.error(f"Error handling context update: {e}")
    
    async def cancel_operation(self, task_id: str) -> bool:
        """
        Cancel a specific operation.
        
        Args:
            task_id: Task ID to cancel
            
        Returns:
            True if cancelled successfully
        """
        if task_id not in self.running_tasks:
            return False
        
        try:
            task_info = self.running_tasks[task_id]
            
            # Cancel the task if it exists
            if 'task' in task_info:
                task = task_info['task']
                task.cancel()
                
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            # Update status
            task_info['status'] = 'cancelled'
            
            # Clean up streaming results if present
            if task_id in self.streaming_results:
                del self.streaming_results[task_id]
            
            logger.info(f"Cancelled operation: {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling operation {task_id}: {e}")
            return False
    
    async def cancel_all_operations(self) -> int:
        """
        Cancel all running operations.
        
        Returns:
            Number of operations cancelled
        """
        task_ids = list(self.running_tasks.keys())
        cancelled_count = 0
        
        for task_id in task_ids:
            if await self.cancel_operation(task_id):
                cancelled_count += 1
        
        logger.info(f"Cancelled {cancelled_count} operations")
        return cancelled_count
