"""
Specialized execution contexts for type-safe hook system.

This module provides type-safe execution contexts that replace the generic ExecutionContext
with specialized context types for different hook categories. Each context type contains
only the fields relevant to its specific hook category, providing better type safety,
IDE support, and performance.

Context Hierarchy:
- BaseExecContext: Common fields shared by all contexts
- ToolExecContext: Tool execution hooks (tool.pre_call, tool.post_call, etc.)
- StreamExecContext: Streaming hooks (streaming.chunk, streaming.tool_detection, etc.)
- ScaffoldExecContext: Scaffold operation hooks (context.on_scaffold_op)
- ContextExecContext: Context lifecycle hooks (context.on_message_start, etc.)
- OperationExecContext: Universal hooks that handle both regular tools and scaffold operations
"""

from typing import Any, Dict, Optional, List, Union, TYPE_CHECKING
from dataclasses import dataclass
from abc import ABC

if TYPE_CHECKING:
    from ...tool_calling.tool_declaration import ToolDeclaration, ScaffoldOpDeclaration


@dataclass
class BaseExecContext(ABC):
    """
    Base execution context with fields common to all hook types.
    
    All specialized contexts inherit from this base to ensure consistent
    agent and execution tracking across all hook categories. This provides
    the common infrastructure while allowing each specialized context to
    add only the fields relevant to its hook category.
    
    Fields:
        agent_id: Unique identifier for the agent instance
        execution_id: Optional execution context identifier
        agent: Direct reference to the agent instance (always available)
        metadata: Optional dictionary for additional context data
        error: Optional exception that occurred during execution
    """
    agent_id: str
    execution_id: Optional[str] = None
    agent: Optional[Any] = None  # Agent reference is always available in practice
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[Exception] = None


@dataclass
class ContextExecContext(BaseExecContext):
    """
    Execution context for context processing hooks.

    Provides direct access to the agent's context for maximum flexibility.
    Users can directly call context operations like select, dispatch, add, etc.

    Used by context operation hooks such as:
    - agent.hooks.context.on_add: When components are added to context
    - agent.hooks.context.on_dispatch: When context notifications/updates are sent
    - agent.hooks.context.on_update: When context is updated
    - agent.hooks.context.before_change: Before any context modification (insert/update/delete)
    - agent.hooks.context.after_change: After any context modification (insert/update/delete)

    Fields:
        context: Full context object from agent for direct operations
        operation_type: Type of context operation being performed
        component: Component being inserted/updated/deleted (Phase 1)
        selector: PACT selector for the operation (Phase 1)
        mode: Update mode for pact_update operations (Phase 1)
    """
    # Direct context access - the whole context object
    context: Optional[Any] = None  # Full context object from agent

    # Operation metadata (minimal)
    operation_type: str = ""  # "add", "dispatch", "update", "seal", "render", "cleanup", "component_add", "insert", "delete"

    # Phase 1: Hook System Unification - Additional fields for context lifecycle hooks
    component: Optional[Any] = None  # Component being modified
    selector: Optional[str] = None  # PACT selector (e.g., "d0,1")
    mode: Optional[str] = None  # Update mode ("replace", "append", etc.)

    @property
    def agent_context(self) -> Optional[Any]:
        """Alias for context - more explicit naming."""
        return self.context


@dataclass
class ToolExecContext(ContextExecContext):
    """
    Context for tool execution hooks with tool-specific fields.

    Tools insert ToolCall/ToolResult components into the context tree, making
    them context-manipulating operations. Inherits from ContextExecContext to
    provide access to the full context tree during tool execution.

    Used by tool execution hooks such as:
    - agent.hooks.tool.pre_call: Before individual tool call
    - agent.hooks.tool.post_call: After individual tool call
    - agent.hooks.tool.on_error: When tool execution errors occur
    - agent.hooks.tool.on_async_complete: When async tool execution completes

    Inherited from ContextExecContext:
        context: Full context tree access
        operation_type: "tool_call_insert" or "tool_result_insert"
        component: ToolCall or ToolResult component being inserted
        selector: PACT selector for insertion point

    Tool-specific fields:
        tool_name: Name of the tool being executed (guaranteed to exist)
        tool_params: Parameters passed to the tool (guaranteed to exist)
        tool_result: Result returned by tool execution (None if not yet executed)
        execution_time: Time taken for tool execution in seconds (None if not measured)
        validation_rejected: Whether tool input/output validation was rejected
        rejection_reason: Reason for validation rejection (if applicable)
    """
    # Required tool fields - use defaults to work with dataclass inheritance
    tool_name: str = ""
    tool_params: Dict[str, Any] = None
    
    # Optional tool fields
    tool_result: Optional[Any] = None
    execution_time: Optional[float] = None
    
    # Validation fields for tool input/output validation
    validation_rejected: bool = False
    rejection_reason: Optional[str] = None
    
    def __post_init__(self):
        """Initialize mutable default values."""
        if self.tool_params is None:
            self.tool_params = {}


