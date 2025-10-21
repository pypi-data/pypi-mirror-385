"""
StreamingOrchestrator - Streaming interface layer for unified tool execution.

Provides streaming tool detection and chunk processing that integrates with
ToolTaskLoop for unified async tool execution with real-time progress updates.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, AsyncIterator, List, TYPE_CHECKING
from dataclasses import dataclass, field
from datetime import datetime

if TYPE_CHECKING:
    from .base import Agent
    from .tool_task_loop import ToolTaskLoop
    from egregore.core.messaging import ProviderResponse

logger = logging.getLogger(__name__)


@dataclass
class StreamingState:
    """State management for streaming orchestrator."""
    active_tool_calls: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    response_accumulator: Dict[str, Any] = field(default_factory=dict)
    tool_accumulators: Dict[str, Any] = field(default_factory=dict)
    tool_results: Dict[str, List[Any]] = field(default_factory=dict)  # Store completed tool results
    active_tool_tasks: Dict[str, Any] = field(default_factory=dict)  # Track background tool execution tasks
    streaming_active: bool = False
    turn_id: Optional[str] = None


class StreamingOrchestrator:
    """
    Streaming interface layer that integrates with ToolTaskLoop.
    
    Provides:
    - Real-time tool call detection from streaming chunks
    - Tool call accumulation and completion detection
    - Integration with ToolTaskLoop for async execution
    - Response building with tool results
    - Complete PACT lifecycle integration
    """
    
    def __init__(self, agent: Optional['Agent'] = None, task_loop: Optional['ToolTaskLoop'] = None):
        """
        Initialize StreamingOrchestrator.
        
        Args:
            agent: Agent instance for context and execution
            task_loop: ToolTaskLoop instance for async tool execution
        """
        self.agent = agent
        self.task_loop = task_loop
        
        # Streaming state management
        self.state = StreamingState()
        
        # Tool execution tracking with stream queues for real-time progress
        self.active_tool_streams: Dict[str, asyncio.Queue] = {}
        
        logger.info(f"StreamingOrchestrator initialized for agent {getattr(agent, 'agent_id', 'unknown')}")
    
    async def process_stream_chunk(self, chunk_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process streaming chunk and return response if available.
        
        Accepts normalized chunk dicts (after provider translation) with possible keys: 
        content/delta, tool_calls (list of OpenAI-style function-call deltas), 
        finish_reason/usage/model.
        
        Args:
            chunk_data: Normalized chunk dict from provider with content/tool_calls/metadata
            
        Returns:
            Complete response dict if available, None if still processing.
            Final response contains content_blocks, tool_calls, and metadata on completion.
        """
        if not self.state.streaming_active:
            logger.warning("Received chunk data but streaming is not active")
            return None
        
        chunk_type = self._determine_chunk_type(chunk_data)
        logger.debug(f"Processing chunk type: {chunk_type}")
        
        if chunk_type == 'content':
            # Add content to response accumulator
            if 'response_accumulator' not in self.state.response_accumulator:
                turn_id = self.state.turn_id or f"turn_{datetime.now().isoformat()}"
                self.state.response_accumulator['response_accumulator'] = StreamResponseAccumulator(turn_id)
            
            accumulator = self.state.response_accumulator['response_accumulator']
            accumulator.add_content_chunk(chunk_data)
            
        elif chunk_type == 'tool_delta':
            # Ensure response accumulator exists for tool-only responses
            if 'response_accumulator' not in self.state.response_accumulator:
                turn_id = self.state.turn_id or f"turn_{datetime.now().isoformat()}"
                self.state.response_accumulator['response_accumulator'] = StreamResponseAccumulator(turn_id)

            # Process tool call delta
            return await self._process_tool_delta(chunk_data)
            
        elif chunk_type == 'metadata':
            # Handle metadata
            if 'response_accumulator' in self.state.response_accumulator:
                accumulator = self.state.response_accumulator['response_accumulator']
                
                model_info = chunk_data.get('model')
                usage_info = chunk_data.get('usage')
                finish_reason = chunk_data.get('finish_reason')
                
                accumulator.set_metadata(
                    model_info=model_info,
                    usage_info=usage_info,
                    finish_reason=finish_reason
                )
        
        return None
    
    def _determine_chunk_type(self, chunk_data: Dict[str, Any]) -> str:
        """
        Determine the type of streaming chunk.
        
        Args:
            chunk_data: Raw chunk data
            
        Returns:
            Chunk type: 'content', 'tool_delta', 'metadata', or 'unknown'
        """
        # Check for content
        if 'content' in chunk_data and chunk_data['content']:
            return 'content'
        
        # Check for tool call deltas
        if 'tool_calls' in chunk_data:
            return 'tool_delta'
        
        # Check for metadata (finish_reason, usage, model)
        if any(key in chunk_data for key in ['finish_reason', 'usage', 'model']):
            return 'metadata'
        
        return 'unknown'
    
    async def _process_tool_delta(self, chunk_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process tool call delta and execute if complete.

        Args:
            chunk_data: Chunk containing tool call delta (flattened format with tool_call_id, function_name, arguments_delta)

        Returns:
            Response dict if tool execution completed, None otherwise
        """
        # Check for flattened tool delta format (tool_call_id, function_name, arguments_delta)
        tool_call_id = chunk_data.get('tool_call_id')
        if not tool_call_id:
            logger.debug(f"No tool_call_id in chunk_data. tool_call_id={tool_call_id}, function_name={chunk_data.get('function_name')}, arguments_delta={chunk_data.get('arguments_delta')}, tool_call_state={chunk_data.get('tool_call_state')}")
            return None

        logger.debug(f"Processing tool call delta for id: {tool_call_id}")

        # Get or create accumulator for this tool call
        if tool_call_id not in self.state.tool_accumulators:
            self.state.tool_accumulators[tool_call_id] = StreamingToolAccumulator(tool_call_id)
            logger.debug(f"Created new tool accumulator for {tool_call_id}")

        accumulator = self.state.tool_accumulators[tool_call_id]

        # Handle flattened format - convert to expected structure for accumulator
        function_name = chunk_data.get('function_name', '')
        arguments_delta = chunk_data.get('arguments_delta', '')
        logger.debug(f"Building converted_chunk: function_name={function_name}, arguments_delta={arguments_delta}")

        converted_chunk = {
            'tool_calls': [{
                'id': tool_call_id,
                'function': {
                    'name': function_name,
                    'arguments': arguments_delta
                }
            }]
        }

        is_complete = accumulator.add_delta(converted_chunk)
        logger.debug(f"Tool accumulator state: complete={is_complete}, function={accumulator.function_name}, args_len={len(accumulator.arguments_str)}")

        if is_complete:
            # Tool call is complete, execute it
            complete_tool_call = accumulator.get_tool_call()
            if complete_tool_call:
                logger.info(f"Tool call {tool_call_id} complete: {complete_tool_call['function']['name']}")

                # Add to active tool calls for execution
                self.state.active_tool_calls[tool_call_id] = complete_tool_call

                # Add to response accumulator
                if 'response_accumulator' not in self.state.response_accumulator:
                    turn_id = self.state.turn_id or f"turn_{datetime.now().isoformat()}"
                    self.state.response_accumulator['response_accumulator'] = StreamResponseAccumulator(turn_id)

                accumulator_resp = self.state.response_accumulator['response_accumulator']
                accumulator_resp.add_tool_call(complete_tool_call)

                # Execute via task loop if available
                if self.task_loop and hasattr(self.task_loop, 'execute_tool_streaming'):
                    try:
                        # Create stream queue for this tool
                        if tool_call_id not in self.active_tool_streams:
                            self.active_tool_streams[tool_call_id] = asyncio.Queue()

                        # Start async execution
                        async def execute_and_collect():
                            if self.task_loop:  # Additional safety check inside nested function
                                logger.info(f"Starting tool execution for {tool_call_id}")
                                async for progress in self.task_loop.execute_tool_streaming(complete_tool_call):
                                    progress_type = progress.get('type')
                                    logger.info(f"Tool {tool_call_id} progress: {progress_type}")

                                    # Check if execution completed
                                    if progress_type == 'completed':
                                        result = progress.get('result')
                                        logger.info(f"Got completed progress with result type: {type(result).__name__}")
                                        accumulator_resp.add_tool_result(tool_call_id, result)

                                        # Store result in state for fusion
                                        if tool_call_id not in self.state.tool_results:
                                            self.state.tool_results[tool_call_id] = []
                                        self.state.tool_results[tool_call_id].append(result)

                                        logger.info(f"Tool {tool_call_id} execution completed, result stored: {result is not None}")
                                        return result

                            logger.warning(f"Tool execution completed without result for {tool_call_id}")
                            return None

                        # Start background execution and track the task
                        task = asyncio.create_task(execute_and_collect())

                        # Store task for finalization to await
                        self.state.active_tool_tasks[tool_call_id] = task
                        logger.debug(f"Stored background task for tool {tool_call_id}")

                    except Exception as e:
                        logger.error(f"Tool execution failed for {tool_call_id}: {e}")
                        # Add error result
                        error_result = {'error': str(e), 'tool_call_id': tool_call_id}
                        accumulator_resp.add_tool_result(tool_call_id, error_result)

        return None
    
    
    async def start_turn(self, turn_id: Optional[str] = None):
        """
        Start a new streaming turn.
        
        Args:
            turn_id: Optional turn identifier
        """
        self.state.turn_id = turn_id or f"turn_{datetime.now().isoformat()}"
        self.state.streaming_active = True
        self.state.active_tool_calls.clear()
        self.state.response_accumulator.clear()
        self.state.tool_accumulators.clear()
        
        logger.info(f"Started streaming turn: {self.state.turn_id}")
    
    async def end_turn(self):
        """End the current streaming turn."""
        self.state.streaming_active = False
        
        # Clean up any remaining streams
        for stream_queue in self.active_tool_streams.values():
            while not stream_queue.empty():
                try:
                    stream_queue.get_nowait()
                except:
                    break
        
        self.active_tool_streams.clear()
        
        logger.info(f"Ended streaming turn: {self.state.turn_id}")
        self.state.turn_id = None
    
    def is_streaming_active(self) -> bool:
        """Check if streaming is currently active."""
        return self.state.streaming_active
    
    def get_active_tool_count(self) -> int:
        """Get count of currently active tool calls."""
        return len(self.state.active_tool_calls)
    
    def get_streaming_stats(self) -> Dict[str, Any]:
        """Get current streaming statistics."""
        return {
            'turn_id': self.state.turn_id,
            'streaming_active': self.state.streaming_active,
            'active_tool_calls': len(self.state.active_tool_calls),
            'tool_accumulators': len(self.state.tool_accumulators),
            'response_parts': len(self.state.response_accumulator),
            'active_streams': len(self.active_tool_streams)
        }
    
    async def _collect_tool_results(self) -> AsyncIterator[Dict[str, Any]]:
        """
        Collect tool execution results from active streams.
        
        Yields:
            Tool execution progress and results
        """
        if not self.active_tool_streams:
            return
        
        logger.debug(f"Collecting results from {len(self.active_tool_streams)} active streams")
        
        # Create tasks for all active streams
        stream_tasks = []
        for tool_call_id, queue in self.active_tool_streams.items():
            
            async def collect_from_stream(tcid: str, q: asyncio.Queue):
                try:
                    while True:
                        try:
                            # Wait for result with timeout
                            result = await asyncio.wait_for(q.get(), timeout=0.1)
                            yield {'tool_call_id': tcid, 'progress': result}
                            
                            # If completed, stop collecting from this stream
                            if result.get('type') == 'completed':
                                break
                                
                        except asyncio.TimeoutError:
                            # No more results available right now
                            break
                            
                except Exception as e:
                    logger.error(f"Error collecting from stream {tcid}: {e}")
                    yield {'tool_call_id': tcid, 'error': str(e)}
            
            stream_tasks.append(collect_from_stream(tool_call_id, queue))
        
        # Collect from all streams
        logger.debug(f"StreamingOrchestrator: Collecting from {len(stream_tasks)} stream tasks")
        for i, task in enumerate(stream_tasks):
            logger.debug(f"StreamingOrchestrator: Processing stream task {i}, type: {type(task)}, is_none: {task is None}")
            if task is not None and hasattr(task, '__aiter__'):
                async for result in task:
                    logger.debug(f"StreamingOrchestrator: Got result from stream task {i}: {type(result)}")
                    yield result
            else:
                logger.warning(f"StreamingOrchestrator: Stream task {i} is None or not async iterable: {type(task)}")
    
    async def finalize_turn(self) -> Optional['ProviderResponse']:
        """
        Finalize the current turn and return complete response.
        
        Returns:
            Complete ProviderResponse object or None if not ready
        """
        if not self.state.streaming_active:
            logger.warning("Cannot finalize turn - streaming not active")
            return None
        
        logger.info(f"Finalizing turn: {self.state.turn_id}")

        # Wait for any pending tool execution tasks
        if self.state.active_tool_tasks:
            pending_tasks = list(self.state.active_tool_tasks.values())
            logger.info(f"Awaiting {len(pending_tasks)} pending tool execution tasks")
            try:
                # Await all tool execution tasks with timeout
                await asyncio.wait_for(
                    asyncio.gather(*pending_tasks, return_exceptions=True),
                    timeout=30.0  # 30 second timeout for tool execution
                )
                logger.info(f"All {len(pending_tasks)} tool tasks completed")
            except asyncio.TimeoutError:
                logger.warning(f"Tool execution tasks timed out after 30 seconds")
            except Exception as e:
                logger.error(f"Error awaiting tool tasks: {e}")
        else:
            logger.debug("No pending tool execution tasks to await")

        # Wait for any pending tool executions
        pending_tools = len(self.state.active_tool_calls)
        if pending_tools > 0:
            logger.debug(f"Waiting for {pending_tools} pending tool executions")
            
            # Collect any remaining results
            async for result in self._collect_tool_results():
                tool_call_id = result.get('tool_call_id')
                progress = result.get('progress', {})
                
                if progress.get('type') == 'completed':
                    logger.debug(f"Tool {tool_call_id} completed during finalization")
                    
                    # Store the result if not already stored
                    result = progress.get('result')
                    if result is not None and tool_call_id:
                        if tool_call_id not in self.state.tool_results:
                            self.state.tool_results[tool_call_id] = []
                        self.state.tool_results[tool_call_id].append(result)
                        logger.debug(f"Late result stored for tool {tool_call_id}")
                    
                    # Remove from active tools
                    if tool_call_id in self.state.active_tool_calls:
                        del self.state.active_tool_calls[tool_call_id]
                    
                    # Clean up stream
                    if tool_call_id in self.active_tool_streams:
                        del self.active_tool_streams[tool_call_id]
        
        # Finalize response if we have one
        if 'response_accumulator' in self.state.response_accumulator:
            accumulator = self.state.response_accumulator['response_accumulator']
            
            # Build final response and convert to ProviderResponse
            final_response_dict = accumulator.finalize_response()
            final_response = self._convert_dict_to_provider_response(final_response_dict)

            # Add response to context via MessageScheduler (creates ToolCall components)
            if self.agent and hasattr(self.agent, '_message_scheduler'):
                self.agent._message_scheduler.add_response(final_response)
                logger.debug("Added streaming response to context via MessageScheduler")

            # Get all tool results from completed executions
            tool_results = []
            logger.info(f"Collecting tool results from {len(self.state.tool_results)} completed executions")
            for task_id, results in self.state.tool_results.items():
                logger.info(f"Tool {task_id} has {len(results)} results")
                tool_results.extend(results)

            logger.info(f"Total tool_results collected: {len(tool_results)}")
            logger.info(f"tool_results content: {[type(r).__name__ for r in tool_results]}")
            logger.info(f"tool_results truthy: {bool(tool_results)}, self.agent: {self.agent is not None}")

            # PACT Lifecycle Integration
            if tool_results and self.agent:
                # Add tool results to context
                logger.info(f"Adding {len(tool_results)} tool results to context")
                self.agent._task_loop_ops.add_tool_results_to_context(tool_results)
                logger.info(f"Added {len(tool_results)} tool results to PACT context")
            elif not tool_results:
                logger.warning("No tool results to add to context")
            elif not self.agent:
                logger.warning("No agent available to add tool results")
            
            # Create conversation turn with streaming response and tool results
            # Extract tool calls from accumulated state
            tool_calls = []
            for tool_call_id, tool_acc in self.state.tool_accumulators.items():
                if tool_acc.is_complete:
                    tool_calls.append({
                        'id': tool_call_id,
                        'type': 'function',
                        'function': {
                            'name': tool_acc.function_name,
                            'arguments': tool_acc.arguments_str
                        }
                    })
            
            # Create conversation turn
            if self.agent:
                self.agent._task_loop_ops.create_conversation_turn(final_response, tool_calls, tool_results)

                # Seal turn with provider response (automatically creates snapshot)
                try:
                    self.agent.context.seal("after_streaming_tool_execution")
                except Exception as e:
                    logger.warning(f"Failed to seal streaming turn: {e}")
            
            logger.info(f"PACT lifecycle completed for streaming turn with {len(tool_results)} tool results")
            
            # End the turn
            await self.end_turn()
            
            return final_response
        
        # No response to finalize
        logger.warning("No response accumulator found during finalization")
        await self.end_turn()
        return None
    
    def _convert_dict_to_provider_response(self, response_dict: Dict[str, Any]) -> 'ProviderResponse':
        """
        Convert dict response from StreamResponseAccumulator to ProviderResponse.
        
        Args:
            response_dict: Dict response with 'role', 'content_blocks', 'metadata'
            
        Returns:
            Proper ProviderResponse object for sealing
        """
        try:
            from egregore.core.messaging import ProviderResponse, TextContent, ProviderToolCall
            
            # Extract content blocks from dict
            content_blocks = []
            raw_content_blocks = response_dict.get('content_blocks', [])
            
            for block in raw_content_blocks:
                if isinstance(block, dict):
                    # Convert dict blocks to proper ContentBlock objects
                    if block.get('type') == 'text':
                        content_blocks.append(TextContent(content=block.get('content', '')))
                    elif block.get('type') in ('tool_call', 'provider_tool_call'):
                        # Handle both 'tool_call' and 'provider_tool_call' types
                        # Extract function info from the block
                        function_info = block.get('function', {})
                        tool_name = function_info.get('name', 'unknown')
                        tool_call_id = block.get('id', 'unknown')

                        # Parse arguments (may be string or dict)
                        arguments = function_info.get('arguments', '{}')
                        if isinstance(arguments, str):
                            import json
                            try:
                                parameters = json.loads(arguments)
                            except:
                                parameters = {}
                        else:
                            parameters = arguments

                        content_blocks.append(ProviderToolCall(
                            tool_name=tool_name,
                            tool_call_id=tool_call_id,
                            parameters=parameters
                        ))
                    else:
                        # Fallback to text content for unknown types
                        content_blocks.append(TextContent(content=str(block)))
                else:
                    # Already a proper ContentBlock object
                    content_blocks.append(block)
            
            # Extract metadata
            metadata = response_dict.get('metadata', {})
            token_count = metadata.get('usage', {}).get('total_tokens', 0)
            
            # Create ProviderResponse
            provider_response = ProviderResponse(
                content=content_blocks,
                token_count=token_count,
                metadata=metadata
            )
            
            logger.debug(f"Converted dict response to ProviderResponse with {len(content_blocks)} content blocks")
            return provider_response
            
        except Exception as e:
            logger.error(f"Failed to convert dict to ProviderResponse: {e}")
            # Fallback: create minimal ProviderResponse
            from egregore.core.messaging import ProviderResponse, TextContent
            return ProviderResponse(
                content=[TextContent(content="Streaming response completed")],
                token_count=0,
                metadata={'error': f'Conversion failed: {e}'}
            )


class StreamingToolAccumulator:
    """
    Accumulates streaming tool call deltas into complete tool calls.
    
    Handles partial tool call data from streaming chunks and detects
    when tool calls are complete for execution.
    """
    
    def __init__(self, tool_call_id: str):
        """
        Initialize tool accumulator.
        
        Args:
            tool_call_id: Unique identifier for this tool call
        """
        self.tool_call_id = tool_call_id
        self.function_name = ""
        self.arguments_str = ""
        self.arguments_dict = {}
        self.is_complete = False
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
    
    def add_delta(self, chunk_data: Dict[str, Any]) -> bool:
        """
        Add streaming chunk data to accumulator.
        
        Args:
            chunk_data: Chunk data containing tool call delta information
            
        Returns:
            True if tool call is now complete
        """
        self.last_updated = datetime.now()
        
        # Extract tool call delta information from chunk
        if 'tool_calls' in chunk_data:
            tool_calls = chunk_data['tool_calls']
            for tool_call in tool_calls:
                if tool_call.get('id') == self.tool_call_id:
                    # Update function name if provided (and not None)
                    if 'function' in tool_call:
                        function = tool_call['function']
                        if 'name' in function and function['name'] is not None:
                            self.function_name = function['name']
                        if 'arguments' in function:
                            # Accumulate arguments string (even if empty string)
                            self.arguments_str += function['arguments']
        
        # Try to parse arguments as complete JSON
        if self.arguments_str and self.function_name:
            try:
                self.arguments_dict = json.loads(self.arguments_str)
                self.is_complete = True
                logger.debug(f"Tool call {self.tool_call_id} completed: {self.function_name}")
                return True
            except json.JSONDecodeError:
                # Still accumulating
                pass
        
        return False
    
    def get_tool_call(self) -> Optional[Dict[str, Any]]:
        """
        Get the accumulated tool call data.
        
        Returns:
            Tool call dictionary or None if not complete
        """
        if not self.is_complete:
            return None
        
        return {
            'id': self.tool_call_id,
            'type': 'function',
            'function': {
                'name': self.function_name,
                'arguments': self.arguments_str,
                'arguments_dict': self.arguments_dict
            }
        }
    
    def get_progress(self) -> Dict[str, Any]:
        """Get accumulation progress information."""
        return {
            'tool_call_id': self.tool_call_id,
            'function_name': self.function_name,
            'arguments_length': len(self.arguments_str),
            'is_complete': self.is_complete,
            'elapsed_seconds': (datetime.now() - self.created_at).total_seconds()
        }


class StreamResponseAccumulator:
    """
    Accumulates streaming response content into final ProviderResponse.
    
    Handles content blocks, tool calls, and response building for complete PACT lifecycle integration.
    
    Methods:
    - add_content_chunk(): Accumulates text content from content/delta chunks
    - add_tool_call(): Adds completed tool calls from tool_complete chunks  
    - add_tool_result(): Adds tool execution results from ToolTaskLoop
    - finalize_response(): Builds final ProviderResponse with all accumulated content
    
    The final ProviderResponse includes content_blocks (text + tool_calls), metadata 
    (turn_id, timestamps, counts), and optional provider metadata (model, usage, finish_reason).
    """
    
    def __init__(self, turn_id: str):
        """
        Initialize response accumulator.
        
        Args:
            turn_id: Turn identifier for this response
        """
        self.turn_id = turn_id
        self.content_parts: List[Dict[str, Any]] = []
        self.tool_calls: List[Dict[str, Any]] = []
        self.content_text = ""
        self.is_complete = False
        self.created_at = datetime.now()
        self.completed_at: Optional[datetime] = None
        
        # Response metadata
        self.model_info: Optional[Dict[str, Any]] = None
        self.usage_info: Optional[Dict[str, Any]] = None
        self.finish_reason: Optional[str] = None
    
    def add_content_chunk(self, chunk_data: Dict[str, Any]):
        """
        Add content chunk to response.
        
        Args:
            chunk_data: Chunk containing content data
        """
        # Extract text content
        content = chunk_data.get('content', '')
        if content:
            self.content_text += content
            self.content_parts.append({
                'type': 'text',
                'content': content,
                'timestamp': datetime.now()
            })
    
    def add_tool_call(self, tool_call: Dict[str, Any]):
        """
        Add completed tool call to response.
        
        Args:
            tool_call: Complete tool call dictionary
        """
        self.tool_calls.append(tool_call)
        self.content_parts.append({
            'type': 'tool_call',
            'tool_call': tool_call,
            'timestamp': datetime.now()
        })
    
    def add_tool_result(self, tool_call_id: str, result: Any):
        """
        Add tool execution result.
        
        Args:
            tool_call_id: ID of the tool call
            result: Tool execution result
        """
        self.content_parts.append({
            'type': 'tool_result',
            'tool_call_id': tool_call_id,
            'result': result,
            'timestamp': datetime.now()
        })
    
    def set_metadata(self, model_info: Optional[Dict[str, Any]] = None,
                    usage_info: Optional[Dict[str, Any]] = None,
                    finish_reason: Optional[str] = None):
        """
        Set response metadata.
        
        Args:
            model_info: Model information
            usage_info: Token usage information
            finish_reason: Reason for completion
        """
        if model_info:
            self.model_info = model_info
        if usage_info:
            self.usage_info = usage_info
        if finish_reason:
            self.finish_reason = finish_reason
    
    def finalize_response(self) -> Dict[str, Any]:
        """
        Finalize and return complete ProviderResponse structure.
        
        Returns:
            Complete provider response dictionary
        """
        self.is_complete = True
        self.completed_at = datetime.now()
        
        # Build content blocks
        content_blocks = []
        
        # Add text content if present
        if self.content_text.strip():
            content_blocks.append({
                'type': 'text',
                'content': self.content_text.strip()
            })
        
        # Add tool calls if present
        for tool_call in self.tool_calls:
            content_blocks.append({
                'type': 'provider_tool_call',
                'id': tool_call['id'],
                'function': tool_call['function']
            })
        
        # Build complete response
        response = {
            'role': 'assistant',
            'content_blocks': content_blocks,
            'metadata': {
                'turn_id': self.turn_id,
                'created_at': self.created_at.isoformat(),
                'completed_at': self.completed_at.isoformat() if self.completed_at else None,
                'content_parts_count': len(self.content_parts),
                'tool_calls_count': len(self.tool_calls)
            }
        }
        
        # Add optional metadata
        if self.model_info:
            response['metadata']['model'] = self.model_info
        if self.usage_info:
            response['metadata']['usage'] = self.usage_info
        if self.finish_reason:
            response['metadata']['finish_reason'] = self.finish_reason
        
        return response
    
    def get_progress(self) -> Dict[str, Any]:
        """Get response building progress."""
        return {
            'turn_id': self.turn_id,
            'content_length': len(self.content_text),
            'content_parts': len(self.content_parts),
            'tool_calls': len(self.tool_calls),
            'is_complete': self.is_complete,
            'elapsed_seconds': (datetime.now() - self.created_at).total_seconds()
        }