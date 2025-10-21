"""
V2 Agent Implementation

The core Agent class that integrates all V2 components with backward compatibility
to V1 patterns. Provides unified interface for AI agent interactions with
sophisticated tool execution, streaming, and context management.
"""

from re import I
import uuid
import logging
from typing import Optional, Dict, Any, List, Iterator, AsyncIterator, Union
from datetime import datetime

from .config import AgentConfig, ConfigAccessor
from .controller import AgentController
from .token_operations import TokenOperations
from ..state import AgentState
from ..hooks.execution import ToolExecutionHooks
from ..hooks_accessor import HooksAccessor
from ..utils import prepare_execution_context, handle_agent_errors
from ..failed_streams import FailedStreamingLog
from ..agent_context import ContextController

from ...context_management.pact.context import Context
from ...context_management.history import ContextHistory
from ..message_scheduler import MessageScheduler
from ...context_scaffolds import BaseContextScaffold, SystemInterface, ScaffoldAccessor
from ..tool_task_loop import ToolTaskLoop
from ..streaming_orchestrator import StreamingOrchestrator
from .task_loop_ops import TaskLoopOps
from .streaming_ops import StreamingOps

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...tool_calling.tool_declaration import ToolDeclaration, ScaffoldOpDeclaration
    from egregore.core.workflow.nodes import AgentNode

from egregore.providers.core.interface import BaseProvider
from .provider_info import ProviderAccessor


logger = logging.getLogger(__name__)


