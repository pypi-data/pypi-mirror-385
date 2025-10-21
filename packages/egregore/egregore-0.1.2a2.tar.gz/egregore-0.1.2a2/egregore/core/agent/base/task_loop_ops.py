"""
Task Loop Operations for Agent.

This module contains task loop orchestration and management operations 
extracted from the Agent class for better maintainability and organization.
"""

import logging
import asyncio
from typing import Any, List

from egregore.core.messaging import ProviderToolCall

# Set up logging
logger = logging.getLogger(__name__)


class TaskLoopOps:
    """
    Task loop operations for agents.
    
    Handles task loop orchestration, tool execution management,
    and non-blocking tool processing for agents.
    """
    
    def __init__(self, agent):
        from egregore.core.agent.base import Agent
        """
        Initialize with reference to parent agent.
        
        Args:
            agent: Parent Agent instance that owns this TaskLoopOps
        """
        self.agent: Agent = agent
        logger.debug(f"TaskLoopOps initialized for agent {agent.agent_id}")
    
    async def ensure_task_loop_started(self) -> None:
        """Ensure the ToolTaskLoop is started for streaming execution."""
        if not self.agent._task_loop_started:
            await self.agent._task_loop.start()
            self.agent._task_loop_started = True
            logger.debug(f"Started ToolTaskLoop for agent {self.agent.agent_id}")
    
    async def orchestrate_turn_with_task_loop(self, response) -> Any:
        """
        Enhanced orchestration using ToolTaskLoop for non-blocking tool execution.
        
        Args:
            response: Provider response that may contain tool calls
            
        Returns:
            Final response after non-blocking tool execution (if any)
        """
        try:
            # Phase 3: Extract tool calls from context (not response)
            tool_calls = self.extract_tool_calls_from_context()
            
            if not tool_calls:
                # No tool calls; seal turn and return response (backward compatibility)
                try:
                    self.agent.context.seal("after_provider_response")
                except Exception:
                    pass
                return response
            
            # Ensure ToolTaskLoop is started
            await self.ensure_task_loop_started()
            
            # Execute tools using ToolTaskLoop for non-blocking execution
            logger.info(f"Executing {len(tool_calls)} tool calls with ToolTaskLoop (non-blocking)")
            
            # Track tool calls
            for _ in tool_calls:
                self.agent.state.increment_tool_calls()
            
            # Execute tools asynchronously using ToolTaskLoop
            tool_results = []
            for tool_call in tool_calls:
                try:
                    # Phase 3: Handle both ToolCall components and dict formats
                    from ...tool_calling.context_components import ToolCall as ToolCallComponent

                    # Extract tool_call_id and tool_name (works for both dict and component)
                    if isinstance(tool_call, ToolCallComponent):
                        tool_call_id = tool_call.tool_call_id
                        tool_name = tool_call.tool_name
                    elif isinstance(tool_call, dict):
                        tool_call_id = tool_call.get('id', 'unknown')
                        tool_name = tool_call.get('function', {}).get('name', 'unknown')
                    else:
                        logger.warning(f"Unknown tool_call type: {type(tool_call)}")
                        tool_call_id = 'unknown'
                        tool_name = 'unknown'

                    # Execute tool asynchronously via task loop and await completion
                    task_id = await self.agent._task_loop.execute_tool_async(tool_call)

                    # Await task completion directly (no busy wait)
                    task_info = await self.agent._task_loop.await_task_completion(task_id)

                    # Process completed task
                    if task_info.get('status') == 'completed':
                        result = task_info.get('result', {})

                        # Check if result is already a ContextComponent (from ToolExecutor)
                        from ...tool_calling.context_components import ToolResult
                        from ...context_management.pact.components.core import PACTCore as ContextComponent

                        if isinstance(result, ContextComponent):
                            # Result is already a ContextComponent - use directly
                            tool_results.append(result)
                        else:
                            # POC: Create ToolResult directly instead of dict
                            tool_result_component = ToolResult(
                                tool_call_id=tool_call_id,
                                tool_name=tool_name,
                                content=str(result),
                                success=True
                            )
                            tool_results.append(tool_result_component)
                    elif task_info.get('status') == 'failed':
                        error = task_info.get('error', 'Unknown error')
                        # POC: Create ToolResult directly instead of dict
                        from ...tool_calling.context_components import ToolResult

                        error_result_component = ToolResult(
                            tool_call_id=tool_call_id,
                            tool_name=tool_name,
                            content=f"Tool failed: {error}",
                            success=False,
                            error_message=error
                        )
                        tool_results.append(error_result_component)

                    logger.debug(f"Tool executed successfully: {tool_name}")

                except Exception as e:
                    logger.error(f"Tool execution failed: {e}")
                    # Track tool error
                    self.agent.state.increment_errors()
                    # POC: Create ToolResult directly instead of dict
                    from ...tool_calling.context_components import ToolResult

                    error_result_component = ToolResult(
                        tool_call_id=tool_call_id if 'tool_call_id' in locals() else 'unknown',
                        tool_name=tool_name if 'tool_name' in locals() else 'unknown',
                        content=f"Tool execution failed: {str(e)}",
                        success=False,
                        error_message=str(e)
                    )
                    tool_results.append(error_result_component)
            
            # Update context with tool results
            self.add_tool_results_to_context(tool_results)

            # Create conversation turn with tool execution
            self.create_conversation_turn(response, tool_calls, tool_results)

            logger.info(f"Non-blocking tool execution completed successfully")

            # Seal turn after tool execution (automatically creates snapshot)
            try:
                self.agent.context.seal("after_tool_execution_task_loop")
            except Exception:
                pass
                
            return response
            
        except Exception as e:
            logger.error(f"Task loop orchestration failed: {e}")
            # Fallback to basic response sealing
            try:
                self.agent._message_scheduler.seal(self.agent.context, provider_response=response)
            except Exception:
                pass
            return response
    
    def orchestrate_turn(self, response=None) -> Any:
        """
        Orchestrate complete turn including tool execution (sync version).

        Args:
            response: Optional provider response (for backward compatibility).
                     If None, will extract from context (Phase 3 complete).

        Returns:
            Final response after tool execution (if any)
        """
        try:
            # Phase 3: If no response provided, extract from context
            if response is None:
                # Get the latest provider response from context (depth 0)
                # For now, create a minimal response object for compatibility
                from ...messaging import ProviderResponse
                response = ProviderResponse(content=[])

            # Integrate pending input tokens into context components
            self.agent._token_ops.integrate_pending_input_tokens(response)
            # Phase 3: Extract tool calls from context (not response)
            tool_calls = self.extract_tool_calls_from_context()
            
            if not tool_calls:
                # No tool calls; seal turn (client + provider) first
                try:
                    self.agent.context.seal("after_provider_response")
                except Exception:
                    pass
                
                # NEW: on_provider_msg hook - edit provider response after seal (final response only)
                if self.agent._hooks_instance:
                    from ..hooks.execution import HookType
                    modified_response, was_modified = self.agent._hooks_instance.execute_message_editing_hook(
                        HookType.MESSAGE_PROVIDER_RESPONSE,
                        response,
                        context=self.agent.context
                    )
                    
                    if was_modified:
                        # Add audit trail to context
                        self.add_response_modification_audit(response, modified_response)
                        response = modified_response
                        logger.info("Provider response modified by on_provider_msg hook")
                
                return response
            
            # Execute tools using ToolExecutor with hooks
            logger.info(f"Executing {len(tool_calls)} tool calls")
            tool_results = self.agent.tool_executor.execute_tools_with_hooks(
                tool_calls=tool_calls,
                agent_id=self.agent.agent_id,
                execution_id=self.agent.controller.execution_id
            )
            logger.debug(f"Tool execution created {len(tool_results)} results:")
            for tr in tool_results:
                logger.debug(f"  - Result for {tr.tool_call_id} (component_id={tr.id}, success={tr.success})")
            
            # Track tool calls and errors
            for _ in tool_calls:
                self.agent.state.increment_tool_calls()
            
            # Track tool errors
            from ...tool_calling.context_components import ToolResult
            for result in tool_results:
                if isinstance(result, ToolResult) and not result.success:
                    self.agent.state.increment_errors()
            
            # Update context with tool results
            self.add_tool_results_to_context(tool_results)

            # Create conversation turn with tool execution
            self.create_conversation_turn(response, tool_calls, tool_results)

            logger.info(f"Tool execution completed successfully")
            # Seal turn after tool execution (automatically creates snapshot)
            try:
                self.agent.context.seal("after_tool_execution")
            except Exception:
                pass
            return response
            
        except Exception as e:
            logger.error(f"Tool orchestration failed: {e}")
            # Return original response even if tool execution fails
            return response
    
    def extract_tool_calls_from_response(self, response: Any) -> List[Any]:
        """
        Extract tool calls from provider response.
        
        Args:
            response: Provider response
            
        Returns:
            List of ProviderToolCall objects, empty if none found
        """
        tool_calls = []
        
        try:
            # Handle different response formats
            if hasattr(response, 'content') and isinstance(response.content, list):
                # ProviderResponse with ContentBlock list
                for content_block in response.content:
                    if isinstance(content_block, ProviderToolCall):
                        tool_calls.append(content_block)
                        
            elif hasattr(response, 'tool_calls') and response.tool_calls:
                # Response with direct tool_calls attribute
                tool_calls.extend(response.tool_calls)
                
            elif isinstance(response, dict) and 'tool_calls' in response:
                # Dictionary response with tool_calls
                tool_calls.extend(response['tool_calls'])
                
        except Exception as e:
            logger.warning(f"Error extracting tool calls from response: {e}")
            
        return tool_calls

    def extract_tool_calls_from_context(self) -> List[Any]:
        """
        Extract tool calls from context using PACT selectors (Phase 3).

        This is the new method that replaces parsing ProviderResponse.
        After MessageScheduler.add_response() converts ProviderToolCall → ToolCall,
        we extract the ToolCall components from context instead of re-parsing.

        Returns:
            List of ToolCall components from active message (depth 0)
        """
        try:
            # Use PACT selector to get tool calls from active message
            # Note: Depth scope must be inside parentheses: (d0) not d0
            tool_calls = self.agent.context.select("(d0) +tool_call")
            logger.debug(f"Extracted {len(tool_calls)} tool calls from context (depth 0 only)")
            for tc in tool_calls:
                logger.debug(f"  - {tc.tool_name} (tool_call_id={tc.tool_call_id}, component_id={tc.id})")
            return tool_calls
        except Exception as e:
            logger.warning(f"Error extracting tool calls from context: {e}")
            return []

    def add_tool_results_to_context(self, tool_results: List[Any]) -> None:
        """
        Add tool execution results to context (ContextComponent only).

        Tool execution happens during USER turn, so we need to:
        1. Start a new user turn (pushes assistant's message to depth 1)
        2. Add tool results to the new user message at depth 0

        Args:
            tool_results: List of ContextComponent instances only
        """
        try:
            if not tool_results:
                return

            # Step 1: Start new user turn for tool results
            # This creates a new user message at depth 0 and pushes the assistant's message to depth 1
            self.agent.context.add_user("Tool execution results")
            logger.debug(f"Started new user turn for {len(tool_results)} tool results")

            # Step 2: Add tool results to the new user message at depth 0
            for result in tool_results:
                # Verify it's a PACT component
                from ...context_management.pact.components.core import PACTNode
                if not isinstance(result, PACTNode):
                    # This would be a dict - should not happen in POC
                    raise ValueError(f"Expected PACTNode, got {type(result)}. "
                                   f"Dict format should be converted at source.")

                # Add ToolResult to depth 0 using PACT API
                logger.debug(f"Adding result {result.id} for tool_call_id={result.tool_call_id} to d0,0")
                self.agent.context.pact_update("d0,0", result, mode="append")

            logger.debug(f"Added {len(tool_results)} tool results to user message at depth 0")

        except Exception as e:
            logger.error(f"Error adding tool results to context: {e}")
            raise  # Re-raise the exception for proper error handling
    
    def create_conversation_turn(self, response: Any, tool_calls: List[Any], tool_results: List[Any]) -> None:
        """
        Create a conversation turn with provider response and tool execution.
        
        Args:
            response: Provider response
            tool_calls: List of executed tool calls
            tool_results: List of tool execution results
        """
        try:
            # For now, this is a placeholder for conversation turn creation
            # In a full implementation, this would create a structured turn
            # in the conversation history with the response and tool execution pair
            
            logger.debug(f"Created conversation turn with {len(tool_calls)} tool calls and {len(tool_results)} results")
            
        except Exception as e:
            logger.error(f"Error creating conversation turn: {e}")
    
    def add_response_modification_audit(self, original_response: Any, modified_response: Any) -> None:
        """Add audit trail when provider response is modified."""
        try:
            from ...context_management.components import TextContextComponent
            from ...context_management.pact.components.core import Metadata as ComponentMetadata
            
            audit_component = TextContextComponent(
                content=f"Provider response modified by hook (hash: {hash(str(original_response))} -> {hash(str(modified_response))})",
                metadata=ComponentMetadata()  # Use proper ComponentMetadata type
            )
            
            # Add audit trail to active message
            self.agent.context.active_message.add_child(audit_component)
            logger.debug("Added provider response modification audit trail")
            
        except Exception as e:
            logger.warning(f"Failed to add response modification audit: {e}")