@dataclass
class StreamExecContext(BaseExecContext):
    """
    Context for streaming hooks with chunk-specific fields.
    
    Used by streaming hooks such as:
    - agent.hooks.streaming.chunk: For streaming chunk processing
    - agent.hooks.streaming.tool_detection: For tool call detection in streaming
    - agent.hooks.streaming.on_response_complete: For streaming response completion
    
    This context provides guaranteed access to streaming-specific information
    such as chunk data, chunk type, and accumulated content without the overhead
    of unused fields from other hook categories.
    
    Fields:
        chunk_data: The actual chunk data from the streaming response
        chunk_type: Type of chunk (content|tool_start|tool_delta|tool_complete|tool_result)
        accumulated_content: Content accumulated so far in the streaming response
        finish_reason: Reason for streaming completion (if applicable)
        tool_calls: Complete tool calls detected in streaming (if applicable)
        partial_tool_calls: Partial/incomplete tool calls being accumulated (if applicable)
    """
    # Required streaming fields
    chunk_data: Any = None
    
    # Streaming metadata fields
    chunk_type: str = "content"
    accumulated_content: str = ""
    finish_reason: Optional[str] = None
    
    # Tool-related streaming data
    tool_calls: Optional[List[Any]] = None
    partial_tool_calls: Optional[List[Any]] = None


@dataclass
class ScaffoldExecContext(ContextExecContext):
    """
    Context for scaffold operation hooks with scaffold-specific fields.

    Scaffolds insert/update state components in the context tree via @operation
    decorator, making them context-manipulating operations. Inherits from
    ContextExecContext to provide access to the full context tree during
    scaffold operations.

    Used by scaffold operation hooks such as:
    - agent.hooks.context.on_scaffold_op: When scaffold operations are executed
    - agent.hooks.context.on_scaffold_state_change: When scaffold state changes

    Inherited from ContextExecContext:
        context: Full context tree access
        operation_type: "scaffold_insert", "scaffold_update", or "scaffold_state_change"
        component: Scaffold state component being inserted/updated
        selector: PACT selector for insertion/update point

    Scaffold-specific fields:
        scaffold_type: Type identifier of the scaffold (e.g., 'file_manager', 'internal_notes')
        scaffold_id: Unique identifier for the scaffold instance
        operation_name: Name of the operation being executed (e.g., 'append', 'create_file')
        scaffold: Direct reference to the scaffold instance (for state access)
        operation_result: Result returned by the scaffold operation (if completed)
        state_changed: Whether the scaffold state was modified by the operation
        operation_start: Timestamp when the operation started (if measured)
        operation_duration: Duration of the operation in seconds (if measured)
    """
    # Required scaffold fields
    scaffold_type: str = ""
    scaffold_id: str = ""
    operation_name: str = ""
    
    # Optional scaffold fields
    scaffold: Optional[Any] = None  # Direct scaffold reference
    operation_result: Optional[Any] = None
    state_changed: bool = False
    
    # Operation timing fields
    operation_start: Optional[float] = None
    operation_duration: Optional[float] = None
    
    # State change fields (for ON_SCAFFOLD_STATE_CHANGE hook)
    changed_fields: Optional[list[str]] = None
    snapshot: Optional[dict] = None
    phase: Optional[str] = None


