"""
Context class for V2 architecture.

Inherits from ContextRootComponent and provides simple helper methods for building 
conversation threads. MessageScheduler rebuilds it each cycle and renders it to 
ProviderThread format.
"""

from typing import Optional, Any, List, Dict, Union, Tuple, TYPE_CHECKING
from pydantic import Field, ConfigDict, PrivateAttr, model_validator
from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterator
from ...pact.components.core import PactRoot, PACTContainer, PACTCore
from .context_registry import ContextRegistry
from ..data_structures.coordinates import Coordinates
from ..data_structures.depth_array import DepthArray

# Type hints only
if TYPE_CHECKING:
    from ....messaging.thread import ProviderThread
    from ...history.context_history import ContextHistory
    from ...history.context_snapshot import RangeDiffLatestResult
    from ...history.context_snapshot import ContextSnapshot
    from ...history.loaders.base import SnapshotLoaderEngine


@dataclass
class UpdateOperation:
    """Represents a queued update operation"""
    selector_or_component: Union[str, PACTCore]
    content: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    agent_id: Optional[str] = None


@dataclass  
class UpdateResult:
    """Result of an update operation"""
    success: bool
    updated_components: List[PACTCore] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class UpdateQueue:
    """Queue system for batching updates until next agent call"""
    
    def __init__(self):
        self.queued_updates: List[UpdateOperation] = []
    
    def add_update(self, operation: UpdateOperation) -> None:
        """Add update to queue"""
        self.queued_updates.append(operation)
    
    def process_queue(self, context: 'Context') -> UpdateResult:
        """Process all queued updates during context rebuild"""
        # Implementation will be added in Task 2.3
        result = UpdateResult(success=True)
        return result
    
    def clear(self) -> None:
        """Clear all queued updates"""
        self.queued_updates.clear()
    
    def __len__(self) -> int:
        """Return number of queued updates"""
        return len(self.queued_updates)


class NodeAccessor:
    """Accessor for nodes in the context"""
    def __init__(self, context: 'Context'):
        self.context = context
    
    def __getitem__(self, id: str) -> PACTCore:
        return self.context._registry._node_registry[id]

    def __iter__(self) -> Iterator[PACTCore]:
        return iter(self.context._registry._node_registry.values())

#TODO check for context_history overlaps
#TODO create TYPED dict for context
#TODO create a walk branch that walks at depth
#TODO delegate all temporal selection to selector engine
#TODO have a method to be able to buble up errors during context ops

