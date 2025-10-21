"""
Unified Hooks Accessor for V2 Agent

Provides clean hierarchical syntax: agent.hooks.tool.*, agent.hooks.streaming.*, agent.hooks.context.*
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base import Agent

from .hooks.accessors import ToolHooks, StreamingHooks, ContextHooks, MessageHooks, ScaffoldHooks, OperationHooks


class HooksAccessor:
    """
    Unified hooks accessor providing hierarchical structure.
    
    Usage:
        # Tool hooks
        @agent.hooks.tool.pre_call
        @agent.hooks.tool.post_call
        @agent.hooks.tool.on_error
        
        # Streaming hooks
        @agent.hooks.streaming.chunk
        @agent.hooks.streaming.tool_detection
        
        # Context hooks  
        @agent.hooks.context.pre
        @agent.hooks.context.post
        @agent.hooks.context.on_error
        
        # Message hooks
        @agent.hooks.message.on_user_msg
        @agent.hooks.message.on_provider_msg
        @agent.hooks.message.on_error
        
        # Scaffold hooks
        @agent.hooks.scaffold.pre
        @agent.hooks.scaffold.post  
        @agent.hooks.scaffold.on_error
        @agent.hooks.scaffold.on_state_change
        
        # Universal operation hooks
        @agent.hooks.operation.before
        @agent.hooks.operation.after
        @agent.hooks.operation.on_error
    """
    
    def __init__(self, agent: 'Agent'):
        self._agent = agent
        # Hierarchical accessors
        self._tool = None
        self._streaming = None
        self._context = None
        self._message = None
        self._scaffold = None
        self._operation = None
    
    # Hierarchical accessors
    
    @property
    def tool(self) -> ToolHooks:
        """New hierarchical tool hooks accessor."""
        if self._tool is None:
            self._tool = ToolHooks(self._agent)
        return self._tool
    
    @property
    def streaming(self) -> StreamingHooks:
        """New hierarchical streaming hooks accessor.""" 
        if self._streaming is None:
            self._streaming = StreamingHooks(self._agent)
        return self._streaming
    
    @property
    def context(self) -> ContextHooks:
        """New hierarchical context hooks accessor."""
        if self._context is None:
            self._context = ContextHooks(self._agent)
        return self._context
    
    @property
    def message(self) -> MessageHooks:
        """Message lifecycle hooks accessor."""
        if self._message is None:
            self._message = MessageHooks(self._agent)
        return self._message
    
    @property
    def scaffold(self) -> ScaffoldHooks:
        """Scaffold operation hooks accessor."""
        if self._scaffold is None:
            self._scaffold = ScaffoldHooks(self._agent)
        return self._scaffold
    
    @property
    def operation(self) -> OperationHooks:
        """Universal operation hooks accessor."""
        if self._operation is None:
            self._operation = OperationHooks(self._agent)
        return self._operation