@dataclass
class MessageExecContext(BaseExecContext):
    """
    Execution context for message editing hooks.
    
    Provides editable message content for hooks that modify user input
    or provider responses, with full context access for audit trails.
    
    Used by message editing hooks such as:
    - agent.hooks.message.on_user_msg: Edit user message before provider
    - agent.hooks.message.on_provider_msg: Edit provider response after seal (final response only)
    - agent.hooks.message.on_error: When message processing errors occur
    
    Fields:
        message_content: The message content that can be edited
        message_type: "user_input" or "provider_response"
        message_id: Unique message identifier
        context: Full context object for audit trails
        is_final_response: True if this is final provider response (not tool calling)
        content_length: Original content length
    """
    # Editable message content - hooks modify this
    message_content: Any = None     # The message content that can be edited
    
    # Message identification
    message_type: str = ""          # "user_input" or "provider_response"
    message_id: str = ""            # Unique message identifier
    
    # Context access for audit trails
    context: Optional[Any] = None  # Full context object for audit trails
    
    # Processing metadata
    is_final_response: bool = False  # True if this is final provider response (not tool calling)
    content_length: int = 0          # Original content length

    # Error handling (Phase 5)
    error: Optional[Exception] = None  # Exception that occurred during message processing

    @property
    def is_user_input(self) -> bool:
        return self.message_type == "user_input"
        
    @property
    def is_provider_response(self) -> bool:
        return self.message_type == "provider_response"


@dataclass
class OperationExecContext(BaseExecContext):
    """
    Context for hooks that handle both regular tools AND scaffold operations.
    
    Used by universal hooks that need to work with both tool types:
    - agent.hooks.execution.universal: For hooks that handle both tool and scaffold operations
    
    This context provides a unified interface that works with both ToolDeclaration and
    ScaffoldOpDeclaration, allowing hooks to handle both types through type-based detection.
    
    Fields:
        tool_declaration: The source tool declaration (ToolDeclaration or ScaffoldOpDeclaration)
        tool_name: Tool name (available for both types - tool_declaration.name)
        tool_params: Tool parameters (always available)
        tool_result: Result from tool/scaffold execution (if completed)
        execution_time: Time taken for execution in seconds (if measured)
        
    Type-specific access:
        Use is_scaffold_operation property to determine if this is a scaffold operation
        Use scaffold_metadata property to get scaffold-specific information
    """
    # Universal fields available for both tool types
    tool_declaration: Union["ToolDeclaration", "ScaffoldOpDeclaration"] = None
    tool_name: str = ""
    tool_params: Dict[str, Any] = None
    tool_result: Optional[Any] = None
    execution_time: Optional[float] = None

    # Validation fields for tool input/output validation
    validation_rejected: bool = False
    rejection_reason: Optional[str] = None
    
    def __post_init__(self):
        """Initialize mutable default values."""
        if self.tool_params is None:
            self.tool_params = {}
    
    @property
    def is_scaffold_operation(self) -> bool:
        """Check if this is a scaffold operation via ScaffoldOpDeclaration type detection."""
        if self.tool_declaration is None:
            return False
        # Import here to avoid circular imports
        from ...tool_calling.tool_declaration import ScaffoldOpDeclaration
        return isinstance(self.tool_declaration, ScaffoldOpDeclaration)
    
    @property
    def scaffold_metadata(self) -> Optional[Dict[str, str]]:
        """Get scaffold metadata if this is a scaffold operation, None otherwise."""
        if self.is_scaffold_operation:
            return {
                'scaffold_type': self.tool_declaration.scaffold_type,
                'scaffold_id': self.tool_declaration.scaffold_id,
                'operation_name': self.tool_declaration.operation_name
            }
        return None