class Context(PactRoot):
    """
    Main context class that provides thread-style building methods.
    
    Inherits from PactRoot which provides:
    - PACT-compliant structure with DepthArray content
    - Canonical PACT fields (id, type, offset, ttl, etc.)
    - Depth-based component organization
    
    Uses PACT depth system: d-1 (system), d0 (active), d1+ (history)
    """
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra='ignore'  # Allow extra fields like computed properties during serialization
    )
    
    # Add template field for declarative context structures
    template: Optional[Any] = Field(default=None)
    # Add agent field for listener dispatch integration
    agent: Optional[Any] = Field(default=None)
    # Add context manager field for agent-specific context operations
    context_manager: Optional[Any] = Field(default=None)
    # DepthArray will be initialized in __init__ since it needs context reference

    # Private runtime-only attributes (not serialized)
    _update_queue: UpdateQueue = PrivateAttr(default_factory=UpdateQueue)
    _registry: ContextRegistry = PrivateAttr(default_factory=ContextRegistry)
    _creation_index_counter: int = PrivateAttr(default=0)
    # Current episode/cycle tracking (private with getter/setter for component notification)
    _current_episode: int = PrivateAttr(default=0)
    # Hook system integration (Phase 1 of Hook System Unification)
    _hooks: Optional[Any] = PrivateAttr(default=None)
    _agent_id: Optional[str] = PrivateAttr(default=None)
    # Phase 3: Reactive Scaffolds - track scaffolds that re-render on context changes
    _reactive_scaffolds: list = PrivateAttr(default_factory=list)
    
    
    def __init__(self, template: Optional[Any] = None, **kwargs):
        """
        Initialize Context with DepthArray handling component creation.
        
        Args:
            template: Optional ContextStructure template to build context from
            **kwargs: Additional parameters
        """
        # Initialize basic fields for PactRoot
        kwargs['template'] = template
        
        # Initialize PactRoot with PACT-compliant structure
        super().__init__(**kwargs)
        
        # Initialize essential registries
        self._registry = ContextRegistry()
        self._creation_index_counter = 0
        self._update_queue = UpdateQueue()
        
        # DepthArray handles all component creation and registration automatically
        self.content = DepthArray(context=self)
        
        # Now that everything is initialized, create the default components
        self.content._initialize_components()
        
        # Assign creation_index=0 to the Context root itself
        self.creation_index = self.get_next_creation_index()
        
        # Register Context root in coordinate registry
        self._registry.set_children_count(self.id, 0)
        
        # Initialize node accessor
        self._nodes = NodeAccessor(self)
        
        # Optional: Initialize context history reference
        self._context_history: Optional[Any] = None
        
        # Build from template if provided (keep template building)
        if template:
            # Use pact operations for template building
            self._build_from_template(template)
        
        # Mark initialization as complete
        self._initialized = True
    
    def _build_from_template(self, template: Any) -> None:
        """
        Build context from template using pact operations.
        
        Args:
            template: ContextStructure template to build from
        """
        # Simple template building - can be expanded later
        # For now, just handle basic string content
        if isinstance(template, str):
            self.pact_insert("d0,0", template)
        elif hasattr(template, 'build'):
            # Delegate to template's own build method
            template.build(self)
        # Add more template handling as needed

    

    # Note: Component registration is now handled automatically by DepthArray
    # during initialization. No manual registration needed.
    

    def nodes(self) -> NodeAccessor:
        return self._nodes

    def __len__(self) -> int:
        return len(self.content) if self.content is not None else 0

    # Removed: selector_parser and selector_engine - using pact operations directly

    def _set_hooks(self, hooks: Any, agent_id: str) -> None:
        """
        Bind hook system to context (called by Agent during initialization).

        This enables CONTEXT_BEFORE_CHANGE and CONTEXT_AFTER_CHANGE hooks to fire
        during pact_insert/update/delete operations.

        Args:
            hooks: ToolExecutionHooks instance from the agent
            agent_id: Agent ID for hook context
        """
        self._hooks = hooks
        self._agent_id = agent_id

    def register_reactive_scaffold(self, scaffold: Any) -> None:
        """
        Register scaffold for automatic re-rendering on context changes (Phase 3).

        Reactive scaffolds will be triggered to re-render when CONTEXT_AFTER_CHANGE
        hooks fire during pact_insert/update/delete operations.

        Args:
            scaffold: BaseContextScaffold instance with should_rerender() method
        """
        if scaffold not in self._reactive_scaffolds:
            self._reactive_scaffolds.append(scaffold)

    @property
    def update_queue(self) -> UpdateQueue:
        return self._update_queue
    
    @property
    def current_episode(self) -> int:
        """Get current episode/cycle number."""
        return self._current_episode
    
    @current_episode.setter
    def current_episode(self, value: int) -> None:
        """Set current episode and trigger automatic cascade to all components."""
        self._current_episode = value

        # Trigger automatic cascade to all depth components
        assert self.content is not None, "Context.content should always be initialized"
        for component in self.content:
            try:
                component.current_episode = value  # This will propagate automatically
            except (KeyError, IndexError, AssertionError):
                # Component may have been deleted during TTL expiration
                continue

        # Process cadence component rehydration after TTL processing
        components_for_rehydration = self._registry.get_components_for_rehydration(value)
        if components_for_rehydration:
            from ..operations.context_insert import PactContextInsertHandler
            insert_handler = PactContextInsertHandler(self)

            for cadence_info in components_for_rehydration:
                try:
                    # Recreate the component from stored data
                    from ..components.core import TextContent, MessageContainer
                    component_data = cadence_info.component_data.copy()
                    component_class_name = component_data.get('__class__', 'TextContent')

                    component_classes = {
                        'TextContent': TextContent,
                        'TextContextComponent': TextContent,  # Legacy alias
                        'MessageContainer': MessageContainer,
                    }

                    component_class = component_classes.get(component_class_name, TextContent)
                    rehydrated_component = component_class.parse_obj(component_data)

                    # Update component's birth cycle to current cycle (fresh lifecycle)
                    if hasattr(rehydrated_component, 'metadata'):
                        rehydrated_component.metadata.born_cycle = value

                    # Insert the component back at the original coordinates
                    insert_result = insert_handler.insert(cadence_info.original_coordinates, rehydrated_component)
                    if not insert_result.success:
                        print(f"⚠️ Failed to rehydrate component at {cadence_info.original_coordinates}")
                except Exception as e:
                    print(f"⚠️ Rehydration error for {cadence_info.component_id}: {e}")
    
    @property  
    def system_header(self):
        """Access the system header component (depth -1)."""
        assert self.content is not None, "Context.content should always be initialized"
        return self.content[-1]
    
    
    @property 
    def conversation_history(self) -> 'DepthArray':
        """Access conversation segments via DepthArray (depths 1+)."""
        assert self.content is not None, "Context.content should always be initialized"
        return self.content
    
    @property
    def active_message(self):
        """Access the active message component (depth 0)."""
        assert self.content is not None, "Context.content should always be initialized"
        return self.content[0]
    
    def __iter__(self) -> Iterator[PACTCore]:
        assert self.content is not None, "Context.content should always be initialized"
        for component in self.content:
            yield component
    
    def traverse_branch(self, depth: int) -> Iterator[PACTCore]:
        """Traverse all components in a specific depth branch (tree walk).
        
        Args:
            depth: The depth to traverse (-1 for system, 0 for active, 1+ for history)
            
        Yields:
            PACTCore: All components in the depth branch tree
        """
        try:
            assert self.content is not None, "Context.content should always be initialized"
            depth_component = self.content[depth]
            yield depth_component
            
            # Recursively traverse all children in the branch
            yield from self._traverse_component_tree(depth_component)
            
        except (KeyError, ValueError, IndexError):
            # Depth doesn't exist - no components to yield
            return
    
    def _traverse_component_tree(self, component: PACTCore) -> Iterator[PACTCore]:
        """Recursively traverse a component tree (depth-first)."""
        if hasattr(component, 'content') and getattr(component, 'content', None):
            # Skip string content (leaf nodes)
            content = getattr(component, 'content', None)
            if isinstance(content, str):
                return
            
            # Handle CoreOffsetArray content (container components)
            from ..data_structures.core_offset_array import CoreOffsetArray
            if isinstance(content, CoreOffsetArray):
                for offset in content.get_offsets():
                    try:
                        child = content[offset]
                        # Filter out expired components during traversal
                        if hasattr(child, '_is_expired') and child._is_expired():
                            continue  # Skip expired components
                        yield child
                        # Recursively traverse this child's tree if it's a container
                        if isinstance(child, PACTContainer):
                            yield from self._traverse_component_tree(child)
                    except (KeyError, IndexError):
                        continue
            else:
                # This shouldn't happen - content should only be str or CoreOffsetArray
                print(f"Warning: {type(component).__name__} has unexpected content type {type(content)}")
    
    @property
    def traverse(self) -> Iterator[PACTCore]:
        """Traverse all components in the entire context tree in canonical order.
        
        Yields components in PACT canonical order: system (-1), active (0), history (1+)
        """
        assert self.content is not None, "Context.content should always be initialized"
        for component in self.content:  # Now iterates over actual components
            yield component
            # Recursively traverse all children in each component
            yield from self._traverse_component_tree(component)

    
    def __getitem__(self, coords: int) -> PACTCore:
        """
        Context indexing with minimum 2 coordinates requirement.
        
        Usage:
            context[-1, 0]     # system_header.content[0]
            context[0, 2]      # active_message.content[2]
            context[1, 0, 3]   # conversation_history.content[0].content[3]
        
        Args:
            coords: Tuple of coordinates or Coordinates object
            
        Returns:
            PACTCore at the specified coordinates
            
        Raises:
            TypeError: If less than 2 coordinates provided
            IndexError: If coordinates are out of bounds
            ValueError: If navigation fails
        """
        # Convert tuple to Coordinates
        if isinstance(coords, tuple):
            if len(coords) < 2:
                raise TypeError(f"Context indexing requires at least 2 coordinates, got {len(coords)}")
            coords_obj = Coordinates(*coords)
        elif isinstance(coords, Coordinates):
            if len(coords) < 2:
                raise TypeError(f"Context indexing requires at least 2 coordinates, got {len(coords)}")
            coords_obj = coords
        else:
            raise TypeError(f"Context indices must be tuple or Coordinates, got {type(coords)}")
        
        # Direct coordinate navigation - simplified implementation
        # Navigate through DepthArray to target coordinates
        assert self.content is not None, "Context.content should always be initialized"
        depth = coords_obj[0]
        component = self.content[depth]
        
        # Navigate deeper if more coordinates provided
        if len(coords_obj) > 1:
            for offset in coords_obj.coords[1:]:  # Use .coords tuple which supports slicing
                component_content = getattr(component, 'content', None)
                if component_content is not None and hasattr(component_content, '__getitem__'):
                    component = component_content[offset]
                else:
                    raise IndexError(f"Cannot navigate to offset {offset} in {type(component)}")
        
        return component
    
    
    def get_component_by_id(self, component_id: str):
        """Get component by ID from registry."""
        return self._registry._node_registry.get(component_id)
    
    
    def select(self, selector: str, snapshot: Optional[str] = None) -> Union[List[PACTCore], 'RangeDiffLatestResult']:
        """
        PACT-compliant selector - delegates to pact_select.
        
        Args:
            selector: PACT selector string (e.g., "^sys .block", "(d1) .seg", "@t0..@t-5")
            snapshot: Snapshot address (None=Working State, @t-1=previous, @cN=cycle N)
            
        Returns:
            - List of PACTCore objects for spatial selectors
            - RangeDiffLatestResult for temporal range selectors (@t0..@t-5)
        """
        # Delegate to pact_select which uses the proper pact selector
        if snapshot:
            # Handle snapshot addressing
            target_context = self._resolve_snapshot(snapshot)
            return target_context.pact_select(selector)
        else:
            return self.pact_select(selector)
    
    
    
    def _resolve_snapshot(self, snapshot: Optional[str] = None) -> 'Context':
        """
        Resolve snapshot address to Context instance.
        
        Handles PACT snapshot addressing format:
        - None: Working State (current active context - PACT v0.1 default)
        - @t0: Current snapshot (legacy)
        - @t-N: N snapshots ago (relative)
        - @cN: Absolute cycle N
        
        Args:
            snapshot: Snapshot address string or None for Working State
            
        Returns:
            Context instance for the specified snapshot
        """
        if snapshot is None or snapshot == "@t0":
            return self  # Current context (Working State)
        
        # Integrate with ContextHistory for full PACT snapshot addressing
        if hasattr(self, 'context_manager'):
            history = getattr(self.context_manager, 'context_history', None)
            if history:
                
                if snapshot.startswith("@t-"):
                    # Relative snapshot (@t-1, @t-2, etc.)
                    try:
                        offset = int(snapshot[3:])
                        snapshot_context = history.get_snapshot_by_offset(offset)
                        if snapshot_context:
                            return snapshot_context
                    except (ValueError, AttributeError):
                        pass
                elif snapshot.startswith("@c"):
                    # Absolute cycle (@c42, @c100, etc.)
                    try:
                        cycle = int(snapshot[2:])
                        snapshot_context = history.get_snapshot_by_cycle(cycle)
                        if snapshot_context:
                            return snapshot_context
                    except (ValueError, AttributeError):
                        pass
                elif snapshot == "@*" or snapshot == "@t*":
                    return self
                elif snapshot == "@hist":
                    snapshot_context = history.get_snapshot_by_offset(1)  # t-1
                    if snapshot_context:
                        return snapshot_context
                elif ".." in snapshot:
                    # Handle time ranges like @t0..@t-3
                    range_parts = snapshot.split("..")
                    if len(range_parts) == 2:
                        try:
                            start_snapshot = range_parts[0]
                            if start_snapshot.startswith("@t"):
                                offset = int(start_snapshot[3:]) if start_snapshot[3:] else 0
                                if offset == 0:
                                    return self  # t0 is current
                                else:
                                    snapshot_context = history.get_snapshot_by_offset(abs(offset))
                                    if snapshot_context:
                                        return snapshot_context
                        except (ValueError, AttributeError):
                            pass
        
        # Fallback to current context if snapshot resolution fails
        return self
    
    
    
    def _update_queued(self, selector_or_component: Union[str, PACTCore, List[PACTCore]], content: Optional[str] = None, **kwargs) -> UpdateResult:
        """
        Queue update operation for next agent call.
        
        Args:
            selector_or_component: Component selector/reference to update
            content: New content to set (if provided)
            **kwargs: Other properties to update (ttl, etc.)
        
        Returns:
            UpdateResult indicating operation was queued successfully
        """
        try:
            # Handle list of components by creating operations for each
            if isinstance(selector_or_component, list):
                operations = []
                for component in selector_or_component:
                    operation = UpdateOperation(
                        selector_or_component=component,
                        content=content,
                        properties=kwargs,
                        timestamp=datetime.now(),
                        agent_id=getattr(self.agent, 'agent_id', None) if self.agent else None
                    )
                    operations.append(operation)
                # For now, just use the first operation (could be enhanced later)
                operation = operations[0] if operations else None
            else:
                # Create update operation
                operation = UpdateOperation(
                    selector_or_component=selector_or_component,
                    content=content,
                    properties=kwargs,
                    timestamp=datetime.now(),
                    agent_id=getattr(self.agent, 'agent_id', None) if self.agent else None
                )
            
            # Add to queue
            if operation is not None:
                self.update_queue.add_update(operation)
            
            return UpdateResult(
                success=True,
                warnings=[f"Update queued for next agent call (queue size: {len(self.update_queue)})"]
            )
            
        except Exception as e:
            return UpdateResult(
                success=False,
                errors=[f"Failed to queue update: {str(e)}"]
            )
    
    
    def __str__(self) -> str:
        """
        Return user-friendly string representation of context.
        
        Provides convenient access via print(context) for debugging.
        Uses render() with sensible defaults for quick inspection.
        
        Returns:
            Basic markdown representation without metadata or empty sections
        """
        return self.render()
    
    def render(self, **kwargs) -> str:
        """
        Render the entire context as a formatted string.
        
        Simplified rendering - delegates to components.
        """
        try:
            sections = []
            
            # Render system header if available
            try:
                system_content = str(self.system_header)
                sections.append(f"# System\n{system_content}")
            except Exception:
                sections.append("# System\n(System header unavailable)")
            
            # Render active message if available
            try:
                active_content = str(self.active_message)
                sections.append(f"# Active Message\n{active_content}")
            except Exception:
                sections.append("# Active Message\n(Active message unavailable)")
            
            # Render conversation history
            assert self.content is not None, "Context.content should always be initialized"
            for depth in self.content.depths():  # Use depths() method to get depth numbers
                if depth > 0:  # Historical depths
                    try:
                        component = self.content[depth]
                        component_content = str(component)
                        sections.append(f"# History {depth}\n{component_content}")
                    except Exception:
                        sections.append(f"# History {depth}\n(Component unavailable)")
            
            return "\n\n---\n\n".join(sections) if sections else "(Empty context)"
        except Exception as e:
            return f"Error rendering context: {str(e)}"
    
    # Simplified rendering - complex rendering logic removed
    
    
    def render_to_thread(self, scheduler=None) -> 'ProviderThread':
        if scheduler is None:
            try:
                from ...agent.message_scheduler import MessageScheduler
                scheduler = MessageScheduler(self)
            except ImportError as e:
                raise ImportError(f"MessageScheduler not available and none provided: {str(e)}") from e
        
        try:
            return scheduler.render()
        except Exception as e:
            raise Exception(f"Failed to render context to thread: {str(e)}") from e
    
    
    

    # --- Pact integration methods ---
    def pact_select(self, selector: str):
        """Select components using pact (Lark) selector semantics.

        - Accepts CSS-style spaces/child combinators (normalized to PACT ?/??).
        - Enforces behavior semantics strictly.
        - For temporal ranges (@tA..@tB) returns RangeDiffLatestResult.
        - Raises on invalid grammar.
        """
        # Fast-path: ensure temporal ranges always return RangeDiff like core
        if ".." in selector and "@t" in selector:
            return self._handle_range_selector(selector)
        from .selector.engine import LarkPACTSelector
        from .selector.parser import LarkPACTParser
        parser = LarkPACTParser()
        selector_ast = parser.parse(selector)
        engine = LarkPACTSelector()
        return engine.select(self, selector_ast)

    def pact_insert(self, selector, component):
        """Insert via pact insertion semantics. Returns UpdateResult."""
        # Validate and convert string to TextContent BEFORE hooks fire
        if isinstance(component, str):
            # Block empty strings - validation only applies to string inputs, not pre-made components
            if not component.strip():
                from . import UpdateResult
                return UpdateResult(success=False, errors=["Empty string content not allowed"])
            from ..components.core import TextContent
            component = TextContent(content=component)

        # Phase 1: Fire CONTEXT_BEFORE_CHANGE hook
        if self._hooks:
            from ....agent.hooks.execution_contexts import ContextFactory
            from ....agent.hooks.execution import HookType
            ctx = ContextFactory.create_context_context(
                agent_id=self._agent_id,
                context=self,
                operation_type="insert",
                component=component,
                selector=selector
            )
            self._hooks.execute_hooks(HookType.CONTEXT_BEFORE_CHANGE, ctx)
            # Use potentially-modified component from hook
            component = ctx.component

        # Perform insertion
        from ..operations.context_insert import PactContextInsertHandler
        handler = PactContextInsertHandler(self)
        result = handler.insert(selector, component)

        # Phase 1: Fire CONTEXT_AFTER_CHANGE hook
        if self._hooks:
            # Update context with result information (use first updated component if available)
            if result.updated_components:
                ctx.component = result.updated_components[0]
            self._hooks.execute_hooks(HookType.CONTEXT_AFTER_CHANGE, ctx)

        return result

    def pact_update(
        self,
        selector_or_component=None,
        component=None,
        mode: str = "replace",
        content=None,
        **kwargs,
    ):
        """Update via pact update semantics. Returns UpdateResult."""
        # Phase 1: Fire CONTEXT_BEFORE_CHANGE hook
        if self._hooks:
            from ....agent.hooks.execution_contexts import ContextFactory
            from ....agent.hooks.execution import HookType
            ctx = ContextFactory.create_context_context(
                agent_id=self._agent_id,
                context=self,
                operation_type="update",
                component=component,
                selector=selector_or_component if isinstance(selector_or_component, str) else None,
                mode=mode
            )
            self._hooks.execute_hooks(HookType.CONTEXT_BEFORE_CHANGE, ctx)
            # Use potentially-modified component from hook
            component = ctx.component

        # Perform update
        from ..operations.context_update import PactContextUpdateHandler
        handler = PactContextUpdateHandler(self)
        result = handler.update(
            pos_or_selector=selector_or_component,
            component=component,
            mode=mode,
            content=content,
            **kwargs,
        )

        # Phase 1: Fire CONTEXT_AFTER_CHANGE hook
        if self._hooks:
            # Update context with result information (use first updated component if available)
            if result.updated_components:
                ctx.component = result.updated_components[0]
            self._hooks.execute_hooks(HookType.CONTEXT_AFTER_CHANGE, ctx)

        return result

    def pact_delete(self, selector_or_component):
        """Delete via pact deletion semantics. Returns UpdateResult."""
        # Phase 1: Fire CONTEXT_BEFORE_CHANGE hook
        if self._hooks:
            from ....agent.hooks.execution_contexts import ContextFactory
            from ....agent.hooks.execution import HookType
            ctx = ContextFactory.create_context_context(
                agent_id=self._agent_id,
                context=self,
                operation_type="delete",
                component=selector_or_component if not isinstance(selector_or_component, str) else None,
                selector=selector_or_component if isinstance(selector_or_component, str) else None
            )
            self._hooks.execute_hooks(HookType.CONTEXT_BEFORE_CHANGE, ctx)

        # Perform deletion
        from ..operations.context_delete import PactContextDeleteHandler
        handler = PactContextDeleteHandler(self)
        result = handler.delete(selector_or_component)

        # Phase 1: Fire CONTEXT_AFTER_CHANGE hook
        if self._hooks:
            # Update context with result information
            ctx.component = result.component if hasattr(result, 'component') else None
            self._hooks.execute_hooks(HookType.CONTEXT_AFTER_CHANGE, ctx)

        return result
    
    # Public API delegation methods for content management
    def add_system(self, content):
        """Add content to system header via pact operations."""
        return self.pact_insert("d-1,0", content)
    
    def add_user(self, content):
        """Add user message via pact operations."""
        return self.pact_insert("d0,0", content)
    
    def add_assistant(self, content):
        """Add assistant message via pact operations."""
        result = self.pact_insert("d0,0", content)
        # Set the role to 'assistant' on the newly created depth-0 MessageTurn
        if len(self.content) > 0:
            for depth_comp in self.content:
                if getattr(depth_comp, 'depth', None) == 0:
                    depth_comp.role = "assistant"
                    break
        return result
    
    def get_next_creation_index(self) -> int:
        """Get next creation index for PACT compliance."""
        index = self._creation_index_counter
        self._creation_index_counter += 1
        return index
    
    def _copy_query_without_temporal(self, query):
        """Create a copy of the query with temporal addressing removed.
        
        Args:
            query: SelectorQuery object with temporal addressing
            
        Returns:
            SelectorQuery object without temporal addressing
        """
        # Create a copy of the query and clear the temporal field
        # This is a simple approach - we'll copy the query object and set temporal to None
        import copy
        non_temporal_query = copy.copy(query)
        non_temporal_query.temporal = None
        return non_temporal_query
    
    def _deduplicate_components(self, components):
        """Remove duplicate components while preserving order.
        
        Args:
            components: List of PACTCore objects
            
        Returns:
            List of unique PACTCore objects in original order
        """
        seen = set()
        unique_components = []
        for component in components:
            # Use component ID for deduplication if available, otherwise use object identity
            component_key = getattr(component, 'id', id(component))
            if component_key not in seen:
                seen.add(component_key)
                unique_components.append(component)
        return unique_components
    
    # Context History Management (Internal)
    
    def _set_context_history(self, history: 'ContextHistory') -> None:
        """Set the context history instance for snapshot creation.
        
        Args:
            history: ContextHistory instance to use for snapshots
        """
        self._context_history = history
    
    def _get_context_history(self) -> Optional['ContextHistory']:
        """Get the current context history instance.
        
        Returns:
            ContextHistory instance if set, None otherwise
        """
        return self._context_history
    
    def seal(self, trigger: str = "context_seal", flush: bool = False) -> str:
        """Create an immutable snapshot of the current context state (PACT commit boundary).

        This is the primary method for creating PACT-compliant snapshots of the context.
        Each seal represents one cycle/episode boundary in PACT terminology.

        Args:
            trigger: What triggered this seal (e.g., 'before_provider_call', 'manual')
            flush: Wait for snapshot write to complete (default: async, returns immediately)

        Returns:
            snapshot_id: Unique identifier for the sealed snapshot

        Raises:
            ContextHistoryError: If no history is attached to this context

        Examples:
            # Seal context (async)
            snapshot_id = context.seal()

            # Seal with specific trigger
            snapshot_id = context.seal(trigger="before_provider_call")

            # Seal and wait for write to complete
            snapshot_id = context.seal(trigger="manual", flush=True)
        """
        from ...history.errors import ContextHistoryError

        if not hasattr(self, '_context_history') or self._context_history is None:
            raise ContextHistoryError("No ContextHistory attached to context. Cannot seal context.")

        snapshot_id = self._context_history.create_snapshot(self, trigger)

        if flush:
            # Wait for async snapshot write to complete
            self._context_history.flush(timeout=10.0)

        return snapshot_id
    
    def _handle_range_selector(self, selector: str) -> 'RangeDiffLatestResult':
        """
        Handle temporal range selectors like @t0..@t-5.
        
        Returns RangeDiffLatestResult with actual PACT nodes instead of just IDs.
        """
        from ...history.context_snapshot import create_range_diff_result, ContextSnapshot
        
        # Parse the range from selector (simplified parsing)
        # Format: @t0..@t-5 or @t-1..@t-5
        if '..' not in selector:
            raise ValueError(f"Invalid range selector: {selector}")
        
        # Extract range parts
        range_part = selector.strip()
        if not range_part.startswith('@t'):
            raise ValueError(f"Range selector must start with @t: {selector}")
        
        # Remove @t prefix and split on ..
        temporal_part = range_part[2:]  # Remove @t
        if '..' not in temporal_part:
            raise ValueError(f"Invalid range syntax: {selector}")
        
        range_parts = temporal_part.split('..')
        if len(range_parts) != 2:
            raise ValueError(f"Invalid range syntax: {selector}")
        
        start_str, end_str = range_parts
        
        # Handle @t prefix in end part
        if end_str.startswith('@t'):
            end_str = end_str[2:]
        
        # Convert to integers
        try:
            start_offset = int(start_str)
            end_offset = int(end_str)
        except ValueError:
            raise ValueError(f"Invalid range values: {selector}")
        
        # Get snapshots from history
        snapshots = self._get_snapshots_in_range(start_offset, end_offset)
        
        # Create range diff result with resolved PACT nodes
        return create_range_diff_result(selector, snapshots, resolve_nodes=True)
    
    def _get_snapshots_in_range(self, start_offset: int, end_offset: int) -> List['ContextSnapshot']:
        """
        Get snapshots in the specified range.
        
        Args:
            start_offset: Start offset (0 = current, -1 = previous, etc.)
            end_offset: End offset (inclusive)
            
        Returns:
            List of ContextSnapshot objects in range
        """
        from ...history.context_snapshot import ContextSnapshot, create_full_snapshot
        
        snapshots = []
        
        # Determine range direction
        if start_offset <= end_offset:
            # Forward range: @t0..@t-5 (0, -1, -2, -3, -4, -5)
            for offset in range(start_offset, end_offset - 1, -1):
                snapshot = self._get_snapshot_at_offset(offset)
                if snapshot:
                    snapshots.append(snapshot)
        else:
            # Reverse range: @t-5..@t0 (-5, -4, -3, -2, -1, 0)
            for offset in range(start_offset, end_offset + 1):
                snapshot = self._get_snapshot_at_offset(offset)
                if snapshot:
                    snapshots.append(snapshot)
        
        return snapshots
    
    def _get_snapshot_at_offset(self, offset: int) -> Optional['ContextSnapshot']:
        """
        Get snapshot at specific temporal offset.
        
        Args:
            offset: Temporal offset (0 = current, -1 = previous, etc.)
            
        Returns:
            ContextSnapshot if available, None otherwise
        """
        from ...history.context_snapshot import ContextSnapshot, create_full_snapshot
        
        if offset == 0:
            # Current state - create snapshot on demand
            return create_full_snapshot(
                context=self,
                snapshot_id=f"current_{int(datetime.now().timestamp())}",
                trigger="range_selector_current"
            )
        elif offset < 0:
            # Historical snapshots - get from context history
            if hasattr(self, 'context_manager'):
                history = getattr(self.context_manager, 'context_history', None)
                if history:
                    # Convert offset to positive index for history lookup
                    abs_offset = abs(offset)
                    return history.get_snapshot_by_offset(abs_offset)
        
        return None
    


    def model_dump(self, **kwargs) -> Dict[str, Any]:
        """
        Override Pydantic's model_dump to only serialize PACT-compliant fields.

        This ensures Context serialization only includes PACT v0.1 fields,
        excluding runtime-only attributes like _registry, _update_queue, etc.

        Returns:
            PACT v0.1 compliant dictionary
        """
        return self.to_pact()

    def to_pact(self) -> Dict[str, Any]:
        """
        Convert Context to full PACT v0.1 compliant tree structure.

        Returns:
            Dictionary containing PACT root node with all regions as children
        """
        from datetime import datetime
        import time
        
        # Get the initial regions from DepthArray
        existing_regions = self.content.seal()
        
        # Ensure all three canonical PACT regions are present
        region_types = {region.get("nodeType") for region in existing_regions if isinstance(region, dict)}
        
        # Build the complete regions list with all canonical regions
        all_regions = list(existing_regions)  # Start with existing regions
        
        # Add missing seq region if not present
        if "seq" not in region_types:
            from ..components.core import generate_hash_id
            seq_region = {
                "id": generate_hash_id("seq", self.id),
                "nodeType": "seq",
                "parent_id": self.id,
                "offset": 1,  # Sequence region has positive offset
                "ttl": None,
                "priority": 0,
                "cycle": getattr(self, 'current_episode', 0),
                "created_at_ns": int(time.time_ns()),
                "created_at_iso": datetime.now().isoformat(),
                "creation_index": len(all_regions),
                "children": []  # Empty for now, would contain conversation segments
            }
            # Insert seq region between sys and ah (canonical order: sys, seq, ah)
            sys_index = next((i for i, r in enumerate(all_regions) if r.get("nodeType") == "sys"), 0)
            all_regions.insert(sys_index + 1, seq_region)
        
        # Create root PACT node
        pact_root = {
            # Required PACT fields
            "id": self.id,
            "nodeType": "root",
            "parent_id": None,
            "offset": 0,
            "ttl": None,
            "priority": 0,
            "cycle": getattr(self, 'current_episode', 0),
            "created_at_ns": getattr(self, 'created_at_ns', int(time.time_ns())),
            "created_at_iso": getattr(self, 'created_at_iso', datetime.now().isoformat()),
            "creation_index": self.creation_index,
            
            # Children are the complete PACT regions
            "children": all_regions
        }
        
        # Add context-level metadata in org attributes
        pact_root["org"] = {
            "context_type": "conversation",
            "agent_id": getattr(self.agent, 'id', None) if self.agent else None,
            "episode": getattr(self, 'current_episode', 0)
        }
        
        # Add optional fields if present
        if hasattr(self, 'key') and self.key:
            pact_root["key"] = self.key
        if hasattr(self, 'tags') and self.tags:
            pact_root["tag"] = self.tags
            
        return pact_root
    
    
