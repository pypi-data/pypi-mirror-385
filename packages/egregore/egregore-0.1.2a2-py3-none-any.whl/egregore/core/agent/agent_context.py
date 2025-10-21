"""
Agent Context Management System

Provides AgentContextManager for agent-specific context operations including:
- @agent.context.listener() decorator for agent-scoped context listeners
- @agent.context.add() decorator for simple content addition
- agent.context["type"] = content direct assignment syntax
"""

from typing import List, Callable, Optional, Dict, Any, Union, Tuple, TYPE_CHECKING
from dataclasses import dataclass
import weakref
import logging

if TYPE_CHECKING:
    from .base import Agent
    from ..context_management.pact.components.core import TextContent as TextContextComponent
    from ..messaging import ClientRequest, TextContent
    from ..context_management.pact.context import Context

from ..context_management.pact.context.position import Pos


logger = logging.getLogger(__name__)


@dataclass
class AgentListenerMetadata:
    """Metadata for agent context listener functions"""
    component_type: str
    handler: Callable
    properties: Dict[str, Any]


@dataclass
class AgentAddMetadata:
    """Metadata for agent context add handlers"""
    handler: Callable
    position: Union[Pos, Tuple[Pos, ...]]


class ContextController:
    """
    Clean controller that eliminates circular references while providing 
    identical API to Context. Simple weak reference solution.
    
    This class acts as a proxy to the actual Context object, breaking the
    circular reference between Agent and Context by using weak references
    for the agent connection while delegating all Context API calls.
    
    Key Features:
    - Breaks Agent ↔ Context circular references using weak references
    - Provides identical API to Context through delegation
    - Enables Context serialization (json.dumps, pickle.dumps)
    - Zero breaking changes - all existing agent.context.* calls work
    - Automatically delegates temporal selectors (@t-1, @c5) to Context
    
    Usage:
        # In Agent.__init__():
        self._context = Context()  # Private, serializable
        self.context = ContextController(self._context)  # Public API
        self.context._set_agent_ref(self)  # Weak reference
        
        # Result: Perfect serialization
        json.dumps(agent._context)  # ✅ No circular references
    """
    
    def __init__(self, context: 'Context'):
        """
        Initialize ContextController with a Context instance.
        
        Args:
            context: The Context instance to control
        """
        self._context = context
        # Use Optional[weakref.ref] to store agent without creating circular reference
        self._agent_ref: Optional[weakref.ref] = None
        
        # CRITICAL: Remove agent reference from real context to break circular dependency
        # This enables serialization of the underlying context
        if hasattr(self._context, 'agent'):
            self._context.agent = None
    
    def _set_agent_ref(self, agent: 'Agent') -> None:
        """
        Set agent reference using weak reference (breaks circular dependency).

        Uses weakref.ref() instead of direct reference to prevent:
        Agent → ContextController → Agent circular reference

        Args:
            agent: Agent instance to set weak reference to
        """
        # Store weak reference instead of direct reference to break circular dependency
        self._agent_ref = weakref.ref(agent)
        # Also set on underlying context for internal systems (MessageScheduler)
        self._context.agent = self._agent_ref
        context_id = getattr(getattr(self._context, 'metadata', None), 'id', 'unknown')
        logger.debug(f"Set agent ref for context {context_id}")
    
    @property
    def agent(self) -> Optional['Agent']:
        """
        Get agent via weak reference.
        
        The weak reference pattern prevents circular dependencies while still
        allowing access to the agent when needed. Returns None if agent
        has been garbage collected.
        
        Returns:
            Agent instance if weak reference is still valid, None otherwise
        """
        # Call weak reference to get agent (returns None if GC'd)
        return self._agent_ref() if self._agent_ref else None
    
    @agent.setter  
    def agent(self, value: 'Agent') -> None:
        """
        Set agent via weak reference.
        
        Args:
            value: Agent instance to set
        """
        self._set_agent_ref(value)
    
    # === 1:1 API Compatibility - All Context methods delegated ===
    def select(self, selector: str, snapshot=None): 
        """
        Delegate to context - temporal routing already implemented!
        
        Context already handles:
        - @t0, @t-1, @t-5, etc. (relative offset) via _resolve_snapshot()
        - @t* (wildcard for all snapshots)
        - @c5, @c10, etc. (absolute cycle)
        - Standard selectors (d0, p1)
        
        All temporal selectors are properly routed through context_manager.context_history
        """
        return self._context.select(selector, snapshot)
    
    def render(self, **kwargs): 
        """Delegate rendering to underlying context."""
        return self._context.render(**kwargs)
    
    @property
    def system_header(self): 
        """Access to system header component."""
        return self._context.system_header
    
    @property 
    def conversation_history(self): 
        """Access to conversation history component."""
        return self._context.conversation_history
    
    @property
    def active_message(self): 
        """Access to active message component."""
        return self._context.active_message
    
    
    def seal(self, trigger: str = "agent_context_seal", flush: bool = False) -> str:
        """
        Create an immutable snapshot of the current context state (PACT commit boundary).

        IMPORTANT: Context sealing is automatically handled by the agent framework.
        Manual sealing should only be used in exceptional debugging cases.

        Automatic sealing occurs:
        - Before provider calls (trigger="before_provider_call")
        - After provider responses (trigger="after_provider_response")

        Args:
            trigger: What triggered this seal (default: "agent_context_seal")
            flush: Wait for snapshot write to complete (default: async)

        Returns:
            snapshot_id: Unique identifier for the sealed snapshot
        """
        return self._context.seal(trigger=trigger, flush=flush)
    
    # All other Context properties and methods...
    def __getitem__(self, key):
        """Delegate subscript access to underlying context."""
        return self._context[key]

    def __getattr__(self, name):
        """Delegate all other attributes to underlying context."""
        return getattr(self._context, name)