class ContextFactory:
    """
    Factory class for creating appropriate execution context types.
    
    Provides static methods to create the correct specialized execution context
    based on the hook category and available data. This factory pattern ensures
    consistent context creation and proper field initialization across the
    hook system.
    
    The factory methods handle:
    - Required parameter validation
    - Optional parameter defaults
    - Proper inheritance hierarchy setup
    - Extensibility via **kwargs pattern
    
    Usage:
        # Create tool execution context
        tool_context = ContextFactory.create_tool_context(
            agent_id="agent_123",
            tool_name="search",
            tool_params={"query": "python"},
            agent=agent_instance
        )
        
        # Create streaming context
        stream_context = ContextFactory.create_stream_context(
            agent_id="agent_123", 
            chunk_data={"delta": "Hello"},
            agent=agent_instance
        )
    """
    
    @staticmethod
    def create_tool_context(
        agent_id: str,
        tool_name: str,
        tool_params: Dict[str, Any],
        agent: Any,
        execution_id: Optional[str] = None,
        **kwargs
    ) -> ToolExecContext:
        """
        Create tool execution context for tool-related hooks.
        
        Args:
            agent_id: Unique identifier for the agent instance
            tool_name: Name of the tool being executed
            tool_params: Parameters passed to the tool
            agent: Direct reference to the agent instance
            execution_id: Optional execution context identifier
            **kwargs: Additional optional fields (tool_result, execution_time, 
                     validation_rejected, rejection_reason, metadata, error)
                     
        Returns:
            ToolExecContext: Configured tool execution context
            
        Example:
            context = ContextFactory.create_tool_context(
                agent_id="agent_123",
                tool_name="search_function", 
                tool_params={"query": "python", "limit": 10},
                agent=agent_instance,
                execution_id="exec_456",
                tool_result={"results": ["item1", "item2"]},
                execution_time=1.5
            )
        """
        return ToolExecContext(
            agent_id=agent_id,
            execution_id=execution_id,
            agent=agent,
            tool_name=tool_name,
            tool_params=tool_params,
            **kwargs
        )
    
    @staticmethod
    def create_stream_context(
        agent_id: str,
        chunk_data: Any,
        agent: Any,
        chunk_type: str = "content",
        execution_id: Optional[str] = None,
        **kwargs
    ) -> StreamExecContext:
        """
        Create streaming context for streaming-related hooks.
        
        Args:
            agent_id: Unique identifier for the agent instance
            chunk_data: The actual chunk data from the streaming response
            agent: Direct reference to the agent instance
            chunk_type: Type of chunk (content|tool_start|tool_delta|tool_complete|tool_result)
            execution_id: Optional execution context identifier
            **kwargs: Additional optional fields (accumulated_content, finish_reason,
                     tool_calls, partial_tool_calls, metadata, error)
                     
        Returns:
            StreamExecContext: Configured streaming execution context
            
        Example:
            context = ContextFactory.create_stream_context(
                agent_id="agent_123",
                chunk_data={"delta": "Hello", "content": "Hello world"},
                agent=agent_instance,
                chunk_type="content",
                execution_id="exec_456",
                accumulated_content="Hello world so far",
                tool_calls=[{"id": "call_123", "function": "search"}]
            )
        """
        return StreamExecContext(
            agent_id=agent_id,
            execution_id=execution_id,
            agent=agent,
            chunk_data=chunk_data,
            chunk_type=chunk_type,
            **kwargs
        )
    
    @staticmethod
    def create_scaffold_context(
        agent_id: str,
        scaffold_type: str,
        scaffold_id: str,
        operation_name: str,
        agent: Any,
        scaffold: Optional[Any] = None,
        execution_id: Optional[str] = None,
        **kwargs
    ) -> ScaffoldExecContext:
        """
        Create scaffold operation context for scaffold-related hooks.
        
        Args:
            agent_id: Unique identifier for the agent instance
            scaffold_type: Type identifier of the scaffold (e.g., 'file_manager', 'internal_notes')
            scaffold_id: Unique identifier for the scaffold instance
            operation_name: Name of the operation being executed (e.g., 'append', 'create_file')
            agent: Direct reference to the agent instance
            scaffold: Optional direct reference to the scaffold instance (for state access)
            execution_id: Optional execution context identifier
            **kwargs: Additional optional fields (operation_result, state_changed,
                     operation_start, operation_duration, metadata, error)
                     
        Returns:
            ScaffoldExecContext: Configured scaffold execution context
            
        Example:
            context = ContextFactory.create_scaffold_context(
                agent_id="agent_123",
                scaffold_type="file_manager",
                scaffold_id="scaffold_456",
                operation_name="create_file",
                agent=agent_instance,
                scaffold=file_manager_instance,
                execution_id="exec_789",
                operation_result={"file": "created.txt"},
                state_changed=True,
                operation_duration=0.5
            )
        """
        return ScaffoldExecContext(
            agent_id=agent_id,
            execution_id=execution_id,
            agent=agent,
            scaffold_type=scaffold_type,
            scaffold_id=scaffold_id,
            operation_name=operation_name,
            scaffold=scaffold,
            **kwargs
        )
    
    @staticmethod
    def create_operation_context(
        agent_id: str,
        tool_declaration: Union["ToolDeclaration", "ScaffoldOpDeclaration"],
        tool_params: Dict[str, Any],
        agent: Any,
        execution_id: Optional[str] = None,
        **kwargs
    ) -> OperationExecContext:
        """
        Create universal operation context for hooks that handle both tool types.
        
        This factory method creates contexts for hooks that need to work with both
        regular tools and scaffold operations, using the ScaffoldOpDeclaration system
        for type-based routing and detection.
        
        Args:
            agent_id: Unique identifier for the agent instance
            tool_declaration: Source tool declaration (ToolDeclaration or ScaffoldOpDeclaration)
            tool_params: Parameters passed to the tool/scaffold operation
            agent: Direct reference to the agent instance
            execution_id: Optional execution context identifier
            **kwargs: Additional optional fields (tool_result, execution_time, metadata, error)
                     
        Returns:
            OperationExecContext: Configured universal operation context
            
        Example:
            # For a regular tool
            context = ContextFactory.create_operation_context(
                agent_id="agent_123",
                tool_declaration=tool_decl,
                tool_params={"query": "search"},
                agent=agent_instance,
                execution_id="exec_456"
            )
            
            # For a scaffold operation (ScaffoldOpDeclaration)
            context = ContextFactory.create_operation_context(
                agent_id="agent_123", 
                tool_declaration=scaffold_tool_decl,
                tool_params={"content": "new note"},
                agent=agent_instance,
                execution_id="exec_789"
            )
            
            # Usage in hook
            if context.is_scaffold_operation:
                metadata = context.scaffold_metadata
                print(f"Scaffold {metadata['scaffold_type']} operation: {metadata['operation_name']}")
            else:
                print(f"Regular tool: {context.tool_name}")
        """
        return OperationExecContext(
            agent_id=agent_id,
            execution_id=execution_id,
            agent=agent,
            tool_declaration=tool_declaration,
            tool_name=tool_declaration.name,
            tool_params=tool_params,
            **kwargs
        )
    
    @staticmethod
    def create_context_context(agent_id: str, context: Any, 
                              operation_type: str, **kwargs) -> ContextExecContext:
        """Create context operation context."""
        return ContextExecContext(
            agent_id=agent_id,
            context=context,
            operation_type=operation_type,
            **kwargs
        )

    @staticmethod  
    def create_user_message_context(message_content: Any, context: Any = None,
                                  message_id: str = "", agent_id: str = "unknown",
                                  **kwargs) -> MessageExecContext:
        """Create user message editing context."""
        return MessageExecContext(
            agent_id=agent_id,
            message_content=message_content,
            message_type="user_input",
            message_id=message_id,
            context=context,
            content_length=len(str(message_content)) if message_content else 0,
            **kwargs
        )
    
    @staticmethod
    def create_provider_message_context(message_content: Any, context: Any = None,
                                      message_id: str = "", agent_id: str = "unknown",
                                      is_final_response: bool = True, **kwargs) -> MessageExecContext:
        """Create provider message editing context."""
        return MessageExecContext(
            agent_id=agent_id,
            message_content=message_content,
            message_type="provider_response",
            message_id=message_id,
            context=context,
            is_final_response=is_final_response,
            content_length=len(str(message_content)) if message_content else 0,
            **kwargs
        )

    @staticmethod
    def create_message_error_context(message_content: Any, context: Any, error: Exception,
                                    message_type: str, agent_id: str = "unknown",
                                    **kwargs) -> MessageExecContext:
        """Create message error context (Phase 5)."""
        return MessageExecContext(
            agent_id=agent_id,
            message_content=message_content,
            message_type=message_type,
            context=context,
            error=error,
            **kwargs
        )