class Agent:
    """
    V2 Agent implementation with comprehensive component integration.
    
    Provides unified interface for AI agent interactions with sophisticated
    tool execution, streaming, context management, and hook systems.
    """
    
    
    def __init__(self, provider: str = None, scaffolds: Optional[list] = None, tools: Optional[list] = None,
                 api_key: Optional[str] = None,
                 provider_config: Optional[dict] = None,
                 instructions: str = "",
                 reasoning: bool = False,
                 max_tool_executions: Optional[int] = None,
                 api_call_delay: Optional[float] = None,
                 operation_ttl: Optional[int] = 3,
                 operation_retention: Union[int, Dict[str, int], None] = 10,
                 context = None,
                 template = None,
                 agent_id: Optional[str] = None):
        """
        Initialize Agent with specified provider and configuration.

        Args:
            provider: Provider name (e.g., 'openai', 'anthropic', 'google')
            scaffolds: List of scaffold instances to register with the agent
            tools: List of tools available to the agent
            api_key: API key for the provider (overrides environment variable)
            provider_config: Provider-specific configuration
            instructions: Instructions for the agent
            reasoning: Whether to require a reasoning-capable model
            max_tool_executions: Maximum tool executions (None for unlimited, default: None)
            api_call_delay: API call delay
            operation_ttl: Default TTL (conversation turns) for scaffold operations (default: 3 turns)
            operation_retention: Retention capacity policy for scaffold operations and regular tools (default: 10 operations)
                - int: Same retention for all operations and tools
                - Dict[str, int]: Per-operation retention for scaffolds (tools use max value from dict)
                - None: No automatic retention (operations never expire)
            context: Optional pre-built Context instance to use
            template: Optional ContextStructure template for declarative context
            agent_id: Optional agent ID (auto-generated if not provided)
        """
        # Handle mutable defaults
        if scaffolds is None:
            scaffolds = []
        if tools is None:
            tools = []

        # Create configuration
        self._agent_config = AgentConfig(
            provider=provider or "openai",  # Default provider for tests
            scaffolds=scaffolds,
            tools=tools,
            api_key=api_key,
            provider_config=provider_config,
            instructions=instructions,
            reasoning=reasoning,
            max_tool_executions=max_tool_executions,
            api_call_delay=api_call_delay
        )

        # Generate or use provided agent ID
        self.agent_id = agent_id if agent_id is not None else f"agent_{str(uuid.uuid4())[:8]}"
        
        # Store retention configuration
        self.operation_ttl = operation_ttl
        self.operation_retention = operation_retention
        
        # Initialize ToolTaskLoop for unified streaming execution
        self._task_loop = ToolTaskLoop(agent=self)
        self._task_loop_started = False
        
        # Initialize StreamingOrchestrator for enhanced streaming
        self._streaming_orchestrator = StreamingOrchestrator(agent=self, task_loop=self._task_loop)

        self._scaffold_list = scaffolds or []

        # Validate no duplicate scaffold types
        if self._scaffold_list:
            scaffold_types = [s.type for s in self._scaffold_list if hasattr(s, 'type')]
            duplicate_types = [t for t in scaffold_types if scaffold_types.count(t) > 1]
            if duplicate_types:
                raise ValueError(
                    f"Cannot have multiple scaffolds of the same type. "
                    f"Duplicate types found: {set(duplicate_types)}. "
                    f"Each scaffold type can only be instantiated once per agent."
                )

        # Store original provider string for parsing (use default if None)
        self._provider_string = provider or "openai"
        # Initialize context with template support
        if context is not None:
            self._context = context
        elif template is not None:
            self._context = Context(template=template)
        else:
            self._context = Context()
        
        # Create ContextController for public API (breaks circular reference)
        self.context = ContextController(self._context)
        self.context._set_agent_ref(self)
        # Initialize components in logical groups
        self._initialize_core_systems()
        self._initialize_tool_and_context_systems()
        self._initialize_optional_systems()
        
        # Comprehensive initialization complete log
        features = []
        features.append("hooks")
        features.append("scaffolds")  # Always enabled
        features_str = f" with {', '.join(features)}" if features else ""
        
        logger.info(f"Agent {self.agent_id} initialized: {self.provider}"
                   f"{features_str}")

        # Auto-discovery: if created inside a workflow node, register the agent
        try:
            # Lazy import to avoid circular dependency
            from ...workflow.agent_interceptor import get_current_node  # type: ignore
            from ...workflow.agent_discovery import get_agent_registry  # type: ignore

            current_node = get_current_node()  # Returns None if not in a node
            if current_node is not None:
                context = {
                    "agent_id": self.agent_id,
                    "agent_class": self.__class__.__name__,
                    "provider": str(self.provider),
                    "timestamp": datetime.now().isoformat(),
                }
                try:
                    discovery_agent_id = get_agent_registry().register_agent(self, current_node, context)
                    # Store lightweight references for later state updates if needed
                    self._discovery_agent_id = discovery_agent_id  # type: ignore[attr-defined]
                    self._discovery_node = current_node  # type: ignore[attr-defined]
                except Exception as e:
                    logger.debug(f"Agent discovery registration skipped: {e}")
        except Exception:
            # Discovery modules not available or other non-critical error
            pass
    
    async def shutdown(self) -> None:
        """
        Gracefully shut down agent subsystems.

        - Ends an active streaming turn if one is in progress
        - Shuts down the ToolTaskLoop (cancels operations, drains queues, stops processors)
        """
        # End streaming turn if active
        try:
            if hasattr(self, "_streaming_orchestrator") and \
               self._streaming_orchestrator and \
               self._streaming_orchestrator.is_streaming_active():
                await self._streaming_orchestrator.end_turn()
        except Exception as e:
            logger.warning(f"Error ending active streaming turn during shutdown: {e}")

        # Shut down tool task loop
        try:
            if hasattr(self, "_task_loop") and self._task_loop:
                await self._task_loop.shutdown()
                self._task_loop_started = False
        except Exception:
            pass  # Suppress all shutdown errors

        # Clean up provider HTTP clients
        try:
            if hasattr(self, "_provider") and self._provider and hasattr(self._provider, "cleanup"):
                await self._provider.cleanup()
        except Exception as e:
            logger.warning(f"Error cleaning up provider: {e}")

    
    @property
    def history(self):
        """Lazily create and return context history."""
        if self._context_history is None:
            self._context_history = ContextHistory(agent_id=self.agent_id, agent=self)
            # Connect to tool executor if not already connected
            if hasattr(self, '_context_history_connected') and not self._context_history_connected:
                self.tool_executor.set_context_history(self._context_history)
                self._context_history_connected = True
            # Wire history to context manager for PACT selector snapshot addressing
            try:
                if hasattr(self.context, 'context_manager') and self.context.context_manager is not None:
                    setattr(self.context.context_manager, 'context_history', self._context_history)
                # Also attach to the actual Context object for seal() support
                if hasattr(self.context, '_context'):
                    # ContextController wrapper
                    self.context._context._set_context_history(self._context_history)
                elif hasattr(self.context, '_set_context_history'):
                    # Direct Context object
                    self.context._set_context_history(self._context_history)
            except Exception:
                pass
        return self._context_history
    
    
    @property
    def hooks(self) -> HooksAccessor:
        """Unified hooks accessor with nested structure: agent.hooks.tools.*, agent.hooks.stream.*"""
        if not hasattr(self, '_hooks_accessor'):
            self._hooks_accessor = HooksAccessor(self)
        return self._hooks_accessor
    
    @property
    def scaffolds(self) -> Optional[ScaffoldAccessor]:
        """Lazily create and return scaffolds accessor."""
        if hasattr(self, '_scaffolds_enabled') and self._scaffolds_enabled and self._scaffolds is None:
            if hasattr(self, '_system_interface') and self._system_interface is not None:
                self._scaffolds = ScaffoldAccessor(self._scaffold_list)
            else:
                logger.error(f"No scaffolds available for agent {self.agent_id}")

                return None
        return self._scaffolds
    
    @property
    def _token_ops(self) -> TokenOperations:
        """Private token operations accessor."""
        if not hasattr(self, '_token_operations'):
            self._token_operations = TokenOperations(self)
        return self._token_operations
    
    @property
    def usage(self) -> Dict[str, Any]:
        """Get token usage summary from context history."""
        return self._token_ops.get_usage_summary()
    
    @property
    def _task_loop_ops(self) -> TaskLoopOps:
        """Private task loop operations accessor."""
        if not hasattr(self, '_task_loop_operations'):
            self._task_loop_operations = TaskLoopOps(self)
        return self._task_loop_operations
    
    @property
    def _streaming(self) -> StreamingOps:
        """Private streaming operations accessor."""
        if not hasattr(self, '_streaming_operations'):
            self._streaming_operations = StreamingOps(self)
        return self._streaming_operations
    
    
    def _initialize_core_systems(self) -> None:
        """Initialize core components (controller, provider_manager)."""
        # Agent Controller for lifecycle management
        self.controller = AgentController(agent_id=self.agent_id)
        
        # Initialize formal IPC state system
        self.state = AgentState()
        
        # Initialize failed streams logging
        self.failed_streams_log = FailedStreamingLog(self.agent_id)
        
        # Link controller to agent state for canonical state updates
        self.controller.set_agent_reference(self)
        
        # Initialize provider with new architecture
        self._initialize_provider()
        
        logger.debug(f"Core components initialized for agent {self.agent_id}")
    
    def _initialize_provider(self) -> None:
        """Initialize provider using the new provider architecture."""
        from egregore.providers.core.provider import GeneralPurposeProvider
        from egregore.providers.data.data_manager import data_manager
        
        try:
            # Validate provider name
            validated_provider = data_manager.validate_provider_name(self.provider.name)
            
            # Build provider config
            provider_config = {}
            if self._agent_config.api_key:
                provider_config['api_key'] = self._agent_config.api_key
            if self._agent_config.provider_config:
                provider_config.update(self._agent_config.provider_config)
            
            # Initialize provider
            self._provider = GeneralPurposeProvider(
                provider_name=validated_provider,
                **provider_config
            )
            
            logger.debug(f"Initialized {validated_provider} provider for agent {self.agent_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize provider {self.provider.name}: {e}")
            raise RuntimeError(f"Provider initialization failed: {e}") from e
    
    @property
    def provider(self) -> ProviderAccessor:
        """Return provider accessor with name, model, client, and settings."""
        if not hasattr(self, '_provider_accessor'):
            self._provider_accessor = ProviderAccessor(self)
        return self._provider_accessor
    
    @property
    def config(self) -> ConfigAccessor:
        """Return configuration accessor with mutable/immutable controls."""
        if not hasattr(self, '_config_accessor'):
            self._config_accessor = ConfigAccessor(self._agent_config, agent_ref=self)
        return self._config_accessor
    
    
    def _initialize_tool_and_context_systems(self) -> None:
        """Initialize tool execution and context management."""
        # Tool Registry and Executor

        from ...tool_calling.tool_executor import ToolExecutor
        from ...tool_calling.tool_registry import ToolRegistry
        self.tool_registry = ToolRegistry()
        self.tool_executor = ToolExecutor(
            registry=self.tool_registry,
            context=self._context  # Pass context for registry population
        )

        # Configure tool executor
        self.tool_executor.set_agent_context(self.agent_id)
        # No artificial concurrency limit

        # Register tools from config
        self._register_tools()

        # Context components - lazy loaded for memory efficiency
        self._context_history = None

        # Message scheduler - always needed (bound to raw context for direct property access)
        self._message_scheduler = MessageScheduler(self._context)

        # Agent context manager for declarative context system
        from ..agent_context import AgentContextManager
        self._context.context_manager = AgentContextManager(self)

        # Add agent instructions to system_header
        self._setup_system_instructions()

        # Mount scaffolds to context tree for PACT serialization
        self._mount_scaffolds_to_context()

        logger.debug(f"Tool system initialized for agent {self.agent_id}")
        logger.debug(f"Context system initialized for agent {self.agent_id}")
    
    def _setup_system_instructions(self) -> None:
        """Add agent instructions to system_header context."""
        if self._agent_config.instructions:
            self.context.add_system(self._agent_config.instructions)
            logger.debug(f"Added agent instructions to system_header for agent {self.agent_id}")

    def _register_tools(self) -> None:
        """Register tools from agent config into tool registry."""
        if not self._agent_config.tools:
            return

        from ...tool_calling.tool_declaration import ToolDeclaration

        for tool in self._agent_config.tools:
            try:
                # Convert to ToolDeclaration if needed
                if isinstance(tool, ToolDeclaration):
                    tool_declaration = tool
                elif callable(tool):
                    tool_declaration = ToolDeclaration.from_callable(tool)
                else:
                    logger.warning(f"Skipping invalid tool: {tool} (not callable or ToolDeclaration)")
                    continue

                # Register in tool registry
                self.tool_registry.register_tool(tool_declaration)
                logger.debug(f"Registered tool: {tool_declaration.name}")

            except Exception as e:
                logger.error(f"Failed to register tool {tool}: {e}")
                continue

        logger.info(f"Registered {len(self.tool_registry.tools)} tools for agent {self.agent_id}")

    def _initialize_optional_systems(self) -> None:
        """Initialize hooks, scaffolds, and other optional features."""
        # Hook system (always enabled)
        self._hooks_instance = ToolExecutionHooks()
        # Configure tool executor with hooks
        self.tool_executor.set_hooks(self._hooks_instance)

        # Phase 1: Bind hooks to context for CONTEXT_BEFORE_CHANGE / CONTEXT_AFTER_CHANGE
        self._context._set_hooks(self._hooks_instance, self.agent_id)

        # Phase 3: Register internal hook to trigger reactive scaffold re-rendering
        self._register_reactive_scaffold_hook()

        # Phase 4: Register internal hook for automatic tool registration (application layer)
        self._register_tool_registration_hook()

        logger.debug(f"Hook system initialized for agent {self.agent_id}")
        
        # Scaffold system (always enabled)
        self._initialize_scaffold_system()
        
        # Component integration setup
        self._setup_component_integration()
        
        logger.debug(f"Component integration setup complete for agent {self.agent_id}")
    
    def _register_scaffold_tools(self) -> None:
        """Generate and register tools from scaffolds."""
        try:
            scaffold_tools = self.get_scaffold_tools()
            logger.info(f"Registered {len(scaffold_tools)} scaffold tools for agent {self.agent_id}")
        except Exception as e:
            logger.error(f"Failed to register scaffold tools: {e}")
    
    def _initialize_scaffold_system(self) -> None:
        """Initialize scaffold system and position scaffolds in context DOM."""
        self._scaffolds_enabled = True
        self._system_interface = SystemInterface()
        self._scaffolds = None  # Will be created lazily
        
        # Add scaffolds to SystemInterface container (positioning handled by MessageScheduler at runtime)
        if self._agent_config.scaffolds:
            for scaffold in self._agent_config.scaffolds:
                if not isinstance(scaffold, BaseContextScaffold):
                    logger.warning(f"Skipping non-scaffold object: {type(scaffold)}")
                    continue
                
                # Set provider access for model-aware features
                scaffold.set_provider_access(self)

                # Phase 3: Bind agent reference for reactive scaffolds
                if hasattr(scaffold, '_agent'):
                    object.__setattr__(scaffold, '_agent', self)

                # Register scaffold with agent state for tracking
                self.state.register_scaffold(scaffold)

                # Phase 3: Auto-register ALL scaffolds as reactive (default behavior)
                # All scaffolds have _reactive=True by default and re-render on context changes
                self._context.register_reactive_scaffold(scaffold)

                # Add scaffold to SystemInterface container
                scaffold_name = getattr(scaffold, 'name', f'scaffold_{id(scaffold)}')
                self._system_interface.add_scaffold(scaffold_name, scaffold)

                logger.debug(f"Added scaffold '{scaffold_name}' to SystemInterface for agent {self.agent_id}")

        # NOTE: Scaffolds are NOT mounted statically - they're rendered dynamically by MessageScheduler
        # When state persistence is needed, we update scaffolds in _scaffold_list before serialization

        logger.debug(f"Scaffold system initialized for agent {self.agent_id} with {len(self._agent_config.scaffolds)} scaffolds")

    def _mount_scaffolds_to_context(self) -> None:
        """Mount scaffolds into context tree at system depth for PACT serialization."""
        if not self._agent_config.scaffolds:
            return

        logger.info(f"[SCAFFOLD MOUNT] Mounting {len(self._agent_config.scaffolds)} scaffolds to context tree")

        # Mount scaffolds at system depth (-1,0,X) for PACT serialization
        for idx, scaffold in enumerate(self._agent_config.scaffolds):
            if not isinstance(scaffold, BaseContextScaffold):
                continue

            try:
                # Insert scaffold at system depth: -1,0,0; -1,0,1; -1,0,2, etc.
                # Use pact_insert to add scaffold to SystemHeader content
                # Note: First insert at -1,0 creates the system header container
                if idx == 0:
                    # First scaffold - insert at -1,0 (creates container and adds at offset 0)
                    self._context.pact_insert("d-1,0", scaffold)
                    logger.info(f"[SCAFFOLD MOUNT] Mounted first scaffold (type={scaffold.type}, id={scaffold.id}) at d-1,0,0")
                else:
                    # Subsequent scaffolds - append using pact_update with append mode
                    # This will add them at offsets 1, 2, 3, etc.
                    self._context.pact_update("d-1,0", scaffold, mode="append")
                    logger.info(f"[SCAFFOLD MOUNT] Mounted scaffold (type={scaffold.type}, id={scaffold.id}) at d-1,0,{idx}")
            except Exception as e:
                logger.error(f"[SCAFFOLD MOUNT] Failed to mount scaffold {idx}: {e}")

        logger.info(f"[SCAFFOLD MOUNT] Successfully mounted {len(self._agent_config.scaffolds)} scaffolds")

    def _setup_component_integration(self) -> None:
        """Setup integration between components."""
        # Tool executor context history connection will be set up lazily when first needed
        self._context_history_connected = False
        
        # Connect message scheduler to context
        # (This would be done when MessageScheduler is fully implemented)
        
        # Generate and register scaffold tools
        self._register_scaffold_tools()
        
        # Setup controller hooks for lifecycle management
        self.controller.add_before_execution_hook(self._on_execution_start)
        self.controller.add_after_execution_hook(self._on_execution_end)
        self.controller.add_interruption_hook(self._on_execution_interrupted)
        self.controller.add_error_hook(self._on_execution_error)

    def _register_reactive_scaffold_hook(self) -> None:
        """
        Register internal CONTEXT_AFTER_CHANGE hook to trigger reactive scaffold re-rendering (Phase 3).

        This hook fires after every context.pact_insert/update/delete operation and
        triggers re-rendering of scaffolds that have registered as reactive.
        """
        from ..hooks.execution_contexts import ContextExecContext

        @self.hooks.context.after_change
        def trigger_reactive_scaffolds(context: ContextExecContext):
            """Re-render reactive scaffolds when context changes."""
            if not hasattr(context.context, '_reactive_scaffolds'):
                return

            for scaffold in context.context._reactive_scaffolds:
                if scaffold.should_rerender(context):
                    scaffold.render()

    def _register_tool_registration_hook(self) -> None:
        """
        Register internal CONTEXT_AFTER_CHANGE hook for automatic tool call/result registration.

        This implements two-phase registration:
        - Phase 1: When ToolCall is inserted, register it with tool_call_id
        - Phase 2: When ToolResult is inserted, complete the pair

        Keeps tool retention logic at application layer, not in PACT operations.
        """
        from ..hooks.execution_contexts import ContextExecContext

        @self.hooks.context.after_change
        def auto_register_tool_components(context: ContextExecContext):
            """Automatically register/unregister ToolCall/ToolResult components for retention tracking."""
            component = context.component
            if not component:
                return

            # Check if this is a tool call or result by looking for tool_call_id attribute
            tool_call_id = getattr(component, 'tool_call_id', None)
            if not tool_call_id:
                return

            # Get registry from context
            registry = context.context._registry
            operation = context.operation_type

            # Handle DELETE operations - unregister the tool pair
            if operation == "delete":
                print(f"[AUTO-UNREG HOOK] Unregistering {tool_call_id} due to delete operation")
                registry.unregister_tool_pair(tool_call_id)
                return

            # Handle INSERT/UPDATE operations - register the tool components
            if operation in ("insert", "update"):
                component_type = type(component).__name__

                # Phase 1: Register ToolCall component
                if 'Call' in component_type:
                    tool_name = getattr(component, 'tool_name', None)
                    if tool_name:
                        print(f"[AUTO-REG HOOK] Registering ToolCall {tool_call_id} for tool '{tool_name}'")
                        registry.register_tool_call(tool_call_id, component.id, tool_name)

                # Phase 2: Complete registration with ToolResult component
                elif 'Result' in component_type:
                    print(f"[AUTO-REG HOOK] Completing registration for ToolResult {tool_call_id}")
                    registry.complete_tool_pair(tool_call_id, component.id)

    # Lifecycle Hook Handlers
    
    def _on_execution_start(self, agent_id: str, execution_id: str, **kwargs) -> None:
        """Handle execution start."""
        logger.info(f"Agent {agent_id} starting execution {execution_id}")
        # Update tool executor with execution context
        self.tool_executor.set_agent_context(agent_id, execution_id)
    
    def _on_execution_end(self, agent_id: str, execution_id: str, duration=None, **kwargs) -> None:
        """Handle execution end."""
        duration_str = f" (duration: {duration})" if duration else ""
        logger.info(f"Agent {agent_id} completed execution {execution_id}{duration_str}")
    
    def _on_execution_interrupted(self, agent_id: str, execution_id: str, **kwargs) -> None:
        """Handle execution interruption."""
        logger.warning(f"Agent {agent_id} execution {execution_id} was interrupted")
    
    def _on_execution_error(self, agent_id: str, execution_id: str, error: Exception, **kwargs) -> None:
        """Handle execution error."""
        logger.error(f"Agent {agent_id} execution {execution_id} failed: {error}")
    
    # Scaffold Tool Extraction
    
    def get_scaffold_tools(self) -> List["ScaffoldOpDeclaration"]:
        """
        Generate ScaffoldOpDeclaration instances from scaffold instances directly.
        
        Gets tools from the scaffold instances passed to the agent, not through
        SystemInterface registration. Supports multiple tool formats:
        - unified: Single tool with action parameter
        - distinct: Multiple tools with semantic naming
        - custom: Developer-defined tools via custom_tool_format()
        
        Returns:
            List of generated ScaffoldOpDeclaration instances
        """
        tools = []
        
        if not self._agent_config.scaffolds:
            return tools
        
        for i, scaffold in enumerate(self._agent_config.scaffolds):
            if not isinstance(scaffold, BaseContextScaffold):
                continue
            
            try:
                # Import ScaffoldOpDeclaration and operation discovery
                from ...tool_calling.tool_declaration import ScaffoldOpDeclaration
                from ...context_scaffolds.decorators import get_scaffold_operations
                
                # Discover scaffold operations using @operation decorator
                operations = get_scaffold_operations(scaffold)
                
                # Create ScaffoldOpDeclaration for each operation
                for operation_name, metadata in operations.items():
                    # Get the bound method
                    method_callable = getattr(scaffold, operation_name)
                    
                    # Create ScaffoldOpDeclaration using from_scaffold_method
                    scaffold_tool = ScaffoldOpDeclaration.from_scaffold_method(
                        scaffold_instance=scaffold,
                        method_callable=method_callable
                    )
                    
                    # Register and add the tool
                    self.tool_registry.register_tool(scaffold_tool)
                    tools.append(scaffold_tool)
                    logger.debug(f"Generated scaffold tool: {scaffold_tool.name} (scaffold_id: {scaffold_tool.scaffold_id}, type: {scaffold_tool.scaffold_type})")
                    
            except Exception as e:
                logger.error(f"Failed to generate tools for scaffold {i}: {e}")
                continue
        
        logger.info(f"Generated {len(tools)} tools from {len(self._agent_config.scaffolds)} scaffolds")
        return tools
    
    def _get_scaffold_by_id(self, scaffold_id: str) -> Optional['BaseContextScaffold']:
        """
        Get scaffold instance by component ID for retention enforcement.

        Private method used by MessageScheduler for retention management.

        Args:
            scaffold_id: The id of the scaffold component (PACTNode level)

        Returns:
            Scaffold instance or None if not found
        """
        # Use direct access to scaffold list (not the property accessor)
        for scaffold in self._scaffold_list:
            if hasattr(scaffold, 'id') and scaffold.id == scaffold_id:
                return scaffold
        return None
    
    
    def status(self) -> Dict[str, Any]:
        """
        Get comprehensive agent status.
        
        Returns:
            Status dictionary with agent information
        """
        status = {
            "agent_id": self.agent_id,
            "provider": str(self.provider),
            "controller": self.controller.get_status(),
            "tools_registered": len(self.tool_registry.list_tool_names()),
        }
        
        status["hooks"] = self._hooks_instance.get_hook_counts()
        
        return status
    
    @handle_agent_errors
    def call(self, *inputs, async_tools: bool = False, **kwargs) -> Any:
        """
        Main sync entry point for agent interactions.
        
        Args:
            *inputs: Input messages/data for the agent
            async_tools: If True, use async tool execution internally (requires event loop)
            **kwargs: Additional parameters for provider calls
            
        Returns:
            Provider response from the call
        """
        # Track conversation start on first call
        if self.state.current_turn == 0:
            from datetime import datetime
            self.state.conversation_started_at = datetime.now()
        
        execution_id = self.controller.start_execution()
        self._current_execution_id = execution_id  # Store for error decorator
        
        # Use extracted utility for context preparation
        context_data = prepare_execution_context(
            self._message_scheduler,
            self.context, 
            execution_id,
            self.history,
            *inputs
        )
        provider_thread = context_data["provider_thread"]
        
        # NEW: on_user_msg hook - edit user message before sending to provider
        if self._hooks_instance:
            from ..hooks.execution import HookType
            modified_thread, was_modified = self._hooks_instance.execute_message_editing_hook(
                HookType.MESSAGE_USER_INPUT,
                provider_thread,
                context=self.context
            )
            if was_modified:
                provider_thread = modified_thread
                logger.info("User message modified by on_user_msg hook")
        
        # Get available tools for LLM awareness
        available_tools = []
        if hasattr(self, 'tool_registry') and self.tool_registry.tools:
            available_tools = list(self.tool_registry.tools.values())
            logger.debug(f"Passing {len(available_tools)} tools to provider")

        # Seal context before provider call
        self.context.seal(trigger="before_provider_call")
        
        # Direct provider call using new provider interface
        response = self._provider.call(
            provider_thread=provider_thread,
            model=self.provider.model,
            tools=available_tools if available_tools else None,
            **kwargs
        )
        
        # Convert provider response back to PACT components
        self._message_scheduler.add_response(response)
        
        # Seal context after successful provider response
        self.context.seal(trigger="after_provider_response")
        
        # Note: Episode increment now handled by MessageScheduler during render()
        
        # Count input tokens asynchronously (no impact on response time)
        # Skip if running in async context to avoid "sync API in async context" error
        import asyncio
        try:

            asyncio.get_running_loop()
            # Event loop running - skip async token counting to avoid conflicts
        except RuntimeError:
            # No event loop - safe to run async token counting in background
            import threading
            threading.Thread(
                target=lambda: asyncio.run(self._token_ops.count_input_tokens_async(provider_thread)),
                daemon=True
            ).start()
        
        # Track provider call
        self.state.increment_provider_calls()
        
        # Orchestrate complete turn including tool execution
        if async_tools:
            # Use async task loop orchestration with event loop
            try:
                # Check if we're in an async context
                asyncio.get_running_loop()
                # Create task and run it in existing loop using thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        lambda: asyncio.run(
                            self._task_loop_ops.orchestrate_turn_with_task_loop(response)
                        )
                    )
                    final_result = future.result()
            except RuntimeError:
                # No event loop - create one for async tool execution
                final_result = asyncio.run(
                    self._task_loop_ops.orchestrate_turn_with_task_loop(response)
                )
        else:
            # Use sync orchestration
            final_result = self._task_loop_ops.orchestrate_turn(response)
        
        self.controller.end_execution(execution_id)
        self._current_execution_id = None
        return final_result
    
    @handle_agent_errors
    async def acall(self, *inputs, **kwargs) -> Any:
        """
        Main async entry point for agent interactions.
        
        Args:
            *inputs: Input messages/data for the agent
            **kwargs: Additional parameters for provider calls
            
        Returns:
            Provider response from the async call
        """
        # Track conversation start on first call
        if self.state.current_turn == 0:
            from datetime import datetime
            self.state.conversation_started_at = datetime.now()
        
        execution_id = self.controller.start_execution()
        self._current_execution_id = execution_id  # Store for error decorator
        
        # Use extracted utility for context preparation
        context_data = prepare_execution_context(
            self._message_scheduler,
            self.context,
            execution_id,
            self.history,
            *inputs
        )
        provider_thread = context_data["provider_thread"]
        
        # Get available tools for LLM awareness
        available_tools = []
        if hasattr(self, 'tool_registry') and self.tool_registry.tools:
            available_tools = list(self.tool_registry.tools.values())
            logger.debug(f"Passing {len(available_tools)} tools to async provider")
        
        # Seal context before provider call
        self.context.seal(trigger="before_provider_call")
        
        # Direct async provider call using new provider interface
        response = await self._provider.acall(
            provider_thread=provider_thread,
            model=self.provider.model,
            tools=available_tools if available_tools else None,
            **kwargs
        )
        
        # Convert provider response back to PACT components
        self._message_scheduler.add_response(response)
        
        # Seal context after successful provider response
        self.context.seal(trigger="after_provider_response")
        
        # Note: Episode increment now handled by MessageScheduler during render()
        
        # Track provider call
        self.state.increment_provider_calls()
        
        # Enhanced: Orchestrate turn with ToolTaskLoop for non-blocking execution
        final_result = await self._task_loop_ops.orchestrate_turn_with_task_loop(response)
        
        self.controller.end_execution(execution_id)
        self._current_execution_id = None
        return final_result
    
    # Streaming Methods Implementation
    
    def stream(self, *inputs, **kwargs) -> Iterator[Any]:
        """
        Streaming version - sync generator for streaming responses.
        
        Args:
            *inputs: Input messages/data for the agent
            **kwargs: Additional parameters for provider calls
            
        Yields:
            Stream chunks from the provider response
        """
        # Delegate to extracted StreamingOps
        yield from self._streaming.stream(*inputs, **kwargs)
    
    async def astream(self, *inputs, **kwargs) -> AsyncIterator[Any]:
        """
        Async streaming version - async generator for streaming responses.
        
        Args:
            *inputs: Input messages/data for the agent
            **kwargs: Additional parameters for provider calls
            
        Yields:
            Stream chunks from the async provider response
        """
        # Delegate to extracted StreamingOps
        async for chunk in self._streaming.astream(*inputs, **kwargs):
            yield chunk
    
    # Helper Methods
    
    def __call__(self, name: Optional[str] = None, run_type: str = "call", **kwargs) -> "AgentNode":
        """
        Create an AgentNode for workflow integration.
        
        This is the ONLY correct way to create workflow nodes from agents.
        Never use AgentNode() constructor directly - always use agent() method.
        
        Args:
            name: Optional node name override (uses agent.agent_id by default)
            run_type: Agent method to call ("call", "acall", "stream", etc.)
            **kwargs: Parameters to pass to the agent method during execution
        
        Returns:
            AgentNode: Workflow node wrapping this agent
            
        Example:
            agent = Agent(provider="openai:gpt-4")
            
            # Use agent ID as node name
            node1 = agent(temperature=0.1)
            
            # Override with custom name
            node2 = agent("custom_processor", temperature=0.8)
            
            # Create workflow
            workflow = Sequence(
                load_data >>
                agent(temperature=0.1) >>  # Uses agent ID
                agent("analyzer", temperature=0.8) >>  # Custom name
                save_results
            )
        """
        from egregore.core.workflow.nodes import AgentNode
            
        return AgentNode(self, name, run_type, **kwargs)

    



    def __del__(self):
        """Cleanup when agent is garbage collected."""
        try:
            # Stop context history processing to prevent event loop issues
            if hasattr(self, '_context_history') and self._context_history:
                self._context_history.stop_processing()
            
            # Clean up task loop if it exists
            if hasattr(self, '_task_loop') and self._task_loop:
                # Don't try to await in __del__, just set shutdown flag
                if hasattr(self._task_loop, '_shutdown_event'):
                    self._task_loop._shutdown_event.set()
                
                # Cancel background processor tasks immediately
                for task_attr in ['_operation_processor_task', '_context_processor_task']:
                    if hasattr(self._task_loop, task_attr):
                        task = getattr(self._task_loop, task_attr)
                        if task and not task.done():
                            task.cancel()
                
                # Cancel any remaining tasks without awaiting

                if hasattr(self._task_loop, 'running_tasks'):
                    try:
                        for task in list(self._task_loop.running_tasks.values()):
                            if hasattr(task, 'cancel'):
                                from typing import cast
                                import asyncio
                                task = cast(asyncio.Task, task)
                                task.cancel()
                    except Exception:
                        pass
            
            # Clean up provider HTTP clients to prevent event loop issues
            if hasattr(self, '_provider') and self._provider:
                # Try to close any HTTP clients synchronously
                provider = self._provider
                # Use getattr with default to avoid attribute errors
                if getattr(provider, '_client', None) is not None:
                    # Set client to None to prevent async cleanup
                    setattr(provider, '_client', None)
                if getattr(provider, '_async_client', None) is not None:
                    # Set async client to None to prevent async cleanup  
                    setattr(provider, '_async_client', None)
            
        except Exception:
            # Ignore all errors in destructor to prevent garbage collection issues
            pass

    def __repr__(self) -> str:
        """String representation."""
        return f"Agent(id={self.agent_id}, provider={self.provider}, state={self.controller.state.value})"