class AgentContextManager:
    """Agent-specific context mounting and listener system"""
    
    def __init__(self, agent: 'Agent'):
        """
        Initialize agent context manager.
        
        Args:
            agent: Agent instance this manager belongs to
        """
        self.agent = agent
        self.listeners: Dict[str, List[AgentListenerMetadata]] = {}
        self.add_handlers: List[AgentAddMetadata] = []
    
    def listener(self, component_type: str, **properties):
        """
        Decorator for agent-scoped context listeners that respond to agent state changes.
        
        Usage:
            @agent.context.listener("task_reminders")
            def handle_task_events(agent: Agent):
                if agent.last_task_status == "completed":
                    agent.context["task_reminders"] = "✅ Task completed successfully"
        
        Args:
            component_type: The type of component to populate
            **properties: Additional properties for listener configuration
            
        Returns:
            Decorator function that registers the listener
        """
        def decorator(func: Callable) -> Callable:
            # Register listener for this component type
            if component_type not in self.listeners:
                self.listeners[component_type] = []
            
            metadata = AgentListenerMetadata(
                component_type=component_type,
                handler=func,
                properties=properties
            )
            
            self.listeners[component_type].append(metadata)
            return func
        
        return decorator
    
    def add(self, position: Union[str, Pos, Tuple[Pos, ...]] = "(d0,1)"):
        """
        Enhanced decorator with Pos-based positioning.
        
        Args:
            position: Position selector (string, Pos object, or tuple of Pos objects)
                     Examples: "(d0,1)", "(d-1)", "#status", "[type='notification']"
                     String selectors automatically converted to Pos objects.
                     Tuple creates multiple copies at different positions.
        
        Usage:
            @agent.context.add("(d0,1)")
            @agent.context.add("(d-1)")  # System header
            @agent.context.add("#status")  # Named position
            @agent.context.add(Pos("(d0,1)", ttl=2, cad=1))  # With temporal properties
            @agent.context.add((Pos("(d0,1)"), Pos("#alerts")))  # Multiple positions
        """
        def decorator(func: Callable) -> Callable:
            # Convert string to Pos if needed
            if isinstance(position, str):
                pos_obj = Pos(position)
            elif isinstance(position, tuple):
                # Multiple positions - store as tuple of Pos objects
                pos_obj = tuple(Pos(p) if isinstance(p, str) else p for p in position)
            else:
                pos_obj = position
            
            # Store metadata
            metadata = AgentAddMetadata(
                handler=func,
                position=pos_obj
            )
            
            self.add_handlers.append(metadata)
            return func
        return decorator
    
    def trigger_listeners(self, agent: 'Agent') -> None:
        """
        Trigger all registered agent-specific listeners.
        
        Args:
            agent: Agent instance to pass to listener functions
        """
        try:
            for component_type, listener_list in self.listeners.items():
                for listener_metadata in listener_list:
                    try:
                        # Call listener function with agent
                        listener_metadata.handler(agent)
                    except Exception as e:
                        print(f"Warning: Agent listener error for '{component_type}': {e}")
                        continue
        except Exception as e:
            print(f"Warning: Could not trigger agent listeners: {e}")
    
    def trigger_add_handlers(self, agent: 'Agent') -> List:
        """
        Trigger all add handlers and create ContextComponents using Context.insert().
        
        Args:
            agent: Agent instance to pass to add handlers
            
        Returns:
            List of ContextComponents created by add handlers
        """
        components = []
        
        try:
            for add_metadata in self.add_handlers:
                try:
                    # Call add handler with agent
                    content = add_metadata.handler(agent)
                    
                    if content:  # Non-empty content
                        # Get agent's context
                        context = getattr(agent, '_context', None) or getattr(agent, 'context', None)
                        if hasattr(context, '_context'):
                            # ContextController - get underlying context
                            context = context._context
                        
                        if context and hasattr(context, 'insert'):
                            # Extract just the position part from Pos object (before attributes/behaviors)
                            position_str = str(add_metadata.position)
                            # Extract base position: "(d0,1) {attrs} [behaviors]" -> "(d0,1)"
                            if ' {' in position_str:
                                base_position = position_str.split(' {')[0]
                            elif ' [' in position_str:
                                base_position = position_str.split(' [')[0]
                            else:
                                base_position = position_str
                            
                            # Use Context.insert() for registry tracking
                            result = context.insert(base_position, str(content))
                            if result and hasattr(result, 'updated_components'):
                                components.extend(result.updated_components)
                        else:
                            print(f"Warning: No context.insert() available for add handler")
                        
                except Exception as e:
                    print(f"Warning: Agent add handler error: {e}")
                    continue
                    
        except Exception as e:
            print(f"Warning: Could not trigger add handlers: {e}")
        
        return components
    
    def __setitem__(self, component_type: str, content) -> None:
        """
        Allow agent.context["type"] = content assignment for direct content manipulation.
        
        This delegates to the agent's MessageScheduler for consistency with template system.
        
        Args:
            component_type: The type of component to assign content to
            content: Content to assign (string, ContextComponent, or list)
        """
        try:
            # Get agent's message scheduler (support both public and private attr)
            scheduler = getattr(self.agent, 'message_scheduler', getattr(self.agent, '_message_scheduler', None))
            if scheduler is not None:
                scheduler.assign_template_content(component_type, content)
            else:
                print(f"Warning: Agent has no message_scheduler for assignment to '{component_type}'")
        except Exception as e:
            print(f"Warning: Could not assign agent context content to '{component_type}': {e}")
    
    def dispatch(self, content: Union[str, 'TextContextComponent']) -> None:
        """
        🎯 Smart execution state-aware message dispatch for bidirectional scaffolds.
        
        Automatically handles message dispatch based on agent execution state:
        - If agent is executing tools → Add to current tool execution batch
        - If agent is idle → Execute new call to provider
        
        Args:
            content: Content to dispatch (string or TextContextComponent)
            
        Example:
            # From scaffold external change handler
            agent.context.dispatch("✅ Approval granted for: sudo rm -rf /tmp")
            agent.context.dispatch(TextContextComponent(content="Task completed", ttl=5))
        """
        try:
            # Import here to avoid circular imports
            from ..context_management.components import TextContextComponent
            from ..messaging import ClientRequest, TextContent
            
            # Convert string to TextContextComponent if needed
            if isinstance(content, str):
                text_component = TextContextComponent(content=content)
            elif hasattr(content, '__class__') and 'TextContextComponent' in str(type(content)):
                text_component = content
            else:
                # Fallback for other content types
                text_component = TextContextComponent(content=str(content))
            
            # Check agent execution state for smart dispatch
            if (hasattr(self.agent, 'controller') and self.agent.controller and
                hasattr(self.agent.controller, 'is_tool_executing') and 
                self.agent.controller.is_tool_executing):
                
                # Scenario 1: Add to current tool execution batch
                if (hasattr(self.agent, 'context') and self.agent.context and
                    hasattr(self.agent.context, 'active_message') and self.agent.context.active_message):
                    self.agent.context.active_message.get_message_container().add_child(text_component)
                else:
                    print(f"Warning: Could not add to active message - agent context not available")
                    
            else:
                # Scenario 2: Execute new call to provider
                text_content = TextContent(content=text_component.content)
                request = ClientRequest(content=[text_content])
                
                if hasattr(self.agent, 'call') and callable(self.agent.call):
                    self.agent.call(request)
                else:
                    print(f"Warning: Could not dispatch message - agent.call() not available")
                    
        except Exception as e:
            print(f"Warning: Could not dispatch message: {e}")
            # Fallback: try to print the message at least
            content_str = str(content)
            print(f"Scaffold message: {content_str}")
    
    def __repr__(self) -> str:
        listener_count = sum(len(listeners) for listeners in self.listeners.values())
        add_handler_count = len(self.add_handlers)
        return f"AgentContextManager(listeners={listener_count}, add_handlers={add_handler_count})"