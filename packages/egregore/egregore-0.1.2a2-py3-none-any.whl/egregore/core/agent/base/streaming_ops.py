"""
Streaming Operations for Agent.

This module contains streaming operations and processing logic 
extracted from the Agent class for better maintainability and organization.
"""

import logging
import asyncio
import threading
from datetime import datetime
from typing import Any, Iterator, AsyncIterator, Dict, cast
from concurrent.futures import ThreadPoolExecutor

# Import utility function for context preparation
from ..utils import prepare_execution_context

# Set up logging
logger = logging.getLogger(__name__)


class StreamingOps:
    """
    Streaming operations for agents.
    
    Handles stream processing, chunk conversion, hook application,
    and streaming orchestration for agents.
    """
    
    def __init__(self, agent):
        """
        Initialize with reference to parent agent.
        
        Args:
            agent: Parent Agent instance that owns this StreamingOps
        """
        self.agent = agent
        logger.debug(f"StreamingOps initialized for agent {agent.agent_id}")
    
    def stream(self, *inputs, **kwargs) -> Iterator[Any]:
        """
        Streaming version - sync generator for streaming responses.
        
        Args:
            *inputs: Input messages/data for the agent
            **kwargs: Additional parameters for provider calls
            
        Yields:
            Stream chunks from the provider response
        """
        execution_id = self.agent.controller.start_execution()
        execution_ended = False
        
        try:
            # Use extracted utility for context preparation
            context_data = prepare_execution_context(
                self.agent._message_scheduler,
                self.agent.context,
                execution_id,
                self.agent.history,
                *inputs
            )
            provider_thread = context_data["provider_thread"]
            
            # NEW: on_user_msg hook - edit user message before sending to provider
            if self.agent._hooks_instance:
                from ..hooks.execution import HookType
                modified_thread, was_modified = self.agent._hooks_instance.execute_message_editing_hook(
                    HookType.MESSAGE_USER_INPUT,
                    provider_thread,
                    context=self.agent.context
                )
                if was_modified:
                    provider_thread = modified_thread
                    logger.info("User message modified by on_user_msg hook in stream()")
            
            # Enhanced: Use enhanced streaming with proper event loop management
            stream_generator = self.process_stream_sync_wrapper(provider_thread, **kwargs)
            try:
                for chunk in stream_generator:
                    yield chunk
            finally:
                # Properly close the inner generator if it wasn't exhausted (duck-typed)
                sg = cast(Any, stream_generator)
                if hasattr(sg, 'close'):
                    sg.close()
            
            # Normal completion - end execution
            self.agent.controller.end_execution(execution_id)
            execution_ended = True
            
        except Exception as e:
            if not execution_ended:
                self.agent.controller.end_execution(execution_id)
            logger.error(f"Agent {self.agent.agent_id} stream failed: {e}")
            raise
        finally:
            # Safety net - ensure execution is ended even if generator is abandoned
            from .controller import ExecutionState
            if not execution_ended and self.agent.controller.state != ExecutionState.IDLE:
                logger.debug(f"StreamingOps safety net - ending abandoned execution {execution_id}")
                self.agent.controller.end_execution(execution_id)
    
    async def astream(self, *inputs, **kwargs) -> AsyncIterator[Any]:
        """
        Async streaming version - async generator for streaming responses.
        
        Args:
            *inputs: Input messages/data for the agent
            **kwargs: Additional parameters for provider calls
            
        Yields:
            Stream chunks from the async provider response
        """
        execution_id = self.agent.controller.start_execution()
        
        try:
            # Use extracted utility for context preparation
            context_data = prepare_execution_context(
                self.agent._message_scheduler,
                self.agent.context,
                execution_id,
                self.agent.history,
                *inputs
            )
            provider_thread = context_data["provider_thread"]
            
            # NEW: on_user_msg hook - edit user message before sending to provider
            if self.agent._hooks_instance:
                from ..hooks.execution import HookType
                modified_thread, was_modified = self.agent._hooks_instance.execute_message_editing_hook(
                    HookType.MESSAGE_USER_INPUT,
                    provider_thread,
                    context=self.agent.context
                )
                if was_modified:
                    provider_thread = modified_thread
                    logger.info("User message modified by on_user_msg hook in astream()")
            
            # Enhanced: Use StreamingOrchestrator for tool detection and execution
            stream_gen = self.aprocess_stream_with_orchestrator(
                provider_thread, **kwargs
            )
            if stream_gen is not None and hasattr(stream_gen, '__aiter__'):
                async for chunk in stream_gen:
                    yield chunk
            
            self.agent.controller.end_execution(execution_id)
            
        except Exception as e:
            self.agent.controller.end_execution(execution_id)
            logger.error(f"Agent {self.agent.agent_id} astream failed: {e}")
            raise
    
    def process_stream(self, stream_response: Any) -> Iterator[Any]:
        """
        Process stream with hooks and completion handling (sync version).
        
        Args:
            stream_response: Stream response from provider
            
        Yields:
            Processed stream chunks
        """
        # Process stream chunks through registered streaming hooks
        
        if isinstance(stream_response, str):
            # Simple string response - yield as single chunk with hook processing
            chunk = {"delta": stream_response, "finish_reason": "completed"}
            processed_chunk = self.apply_streaming_hooks(chunk)
            yield processed_chunk
        else:
            # Assume iterable stream response  
            try:
                for chunk in stream_response:
                    # Apply streaming hooks if enabled
                    processed_chunk = self.apply_streaming_hooks(chunk)
                    yield processed_chunk
            except TypeError:
                # Not iterable, yield as single chunk with hook processing
                chunk = {"delta": str(stream_response), "finish_reason": "completed"}
                processed_chunk = self.apply_streaming_hooks(chunk)
                yield processed_chunk
    
    def process_stream_sync_wrapper(self, provider_thread, **kwargs) -> Iterator[Any]:
        """
        Sync wrapper for enhanced streaming with thread-safe event loop management.
        
        Args:
            provider_thread: Provider thread for the request
            **kwargs: Additional parameters for provider calls
            
        Yields:
            Stream chunks with enhanced tool detection (sync interface)
        """
        try:
            # Check if we're already in an event loop
            try:
                loop = asyncio.get_running_loop()
                # We're in an async context, run in thread pool
                logger.debug("Running enhanced streaming in thread pool (async context detected)")
                
                def run_async_streaming():
                    # Create new event loop for the thread
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        # Collect all chunks from async generator
                        chunks = []
                        async def collect_chunks():
                            stream_gen = self.aprocess_stream_with_orchestrator(provider_thread, **kwargs)
                            if stream_gen is not None and hasattr(stream_gen, '__aiter__'):
                                async for chunk in stream_gen:
                                    chunks.append(chunk)
                        
                        new_loop.run_until_complete(collect_chunks())
                        return chunks
                    finally:
                        new_loop.close()
                
                # Run in thread pool
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(run_async_streaming)
                    chunks = future.result()
                    
                # Yield collected chunks
                for chunk in chunks:
                    yield chunk
                    
            except RuntimeError:
                # No event loop running, we can use asyncio directly
                logger.debug("Running enhanced streaming with new event loop (sync context)")
                
                # Create and run event loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    # Collect all chunks from async generator
                    chunks = []
                    async def collect_chunks():
                        stream_gen = self.aprocess_stream_with_orchestrator(provider_thread, **kwargs)
                        if stream_gen is not None and hasattr(stream_gen, '__aiter__'):
                            async for chunk in stream_gen:
                                chunks.append(chunk)
                    
                    loop.run_until_complete(collect_chunks())
                    
                    # Yield collected chunks
                    for chunk in chunks:
                        yield chunk
                        
                finally:
                    loop.close()
                    
        except Exception as e:
            logger.error(f"Enhanced sync streaming failed: {e}")
            # Fallback to original sync streaming
            stream_response = self.agent._provider.stream(
                provider_thread=provider_thread,
                model=self.agent.provider.model,
                **kwargs
            )
            
            # Process stream chunks through original method
            yield from self.process_stream(stream_response)
    
    async def aprocess_stream_with_orchestrator(self, provider_thread, **kwargs) -> AsyncIterator[Any]:
        """
        Enhanced streaming with StreamingOrchestrator for tool detection and execution.
        
        Args:
            provider_thread: Provider thread for the request
            **kwargs: Additional parameters for provider calls
            
        Yields:
            Stream chunks with enhanced tool detection and execution
        """
        try:
            # Ensure both ToolTaskLoop and StreamingOrchestrator are ready
            await self.agent._task_loop_ops.ensure_task_loop_started()
            
            # Start streaming orchestrator turn
            turn_id = f"stream_{self.agent.controller.execution_id or 'unknown'}"
            await self.agent._streaming_orchestrator.start_turn(turn_id)
            
            # Get available tools for LLM awareness
            available_tools = []
            if hasattr(self.agent, 'tool_registry') and self.agent.tool_registry.tools:
                available_tools = list(self.agent.tool_registry.tools.values())
                logger.debug(f"Passing {len(available_tools)} tools to streaming provider")
            
            # Stream from provider using new provider interface
            logger.debug(f"Agent {self.agent.agent_id}: Calling provider.astream with {len(available_tools) if available_tools else 0} tools")
            stream_response = self.agent._provider.astream(
                provider_thread=provider_thread,
                model=self.agent.provider.model,
                tools=available_tools if available_tools else None,
                **kwargs
            )
            logger.debug(f"Agent {self.agent.agent_id}: Provider returned stream_response type: {type(stream_response)}, is_none: {stream_response is None}, has_aiter: {hasattr(stream_response, '__aiter__') if stream_response is not None else 'N/A'}")
            
            # Process stream chunks directly through orchestrator (eliminated conversion layer)
            if stream_response is not None and hasattr(stream_response, '__aiter__'):
                logger.debug(f"Agent {self.agent.agent_id}: Starting async iteration over stream_response")
                chunk_count = 0
                async for raw_chunk in stream_response:
                    chunk_count += 1
                    logger.debug(f"Agent {self.agent.agent_id}: Processing chunk {chunk_count}, type: {type(raw_chunk)}")
                    # Debug: check raw_chunk before normalization
                    if hasattr(raw_chunk, 'tool_call_id'):
                        logger.debug(f"Before normalize: raw_chunk.tool_call_id={raw_chunk.tool_call_id}, raw_chunk.function_name={raw_chunk.function_name}")
                    # Normalize provider chunk directly to dict for orchestrator
                    chunk_dict = self.normalize_provider_chunk(raw_chunk)
                    logger.debug(f"After normalize: tool_call_id={chunk_dict.get('tool_call_id')}, function_name={chunk_dict.get('function_name')}")

                    # Process through StreamingOrchestrator for tool detection
                    await self.agent._streaming_orchestrator.process_stream_chunk(chunk_dict)
                    
                    # Apply streaming hooks to the raw chunk (simplified)
                    processed_chunk = await self.apply_async_streaming_hooks(raw_chunk)
                    
                    # Yield the processed chunk
                    logger.debug(f"Agent {self.agent.agent_id}: Yielding processed chunk {chunk_count}")
                    yield processed_chunk
                
                logger.debug(f"Agent {self.agent.agent_id}: Completed async iteration, processed {chunk_count} chunks")
                        
            else:
                # Handle non-async iterator fallback
                logger.debug(f"Agent {self.agent.agent_id}: Using non-async iterator fallback for stream_response type: {type(stream_response)}")
                processed_chunk = await self.apply_async_streaming_hooks(stream_response)
                chunk_data = self.convert_chunk_to_dict(processed_chunk)
                await self.agent._streaming_orchestrator.process_stream_chunk(chunk_data)
                yield processed_chunk
            
            # Finalize the streaming turn
            final_response = await self.agent._streaming_orchestrator.finalize_turn()
            if final_response:
                logger.info("StreamingOrchestrator finalized response with tool execution")
                
                # Track provider call
                self.agent.state.increment_provider_calls()
                
                # Update context with final response if needed
                self.handle_streaming_finalization(final_response)
            
        except Exception as e:
            logger.error(f"Agent {self.agent.agent_id}: Enhanced streaming failed: {e}")
            logger.exception("Full streaming error traceback:")
            # Fallback to original streaming
            logger.debug(f"Agent {self.agent.agent_id}: Attempting fallback to original streaming")
            try:
                stream_response = self.agent._provider.astream(
                    provider_thread=provider_thread,
                    model=self.agent.provider.model,
                    **kwargs
                )
                logger.debug(f"Agent {self.agent.agent_id}: Fallback stream_response type: {type(stream_response)}")
                stream_gen = self.aprocess_stream(stream_response)
                if stream_gen is not None and hasattr(stream_gen, '__aiter__'):
                    logger.debug(f"Agent {self.agent.agent_id}: Starting fallback async iteration")
                    async for chunk in stream_gen:
                        yield chunk
                else:
                    logger.warning(f"Agent {self.agent.agent_id}: Fallback stream_gen is None or not iterable: {type(stream_gen)}")
            except Exception as fallback_e:
                logger.error(f"Agent {self.agent.agent_id}: Fallback streaming also failed: {fallback_e}")
                logger.exception("Fallback streaming error traceback:")
                raise
    
    # Stream Utility Methods
    def apply_streaming_hooks(self, chunk: Any) -> Any:
        """
        Apply streaming hooks to chunk (sync version).
        
        Args:
            chunk: Stream chunk to process
            
        Returns:
            Processed chunk
        """
        try:
            # Apply streaming hooks from ToolExecutionHooks (always enabled)
            return self.agent._hooks_instance.process_stream_chunk(chunk, self.agent.context)
        except Exception as e:
            logger.warning(f"Streaming hook failed: {e}")
            return chunk
    
    async def apply_async_streaming_hooks(self, chunk: Any) -> Any:
        """
        Apply async streaming hooks to chunk (async version).
        
        Args:
            chunk: Stream chunk to process
            
        Returns:
            Processed chunk
        """
        try:
            # Apply async streaming hooks from ToolExecutionHooks (always enabled)
            return await self.agent._hooks_instance.aprocess_stream_chunk(chunk, self.agent.context)
        except Exception as e:
            logger.warning(f"Async streaming hook failed: {e}")
            return chunk
    
    def convert_chunk_to_dict(self, chunk: Any) -> Dict[str, Any]:
        """Convert stream chunk to dictionary format for orchestrator."""
        if isinstance(chunk, dict):
            return chunk
        elif hasattr(chunk, 'model_dump'):
            # Pydantic v2 model - use model_dump()
            return chunk.model_dump()
        elif hasattr(chunk, 'dict'):
            # Pydantic v1 model - use dict()
            return chunk.dict()
        elif hasattr(chunk, '__dict__'):
            return chunk.__dict__
        elif hasattr(chunk, 'delta'):
            return {'content': getattr(chunk, 'delta', '')}
        else:
            return {'content': str(chunk)}
    
    def normalize_provider_chunk(self, chunk: Any) -> Dict[str, Any]:
        """
        Normalize provider chunk directly to dict for StreamingOrchestrator.
        
        Eliminates unnecessary StreamChunk conversion layer for better performance.
        Injects metadata directly during normalization.
        
        Args:
            chunk: Raw provider chunk (any format)
            
        Returns:
            Normalized dict with metadata injection for orchestrator consumption
        """
        # Convert to dict first
        chunk_dict = self.convert_chunk_to_dict(chunk)
        
        # Add agent-specific metadata directly (no intermediate object)
        if 'metadata' not in chunk_dict:
            chunk_dict['metadata'] = {}
        
        chunk_dict['metadata'].update({
            'processed_at': datetime.now().isoformat(),
            'agent_id': self.agent.agent_id,
            'execution_id': getattr(self.agent.controller, 'execution_id', None),
            'turn_id': getattr(self.agent, '_current_turn_id', None),
            'provider': getattr(self.agent.provider, 'provider_name', 'unknown'),
            'model': getattr(self.agent.provider, 'model', 'unknown'),
            'sequence': getattr(self.agent, '_chunk_sequence', 0) + 1
        })
        
        # Increment sequence counter for ordering  
        if not hasattr(self.agent, '_chunk_sequence'):
            self.agent._chunk_sequence = 0
        self.agent._chunk_sequence += 1
        
        return chunk_dict
    
    def handle_streaming_finalization(self, final_response: Any) -> None:
        """Handle finalization of streaming response with tool results."""
        try:
            # Add final response to context if needed
            # This is where we'd integrate the complete response with tool results
            try:
                if isinstance(final_response, dict):
                    blocks_count = len(final_response.get('content_blocks', []))
                elif hasattr(final_response, 'content') and isinstance(final_response.content, list):
                    blocks_count = len(final_response.content)
                else:
                    blocks_count = 0
            except Exception:
                blocks_count = 0
            logger.debug(f"Handling streaming finalization with {blocks_count} content blocks")
            
            # Seal after streaming with tools (automatically creates snapshot)
            self.agent.context.seal("after_streaming_with_tools")
            
        except Exception as e:
            logger.error(f"Error handling streaming finalization: {e}")
    
    async def aprocess_stream(self, stream_response: Any) -> AsyncIterator[Any]:
        """
        Process async stream with hooks and completion handling.
        
        Args:
            stream_response: Async stream response from provider
            
        Yields:
            Processed stream chunks
        """
        # Process stream chunks through registered async streaming hooks
        
        if isinstance(stream_response, str):
            # Simple string response - yield as single chunk with hook processing
            chunk = {"delta": stream_response, "finish_reason": "completed"}
            processed_chunk = await self.apply_async_streaming_hooks(chunk)
            yield processed_chunk
        else:
            # Assume async iterable stream response  
            if hasattr(stream_response, '__aiter__'):
                async for chunk in stream_response:
                    # Apply streaming hooks if enabled
                    processed_chunk = await self.apply_async_streaming_hooks(chunk)
                    yield processed_chunk
            else:
                # Try to iterate synchronously
                try:
                    for chunk in stream_response:
                        # Apply streaming hooks if enabled
                        processed_chunk = await self.apply_async_streaming_hooks(chunk)
                        yield processed_chunk
                except TypeError:
                    # Not iterable, yield as single chunk with hook processing
                    chunk = {"delta": str(stream_response), "finish_reason": "completed"}
                    processed_chunk = await self.apply_async_streaming_hooks(chunk)
                    yield processed_chunk