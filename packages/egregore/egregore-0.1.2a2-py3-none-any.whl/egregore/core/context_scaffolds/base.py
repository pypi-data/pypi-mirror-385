"""
BaseContextScaffold - Smart ContextComponents with V2 scaffold infrastructure.

Scaffolds are ContextComponents that:
- Hold persistent state using V2 ScaffoldState with change detection
- Render themselves as HTML/text for the LLM to see via render() method  
- Have @scaffold_operation decorated methods for agent tool generation
- User-controlled positioning - users specify where scaffolds appear in context tree
- Automatic state management and change detection
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, ClassVar, get_type_hints, List, Union, Callable, Tuple, cast, Literal, TYPE_CHECKING
import inspect
import difflib
import re
from dataclasses import dataclass, field
from pydantic import Field, PrivateAttr
from ..context_management.pact.components.core import PACTNode
from .data_types import ScaffoldState, StateChangeSource
from .decorators import get_scaffold_operations
if TYPE_CHECKING:
    from .approval import PolicyResult

if TYPE_CHECKING:
    from ..tool_calling.tool_declaration import ToolDeclaration


@dataclass
class OperationSpec:
    """
    Specification for a custom scaffold operation.
    
    Used by custom tool format scaffolds to define operations with detailed
    parameter information, descriptions, and examples for better LLM interaction.
    
    Attributes:
        action: The operation action/name (e.g., 'append', 'update', 'delete')
        description: Human-readable description of what this operation does
        required_params: List of required parameter names
        param_hints: Dict mapping parameter names to hint/description strings
        examples: List of example usage strings or dicts showing typical usage
        
    Example:
        >>> spec = OperationSpec(
        ...     action="add_task",
        ...     description="Add a new task to the task manager",
        ...     required_params=["title"],
        ...     param_hints={
        ...         "title": "Brief description of the task",
        ...         "priority": "Priority level: low, medium, high (default: medium)",
        ...         "due_date": "Due date in YYYY-MM-DD format (optional)"
        ...     },
        ...     examples=[
        ...         "Add a high priority task: add_task(title='Review code', priority='high')",
        ...         "Add simple task: add_task(title='Update documentation')"
        ...     ]
        ... )
    """
    action: str
    description: str
    required_params: List[str] = field(default_factory=list)
    param_hints: Dict[str, str] = field(default_factory=dict)
    examples: List[Union[str, Dict[str, Any]]] = field(default_factory=list)


 


class ScaffoldMeta(type(PACTNode)):
    """Metaclass to provide clean __init__ signatures for scaffold classes."""
    
    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        
        # Only apply to actual scaffold subclasses (not BaseContextScaffold itself)
        if name != 'BaseContextScaffold' and any(hasattr(base, '__name__') and base.__name__ == 'BaseContextScaffold' or any(getattr(b, '__name__', '') == 'BaseContextScaffold' for b in getattr(base, '__mro__', ())) for base in bases):
            # Validate required properties
            mcs._validate_required_properties(name, namespace)
            
            def clean_init(self, *, position: str = "system", scaffold_op_fmt: Optional[Literal['unified', 'distinct', 'custom']] = 'distinct',
                          operation_ttl: Optional[int] = None,
                          operation_retention: Optional[int] = None,
                          operation_config: Optional[Dict[str, Dict[str, Union[int, bool]]]] = None,
                          disabled_operations: Optional[List[str]] = None) -> None:
                BaseContextScaffold.__init__(self, position=position, scaffold_op_fmt=scaffold_op_fmt,
                                           operation_ttl=operation_ttl, operation_retention=operation_retention,
                                           operation_config=operation_config, disabled_operations=disabled_operations)
            # Assign in a way acceptable to the type checker
            cast(Any, cls).__init__ = clean_init
        
        return cls
    
    @staticmethod
    def _validate_required_properties(name: str, namespace: Dict[str, Any]) -> None:
        from .exceptions import ScaffoldDefinitionError
        from .data_types import ScaffoldState
        
        missing_properties = []
        invalid_properties = {}
        
        # Check for 'type' property
        if 'type' not in namespace:
            missing_properties.append('type')
        elif not isinstance(namespace['type'], str) or not namespace['type'].strip():
            invalid_properties['type'] = "must be a non-empty string"
        
        # Check for 'state' property
        if 'state' not in namespace:
            missing_properties.append('state')
        else:
            # Validate state is a ScaffoldState instance or subclass
            state_value = namespace['state']
            if not hasattr(state_value, '__class__'):
                invalid_properties['state'] = "must be an instance of ScaffoldState or its subclass"
            else:
                state_class = state_value.__class__
                # Check if it's ScaffoldState or inherits from ScaffoldState
                is_scaffold_state = (
                    state_class.__name__ == 'ScaffoldState' or
                    any(base.__name__ == 'ScaffoldState' for base in state_class.__mro__)
                )
                if not is_scaffold_state:
                    invalid_properties['state'] = "must be an instance of ScaffoldState or its subclass"
        
        # Raise error if any validation failures
        if missing_properties or invalid_properties:
            raise ScaffoldDefinitionError(
                message=f"Scaffold class '{name}' has invalid property definitions.",
                scaffold_name=name,
                missing_properties=missing_properties,
                invalid_properties=invalid_properties
            )


class BaseContextScaffold(PACTNode, ABC, metaclass=ScaffoldMeta):
    """
    Base class for smart scaffolds with persistent state and self-rendering.
    
    V2 BaseContextScaffold provides:
    - ScaffoldState with automatic change detection
    - @scaffold_operation method discovery for agent tool generation
    - Automatic state initialization patterns
    - Position management for context tree mounting
    - Change-based re-rendering optimization
    - Built-in hint generation system for better user experience
    """
    
    # =====================================================================
    # HINT CONFIGURATION - Override in subclasses for enhanced UX
    # =====================================================================
    
    OPERATION_SYNONYMS: ClassVar[Dict[str, List[str]]] = {}
    """Map operation names to alternative words users might use."""
    
    PARAMETER_SUGGESTIONS: ClassVar[Dict[Tuple[str, str], Union[str, Callable]]] = {}
    """Map (operation, parameter) tuples to suggestions or callables that return suggestions."""
    
    ERROR_RECOVERY_PATTERNS: ClassVar[Dict[str, List[str]]] = {}
    """Map error regex patterns to recovery hint lists."""
    
    # =====================================================================
    # RETENTION CONFIGURATION - TTL and capacity management
    # =====================================================================

    operation_ttl: Optional[int] = Field(default=None, description="Default TTL (conversation turns) for all operations")
    operation_retention: Optional[int] = Field(default=None, description="Default capacity limit for all operations")
    operation_config: Dict[str, Dict[str, Union[int, bool]]] = Field(default_factory=dict, description="Per-operation config: ttl, retention, enabled")
    disabled_operations: Optional[List[str]] = Field(default=None, description="List of operation names to disable at initialization")

    # =====================================================================
    # SCAFFOLD STATE PERSISTENCE - Automatic serialization to org namespace
    # =====================================================================
    # State is stored in metadata.aux['scaffold_state'] and metadata.aux['scaffold_id_data']
    # which get flattened into org namespace during model_dump()

    # Typed stubs for dynamically set attributes (for type checkers)
    _agent: Optional[Any] = None
    _provider_access: Optional[Any] = None
    _system_render: Optional[Callable[[], str]] = None

    # Phase 3: Reactive rendering - private, cannot be overridden
    _reactive: bool = PrivateAttr(default=True)
    
    def __init__(self, position: str = "system", scaffold_op_fmt: Optional[Literal['unified', 'distinct', 'custom']] = 'distinct',
                 operation_ttl: Optional[int] = None,
                 operation_retention: Optional[int] = None,
                 operation_config: Optional[Dict[str, Dict[str, Union[int, bool]]]] = None,
                 disabled_operations: Optional[List[str]] = None,
                 **kwargs):
        """
        Initialize BaseContextScaffold with V2 state management and retention parameters.
        
        Scaffolds provide intelligent memory management through the retention system:
        - **TTL (Time-To-Live)**: How many conversation turns operation results remain visible
        - **Retention capacity**: Maximum number of operations to keep per operation type
        - **Per-operation config**: Fine-grained control over specific operations
        
        Args:
            position: Where to mount the scaffold in context tree ("system", "active", "history")
            scaffold_op_fmt: Tool generation format ('unified', 'distinct', 'custom')
                - 'unified': Single tool with action parameter for all operations
                - 'distinct': Separate tool for each operation (scaffold_name_operation)
                - 'custom': Use custom_tool_format() method for full control
            operation_ttl: Default TTL (conversation turns) for all operations
                None = inherit from agent or use system default (3 turns)
            operation_retention: Default capacity limit for all operations
                None = inherit from agent or use system default (10 operations)
            operation_config: Per-operation retention overrides with format:
                {"operation_name": {"ttl": int, "retention": int}}
                Example: {"append": {"ttl": 2, "retention": 5}, "clear": {"ttl": 20}}
            **kwargs: Additional PACTNode arguments (ignored for compatibility)
            
        Examples:
            >>> # Memory-efficient scaffold for long conversations
            >>> scaffold = InternalNotesScaffold(
            ...     position="system",
            ...     operation_ttl=3,      # Notes visible for 3 turns
            ...     operation_retention=5  # Keep max 5 notes
            ... )
            
            >>> # High-retention scaffold for important data
            >>> data_scaffold = MyDataScaffold(
            ...     operation_ttl=15,     # Long-lived operations
            ...     operation_retention=50 # Large capacity
            ... )
            
            >>> # Mixed retention with per-operation control
            >>> task_scaffold = TaskManagerScaffold(
            ...     operation_ttl=10,
            ...     operation_retention=20,
            ...     operation_config={
            ...         "create_task": {"ttl": 15, "retention": 30},  # Important
            ...         "mark_done": {"ttl": 3, "retention": 5},      # Brief
            ...         "list_tasks": {"ttl": 1, "retention": 1}      # Queries
            ...     }
            ... )
        """
        # Initialize parent PACTNode with retention parameters and disabled operations
        super().__init__(operation_ttl=operation_ttl, operation_retention=operation_retention,
                        operation_config=operation_config or {}, disabled_operations=disabled_operations)
        
        # Store positioning metadata
        object.__setattr__(self, '_mount_position', position)
        
        # Store tool format preference
        object.__setattr__(self, '_scaffold_op_fmt', scaffold_op_fmt)
        
        # Initialize scaffold state
        self._init_state()
        
        # Set up bidirectional reference for automatic source detection
        if hasattr(self, 'state') and self.state:
            self.state.__dict__['_scaffold_ref'] = self
            
            # Trigger auto-tracking for existing state fields
            self._initialize_state_tracking()
        
        # Initialize provider access (can be set later)
        object.__setattr__(self, '_provider_access', None)
        object.__setattr__(self, '_agent', None)
        
        # Initialize scaffold hooks system
        from .approval import ScaffoldHooks
        object.__setattr__(self, '_scaffold_hooks', ScaffoldHooks(self))

        # Initialize operations accessor
        from .operations import OperationsAccessor
        object.__setattr__(self, '_operations', OperationsAccessor(self))

        # Validate disabled operations immediately
        _ = self.operations.enabled  # Triggers validation on first access

        # Initial render
        self.content = self.render()
        self.metadata.aux['scaffold'] = "true"
    
    def _init_state(self) -> None:
        # Use __annotations__ directly instead of get_type_hints()
        # because PACTCore has forward references that break get_type_hints()
        if hasattr(self.__class__, '__annotations__') and 'state' in self.__class__.__annotations__:
            state_type = self.__class__.__annotations__['state']

            # Check if we have a custom state type that inherits from ScaffoldState
            if (state_type is not None and
                inspect.isclass(state_type) and
                issubclass(state_type, ScaffoldState) and
                state_type is not ScaffoldState):

                # Create instance of the custom state class
                state = state_type()
                object.__setattr__(self, '_scaffold_state', state)
                return

        # Default: create generic ScaffoldState
        state = ScaffoldState()
        object.__setattr__(self, '_scaffold_state', state)
    
    def _initialize_state_tracking(self) -> None:
        if not hasattr(self, 'state') or not self.state:
            return
        
        # Get all state field values that need tracking
        state_dict = self.state.model_dump()
        
        # Re-assign each field to trigger auto-tracking
        for field_name, field_value in state_dict.items():
            if not field_name.startswith('_'):
                # This will trigger __setattr__ with auto-tracking
                setattr(self.state, field_name, field_value)
        
        # For BaseXMLScaffold, also update content after tracking is set up
        if self._system_render is not None:
            self.content = self._system_render()

    def _update_scaffold_state_field(self) -> None:
        """
        Update scaffold_state and scaffold_id_data in metadata.aux before serialization.

        This method should be called before saving context snapshots to ensure
        scaffold state is persisted in the org namespace (via aux flattening).
        """
        import json
        import logging
        logger = logging.getLogger(__name__)

        if hasattr(self, 'state') and self.state:
            # Convert state to dict, handling nested Pydantic models
            state_dict = self._serialize_state_for_persistence(self.state)
            scaffold_state_json = json.dumps(state_dict)

            # Store in metadata.aux so it gets flattened into org during model_dump()
            self.metadata.aux['scaffold_state'] = scaffold_state_json
            logger.info(f"[SCAFFOLD _update] Set metadata.aux['scaffold_state'], length={len(scaffold_state_json)}")
        else:
            logger.warning(f"[SCAFFOLD _update] No state to serialize")

        # Use the PACTNode 'id' field as scaffold_id for restoration
        if hasattr(self, 'id') and self.id:
            # Store in metadata.aux so it gets flattened into org during model_dump()
            self.metadata.aux['scaffold_id_data'] = self.id
            logger.info(f"[SCAFFOLD _update] Set metadata.aux['scaffold_id_data']={self.id}")
        else:
            logger.warning(f"[SCAFFOLD _update] No id to use for scaffold_id_data")

    def _serialize_state_for_persistence(self, state: 'ScaffoldState') -> dict:
        """
        Convert scaffold state to JSON-serializable dict.

        Recursively handles Pydantic models, lists, and complex types like Coordinates.
        """
        from ..context_management.pact.data_structures.coordinates import Coordinates

        def make_serializable(obj):
            """Recursively convert objects to JSON-serializable types."""
            if obj is None:
                return None
            elif isinstance(obj, (str, int, float, bool)):
                return obj
            elif isinstance(obj, set):
                # Convert sets to lists for JSON serialization
                return list(obj)
            elif isinstance(obj, Coordinates):
                # Serialize Coordinates using its serialize() method
                return obj.serialize()
            elif isinstance(obj, dict):
                return {k: make_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [make_serializable(item) for item in obj]
            elif hasattr(obj, 'model_dump'):
                # Pydantic model - recursively convert
                return make_serializable(obj.model_dump())
            else:
                # Fall back to string representation
                return str(obj)

        # Serialize state as-is - PACT components will use their model_dump() properly
        state_dict = state.model_dump()
        result = make_serializable(state_dict)
        return result

    @property
    def mount_position(self) -> str:
        """Get the mount position for this scaffold."""
        return getattr(self, '_mount_position', 'system')
    
    @property 
    def state(self) -> ScaffoldState:
        """Get the scaffold state with change detection."""
        return getattr(self, '_scaffold_state', ScaffoldState())
    
    @property
    def hooks(self):
        """Get the scaffold hooks accessor for approval and validation."""
        from .approval import ScaffoldHooks
        return getattr(self, '_scaffold_hooks', ScaffoldHooks(self))

    @property
    def operations(self):
        """Get the operations accessor for operation management."""
        from .operations import OperationsAccessor
        return getattr(self, '_operations', OperationsAccessor(self))

    def get_tool_name(self) -> str:
        """Get base tool name for this scaffold."""
        if hasattr(self, '_get_tool_name') and callable(getattr(self, '_get_tool_name')):
            custom_name = self._get_tool_name()
            if custom_name:
                return custom_name
        
        # Default: class name without "Scaffold" suffix, lowercased
        class_name = self.__class__.__name__
        if class_name.endswith("Scaffold"):
            class_name = class_name[:-8]  # Remove "Scaffold" suffix
        return class_name.lower()
    
    def _get_tool_name(self) -> Optional[str]:
        return None  # Default implementation
    
    def has_custom_tool_format(self) -> bool:
        """Check if scaffold defines custom tool format."""
        # Check if the subclass has overridden custom_tool_format method
        return (hasattr(self, 'custom_tool_format') and 
                callable(self.custom_tool_format) and 
                self.custom_tool_format.__func__ is not BaseContextScaffold.custom_tool_format)
    
    def custom_tool_format(self) -> Optional[List['ToolDeclaration']]:
        """Override in subclasses to provide custom tools. Return None to use default."""
        return None  # Default implementation - use format-based generation
    
    def get_tools(self) -> List['ToolDeclaration']:
        """Generate tools based on scaffold_op_fmt setting."""
        format_type = getattr(self, '_scaffold_op_fmt', 'distinct')
        
        if format_type == 'unified':
            return self._generate_unified_tool()
        elif format_type == 'distinct':
            return self._generate_distinct_tools()
        elif format_type == 'custom':
            return self._generate_custom_tools()
        else:
            raise ValueError(f"Unknown scaffold_op_fmt: {format_type}")
    
    def _generate_unified_tool(self) -> List['ToolDeclaration']:
        from ..tool_calling.tool_declaration import ToolDeclaration
        
        # Get available operations
        operations = self.get_agent_operations()
        if not operations:
            return []
        
        # Create unified tool callable that dispatches to operations
        def unified_callable(action: str, **kwargs):
            if action not in operations:
                available_actions = list(operations.keys())
                raise ValueError(f"Invalid action '{action}'. Available actions: {', '.join(available_actions)}")
            
            # Get the bound method and call it
            bound_method = getattr(self, action)
            return bound_method(**kwargs)
        
        # Set up the unified callable with proper metadata
        unified_callable.__name__ = f"{self.get_tool_name()}_unified"
        
        # Create description that lists all available operations
        operation_list = []
        for op_name, op_metadata in operations.items():
            operation_list.append(f"- {op_name}: {op_metadata.description}")
        operations_desc = "\n".join(operation_list)
        
        description = f"Unified tool for {self.__class__.__name__}. Available operations:\n{operations_desc}"
        
        # ToolDeclaration.from_callable() handles schema automatically!
        tool = ToolDeclaration.from_callable(
            unified_callable,
            name=self.get_tool_name(),
            description=description
        )
        
        return [tool]
    
    def _generate_distinct_tools(self) -> List['ToolDeclaration']:
        from ..tool_calling.tool_declaration import ToolDeclaration
        
        tools = []
        base_name = self.get_tool_name()
        operations = self.get_agent_operations()
        
        for operation_name, operation_metadata in operations.items():
            tool_name = f"{base_name}_{operation_name}"
            bound_method = getattr(self, operation_name)
            
            tool = ToolDeclaration.from_callable(
                bound_method,
                name=tool_name,
                description=operation_metadata.description or f"{base_name} {operation_name}"
            )
            tools.append(tool)
        
        return tools
    
    def _generate_custom_tools(self) -> List['ToolDeclaration']:
        """Generate custom tools if defined, otherwise fall back to distinct."""
        if self.has_custom_tool_format():
            custom_tools = self.custom_tool_format()
            if custom_tools:
                return custom_tools
        
        # Fallback to distinct if custom not properly defined
        return self._generate_distinct_tools()
    
    @abstractmethod
    def render(self) -> str:
        """
        Render scaffold state as HTML/text for LLM consumption.

        This method should convert the scaffold's internal state into
        a string representation that the LLM can understand and work with.

        Returns:
            str: Rendered content for display in context
        """
        pass

    def should_rerender(self, ctx: Any) -> bool:
        """
        Determine if scaffold should re-render on this context change (Phase 3).

        All scaffolds are reactive by default - they automatically re-render when
        the context changes. Override in subclasses to implement selective re-rendering
        logic based on operation type, component type, depth, etc.

        Common patterns:
        - Filter by operation_type (insert/update/delete)
        - Filter by component type
        - Filter by depth/position
        - Filter by changed field names

        Args:
            ctx: ContextExecContext with operation details

        Returns:
            bool: True if scaffold should re-render

        Example:
            >>> def should_rerender(self, ctx):
            ...     # Only re-render on inserts
            ...     return ctx.operation_type == "insert"
        """
        # Default: All scaffolds are reactive (controlled by private _reactive flag)
        # Override this method for selective re-rendering logic
        return self._reactive

    def on_state_change(self, old_state: Dict[str, Any], new_state: Dict[str, Any], 
                       source: StateChangeSource, metadata: Dict[str, Any]) -> None:
        """
        Hook called whenever scaffold state changes.
        Override in subclasses for custom state change reactions.
        
        Args:
            old_state: Previous state as dict
            new_state: Current state as dict
            source: Source of the state change (AGENT or EXTERNAL)
            metadata: Additional metadata about the change (changes dict, timestamp, etc.)
        """
        # Enhanced state change handling with automatic dispatch support
        if source == StateChangeSource.EXTERNAL:
            # Override this method for custom external change behavior
            self._handle_external_state_change(old_state, new_state, metadata)
    
    def _handle_external_state_change(self, old_state: Dict[str, Any], 
                                    new_state: Dict[str, Any], metadata: Dict[str, Any]) -> None:
        """
        Override in subclasses for custom dispatch logic on external state changes.
        
        Args:
            old_state: Previous state as dict
            new_state: Current state as dict
            metadata: Additional metadata about the change
        """
        pass  # Override in subclasses for custom external change handling
    
    def pre_state_change(self, old_state: Dict[str, Any], pending_changes: Dict[str, Any], 
                        source: StateChangeSource, metadata: Dict[str, Any]) -> Union[bool, Dict[str, Any]]:
        """
        Hook called BEFORE state changes are applied.
        Override in subclasses for validation, modification, or blocking of state changes.
        
        Args:
            old_state: Current state before changes
            pending_changes: Changes that will be applied
            source: Source of the state change (AGENT or EXTERNAL)
            metadata: Additional metadata about the change
            
        Returns:
            - True: Allow changes as-is
            - False: Block all changes  
            - Dict: Modified changes to apply instead
        """
        return True  # Default: allow all changes
    
    def _reactive_context_update(self, old_state: Optional[Dict[str, Any]] = None, new_state: Optional[Dict[str, Any]] = None) -> None:
        """
        Update scaffold in context using PACT operations for reactive scaffold rendering.
        
        This method implements bidirectional scaffold integration by delegating to
        ContextOperations for comprehensive reactive updates including notifications.
        
        Args:
            old_state: Previous state (for notification comparison)
            new_state: Current state (for notification comparison)
        """
        # Check if agent is available for context operations
        if not self.agent:
            return
        
        # Check if agent has context available
        if not hasattr(self.agent, 'context') or not self.agent.context:
            return
        
        # Check if context operations are available
        if not hasattr(self.agent.context, '_ops') or not self.agent.context._ops:
            return
        
        try:
            # Delegate to ContextOperations for comprehensive reactive update
            self.agent.context._ops.reactive_scaffold_update(self, old_state, new_state)
        except Exception as e:
            # Log error but don't crash the scaffold
            print(f"Warning: Reactive context update failed for {self.__class__.__name__}: {e}")
    
    def _resolve_mount_position(self) -> str:
        """
        Resolve the mount position for this scaffold in the context tree.
        
        Returns:
            Position string for PACT operations (e.g., "d-1,0", "d0,1")
        """
        mount_position = getattr(self, '_mount_position', 'system')
        
        # Map position names to PACT coordinates
        position_map = {
            'system': 'd-1,0',     # System header depth
            'active': 'd0,1',      # Active message depth
            'history': 'd1,0'      # Conversation history depth
        }
        
        return position_map.get(mount_position, 'd-1,0')  # Default to system
    
    def post_state_change(self, old_state: Dict[str, Any], new_state: Dict[str, Any],
                         source: StateChangeSource, metadata: Dict[str, Any]) -> None:
        """
        Hook called AFTER state changes have been applied.
        Override in subclasses for reactions, notifications, side effects.
        
        Args:
            old_state: Previous state before changes
            new_state: Current state after changes  
            source: Source of the state change (AGENT or EXTERNAL)
            metadata: Additional metadata about the change
        """
        # Call legacy hook for backward compatibility (internal only)
        self.on_state_change(old_state, new_state, source, metadata)
        
        # NEW: Reactive context update - update scaffold in context after state changes including notifications
        try:
            self._reactive_context_update(old_state, new_state)
        except Exception as e:
            # Log error but don't crash the state change process
            print(f"Warning: Reactive context update failed in post_state_change for {self.__class__.__name__}: {e}")
        
        # Emit framework hook if agent is available
        self._emit_scaffold_state_change_hook(old_state, new_state, source, metadata)
    
    def _emit_scaffold_state_change_hook(self, old_state: Dict[str, Any], new_state: Dict[str, Any],
                                       source: StateChangeSource, metadata: Dict[str, Any]) -> None:
        """
        Emit ON_SCAFFOLD_STATE_CHANGE framework hook if agent is available.
        
        This method creates the proper hook context and emits the framework hook
        for scaffold state changes. The hook includes the required payload with
        phase='post', changed_fields, snapshot, and metadata.
        
        Args:
            old_state: State before changes
            new_state: State after changes
            source: Source of the change 
            metadata: Change metadata
        """
        # For now, this is a placeholder for future agent integration
        # When agents are properly integrated with scaffolds, this will:
        # 1. Get agent reference 
        # 2. Create ScaffoldExecContext with required fields
        # 3. Execute HookType.ON_SCAFFOLD_STATE_CHANGE hook
        
        # Determine changed fields by comparing old and new state
        changed_fields = []
        all_keys = set(old_state.keys()) | set(new_state.keys())
        for key in all_keys:
            if old_state.get(key) != new_state.get(key):
                changed_fields.append(key)
        
        # Create hook payload as specified in acceptance criteria
        hook_payload = {
            'phase': 'post',
            'changed_fields': changed_fields,
            'snapshot': new_state.copy(),  # Minimal snapshot as specified
            'metadata': metadata.copy(),
            'old_state': old_state.copy(),
            'new_state': new_state.copy(),
            'source': source.value if hasattr(source, 'value') else str(source)
        }

        # Debug log for hook payload
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"Scaffold state change hook payload ready: {hook_payload}")

        # Phase 4: Emit ON_SCAFFOLD_STATE_CHANGE hook when agent is available
        if hasattr(self, '_agent') and self._agent:
            from ..agent.hooks.execution import HookType
            from ..agent.hooks.execution_contexts import ContextFactory

            # Filter hook_payload to only include fields accepted by ScaffoldExecContext
            allowed_fields = {'phase', 'changed_fields', 'snapshot'}
            filtered_payload = {k: v for k, v in hook_payload.items() if k in allowed_fields}

            context = ContextFactory.create_scaffold_context(
                agent_id=self._agent.agent_id,
                scaffold_type=self.type,
                scaffold_id=getattr(self, 'id', str(id(self))),
                operation_name='state_change',
                agent=self._agent,
                scaffold=self,
                **filtered_payload
            )
            self._agent._hooks_instance.execute_hooks(HookType.ON_SCAFFOLD_STATE_CHANGE, context)
    
    def update_state(self, **updates: Any) -> None:
        """
        Update scaffold state and trigger re-render if changed.
        
        Uses _batch_update to avoid N+1 hook execution and properly implements
        the PRE → apply → POST hook flow for batch updates.
        
        Args:
            **updates: Key-value pairs to update in scaffold state
        """
        if not updates:
            return
        
        # Capture old state before update
        old_state = self.get_state_dict()
        
        # Auto-detect source
        from .data_types import StateChangeSource
        source = self.state._detect_change_source() if hasattr(self.state, '_detect_change_source') else StateChangeSource.EXTERNAL
        
        # Create metadata
        from datetime import datetime
        metadata = {
            'changes': updates.copy(),
            'detection': 'batch_update',
            'timestamp': datetime.now()
        }
        
        # PRE hook - call pre_state_change with pending changes
        pre_result = self.pre_state_change(old_state, updates, source, metadata)
        
        # If pre hook returns False, abort the entire batch update
        if pre_result is False:
            return
        
        # If pre hook returns a dict, use it as modified pending changes
        if isinstance(pre_result, dict):
            updates = pre_result
        
        # Apply changes using _batch_update to avoid N+1 hook execution
        changes_applied = self.state._batch_update(updates)
        
        # Only proceed if changes were actually applied
        if changes_applied:
            # Get new state after changes
            new_state = self.get_state_dict()
            
            # POST hook - call post_state_change with old and new state
            self.post_state_change(old_state, new_state, source, metadata)
            
            # Re-render after state change
            self.content = self.render()
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """
        Get value from scaffold state.
        
        Args:
            key: State key to retrieve
            default: Default value if key not found
            
        Returns:
            State value or default
        """
        return getattr(self.state, key, default)
    
    def clear_state(self) -> None:
        """Clear all scaffold state and re-render."""
        object.__setattr__(self, '_scaffold_state', ScaffoldState())
        self.content = self.render()
    
    def get_agent_operations(self) -> Dict[str, Any]:
        """
        Get all enabled @scaffold_operation decorated methods for agent tool generation.

        Returns only operations that are not disabled via disabled_operations,
        operation_config, or runtime disable() calls.

        Returns:
            Dictionary mapping operation names to their metadata (filtered)
        """
        return self.operations.enabled
    
    # =====================================================================
    # HINT SYSTEM - Public API for operation suggestions and recovery
    # =====================================================================
    
    def get_operation_suggestions(self, attempted_action: str) -> Dict[str, Any]:
        """
        Get suggestions for unknown or mistyped actions.
        
        Args:
            attempted_action: The action name that was attempted
            
        Returns:
            Dictionary containing suggestions, reasons, and examples
        """
        available = list(self.get_agent_operations().keys())
        
        # Check synonyms first if configured
        if self.OPERATION_SYNONYMS:
            for correct_action, variants in self.OPERATION_SYNONYMS.items():
                if attempted_action.lower() in [v.lower() for v in variants]:
                    suggestion = {
                        'suggested_action': correct_action,
                        'reason': 'synonym_match',
                        'example': self._get_operation_example(correct_action),
                        'available_actions': available
                    }
                    return self.customize_operation_suggestion(attempted_action, suggestion)
        
        # Fuzzy matching for typos (always available)
        matches = difflib.get_close_matches(attempted_action, available, n=3, cutoff=0.6)
        
        suggestion = {
            'suggested_actions': matches,
            'reason': 'fuzzy_match' if matches else 'no_match',
            'available_actions': available,
            'examples': {action: self._get_operation_example(action) for action in matches[:2]}
        }
        return self.customize_operation_suggestion(attempted_action, suggestion)
    
    def get_parameter_hints(self, action: str, **provided_params) -> Dict[str, Any]:
        """
        Get hints for parameters of a specific action.
        
        Args:
            action: The operation name
            **provided_params: Parameters already provided
            
        Returns:
            Dictionary containing missing parameters, hints, and examples
        """
        if action not in self.get_agent_operations():
            return {'error': f'Unknown action: {action}'}
        
        # Get required parameters
        operation_info = self.get_agent_operations()[action]
        parameters = operation_info.parameters if hasattr(operation_info, 'parameters') else {}
        
        required_params = []
        for param_name, param_info in parameters.items():
            if param_info.get('required', False):
                required_params.append(param_name)
        
        missing_params = [p for p in required_params if p not in provided_params]
        
        # Generate hints for missing parameters
        hints = {}
        for param in missing_params:
            suggestion_key = (action, param)
            if suggestion_key in self.PARAMETER_SUGGESTIONS:
                suggestion = self.PARAMETER_SUGGESTIONS[suggestion_key]
                base_hint = suggestion(self) if callable(suggestion) else suggestion
            else:
                # Auto-generate basic hint from parameter info
                param_info = parameters.get(param, {})
                param_type = param_info.get('type', 'any')
                base_hint = f"Required parameter of type {param_type}"
            
            # Allow customization
            hints[param] = self.customize_parameter_hint(action, param, base_hint)
        
        return {
            'missing_parameters': missing_params,
            'parameter_hints': hints,
            'example_usage': self._get_operation_example(action),
            'context_info': self._get_current_context_info()
        }
    
    def get_recovery_hints(self, action: str, error: Exception, **params) -> Dict[str, Any]:
        """
        Get recovery suggestions for failed operations.
        
        Args:
            action: The operation that failed
            error: The exception that occurred
            **params: Parameters that were passed to the operation
            
        Returns:
            Dictionary containing recovery hints and alternatives
        """
        error_message = str(error).lower()
        recovery_hints = []
        
        # Check configured error patterns
        for pattern, hints in self.ERROR_RECOVERY_PATTERNS.items():
            if re.search(pattern.lower(), error_message):
                recovery_hints.extend(hints)
        
        # Add context-specific recovery hints
        context_hints = self._generate_context_recovery_hints(action, error, params)
        recovery_hints.extend(context_hints)
        
        # Allow customization
        final_hints = self.customize_recovery_hints(action, error, recovery_hints)
        
        return {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'recovery_hints': final_hints,
            'alternative_actions': self._suggest_alternative_actions(action, error),
            'current_state': self._get_current_context_info()
        }
    
    # =====================================================================
    # POWER USER OVERRIDE METHODS - For complete customization
    # =====================================================================
    
    def customize_operation_suggestion(self, attempted_action: str, default_suggestion: Dict[str, Any]) -> Dict[str, Any]:
        """Override for custom operation suggestion logic."""
        return default_suggestion
    
    def customize_parameter_hint(self, action: str, param: str, default_hint: str) -> str:
        """Override for custom parameter hint logic."""
        return default_hint
    
    def customize_recovery_hints(self, action: str, error: Exception, default_hints: List[str]) -> List[str]:
        """Override for custom error recovery logic."""
        return default_hints
    
    def customize_tool_description(self, operation_name: str, default_description: str) -> str:
        """Override for custom tool description generation."""
        return default_description
    
    # =====================================================================
    # INTERNAL HELPER METHODS - Can be overridden for scaffold-specific behavior
    # =====================================================================
    
    def _get_operation_example(self, action: str) -> str:
        """Auto-generate examples from method signature."""
        operations = self.get_agent_operations()
        if action not in operations:
            return f"{action}()"
        
        operation_info = operations[action]
        parameters = operation_info.parameters if hasattr(operation_info, 'parameters') else {}
        
        example_params = []
        for param_name, param_info in parameters.items():
            if param_info.get('required', False):
                param_type = param_info.get('type', str)
                if param_type == str or param_type == 'str':
                    example_params.append(f"{param_name}='example'")
                elif param_type == int or param_type == 'int':
                    example_params.append(f"{param_name}=1")
                elif param_type == float or param_type == 'float':
                    example_params.append(f"{param_name}=1.0")
                elif param_type == bool or param_type == 'bool':
                    example_params.append(f"{param_name}=True")
                else:
                    example_params.append(f"{param_name}=...")
        
        example = f"{action}({', '.join(example_params)})"
        # Allow customization
        return self.customize_tool_description(action, example)
    
    def _get_current_context_info(self) -> Dict[str, Any]:
        """Get current scaffold context for hints."""
        return {
            'scaffold_type': self.__class__.__name__,
            'has_state': hasattr(self, 'state'),
            'state_fields': list(self.state.__fields__.keys()) if hasattr(self, 'state') and hasattr(self.state, '__fields__') else [],
            'available_operations': list(self.get_agent_operations().keys())
        }
    
    def _generate_context_recovery_hints(self, action: str, error: Exception, params: Dict) -> List[str]:
        """Generate context-specific recovery hints. Override in subclasses."""
        return []
    
    def _suggest_alternative_actions(self, failed_action: str, error: Exception) -> List[str]:
        """Suggest alternative actions when one fails. Override in subclasses."""
        available_actions = list(self.get_agent_operations().keys())
        return [action for action in available_actions if action != failed_action][:3]
    
    def has_state_changed(self, update_hash: bool = True) -> bool:
        """
        Check if scaffold state has changed since last check.
        
        Args:
            update_hash: Whether to update the stored hash after checking
            
        Returns:
            True if state has changed, False otherwise
        """
        return self.state.has_changed(update_hash=update_hash)
    
    def get_state_dict(self) -> Dict[str, Any]:
        """
        Get current state as dictionary.
        
        Returns:
            Dictionary representation of current state
        """
        return self.state.get_state_dict()
    
    def mark_state_changed(self, *keys: str) -> None:
        """
        Manually mark specific state keys as changed.
        
        Args:
            *keys: State keys to mark as changed
        """
        self.state.mark_changed(*keys)
        
        # Re-render if needed
        if self.state.has_changed():
            self.content = self.render()
    
    def set_provider_access(self, provider_or_agent):
        """
        Set provider access for model-aware features and auto-register with agent state.
        
        Args:
            provider_or_agent: Either a provider instance or agent with provider
        """
        # Agent instance path: support both new `_provider` and legacy `_provider_manager`
        if hasattr(provider_or_agent, 'provider_name') or hasattr(provider_or_agent, '_provider') or hasattr(provider_or_agent, '_provider_manager'):
            object.__setattr__(self, '_agent', provider_or_agent)
            provider_instance = (
                getattr(provider_or_agent, '_provider', None)
                or getattr(provider_or_agent, '_provider_manager', None)
            )
            object.__setattr__(self, '_provider_access', provider_instance)
            
            # AUTO-REGISTER WITH AGENT STATE (happens once during agent init)
            if hasattr(provider_or_agent, 'state') and hasattr(provider_or_agent.state, 'register_scaffold'):
                provider_or_agent.state.register_scaffold(self)
                
            # AUTO-REGISTER BUILT-IN INTERCEPT SYSTEM (happens once during agent connection)
            self._register_built_in_intercept()
        else:
            # Direct provider instance
            object.__setattr__(self, '_provider_access', provider_or_agent)
    
    @property
    def provider_access(self):
        """Get provider access if available."""
        return getattr(self, '_provider_access', None)
    
    @property 
    def agent(self):
        """Get agent instance if available."""
        return getattr(self, '_agent', None)
    
    # =====================================================================
    # SCAFFOLD IPC CONVENIENCE METHODS - For elegant state sharing
    # =====================================================================
    
    def set_agent_state(self, key: str, value: Any) -> None:
        """
        Convenience method to set agent state with automatic source tracking.
        
        Args:
            key: State key to set
            value: Value to set
            
        Example:
            >>> self.set_agent_state('cwd', '/new/path')
            # Equivalent to: self.agent.state.set_from_registered(self, 'cwd', '/new/path')
        """
        agent = getattr(self, '_agent', None)
        if agent is not None and hasattr(agent, 'state'):
            agent.state.set_from_registered(self, key, value)
    
    @property
    def agent_state(self):
        """
        Quick access to agent state for reading operations.
        
        Returns:
            AgentState instance if available, None otherwise
            
        Example:
            >>> cwd = self.agent_state.get('cwd')
            >>> cwd, source = self.agent_state.get_with_source('cwd') 
        """
        agent = getattr(self, '_agent', None)
        if agent is not None and hasattr(agent, 'state'):
            return agent.state
        return None
    
    def count_tokens(self, text: str, model: Optional[str] = None, provider: Optional[str] = None) -> int:
        """
        Count tokens using V2 universal token counting system.
        
        Args:
            text: Text to count tokens for
            model: Model name (auto-detected from agent/provider if None)
            provider: Provider name (auto-detected from agent/provider if None)
            
        Returns:
            Token count for the text
        """
        # Auto-detect model and provider if not specified, with fallbacks
        if model is None:
            model = self.get_current_model() or "gpt-4"  # Fallback only for token counting
        if provider is None:
            provider = self.get_current_provider() or "openai"  # Fallback only for token counting
        
        # Try to use provider access if available
        if self.provider_access and hasattr(self.provider_access, 'token_counter'):
            try:
                return self.provider_access.token_counter.count_text(text, model, provider)
            except Exception:
                pass
        
        # Fallback: Use TokenCountingManager directly
        try:
            from egregore.providers.core.token_counting import TokenCountingManager
            manager = TokenCountingManager()
            return manager.count_text(text, model, provider)
        except Exception:
            # Ultimate fallback: rough estimation
            return len(text) // 4
    
    def get_current_model(self) -> Optional[str]:
        """
        Get current model from agent/provider if available.
        
        Returns:
            Model name or None if not available
        """
        if self.agent and hasattr(self.agent, 'provider'):
            return getattr(self.agent.provider, 'model', None)
        elif self.provider_access and hasattr(self.provider_access, 'model'):
            return self.provider_access.model
        else:
            return None
    
    def get_current_provider(self) -> Optional[str]:
        """
        Get current provider from agent/provider if available.
        
        Returns:
            Provider name or None if not available
        """
        if self.agent and hasattr(self.agent, 'provider'):
            return getattr(self.agent.provider, 'name', None)
        elif self.provider_access and hasattr(self.provider_access, 'provider_name'):
            return self.provider_access.provider_name
        else:
            return None
    
    def get_token_limit(self, percentage: float = 0.1, minimum: int = 500) -> int:
        """
        Get model-aware token limit for scaffold content.
        
        Args:
            percentage: Percentage of model context to use (default 10%)
            minimum: Minimum token limit (default 500)
            
        Returns:
            Token limit based on current model's context window
        """
        try:
            # Get current model - scaffolds are always attached to agents
            model_name = self.get_current_model()
            if not model_name:
                # This should never happen since scaffolds are always attached to agents
                return max(int(4096 * percentage), minimum)
            
            # Get model info through provider - guaranteed to exist
            if self.agent and hasattr(self.agent, 'provider') and self.agent.provider:
                client = getattr(self.agent.provider, 'client', None)
                model_info = client.get_model(model_name) if client else None
                if model_info is not None and hasattr(model_info, 'limits') and hasattr(model_info.limits, 'context_tokens'):
                    context_limit = model_info.limits.context_tokens
                    return max(int(context_limit * percentage), minimum)
            elif self.provider_access and hasattr(self.provider_access, 'get_model'):
                model_info = self.provider_access.get_model(model_name)
                if model_info is not None and hasattr(model_info, 'limits') and hasattr(model_info.limits, 'context_tokens'):
                    context_limit = model_info.limits.context_tokens
                    return max(int(context_limit * percentage), minimum)
            else:
                # Fallback - should rarely happen
                return max(int(4096 * percentage), minimum)

            # If we reach here, we didn't get a context limit from provider paths
            return max(int(4096 * percentage), minimum)
        except Exception:
            # Safe fallback if model info retrieval fails
            return max(int(4096 * percentage), minimum)
    
    # =====================================================================
    # CUSTOM TOOL CREATION HELPERS - For advanced scaffold customization
    # =====================================================================
    
    def create_custom_tool(
        self, 
        name: str, 
        operations: Dict[str, OperationSpec], 
        description: str = "",
        use_when: str = "",
        examples: Optional[List[str]] = None
    ) -> 'ToolDeclaration':
        """
        Create a custom scaffold tool with multiple operations.
        
        This helper method creates a unified tool that accepts an 'action' parameter
        to determine which operation to execute. Useful for custom tool formats.
        
        Args:
            name: Name of the tool (e.g., 'taskmanager', 'filemanager')
            operations: Dict mapping action names to OperationSpec instances
            description: Overall description of what this tool does
            use_when: When to use this tool (for LLM guidance)
            examples: List of usage examples
            
        Returns:
            ToolDeclaration instance ready for registration
            
        Example:
            >>> operations = {
            ...     'add': OperationSpec(
            ...         action='add',
            ...         description='Add a new task',
            ...         required_params=['title'],
            ...         param_hints={'title': 'Task description'}
            ...     ),
            ...     'complete': OperationSpec(
            ...         action='complete', 
            ...         description='Mark task as complete',
            ...         required_params=['task_id'],
            ...         param_hints={'task_id': 'ID of task to complete'}
            ...     )
            ... }
            >>> tool = self.create_custom_tool(
            ...     'taskmanager',
            ...     operations,
            ...     'Manage tasks and track completion',
            ...     'When you need to add, complete, or manage tasks'
            ... )
        """
        from ..tool_calling.tool_declaration import ToolDeclaration
        from ..tool_calling.decorators import tool
        
        # Validate inputs
        if not name:
            raise ValueError("Tool name cannot be empty")
        if not operations:
            raise ValueError("Operations dictionary cannot be empty")
        
        # Validate all operations are OperationSpec instances
        for action, op_spec in operations.items():
            if not isinstance(op_spec, OperationSpec):
                raise TypeError(f"Operation '{action}' must be an OperationSpec instance")
        
        # Create the inner tool function
        def custom_tool_function(action: str, **kwargs) -> Any:
            """
            Custom tool function that routes to specific operations.
            
            Args:
                action: The operation to perform
                **kwargs: Parameters specific to the operation
                
            Returns:
                Result of the operation
            """
            # Validate action
            if action not in operations:
                available_actions = list(operations.keys())
                raise ValueError(f"Unknown action '{action}'. Available actions: {available_actions}")
            
            op_spec = operations[action]
            
            # Validate required parameters
            missing_params = [param for param in op_spec.required_params if param not in kwargs]
            if missing_params:
                raise ValueError(f"Missing required parameters for '{action}': {missing_params}")
            
            # Call the scaffold's operation method if it exists
            operation_method_name = action
            if hasattr(self, operation_method_name) and callable(getattr(self, operation_method_name)):
                operation_method = getattr(self, operation_method_name)
                return operation_method(**kwargs)
            else:
                raise NotImplementedError(f"Operation method '{operation_method_name}' not implemented")
        
        # Generate comprehensive documentation
        doc_parts = []
        if description:
            doc_parts.append(description)
        
        if use_when:
            doc_parts.append(f"\\nUSE WHEN: {use_when}")
        
        # Add operations documentation
        doc_parts.append("\\nOPERATIONS:")
        for action, op_spec in operations.items():
            doc_parts.append(f"\\n• {action}: {op_spec.description}")
            if op_spec.required_params:
                doc_parts.append(f"  Required: {', '.join(op_spec.required_params)}")
            if op_spec.param_hints:
                for param, hint in op_spec.param_hints.items():
                    doc_parts.append(f"  - {param}: {hint}")
        
        # Add examples
        all_examples: List[str] = examples or []
        for op_spec in operations.values():
            for example in op_spec.examples:
                if isinstance(example, str):
                    all_examples.append(example)
                else:
                    all_examples.append(str(example))
        
        if all_examples:
            doc_parts.append("\\nEXAMPLES:")
            for example in all_examples[:5]:  # Limit to 5 examples
                if isinstance(example, str):
                    doc_parts.append(f"\\n• {example}")
                elif isinstance(example, dict):
                    doc_parts.append(f"\\n• {example}")
        
        full_documentation = "".join(doc_parts)
        
        # Set the function's docstring to our generated documentation
        custom_tool_function.__doc__ = full_documentation
        
        # Apply the @tool decorator with the function name
        decorated_function = tool(name=name)(custom_tool_function)
        
        # Return the ToolDeclaration attached by the decorator
        return decorated_function._tool_declaration
    
    def create_custom_tools(self, tool_specs: List[Dict[str, Any]]) -> List['ToolDeclaration']:
        """
        Create multiple custom scaffold tools from a list of specifications.
        
        This helper method creates multiple custom tools at once, useful for
        scaffolds that need to register many tools with similar patterns.
        
        Args:
            tool_specs: List of tool specification dictionaries, each containing:
                - name: Tool name (required)
                - operations: Dict mapping action names to OperationSpec instances (required)
                - description: Overall tool description (optional)
                - use_when: When to use this tool (optional)
                - examples: List of usage examples (optional)
                
        Returns:
            List of ToolDeclaration instances ready for registration
            
        Raises:
            ValueError: If any tool specification is malformed
            TypeError: If operations are not OperationSpec instances
            
        Example:
            >>> tool_specs = [
            ...     {
            ...         'name': 'taskmanager',
            ...         'operations': {
            ...             'add': OperationSpec(action='add', description='Add task', required_params=['title']),
            ...             'complete': OperationSpec(action='complete', description='Complete task', required_params=['id'])
            ...         },
            ...         'description': 'Manage tasks',
            ...         'use_when': 'When managing tasks'
            ...     },
            ...     {
            ...         'name': 'notekeeper', 
            ...         'operations': {
            ...             'write': OperationSpec(action='write', description='Write note', required_params=['content']),
            ...             'delete': OperationSpec(action='delete', description='Delete note', required_params=['note_id'])
            ...         },
            ...         'description': 'Manage notes'
            ...     }
            ... ]
            >>> tools = self.create_custom_tools(tool_specs)
        """
        if not tool_specs:
            raise ValueError("Tool specifications list cannot be empty")
        
        if not isinstance(tool_specs, list):
            raise TypeError("Tool specifications must be provided as a list")
        
        created_tools = []
        
        for i, spec in enumerate(tool_specs):
            try:
                # Validate specification format
                if not isinstance(spec, dict):
                    raise TypeError(f"Tool specification {i} must be a dictionary")
                
                # Extract required fields
                if 'name' not in spec:
                    raise ValueError(f"Tool specification {i} missing required 'name' field")
                if 'operations' not in spec:
                    raise ValueError(f"Tool specification {i} missing required 'operations' field")
                
                name = spec['name']
                operations = spec['operations']
                
                # Validate name
                if not name or not isinstance(name, str):
                    raise ValueError(f"Tool specification {i}: 'name' must be a non-empty string")
                
                # Validate operations
                if not operations or not isinstance(operations, dict):
                    raise ValueError(f"Tool specification {i}: 'operations' must be a non-empty dictionary")
                
                # Extract optional fields
                description = spec.get('description', '')
                use_when = spec.get('use_when', '')
                examples = spec.get('examples', [])
                
                # Validate examples if provided
                if examples and not isinstance(examples, list):
                    raise ValueError(f"Tool specification {i}: 'examples' must be a list")
                
                # Create the tool using our existing create_custom_tool method
                tool = self.create_custom_tool(
                    name=name,
                    operations=operations,
                    description=description,
                    use_when=use_when,
                    examples=examples
                )
                
                created_tools.append(tool)
                
            except Exception as e:
                # Wrap with more context about which tool spec failed
                spec_name = spec.get('name', 'unknown') if isinstance(spec, dict) else 'unknown'
                raise ValueError(f"Failed to create tool from specification {i} (name: {spec_name}): {str(e)}") from e
        
        return created_tools
    
    def _create_error_result(self, operation: str, error: Exception, suggestion: str = "") -> Dict[str, Any]:
        """Create standardized error result for custom tools."""
        return {
            'success': False,
            'error': str(error),
            'error_type': type(error).__name__,
            'operation': operation,
            'suggestion': suggestion
        }
    
    def _create_parameter_error(self, operation: str, missing_params: List[str]) -> Dict[str, Any]:
        """Create parameter error result with helpful hints."""
        suggestion = f"Required parameters for '{operation}': {', '.join(missing_params)}"
        return self._create_error_result(
            operation, 
            ValueError(f"Missing required parameters: {missing_params}"),
            suggestion
        )
    
    def _create_execution_error(self, operation: str, error: Exception) -> Dict[str, Any]:
        """Create execution error result with context."""
        suggestion = f"The '{operation}' operation failed. Check parameters and try again."
        return self._create_error_result(operation, error, suggestion)
    
    def _generate_tool_documentation(self, name: str, operations: Dict[str, OperationSpec], 
                                   description: str, use_when: str, examples: List[str]) -> str:
        """Generate comprehensive tool documentation from OperationSpec data."""
        return self.create_custom_tool(name, operations, description, use_when, examples).description
    
    def validate_tool_generation(self) -> List[str]:
        """
        Validate scaffold's tool generation capabilities and detect potential issues.
        
        Analyzes the scaffold for:
        - @scaffold_operation methods that exist and can be called
        - Parameter conflicts for unified tool format
        - Missing required methods for custom operations
        - Tool format compatibility issues
        
        Returns:
            List of warning messages describing validation issues.
            Empty list means no issues detected.
            
        Example:
            >>> scaffold = MyCustomScaffold()
            >>> warnings = scaffold.validate_tool_generation()
            >>> if warnings:
            ...     for warning in warnings:
            ...         print(f"WARNING: {warning}")
        """
        warnings = []
        
        # Get all scaffold_operation methods
        scaffold_methods = self._get_scaffold_operation_methods()
        
        if not scaffold_methods:
            warnings.append(
                "No @scaffold_operation methods found. "
                "Add @scaffold_operation decorator to methods that should be tools."
            )
            return warnings
        
        # Check each scaffold method for potential issues
        for method_name, method in scaffold_methods.items():
            try:
                # Check if method is callable
                if not callable(method):
                    warnings.append(f"Method '{method_name}' marked with @scaffold_operation is not callable")
                    continue
                
                # Check method signature for parameter conflicts
                import inspect
                try:
                    sig = inspect.signature(method)
                    params = list(sig.parameters.keys())
                    
                    # Check for 'action' parameter conflict in unified format
                    if 'action' in params:
                        warnings.append(
                            f"Method '{method_name}' has 'action' parameter which conflicts with "
                            f"unified tool format. Consider renaming parameter to avoid conflicts."
                        )
                    
                    # Check for empty parameter list (might indicate missing parameters)
                    if len(params) == 0:
                        warnings.append(
                            f"Method '{method_name}' has no parameters. "
                            f"Consider if this method should accept parameters for tool usage."
                        )
                    
                except Exception as e:
                    warnings.append(f"Could not inspect signature of method '{method_name}': {e}")
                
                # Test method execution safety (check for obvious issues)
                try:
                    # Try to get method docstring
                    if not method.__doc__ or method.__doc__.strip() == "":
                        warnings.append(
                            f"Method '{method_name}' lacks documentation. "
                            f"Add docstring to improve tool usage experience."
                        )
                except Exception:
                    pass  # Docstring check is optional
                
            except Exception as e:
                warnings.append(f"Error validating method '{method_name}': {e}")
        
        # Check for unified format compatibility
        action_conflicts = self._check_unified_format_conflicts(scaffold_methods)
        warnings.extend(action_conflicts)
        
        # Check for missing state management
        state_warnings = self._check_state_management()
        warnings.extend(state_warnings)
        
        return warnings
    
    def _get_operation_ttl(self, operation_name: str) -> int:
        """
        Resolve TTL (Time-To-Live) configuration with cascading priority system.
        
        TTL represents the number of conversation turns an operation result will remain
        visible in the context before expiring. This enables episodic memory management
        where old operations naturally age out of conversation context.
        
        Resolution Priority (highest to lowest):
        1. **Per-operation config** - Specific override for this operation type
           Via: operation_config={"operation_name": {"ttl": int}}
        2. **Scaffold-level default** - Scaffold instance configuration
           Via: operation_ttl=int parameter
        3. **Agent-level default** - Agent-wide configuration for all scaffolds
           Via: Agent(operation_ttl=int)  
        4. **System default** - Built-in fallback (3 conversation turns)
        
        Args:
            operation_name: Name of the scaffold operation (e.g. 'append', 'update', 'clear')
            
        Returns:
            TTL value in conversation turns (always >= 1)
            
        Examples:
            >>> # Per-operation override takes precedence
            >>> scaffold = InternalNotesScaffold(
            ...     operation_ttl=5,  # Scaffold default
            ...     operation_config={"append": {"ttl": 2}}  # Operation override
            ... )
            >>> scaffold._get_operation_ttl("append")  # Returns 2 (override)
            >>> scaffold._get_operation_ttl("update")  # Returns 5 (scaffold default)
            
            >>> # Agent-level fallback when scaffold has no configuration
            >>> agent = Agent(operation_ttl=8, scaffolds=[scaffold])
            >>> scaffold._agent = agent  # Connect to agent
            >>> scaffold._get_operation_ttl("unknown_op")  # Returns 8 (agent default)
        """
        # 1. Check per-operation override
        if (self.operation_config and 
            operation_name in self.operation_config and
            "ttl" in self.operation_config[operation_name]):
            return self.operation_config[operation_name]["ttl"]
        
        # 2. Scaffold default
        if self.operation_ttl is not None:
            return self.operation_ttl
        
        # 3. Agent default
        if self.agent and hasattr(self.agent, 'operation_ttl') and self.agent.operation_ttl is not None:
            return self.agent.operation_ttl
        
        # 4. System default
        return 3
    
    def _get_operation_retention(self, operation_name: str) -> int:
        """
        Resolve retention capacity configuration with cascading priority system.
        
        Retention capacity represents the maximum number of operation results of this
        type to keep in conversation memory. When the limit is exceeded, the oldest
        operations are automatically removed by MessageScheduler. This provides
        bounded memory growth and prevents context bloat in long conversations.
        
        Resolution Priority (highest to lowest):
        1. **Per-operation config** - Specific override for this operation type
           Via: operation_config={"operation_name": {"retention": int}}
        2. **Scaffold-level default** - Scaffold instance configuration
           Via: operation_retention=int parameter
        3. **Agent-level default** - Agent-wide configuration for all scaffolds
           Via: Agent(operation_retention=int)
        4. **System default** - Built-in fallback (10 operations)
        
        Args:
            operation_name: Name of the scaffold operation (e.g. 'append', 'update', 'clear')
            
        Returns:
            Retention capacity (maximum number of operations to keep, always >= 1)
            
        Examples:
            >>> # Different operations can have different retention limits
            >>> scaffold = TaskManagerScaffold(
            ...     operation_retention=15,  # Scaffold default
            ...     operation_config={
            ...         "create_task": {"retention": 20},  # Keep more task creations
            ...         "mark_done": {"retention": 5},     # Keep fewer completion events
            ...     }
            ... )
            >>> scaffold._get_operation_retention("create_task")  # Returns 20 (override)
            >>> scaffold._get_operation_retention("mark_done")    # Returns 5 (override)
            >>> scaffold._get_operation_retention("list_tasks")  # Returns 15 (scaffold default)
            
            >>> # Memory-efficient configuration for high-volume operations
            >>> notes = InternalNotesScaffold(operation_retention=3)  # Only keep 3 notes
            >>> notes._get_operation_retention("append")  # Returns 3
        """
        # 1. Check per-operation override
        if (self.operation_config and 
            operation_name in self.operation_config and
            "retention" in self.operation_config[operation_name]):
            return self.operation_config[operation_name]["retention"]
        
        # 2. Scaffold default
        if self.operation_retention is not None:
            return self.operation_retention
        
        # 3. Agent default
        if self.agent and hasattr(self.agent, 'operation_retention') and self.agent.operation_retention is not None:
            return self.agent.operation_retention
        
        # 4. System default
        return 10
    
    def _get_scaffold_operation_methods(self) -> Dict[str, Callable]:
        scaffold_methods = {}
        import inspect
        for attr_name in dir(self):
            if attr_name.startswith('_'):
                continue
            try:
                attr = getattr(self, attr_name)
                if callable(attr) and hasattr(attr, '_is_scaffold_operation'):
                    scaffold_methods[attr_name] = attr
            except Exception:
                continue
        return scaffold_methods
    
    def _check_unified_format_conflicts(self, methods: Dict[str, Callable]) -> List[str]:
        conflicts = []
        all_params = set()
        method_params = {}
        import inspect
        for method_name, method in methods.items():
            try:
                sig = inspect.signature(method)
                params = set(sig.parameters.keys())
                method_params[method_name] = params
                all_params.update(params)
            except Exception as e:
                conflicts.append(f"Could not analyze parameters for '{method_name}': {e}")
        if 'action' in all_params:
            conflicting_methods = [name for name, params in method_params.items() if 'action' in params]
            conflicts.append(
                f"Methods {conflicting_methods} use 'action' parameter which conflicts with "
                f"unified tool format. In unified format, 'action' is reserved for operation selection."
            )
        param_conflicts = {}
        for param in all_params:
            methods_with_param = [name for name, params in method_params.items() if param in params]
            if len(methods_with_param) > 1:
                param_conflicts[param] = methods_with_param
        if param_conflicts:
            for param, methods_list in param_conflicts.items():
                if param not in ['self']:
                    conflicts.append(
                        f"Parameter '{param}' appears in multiple methods {methods_list}. "
                        f"Ensure consistent parameter meaning across operations for unified format."
                    )
        return conflicts
    
    def _check_state_management(self) -> List[str]:
        warnings = []
        
        # Check if scaffold has _scaffold_state attribute (the actual storage)
        if not hasattr(self, '_scaffold_state'):
            warnings.append(
                "Scaffold does not have '_scaffold_state' attribute. "
                "This usually indicates a problem with state initialization."
            )
        else:
            # Check if state is a ScaffoldState instance
            from .data_types import ScaffoldState
            actual_state = getattr(self, '_scaffold_state', None)
            if actual_state is not None and not isinstance(actual_state, ScaffoldState):
                warnings.append(
                    f"Scaffold state is not a ScaffoldState instance (found: {type(actual_state)}). "
                    f"Consider using ScaffoldState for proper change tracking."
                )
        
        # Also check the public state property
        if hasattr(self, 'state'):
            from .data_types import ScaffoldState
            try:
                state_value = self.state
                if not isinstance(state_value, ScaffoldState):
                    warnings.append(
                        f"State property returns non-ScaffoldState instance (found: {type(state_value)}). "
                        f"This may indicate state management issues."
                    )
            except Exception as e:
                warnings.append(f"Error accessing state property: {e}")
        
        return warnings
    
    # Built-in Intercept System for Tool Validation
    
    def _register_built_in_intercept(self):
        """
        Automatically register the built-in call intercept system with agent hooks.
        
        This method registers the scaffold's built-in intercept system with the agent's
        hook system when the scaffold is connected to an agent. The intercept system
        handles execution policies and result enhancement.
        """
        if self.agent and hasattr(self.agent, 'hooks') and hasattr(self.agent.hooks, 'tool'):
            from egregore.core.agent.hooks.execution import HookType
            # Register built-in intercept hook with agent's tool hooks system
            self.agent.hooks.tool._register_hook(HookType.CALL_INTERCEPT, self._built_in_intercept)
    
    def _built_in_intercept(self, context):
        """
        Built-in intercept that handles policies + user customization separately.
        
        This method is automatically registered as a CALL_INTERCEPT hook and handles:
        - PRE-EXECUTION: Check execution policies with approval hook support
        - POST-EXECUTION: Handle result enhancement
        - User customization: Call user's custom call_intercept if defined
        
        Args:
            context: HookContext with tool execution information
        """
        from .approval import PolicyResult
        
        # PRE-EXECUTION: Check execution policies with approval hook support
        if context.tool_result is None:
            policy_result = self._check_execution_policies(context)
            if policy_result.action == "BLOCK":
                if policy_result.message and context.agent:
                    # Dispatch policy message to context
                    self._dispatch_policy_message(context.agent, policy_result.message)
                context.validation_rejected = True
                context.rejection_reason = policy_result.reason
                return
            elif policy_result.action == "MODIFY" and policy_result.message:
                if context.agent:
                    self._dispatch_policy_message(context.agent, policy_result.message)
        
        # POST-EXECUTION: Handle result enhancement
        elif context.tool_result is not None:
            self._enhance_results(context)
        
        # Call user's custom intercept if they defined one (advanced usage)
        if hasattr(self, 'call_intercept') and callable(getattr(self, 'call_intercept')):
            self.call_intercept(context)
    
    def _check_execution_policies(self, context):
        """
        Check user-defined execution policies with approval hook support.
        
        Calls the scaffold's execution_policies method if defined, passing the
        approval hook for user interaction. Handles approval result processing.
        
        Args:
            context: HookContext with tool execution information
            
        Returns:
            PolicyResult with action decision and optional messages
        """
        from .approval import PolicyResult
        
        if hasattr(self, 'execution_policies') and callable(getattr(self, 'execution_policies')):
            try:
                policy_result = self.execution_policies(
                    tool_name=context.tool_name,
                    tool_params=context.tool_params,
                    approval_hook=self.hooks.request_approval  # Pass approval hook
                )
                
                # Handle approval result messages automatically
                if hasattr(policy_result, 'approval_result') and policy_result.approval_result:
                    approval = policy_result.approval_result
                    
                    # Send notification component if provided (simple string -> component)
                    if approval.notification and context.agent:
                        self._dispatch_notification_component(context.agent, approval.notification)
                    
                    # Use custom tool message if provided
                    if approval.tool_message and policy_result.action in ["ALLOW", "BLOCK"]:
                        policy_result.message = approval.tool_message
                
                return policy_result
            except Exception as e:
                # If execution_policies fails, log and allow by default
                import logging
                logging.warning(f"Scaffold execution_policies failed: {e}")
                return PolicyResult.ALLOW()
        
        return PolicyResult.ALLOW()  # Default: allow all
    
    def _enhance_results(self, context):
        """
        Handle result enhancement with clean interface.
        
        Calls the scaffold's enhance_results method if defined, allowing scaffolds
        to modify tool results after execution.
        
        Args:
            context: HookContext with tool execution information
        """
        if hasattr(self, 'enhance_results') and callable(getattr(self, 'enhance_results')):
            try:
                self.enhance_results(
                    tool_name=context.tool_name,
                    tool_result=context.tool_result
                )
            except Exception as e:
                # If result enhancement fails, log but don't fail the tool
                import logging
                logging.warning(f"Scaffold result enhancement failed: {e}")
    
    def _dispatch_policy_message(self, agent, message):
        """Dispatch policy message to agent context."""
        if hasattr(agent, 'context') and hasattr(agent.context, 'dispatch'):
            try:
                agent.context.dispatch(message)
            except Exception as e:
                import logging
                logging.warning(f"Failed to dispatch policy message: {e}")
    
    def _dispatch_notification_component(self, agent, notification):
        """Dispatch notification as context component with proper positioning."""
        if hasattr(agent, 'context') and hasattr(agent.context, 'dispatch'):
            try:
                from egregore.core.context_management.pact.components.core import PACTCore
                component = PACTCore(
                    content=notification,
                    depth=0,
                    offset=1,  # Post-message area
                    ttl=1  # Expires after 1 cycle
                )
                agent.context.dispatch(component)
            except Exception as e:
                # Fallback to simple message dispatch
                try:
                    agent.context.dispatch(notification)
                except:
                    import logging
                    logging.warning(f"Failed to dispatch notification: {e}")
    
    # Override points for scaffolds
    
    def execution_policies(self, tool_name: str, tool_params: dict, approval_hook) -> 'PolicyResult':
        """
        Override in scaffolds to define execution policies with approval support.
        
        This method is called during the PRE-EXECUTION phase of tool calls to
        determine if the tool should be allowed, blocked, or modified.
        
        Args:
            tool_name: Name of the tool being executed
            tool_params: Parameters passed to the tool
            approval_hook: Callable for requesting user approval/input
            
        Returns:
            PolicyResult with action decision (ALLOW/BLOCK/MODIFY)
            
        Example:
            def execution_policies(self, tool_name, tool_params, approval_hook):
                if 'dangerous' in tool_name.lower():
                    approval = approval_hook(
                        title="Dangerous Operation",
                        message=f"Allow {tool_name}?",
                        command=str(tool_params),
                        context={}
                    )
                    return PolicyResult.APPROVAL_REQUIRED(approval)
                return PolicyResult.ALLOW()
        """
        from .approval import PolicyResult
        return PolicyResult.ALLOW()  # Default: allow all
    
    def enhance_results(self, tool_name: str, tool_result):
        """
        Override in scaffolds to enhance tool results after execution.
        
        This method is called during the POST-EXECUTION phase of tool calls to
        allow scaffolds to modify or enhance the tool results.
        
        Args:
            tool_name: Name of the tool that was executed
            tool_result: The PACTCore result from tool execution
            
        Example:
            def enhance_results(self, tool_name, tool_result):
                if tool_name == "execute":
                    original_content = tool_result.content
                    tool_result.content = f"{original_content}\\n\\n📁 CWD: {self.state.cwd}"
        """
        pass  # Default: no enhancement
    
    def call_intercept(self, context):
        """
        Override for advanced intercept customization (exposes full context).
        
        This method is called during both PRE and POST execution phases for
        advanced users who need full access to the HookContext. Most users
        should use execution_policies and enhance_results instead.
        
        Args:
            context: Full HookContext with all execution information
            
        Example:
            def call_intercept(self, context):
                if context.tool_result is None:
                    # PRE-EXECUTION: Custom validation logic
                    if self.should_block(context):
                        context.validation_rejected = True
                        context.rejection_reason = "Custom block reason"
                else:
                    # POST-EXECUTION: Custom result processing
                    self.log_execution(context)
        """
        pass  # Default: no custom interception
