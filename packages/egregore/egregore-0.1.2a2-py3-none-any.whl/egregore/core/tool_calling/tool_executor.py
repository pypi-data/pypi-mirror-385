"""
Tool Executor System

ToolExecutor with ContextComponent output and ScaffoldManager integration.
Executes tools and scaffolds, produces ContextComponents for context tree.
Enhanced with ToolExecutionHooks support for lifecycle management.
"""

import asyncio
import threading
import time
from pydantic import BaseModel
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
import logging
import difflib

from egregore.core.tool_calling.tool_registry import ToolRegistry
from egregore.core.tool_calling.context_components import ToolResult, ScaffoldResult
from egregore.core.messaging import ProviderToolCall
from egregore.core.context_management.pact.components.core import PACTCore as ContextComponent
from egregore.core.agent.hooks.execution import ToolExecutionHooks, HookType
from egregore.core.agent.hooks.execution_contexts import ContextFactory, BaseExecContext, OperationExecContext

logger = logging.getLogger(__name__)


class ToolExecutor(BaseModel):
    """V2 tool executor that produces ContextComponents for context tree"""

    model_config = {"arbitrary_types_allowed": True}

    registry: ToolRegistry
    context: Optional[Any] = None  # Context for registry population - avoid circular import
    context_history: Optional[Any] = None  # ContextHistory - avoid circular import

    # Hook system integration
    hooks: Optional[ToolExecutionHooks] = None

    # Concurrency control
    _execution_semaphore: Optional[threading.Semaphore] = None
    _max_concurrent_executions: int = 5

    # Agent context for hooks
    _agent_id: Optional[str] = None
    _execution_id: Optional[str] = None

    # NEW: Agent reference for enhanced hook context
    agent: Optional[Any] = None
    
    def __init__(self, **data):
        """Initialize ToolExecutor with optional hooks and concurrency control."""
        super().__init__(**data)
        
        # Initialize semaphore for concurrency control
        if self._execution_semaphore is None:
            self._execution_semaphore = threading.Semaphore(self._max_concurrent_executions)
    
    # Hook System Configuration
    
    def set_hooks(self, hooks: ToolExecutionHooks) -> None:
        """Set the hook system for tool execution lifecycle management."""
        self.hooks = hooks
        logger.debug("ToolExecutionHooks configured for ToolExecutor")
    
    def set_agent_context(self, agent_id: str, execution_id: Optional[str] = None) -> None:
        """Set agent context for hook execution."""
        self._agent_id = agent_id
        self._execution_id = execution_id
        logger.debug(f"Agent context set: {agent_id}, execution: {execution_id}")
    
    def set_concurrency_limit(self, max_concurrent: int) -> None:
        """Set maximum concurrent tool executions."""
        self._max_concurrent_executions = max_concurrent
        self._execution_semaphore = threading.Semaphore(max_concurrent)
        logger.debug(f"Concurrency limit set to {max_concurrent}")
    
    # Enhanced Tool Execution with Hooks
    
    def execute_tools_with_hooks(
        self,
        tool_calls: List[ProviderToolCall],
        agent_id: Optional[str] = None,
        execution_id: Optional[str] = None
    ) -> List[ContextComponent]:
        """
        Execute multiple tools with full hook lifecycle management.
        
        Args:
            tool_calls: List of tool calls to execute
            agent_id: Agent identifier for hook context
            execution_id: Execution identifier for hook context
            
        Returns:
            List of tool execution results (ToolResult or ScaffoldResult)
        """
        # Use provided context or fall back to instance context
        effective_agent_id = agent_id or self._agent_id or "unknown"
        effective_execution_id = execution_id or self._execution_id
        
        # Create hook context for the overall execution
        execution_context = BaseExecContext(
            agent_id=effective_agent_id,
            execution_id=effective_execution_id,
            agent=self.agent,
            metadata={
                "tool_count": len(tool_calls),
                "tool_names": [call.tool_name for call in tool_calls]
            }
        )
        
        # Execute before tool execution hooks
        if self.hooks:
            self.hooks.execute_hooks(HookType.BEFORE_TOOL_EXECUTION, execution_context)
        
        results = []
        execution_start_time = datetime.now()
        
        try:
            # Execute each tool with individual hooks
            for tool_call in tool_calls:
                try:
                    result = self._execute_single_tool_with_hooks(
                        tool_call, effective_agent_id, effective_execution_id
                    )
                    results.append(result)
                except Exception as e:
                    logger.error(f"Tool execution failed for {tool_call.tool_name}: {e}")
                    # Create error result
                    error_result = ToolResult(
                        tool_call_id=tool_call.tool_call_id,
                        tool_name=tool_call.tool_name,
                        content=f"Execution failed: {str(e)}",
                        success=False,
                        execution_time=datetime.now(),
                        error_message=str(e)
                    )
                    # Ensure proper ID generation for tool result
                    error_result.metadata.ensure_id(node_type="block", parent_id="")
                    results.append(error_result)
            
            # Update context with results
            md = execution_context.metadata or {}
            md.update({
                "execution_duration": (datetime.now() - execution_start_time).total_seconds(),
                "success_count": sum(1 for r in results if getattr(r, 'success', False)),
                "failure_count": sum(1 for r in results if not getattr(r, 'success', True))
            })
            execution_context.metadata = md
            
            # Execute after tool execution hooks
            if self.hooks:
                self.hooks.execute_hooks(HookType.AFTER_TOOL_EXECUTION, execution_context)
            
            return results
            
        except Exception as e:
            # Execute error hooks
            execution_context.error = e
            if self.hooks:
                self.hooks.execute_hooks(HookType.ON_TOOL_ERROR, execution_context)
            raise
    
    def _execute_single_tool_with_hooks(
        self,
        tool_call: ProviderToolCall,
        agent_id: str,
        execution_id: Optional[str]
    ) -> ContextComponent:
        """Execute a single tool with hooks and concurrency control."""
        
        # Acquire semaphore for concurrency control
        semaphore = self._execution_semaphore
        if semaphore is None:
            raise RuntimeError("Execution semaphore not initialized")
        with semaphore:
            # Get tool declaration to determine type
            tool_decl = self.registry.get_tool(tool_call.tool_name)
            from egregore.core.tool_calling.tool_declaration import ScaffoldOpDeclaration
            is_scaffold = isinstance(tool_decl, ScaffoldOpDeclaration)
            
            # Create operation context for individual tool call (handles both tools and scaffolds)
            call_context = ContextFactory.create_operation_context(
                agent_id=agent_id,
                tool_declaration=tool_decl,
                tool_params=tool_call.parameters,
                agent=self.agent,
                execution_id=execution_id,
                metadata={
                    'tool_call_id': getattr(tool_call, 'tool_call_id', None),
                    'execution_start': time.time()
                }
            )
            
            # Apply injection patterns if hooks are available
            if self.hooks:
                modified_params = self.hooks.apply_injection_patterns(
                    tool_call.tool_name,
                    tool_call.parameters,
                    call_context
                )
                # Create modified tool call if parameters were injected
                if modified_params != tool_call.parameters:
                    tool_call = ProviderToolCall(
                        tool_call_id=tool_call.tool_call_id,
                        tool_name=tool_call.tool_name,
                        parameters=modified_params
                    )
                    call_context.tool_params = modified_params
            
            # Execute before tool call hooks
            if self.hooks:
                self.hooks.execute_hooks(HookType.BEFORE_TOOL_CALL, call_context)
            
            # Execute call intercept hooks (PRE-EXECUTION PHASE)
            if self.hooks:
                self.hooks.execute_hooks(HookType.CALL_INTERCEPT, call_context)
                
                # Check if any hook rejected the call
                if call_context.validation_rejected:
                    return self._create_rejection_response(tool_call, call_context.rejection_reason or "Tool execution blocked")
            
            try:
                # Execute the actual tool (already format-aware in execute_tool)
                result = self.execute_tool(tool_call)
                
                # Update context with result for POST-EXECUTION PHASE
                call_context.tool_result = result
                
                # Execute call intercept hooks again (POST-EXECUTION PHASE)
                if self.hooks:
                    self.hooks.execute_hooks(HookType.CALL_INTERCEPT, call_context)
                
                # Execute after tool call hooks
                if self.hooks:
                    self.hooks.execute_hooks(HookType.AFTER_TOOL_CALL, call_context)
                
                # Return potentially modified result
                return call_context.tool_result
                
            except Exception as e:
                # Execute error hooks for individual tool call
                call_context.error = e
                if self.hooks:
                    self.hooks.execute_hooks(HookType.ON_TOOL_ERROR, call_context)
                raise
    
    def _create_rejection_response(self, tool_call: ProviderToolCall, reason: str) -> ToolResult:
        """Create standardized rejection response for blocked tool calls."""
        from egregore.core.tool_calling.context_components import ToolResult
        from datetime import datetime
        
        return ToolResult(
            tool_call_id=tool_call.tool_call_id,
            tool_name=tool_call.tool_name,
            content=f"Tool execution blocked: {reason}",
            success=False,
            execution_time=datetime.now(),
            error_message=f"Rejected: {reason}",
            metadata={"rejected": True, "reason": reason}
        )
    
    async def execute_tools_with_hooks_async(
        self,
        tool_calls: List[ProviderToolCall],
        agent_id: Optional[str] = None,
        execution_id: Optional[str] = None
    ) -> List[ContextComponent]:
        """
        Async version of execute_tools_with_hooks with async hook support.
        
        Args:
            tool_calls: List of tool calls to execute
            agent_id: Agent identifier for hook context
            execution_id: Execution identifier for hook context
            
        Returns:
            List of tool execution results (ToolResult or ScaffoldResult)
        """
        # Use provided context or fall back to instance context
        effective_agent_id = agent_id or self._agent_id or "unknown"
        effective_execution_id = execution_id or self._execution_id
        
        # Create hook context for the overall execution
        execution_context = BaseExecContext(
            agent_id=effective_agent_id,
            execution_id=effective_execution_id,
            agent=self.agent,
            metadata={
                "tool_count": len(tool_calls),
                "tool_names": [call.tool_name for call in tool_calls]
            }
        )
        
        # Execute before tool execution hooks (async)
        if self.hooks:
            await self.hooks.execute_hooks_async(HookType.BEFORE_TOOL_EXECUTION, execution_context)
        
        results = []
        execution_start_time = datetime.now()
        
        try:
            # Execute each tool with individual hooks
            for tool_call in tool_calls:
                try:
                    result = await self._execute_single_tool_with_hooks_async(
                        tool_call, effective_agent_id, effective_execution_id
                    )
                    results.append(result)
                except Exception as e:
                    logger.error(f"Tool execution failed for {tool_call.tool_name}: {e}")
                    # Create error result
                    error_result = ToolResult(
                        tool_call_id=tool_call.tool_call_id,
                        tool_name=tool_call.tool_name,
                        content=f"Execution failed: {str(e)}",
                        success=False,
                        execution_time=datetime.now(),
                        error_message=str(e)
                    )
                    # Ensure proper ID generation for tool result
                    error_result.metadata.ensure_id(node_type="block", parent_id="")
                    results.append(error_result)
            
            # Update context with results
            md = execution_context.metadata or {}
            md.update({
                "execution_duration": (datetime.now() - execution_start_time).total_seconds(),
                "success_count": sum(1 for r in results if getattr(r, 'success', False)),
                "failure_count": sum(1 for r in results if not getattr(r, 'success', True))
            })
            execution_context.metadata = md
            
            # Execute after tool execution hooks (async)
            if self.hooks:
                await self.hooks.execute_hooks_async(HookType.AFTER_TOOL_EXECUTION, execution_context)
            
            return results
            
        except Exception as e:
            # Execute error hooks (async)
            execution_context.error = e
            if self.hooks:
                await self.hooks.execute_hooks_async(HookType.ON_TOOL_ERROR, execution_context)
            raise
    
    async def _execute_single_tool_with_hooks_async(
        self,
        tool_call: ProviderToolCall,
        agent_id: str,
        execution_id: Optional[str]
    ) -> ContextComponent:
        """Async version of single tool execution with hooks."""
        
        # Get tool declaration to determine type (async version)
        tool_decl = self.registry.get_tool(tool_call.tool_name)
        from egregore.core.tool_calling.tool_declaration import ScaffoldOpDeclaration
        is_scaffold = isinstance(tool_decl, ScaffoldOpDeclaration)
        
        # Create operation context for individual tool call (handles both tools and scaffolds)
        call_context = ContextFactory.create_operation_context(
            agent_id=agent_id,
            tool_declaration=tool_decl,
            tool_params=tool_call.parameters,
            agent=self.agent,
            execution_id=execution_id,
            metadata={
                'tool_call_id': getattr(tool_call, 'tool_call_id', None),
                'execution_start': time.time()
            }
        )
        
        # Apply injection patterns if hooks are available
        if self.hooks:
            modified_params = self.hooks.apply_injection_patterns(
                tool_call.tool_name,
                tool_call.parameters,
                call_context
            )
            # Create modified tool call if parameters were injected
            if modified_params != tool_call.parameters:
                tool_call = ProviderToolCall(
                    tool_call_id=tool_call.tool_call_id,
                    tool_name=tool_call.tool_name,
                    parameters=modified_params
                )
                call_context.tool_params = modified_params
        
        # Execute before tool call hooks (async)
        if self.hooks:
            await self.hooks.execute_hooks_async(HookType.BEFORE_TOOL_CALL, call_context)
        
        try:
            # Execute the actual tool (sync - tools are typically sync)
            result = self.execute_tool(tool_call)
            
            # Update context with result
            call_context.tool_result = result
            
            # Execute after tool call hooks (async)
            if self.hooks:
                await self.hooks.execute_hooks_async(HookType.AFTER_TOOL_CALL, call_context)
            
            return result
            
        except Exception as e:
            # Execute error hooks for individual tool call (async)
            call_context.error = e
            if self.hooks:
                await self.hooks.execute_hooks_async(HookType.ON_TOOL_ERROR, call_context)
            raise
    
    # Streaming Support with Hooks
    
    def process_streaming_chunk(
        self,
        chunk_data: Any,
        agent_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Process streaming chunk with hook integration.
        
        Args:
            chunk_data: Raw chunk data from provider
            agent_id: Agent identifier for hook context
            execution_id: Execution identifier for hook context
            metadata: Additional metadata for the chunk
            
        Returns:
            Processed chunk information or None if chunk was filtered
        """
        if not self.hooks:
            return {"raw_chunk": chunk_data, "processed": False}
        
        # Use provided context or fall back to instance context
        effective_agent_id = agent_id or self._agent_id or "unknown"
        effective_execution_id = execution_id or self._execution_id
        
        # Create streaming context for chunk processing
        chunk_context = ContextFactory.create_stream_context(
            agent_id=effective_agent_id,
            chunk_data=chunk_data,
            agent=self.agent,
            execution_id=effective_execution_id,
            chunk_type="content",  # Default chunk type
            metadata=metadata or {}
        )
        
        try:
            # Execute streaming chunk hooks
            self.hooks.execute_hooks(HookType.ON_STREAMING_CHUNK, chunk_context)
            
            # Check for tool call detection in chunk
            tool_call_info = self._detect_tool_call_in_chunk(chunk_data)
            if tool_call_info:
                # Update context with detected tool call
                chunk_context.tool_calls = [tool_call_info]  # Use StreamExecContext's tool_calls field
                chunk_context.chunk_type = "tool_start"  # Update chunk type for tool detection
                
                # Execute tool call detected hooks
                self.hooks.execute_hooks(HookType.ON_TOOL_CALL_DETECTED, chunk_context)
                
                return {
                    "raw_chunk": chunk_data,
                    "processed": True,
                    "tool_call_detected": True,
                    "tool_info": tool_call_info
                }
            
            return {
                "raw_chunk": chunk_data,
                "processed": True,
                "tool_call_detected": False
            }
            
        except Exception as e:
            logger.error(f"Streaming chunk processing error: {e}")
            # Execute error hooks
            chunk_context.error = e
            if self.hooks:
                self.hooks.execute_hooks(HookType.ON_TOOL_ERROR, chunk_context)
            
            return {
                "raw_chunk": chunk_data,
                "processed": False,
                "error": str(e)
            }
    
    async def process_streaming_chunk_async(
        self,
        chunk_data: Any,
        agent_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Async version of streaming chunk processing.
        
        Args:
            chunk_data: Raw chunk data from provider
            agent_id: Agent identifier for hook context
            execution_id: Execution identifier for hook context
            metadata: Additional metadata for the chunk
            
        Returns:
            Processed chunk information or None if chunk was filtered
        """
        if not self.hooks:
            return {"raw_chunk": chunk_data, "processed": False}
        
        # Use provided context or fall back to instance context
        effective_agent_id = agent_id or self._agent_id or "unknown"
        effective_execution_id = execution_id or self._execution_id
        
        # Create streaming context for chunk processing (async)
        chunk_context = ContextFactory.create_stream_context(
            agent_id=effective_agent_id,
            chunk_data=chunk_data,
            agent=self.agent,
            execution_id=effective_execution_id,
            chunk_type="content",  # Default chunk type
            metadata=metadata or {}
        )
        
        try:
            # Execute streaming chunk hooks (async)
            await self.hooks.execute_hooks_async(HookType.ON_STREAMING_CHUNK, chunk_context)
            
            # Check for tool call detection in chunk
            tool_call_info = self._detect_tool_call_in_chunk(chunk_data)
            if tool_call_info:
                # Update context with detected tool call
                chunk_context.tool_calls = [tool_call_info]  # Use StreamExecContext's tool_calls field
                chunk_context.chunk_type = "tool_start"  # Update chunk type for tool detection
                
                # Execute tool call detected hooks (async)
                await self.hooks.execute_hooks_async(HookType.ON_TOOL_CALL_DETECTED, chunk_context)
                
                return {
                    "raw_chunk": chunk_data,
                    "processed": True,
                    "tool_call_detected": True,
                    "tool_info": tool_call_info
                }
            
            return {
                "raw_chunk": chunk_data,
                "processed": True,
                "tool_call_detected": False
            }
            
        except Exception as e:
            logger.error(f"Streaming chunk processing error: {e}")
            # Execute error hooks (async)
            chunk_context.error = e
            if self.hooks:
                await self.hooks.execute_hooks_async(HookType.ON_TOOL_ERROR, chunk_context)
            
            return {
                "raw_chunk": chunk_data,
                "processed": False,
                "error": str(e)
            }
    
    def _detect_tool_call_in_chunk(self, chunk_data: Any) -> Optional[Dict[str, Any]]:
        """
        Detect tool calls in streaming chunks.
        
        This is a basic implementation that can be enhanced for specific providers.
        
        Args:
            chunk_data: Raw chunk data to analyze
            
        Returns:
            Tool call information if detected, None otherwise
        """
        try:
            # Convert chunk to string for analysis
            chunk_str = str(chunk_data)
            
            # Basic tool call detection patterns
            # This is a simplified implementation - real detection would be provider-specific
            
            # Look for function call patterns
            import re
            
            # Pattern for OpenAI-style function calls in chunks
            function_call_pattern = r'"function_call":\s*{\s*"name":\s*"([^"]+)"'
            match = re.search(function_call_pattern, chunk_str)
            if match:
                tool_name = match.group(1)
                return {
                    "tool_name": tool_name,
                    "parameters": {},  # Would need more parsing for actual parameters
                    "detection_method": "function_call_pattern",
                    "chunk_content": chunk_str[:100]  # First 100 chars for debugging
                }
            
            # Pattern for tool use markers
            tool_use_pattern = r'"tool_use".*?"name":\s*"([^"]+)"'
            match = re.search(tool_use_pattern, chunk_str)
            if match:
                tool_name = match.group(1)
                return {
                    "tool_name": tool_name,
                    "parameters": {},
                    "detection_method": "tool_use_pattern",
                    "chunk_content": chunk_str[:100]
                }
            
            return None
            
        except Exception as e:
            logger.debug(f"Tool call detection error: {e}")
            return None
    
    def create_streaming_accumulator(
        self,
        agent_id: Optional[str] = None,
        execution_id: Optional[str] = None
    ) -> 'StreamingAccumulator':
        """
        Create a streaming accumulator for building responses from chunks.
        
        Args:
            agent_id: Agent identifier for hook context
            execution_id: Execution identifier for hook context
            
        Returns:
            StreamingAccumulator instance
        """
        return StreamingAccumulator(
            tool_executor=self,
            agent_id=agent_id or self._agent_id,
            execution_id=execution_id or self._execution_id
        )
    
    def execute_tool(self, tool_call: Union[ProviderToolCall, "ToolCall"]) -> ContextComponent:
        """Execute tool and return ContextComponent for context tree (Phase 3: Union type support)

        Args:
            tool_call: Either ProviderToolCall (legacy) or ToolCall component (Phase 3)

        Returns:
            Either ToolResult or ScaffoldResult
        """
        # Phase 3: Extract component ID if available (for registry population)
        from .context_components import ToolCall

        call_component_id = None
        if isinstance(tool_call, ToolCall):
            # New Phase 3 flow: ToolCall component from context
            call_component_id = tool_call.id
            tool_call_id = tool_call.tool_call_id
            tool_name = tool_call.tool_name

            # Convert ToolCall → ProviderToolCall for internal execution (backward compat)
            provider_tool_call = ProviderToolCall(
                tool_name=tool_call.tool_name,
                tool_call_id=tool_call.tool_call_id,
                parameters=tool_call.parameters
            )
        else:
            # Legacy flow: ProviderToolCall from response parsing
            provider_tool_call = tool_call
            tool_call_id = tool_call.tool_call_id
            tool_name = tool_call.tool_name

        # Get tool declaration from registry
        tool_decl = self.registry.get_tool(tool_name)
        if not tool_decl:
            return self._create_tool_not_found_error(provider_tool_call)

        # Use type-based detection instead of pattern matching
        from egregore.core.tool_calling.tool_declaration import ScaffoldOpDeclaration

        # Execute tool
        if isinstance(tool_decl, ScaffoldOpDeclaration):
            # Route to scaffold execution - tool already has scaffold metadata
            logger.debug(f"Executing ScaffoldOpDeclaration: {tool_name}")
            result = tool_decl.execute(provider_tool_call)
        else:
            # Route to regular tool execution
            logger.debug(f"Executing regular ToolDeclaration: {tool_name}")
            result = tool_decl.execute(provider_tool_call)

        # Note: Tool pair registration primarily handled automatically via CONTEXT_AFTER_CHANGE hook
        # in Agent._register_tool_registration_hook() when components are inserted into context.
        # However, for Phase 3 flow where execute_tool is called directly with ToolCall component,
        # we need to complete the pair registration here since the result may not be inserted immediately.
        if call_component_id and hasattr(result, 'id'):
            # Phase 3: Complete the tool pair registration
            self.context._registry.complete_tool_pair(tool_call_id, result.id)

        return result
    
    
    def execute_regular_tool(self, tool_call: ProviderToolCall) -> ToolResult:
        """Execute regular tool via ToolRegistry"""
        try:
            # Get tool declaration
            tool = self.registry.get_tool(tool_call.tool_name)
            if not tool:
                return self._create_tool_not_found_error(tool_call)
            
            # Validate parameters
            if tool.parameters:
                validation_error = self._validate_parameters(tool, tool_call.parameters, tool_call.tool_call_id)
                if validation_error:
                    return validation_error
            
            # Execute tool - returns ToolResult
            return tool.execute(tool_call)
            
        except Exception as e:
            # Always return ToolResult, even for errors
            result = ToolResult(
                tool_call_id=tool_call.tool_call_id,
                tool_name=tool_call.tool_name,
                content=f"Internal error executing tool '{tool_call.tool_name}': {str(e)}",
                success=False,
                execution_time=datetime.now(),
                error_message=str(e)
            )
            # Ensure proper ID generation for tool result
            result.metadata.ensure_id(node_type="block", parent_id="")
            return result
    
    
    
    def _create_scaffold_error(self, tool_call: ProviderToolCall, error_message: str) -> ScaffoldResult:
        """Create error ScaffoldResult for scaffold execution failures."""
        return ScaffoldResult(
            tool_call_id=tool_call.tool_call_id,
            tool_name=tool_call.tool_name,
            scaffold_id="error",
            scaffold_type="error",
            operation_name=tool_call.tool_name,
            content=f"Scaffold execution error: {error_message}",
            success=False,
            execution_time=datetime.now(),
            error_message=error_message
        )
    
    def _create_tool_not_found_error(self, tool_call: ProviderToolCall) -> ToolResult:
        """Create error ToolResult for unknown tool with helpful suggestions"""
        
        # Get available tools for suggestions
        available_tools = self.registry.get_all_tools()
        available_names = [tool.name for tool in available_tools]
        
        # Check if this might be a scaffold tool format issue
        scaffold_suggestions = self._generate_scaffold_suggestions(tool_call.tool_name, available_names)
        
        # Generate helpful error message
        if scaffold_suggestions:
            content = f"Tool '{tool_call.tool_name}' not found. {scaffold_suggestions}"
            error_message = f"Tool '{tool_call.tool_name}' not registered. {scaffold_suggestions}"
        else:
            # Find similar tool names
            similar_tools = self._find_similar_tools(tool_call.tool_name, available_names)
            if similar_tools:
                suggestions = f"Did you mean: {', '.join(similar_tools[:3])}?"
                content = f"Tool '{tool_call.tool_name}' not found. {suggestions}"
                error_message = f"Tool '{tool_call.tool_name}' not registered. {suggestions}"
            else:
                if available_names:
                    available_list = ', '.join(available_names[:5])
                    if len(available_names) > 5:
                        available_list += f" (and {len(available_names) - 5} more)"
                    content = f"Tool '{tool_call.tool_name}' not found. Available tools: {available_list}"
                    error_message = f"Tool '{tool_call.tool_name}' not registered. Available: {available_list}"
                else:
                    content = f"Tool '{tool_call.tool_name}' not found. No tools are currently registered."
                    error_message = f"Tool '{tool_call.tool_name}' not registered. No tools available."
        
        result = ToolResult(
            tool_call_id=tool_call.tool_call_id,
            tool_name=tool_call.tool_name,
            content=content,
            success=False,
            execution_time=datetime.now(),
            error_message=error_message
        )
        # Ensure proper ID generation for tool result
        result.metadata.ensure_id(node_type="block", parent_id="")
        return result
    
    def _generate_scaffold_suggestions(self, tool_name: str, available_tools: List[str]) -> str:
        """Generate suggestions for scaffold tool format issues"""
        
        # Check if this looks like a scaffold tool pattern
        if '_' in tool_name:
            # Looks like distinct format: scaffoldname_operation
            parts = tool_name.split('_', 1)
            if len(parts) == 2:
                scaffold_name, operation = parts
                
                # Look for unified format alternative
                if scaffold_name in available_tools:
                    return f"Did you mean '{scaffold_name}' with action parameter? Try: '{scaffold_name}' with action='{operation}'"
                
                # Look for similar scaffold names
                scaffold_matches = [t for t in available_tools if t.startswith(scaffold_name)]
                if scaffold_matches:
                    return f"Found similar scaffold tools: {', '.join(scaffold_matches[:3])}"
        else:
            # Might be unified format but scaffold not available
            # Look for distinct format alternatives
            distinct_matches = [t for t in available_tools if t.startswith(f"{tool_name}_")]
            if distinct_matches:
                return f"Found distinct format tools: {', '.join(distinct_matches[:3])}"
        
        return ""
    
    def _find_similar_tools(self, target: str, available_tools: List[str]) -> List[str]:
        """Find similar tool names using difflib"""
        # Use difflib to get close matches with cutoff of 0.6
        close_matches = difflib.get_close_matches(target, available_tools, n=3, cutoff=0.6)
        return close_matches
    
    def _create_scaffold_not_found_error(self, tool_call: ProviderToolCall) -> ScaffoldResult:
        """Create error ScaffoldResult for unknown scaffold."""
        # Since this method is only called when we have a ScaffoldOpDeclaration but execution failed,
        # we can extract scaffold info from the tool name or just use 'unknown'
        scaffold_name = tool_call.tool_name  # Use tool name as fallback
        
        # Try to provide helpful suggestions
        available_scaffolds = []
        if self.agent and hasattr(self.agent, '_agent_config') and self.agent._agent_config.scaffolds:
            available_scaffolds = [getattr(s, 'type', 'unknown') for s in self.agent._agent_config.scaffolds]
        
        if available_scaffolds:
            content = f"Scaffold '{scaffold_name}' not found. Available scaffolds: {', '.join(available_scaffolds)}"
        else:
            content = f"Scaffold '{scaffold_name}' not found. No scaffolds are configured for this agent."
        
        return ScaffoldResult(
            tool_call_id=tool_call.tool_call_id,
            tool_name=tool_call.tool_name,
            scaffold_id="not_found",
            scaffold_type="not_found",
            operation_name=tool_call.tool_name,
            content=content,
            success=False,
            execution_time=datetime.now(),
            error_message=f"Scaffold '{scaffold_name}' not found"
        )
    
    def _validate_parameters(self, tool, params: Dict[str, Any], tool_call_id: str) -> Optional[ToolResult]:
        """Validate tool parameters and return error ToolResult if invalid"""
        try:
            # Check if tool has parameter schema
            if not tool.parameters:
                return None  # No validation needed if no parameters defined
            
            # Check required parameters are present
            required_params = getattr(tool.parameters, 'required', [])
            if required_params:
                missing_params = [param for param in required_params if param not in params]
                if missing_params:
                    result = ToolResult(
                        tool_call_id=tool_call_id,
                        tool_name=tool.name,
                        content=f"Missing required parameters: {', '.join(missing_params)}",
                        success=False,
                        execution_time=datetime.now(),
                        error_message=f"Required parameters missing: {missing_params}"
                    )
                    # Ensure proper ID generation for tool result
                    result.metadata.ensure_id(node_type="block", parent_id="")
                    return result
            
            # Basic type validation for provided parameters
            properties = getattr(tool.parameters, 'properties', {})
            if properties:
                for param_name, param_value in params.items():
                    if param_name in properties:
                        param_schema = properties[param_name]
                        validation_error = self._validate_parameter_type(param_name, param_value, param_schema)
                        if validation_error:
                            result = ToolResult(
                                tool_call_id=tool_call_id,
                                tool_name=tool.name,
                                content=f"Parameter validation failed for '{param_name}': {validation_error}",
                                success=False,
                                execution_time=datetime.now(),
                                error_message=validation_error
                            )
                            # Ensure proper ID generation for tool result
                            result.metadata.ensure_id(node_type="block", parent_id="")
                            return result
            
            return None  # Validation passed
            
        except Exception as e:
            # If validation itself fails, return error
            result = ToolResult(
                tool_call_id=tool_call_id,
                tool_name=tool.name,
                content=f"Parameter validation error: {str(e)}",
                success=False,
                execution_time=datetime.now(),
                error_message=f"Validation system error: {str(e)}"
            )
            # Ensure proper ID generation for tool result
            result.metadata.ensure_id(node_type="block", parent_id="")
            return result
    
    def _validate_parameter_type(self, param_name: str, param_value: Any, param_schema) -> Optional[str]:
        """Validate a single parameter type and return error message if invalid"""
        try:
            from egregore.core.tool_calling.schema import SchemaType
            
            schema_type = getattr(param_schema, 'type', None)
            
            if schema_type == SchemaType.STRING and not isinstance(param_value, str):
                return f"Expected string, got {type(param_value).__name__}"
            elif schema_type == SchemaType.INTEGER and not isinstance(param_value, int):
                return f"Expected integer, got {type(param_value).__name__}"
            elif schema_type == SchemaType.NUMBER and not isinstance(param_value, (int, float)):
                return f"Expected number, got {type(param_value).__name__}"
            elif schema_type == SchemaType.BOOLEAN and not isinstance(param_value, bool):
                return f"Expected boolean, got {type(param_value).__name__}"
            elif schema_type == SchemaType.ARRAY and not isinstance(param_value, list):
                return f"Expected array, got {type(param_value).__name__}"
            elif schema_type == SchemaType.OBJECT and not isinstance(param_value, dict):
                return f"Expected object, got {type(param_value).__name__}"
            
            return None  # Type validation passed
            
        except Exception as e:
            return f"Type validation error: {str(e)}"
    
    # ContextHistory integration methods
    
    def set_context_history(self, history) -> None:
        """Set the context history for tracking tool executions
        
        Args:
            history: ContextHistory instance to integrate with
        """
        self.context_history = history
    
    def execute_tools_with_tracking(
        self,
        tool_calls: List[ProviderToolCall],
        cycle_id: str,
        snapshot_id: Optional[str] = None,
        provider_name: Optional[str] = None
    ) -> List[ToolResult]:
        """Execute multiple tools and track execution in history
        
        Args:
            tool_calls: List of tool calls to execute
            cycle_id: Message cycle identifier
            snapshot_id: Optional snapshot ID that triggered execution
            provider_name: Optional provider name
            
        Returns:
            List of tool execution results (only ToolResult, not ScaffoldResult)
        """
        results = []
        
        # Execute each tool call
        for tool_call in tool_calls:
            result = self.execute_tool(tool_call)
            # Only include ToolResult in tracking (not scaffolds)
            if isinstance(result, ToolResult):
                results.append(result)
        
        # Track execution if history is available and we have results
        if self.context_history and results:
            self._track_tool_execution(
                tool_calls=tool_calls,
                results=results,
                snapshot_id=snapshot_id or f"snapshot_{cycle_id}",
                cycle_id=cycle_id,
                provider_name=provider_name
            )
        
        return results
    
    def _track_tool_execution(
        self,
        tool_calls: List[ProviderToolCall],
        results: List[ToolResult],
        snapshot_id: str,
        cycle_id: str,
        provider_name: Optional[str] = None
    ) -> None:
        """Track tool execution by creating and adding ToolExecutionGroup
        
        Args:
            tool_calls: List of tool calls made
            results: List of execution results
            snapshot_id: ID of snapshot that triggered execution
            cycle_id: Message cycle identifier
            provider_name: Name of provider that made the calls
        """
        from .tool_execution_group import ToolExecutionGroup, ToolExecution
        
        group_id = f"group_{cycle_id}_{int(datetime.now().timestamp())}"
        
        group = ToolExecutionGroup(
            id=group_id,
            cycle_id=cycle_id,
            snapshot_id=snapshot_id,
            provider_name=provider_name,
            context_size_before=None,  # Could be set by caller
            context_size_after=None,   # Could be set by caller
            completed_at=None,
            total_duration_ms=None,
        )
        
        # Pair tool calls with results
        for i, tool_call in enumerate(tool_calls):
            result = results[i] if i < len(results) else None
            
            execution = ToolExecution(
                tool_call=tool_call,
                result=result,
                scaffold_result=None,
                tool_name=tool_call.tool_name,
                tool_call_id=tool_call.tool_call_id,
                execution_time=(result.execution_time or datetime.now()) if result else datetime.now(),
                duration_ms=None,  # Could be calculated if timing data available
                error=None if result and result.success else "Execution failed"
            )
            
            group.add_execution(execution)
        
        group.mark_completed()
        
        # Add to history
        if self.context_history is not None:
            self.context_history.add_execution_group(group, snapshot_id)


class StreamingAccumulator:
    """
    Accumulates streaming chunks into complete responses with hook integration.
    
    Provides methods for building final responses from streaming chunks
    and detecting when tool calls are complete.
    """
    
    def __init__(self, tool_executor: ToolExecutor, agent_id: Optional[str], execution_id: Optional[str]):
        """
        Initialize streaming accumulator.
        
        Args:
            tool_executor: ToolExecutor instance for hook integration
            agent_id: Agent identifier for hook context
            execution_id: Execution identifier for hook context
        """
        self.tool_executor = tool_executor
        self.agent_id = agent_id
        self.execution_id = execution_id
        
        # Accumulation state
        self.chunks: List[Any] = []
        self.accumulated_content: str = ""
        self.detected_tool_calls: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {}
        
        # Processing state
        self.is_complete: bool = False
        self.completion_reason: Optional[str] = None
        
        logger.debug(f"StreamingAccumulator initialized for agent {agent_id}")
    
    def add_chunk(self, chunk_data: Any, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Add a chunk to the accumulator with hook processing.
        
        Args:
            chunk_data: Raw chunk data from provider
            metadata: Optional metadata for the chunk
            
        Returns:
            Processing result from tool executor
        """
        # Process chunk through tool executor hooks
        result = self.tool_executor.process_streaming_chunk(
            chunk_data=chunk_data,
            agent_id=self.agent_id,
            execution_id=self.execution_id,
            metadata=metadata
        )
        
        # Store chunk and update accumulation
        self.chunks.append(chunk_data)
        
        # Update accumulated content (basic string concatenation)
        chunk_str = str(chunk_data)
        self.accumulated_content += chunk_str
        
        # Track detected tool calls
        if result and result.get("tool_call_detected"):
            tool_info = result.get("tool_info")
            if tool_info:
                self.detected_tool_calls.append(tool_info)
        
        # Update metadata
        if metadata:
            self.metadata.update(metadata)
        
        return result or {"processed": False}
    
    async def add_chunk_async(self, chunk_data: Any, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Async version of add_chunk.
        
        Args:
            chunk_data: Raw chunk data from provider
            metadata: Optional metadata for the chunk
            
        Returns:
            Processing result from tool executor
        """
        # Process chunk through tool executor hooks (async)
        result = await self.tool_executor.process_streaming_chunk_async(
            chunk_data=chunk_data,
            agent_id=self.agent_id,
            execution_id=self.execution_id,
            metadata=metadata
        )
        
        # Store chunk and update accumulation
        self.chunks.append(chunk_data)
        
        # Update accumulated content (basic string concatenation)
        chunk_str = str(chunk_data)
        self.accumulated_content += chunk_str
        
        # Track detected tool calls
        if result and result.get("tool_call_detected"):
            tool_info = result.get("tool_info")
            if tool_info:
                self.detected_tool_calls.append(tool_info)
        
        # Update metadata
        if metadata:
            self.metadata.update(metadata)
        
        return result or {"processed": False}
    
    def mark_complete(self, reason: str = "stream_ended") -> None:
        """
        Mark the streaming as complete.
        
        Args:
            reason: Reason for completion
        """
        self.is_complete = True
        self.completion_reason = reason
        logger.debug(f"StreamingAccumulator marked complete: {reason}")
    
    def get_accumulated_content(self) -> str:
        """Get the accumulated content string."""
        return self.accumulated_content
    
    def get_detected_tool_calls(self) -> List[Dict[str, Any]]:
        """Get list of detected tool calls."""
        return self.detected_tool_calls.copy()
    
    def get_chunk_count(self) -> int:
        """Get number of chunks processed."""
        return len(self.chunks)
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get accumulated metadata."""
        return self.metadata.copy()
    
    def build_final_response(self) -> Dict[str, Any]:
        """
        Build final response from accumulated chunks.
        
        Returns:
            Complete response information
        """
        return {
            "content": self.accumulated_content,
            "chunk_count": len(self.chunks),
            "tool_calls_detected": len(self.detected_tool_calls),
            "tool_calls": self.detected_tool_calls,
            "metadata": self.metadata,
            "is_complete": self.is_complete,
            "completion_reason": self.completion_reason
        }
    
    def reset(self) -> None:
        """Reset the accumulator for reuse."""
        self.chunks.clear()
        self.accumulated_content = ""
        self.detected_tool_calls.clear()
        self.metadata.clear()
        self.is_complete = False
        self.completion_reason = None
        logger.debug("StreamingAccumulator reset")
    
    def __len__(self) -> int:
        """Get number of chunks."""
        return len(self.chunks)
    
    def __str__(self) -> str:
        """String representation."""
        return f"StreamingAccumulator(chunks={len(self.chunks)}, content_length={len(self.accumulated_content)}, complete={self.is_complete})"