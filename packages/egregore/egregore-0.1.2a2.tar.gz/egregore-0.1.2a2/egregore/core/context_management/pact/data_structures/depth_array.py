"""
DepthArray - PACT depth-aware dynamic array for Context components.

Provides type-safe access to PACT components by depth:
- depth -1: SystemHeaderComponent (system instructions)
- depth 0: ActiveMessageComponent (current working message)
- depth 1, 2, 3, ...: Individual MessageTurnComponents (conversation segments)

Integrates with existing coordinate shifting system for automatic depth recalculation
when segments are removed.
"""

from typing import Union, List, Iterator, Optional, TYPE_CHECKING, overload, Literal, Dict, Any
from pydantic import BaseModel, computed_field, Field, PrivateAttr

if TYPE_CHECKING:
    from ..context.base import Context
    from ..components.core import (
        SystemHeader,
        MessageTurn,
    )

# Union type for DepthArray components  
DepthComponent = Union['SystemHeader', 'MessageTurn']

class DepthArray(BaseModel):
    """
    PACT depth-aware dynamic array with single list storage.
    
    Structure:
    - depth -1: SystemHeader (at index 0 in list)
    - depth 0: MessageTurn with MessageContainer at offset 0 (active message)
    - depth 1, 2, 3, ...: MessageTurn with MessageContainer at offset 0 (historical)
    
    Storage: Single list where depth = index - 1 (so d[-1] = list[0], d[0] = list[1], etc.)
    Auto-creates MessageTurn + MessageContainer when adding depths.
    Maintains Context reference for all components.
    """
    
    # Pydantic fields
    _context: Optional['Context'] = PrivateAttr(default=None)
    _depths: List[DepthComponent] = PrivateAttr(default_factory=list)
    
    model_config = {
        "arbitrary_types_allowed": True,
        "extra": "forbid"
    }
    
    def __init__(self, context: 'Context' = None, **kwargs):
        """Initialize DepthArray with Context reference."""
        super().__init__(**kwargs)
        
        self._context = context
        self._depths = []
        self._initialized = False
        
        # Delay component creation until Context is fully initialized
        if context is not None:
            self._initialize_components()
    
    def _initialize_components(self):
        """Initialize the default components when Context is ready."""
        if self._initialized or self._context is None:
            return
            
        from ..components.core import SystemHeader, MessageTurn, MessageContainer
        
        # Only initialize if context has _registry (fully initialized)
        if not hasattr(self._context, '_registry'):
            return
        
        # Create SystemHeader at index 0 (depth -1) and auto-register
        system_header = SystemHeader(context=self._context)
        self._context._registry.register_component(system_header)
        self._depths.append(system_header)
        
        # Create initial MessageTurn at index 1 (depth 0) - MessageContainer is auto-created in MessageTurn.__init__
        message_turn = MessageTurn(context=self._context)
        self._context._registry.register_component(message_turn)
        self._depths.append(message_turn)
        
        self._initialized = True
    
    @overload
    def __getitem__(self, depth: Literal[-1]) -> 'SystemHeader':
        ...

    @overload
    def __getitem__(self, depth: int) -> 'MessageTurn':
        ...

    @overload
    def __getitem__(self, depth: slice) -> List[Union['SystemHeader', 'MessageTurn']]:
        ...

    def __getitem__(self, depth: Union[int, slice]) -> Union['SystemHeader', 'MessageTurn', List[Union['SystemHeader', 'MessageTurn']]]:
        """Get component by PACT depth with proper typing."""
        if isinstance(depth, slice):
            # Handle slice access - treat slice as depth range, not index range
            result = []
            start, stop, step = depth.indices(100)  # Large upper bound for depth range
            
            # If step is None, default to 1
            if step == 0:
                step = 1
            
            # Handle negative start/stop by treating them as actual depth values
            if depth.start is not None and depth.start < 0:
                start = depth.start
            if depth.stop is not None and depth.stop < 0:
                stop = depth.stop
            elif depth.stop is not None:
                stop = depth.stop
            else:
                # Calculate max depth from list length
                stop = len(self._depths) - 2  # -1 for 0-based, -1 more for depth offset
                
            # Generate range of depths to include
            if start <= stop:
                depth_range = range(start, stop, step)
            else:
                depth_range = range(start, stop, -abs(step))
            
            # Collect components that exist at these depths
            for d in depth_range:
                try:
                    component = self[d]
                    result.append(component)
                except (KeyError, IndexError):
                    # Skip depths that don't exist
                    continue
            
            return result
            
        # Handle single int access - validate depth first
        if depth < -1:
            raise ValueError(f"Invalid PACT depth: {depth}")
            
        # Convert depth to list index: depth -1 → index 0, depth 0 → index 1, etc.
        list_index = depth + 1
        
        if list_index >= len(self._depths):
            raise KeyError(f"No component at depth {depth}")
            
        component = self._depths[list_index]
            
        return component  # type: ignore
    
    def __setitem__(self, depth: int, component: DepthComponent) -> None:
        """Set component by PACT depth."""
        list_index = depth + 1  # depth -1 → index 0, depth 0 → index 1, etc.
        
        if depth < -1:
            raise ValueError(f"Invalid PACT depth: {depth}")
            
        # Extend list if needed (should rarely happen with proper usage)
        while len(self._depths) <= list_index:
            # This should only happen for historical depths, create placeholder MessageTurns
            from ..components.core import MessageTurn, MessageContainer
            temp_turn = MessageTurn(context=self._context)
            temp_container = MessageContainer(context=self._context)
            temp_turn.content.insert(0, temp_container)
            self._depths.append(temp_turn)
            
        self._depths[list_index] = component
        
        # Set component's depth and context reference
        component.depth = depth
        component._context_ref = self._context
    
    def __contains__(self, depth: int) -> bool:
        """Check if component exists at depth."""
        try:
            self[depth]
            return True
        except (KeyError, ValueError, IndexError):
            return False
    
    def __len__(self) -> int:
        """Return total conversation depth count (d0+), excluding system header."""
        # Count components excluding system header (index 0)
        return len(self._depths) - 1
    
    def __iter__(self) -> Iterator['MessageTurn']:
        """Iterate over actual components at each depth."""
        # Return actual components, not depth integers - this is more appropriate!
        for component in self._depths:
            if component is not None:
                yield component
                
    def depths(self) -> Iterator[int]:
        """Iterate over depth integers for when you need the actual depth numbers."""
        for i, component in enumerate(self._depths):
            if component is not None:
                # Convert array index to depth: index 0 = depth -1, index 1 = depth 0, etc.
                depth = i - 1
                yield depth
    
    def __delitem__(self, depth: int) -> None:
        """Delete component at depth like list.__delitem__ but protect d[-1] and d[0]."""
        # Validate depth
        if depth == -1:
            raise ValueError("Cannot remove system header (depth -1)")
        elif depth == 0:
            raise ValueError("Cannot remove active message (depth 0)")
        elif depth < -1:
            raise ValueError(f"Invalid PACT depth: {depth}")
        
        # Convert to list index
        list_index = depth + 1
        
        if list_index >= len(self._depths):
            raise KeyError(f"No component at depth {depth}")
            
        # Remove and shift down like list.pop()
        self._depths.pop(list_index)
        
        # Update depth attributes for all shifted components
        for i in range(list_index, len(self._depths)):
            component = self._depths[i]
            component.depth = i - 1  # Convert back to depth coordinate
    
    
    def insert(self, depth: int, component_or_content) -> None:
        """
        Insert at depth with automatic handling based on input type:
        
        - MessageTurn: Insert the provided MessageTurn at depth
        - MessageContainer: Replace existing MessageContainer at d[depth,0,0] 
        - Other content: Create new MessageTurn+MessageContainer, put content at d[depth,0,0]
        
        Example: insert(2, comp) shifts depth 2→3, depth 3→4, etc.
        Only works for conversation segments (depth >= 1).
        """
        if depth <= 0:
            raise ValueError("Can only insert conversation segments at depth >= 1")
        
        from ..components.core import MessageTurn, MessageContainer
        
        if isinstance(component_or_content, MessageTurn):
            # Case 1: Direct MessageTurn insertion
            component = component_or_content
            
        elif isinstance(component_or_content, MessageContainer):
            # Case 2: MessageContainer replacement
            # Get existing MessageTurn at this depth or create new one
            if depth + 1 < len(self._depths):
                # Existing MessageTurn - replace its MessageContainer
                existing_turn = self._depths[depth + 1]
                # Delete old MessageContainer at offset 0
                if hasattr(existing_turn, 'content') and 0 in existing_turn.content:
                    existing_turn.content.remove(0)
                # Insert new MessageContainer at offset 0
                existing_turn.content.insert(0, component_or_content)
                # Set proper parent reference
                if hasattr(component_or_content, '_context_ref'):
                    component_or_content._context_ref = self._context
                return
            else:
                # No existing MessageTurn - create new one with this MessageContainer
                component = MessageTurn(context=self._context)
                component.content.insert(0, component_or_content)
                
        else:
            # Case 3: Content - create new MessageTurn+MessageContainer
            component = MessageTurn(context=self._context)
            message_container = MessageContainer(context=self._context)
            
            # Put content in MessageContainer at d[depth,0,0]
            if hasattr(message_container, 'content'):
                message_container.content = component_or_content
            
            component.content.insert(0, message_container)
        
        list_index = depth + 1
        
        # Extend array if needed (create placeholder MessageTurns)
        while len(self._depths) < list_index:
            temp_turn = MessageTurn(context=self._context)
            temp_container = MessageContainer(context=self._context)
            temp_turn.content.insert(0, temp_container)
            self._depths.append(temp_turn)
        
        # Insert and shift subsequent elements up
        self._depths.insert(list_index, component)
        
        # Set context reference and depth
        assert hasattr(component, '_context_ref'), f"Component {type(component)} must have _context_ref attribute"
        component._context_ref = self._context
        component.depth = depth
        
        # Update depth attributes for all shifted components
        for i in range(list_index + 1, len(self._depths)):
            comp = self._depths[i]
            comp.depth = i - 1  # Convert back to depth coordinate
    
    def append(self, component: 'MessageTurn') -> int:
        """
        Append conversation segment at next available depth.
        
        Returns:
            The depth where the segment was added
        """
        from ..components.core import MessageTurn
        if not isinstance(component, MessageTurn):
            raise TypeError(f"Can only append MessageTurn, got {type(component)}")
        
        # Append to end of list
        self._depths.append(component)
        depth = len(self._depths) - 2  # Convert back to depth coordinate
        
        # Set context reference and depth
        assert hasattr(component, '_context_ref'), f"Component {type(component)} must have _context_ref attribute"
        component._context_ref = self._context
        component.depth = depth
        
        return depth
    
    
    
    
    def items(self) -> List[DepthComponent]:
        """Get all components in the DepthArray for selector engine traversal."""
        return self._depths.copy()

    def get_all_items(self) -> List[DepthComponent]:
        """Get all components in the DepthArray (alias for items() for selector engine compatibility)."""
        return self.items()
    
    
    @computed_field
    @property
    def max_depth(self) -> int:
        """Get the maximum depth currently available in the DepthArray."""
        # Empty array starts at depth -1 (ready for system header)
        if len(self._depths) == 0:
            return -1
        # Return the highest depth: len=1 → depth -1, len=2 → depth 0, etc.
        return len(self._depths) - 2  # Convert back to depth coordinate
    
    def seal(self) -> List[Dict[str, Any]]:
        """
        Convert DepthArray to PACT v0.1 compliant format.
        
        Returns:
            List of PACT nodes representing all components in depth order,
            with proper PACT region mapping:
            - depth -1: system region (nodeType="sys")
            - depth 0: active head region (nodeType="ah")  
            - depth 1+: sequence segments (nodeType="seg")
        """
        pact_regions = []
        
        # Serialize components in depth order
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[SEAL] Starting seal() with depths: {list(self.depths())}")

        for depth in sorted(self.depths()):
            component = self[depth]
            logger.info(f"[SEAL] Depth {depth}: {type(component).__name__}, id={id(component)}")

            if hasattr(component, 'model_dump'):
                # TEMP DEBUG: Log scaffold specifically
                if hasattr(component, '_update_scaffold_state_field'):
                    logger.info(f"[SEAL] Found SCAFFOLD at depth {depth}, object_id={id(component)}, scaffold_state={getattr(component, 'scaffold_state', 'NO ATTR')[:50] if getattr(component, 'scaffold_state', None) else 'None'}...")

                # Use Pydantic model_dump for PACT compliance
                pact_node = component.model_dump()

                # TEMP DEBUG: Check if pact_node has scaffold_state in org for scaffolds
                if hasattr(component, '_update_scaffold_state_field'):
                    org_keys = list(pact_node.get('org', {}).keys())
                    logger.info(f"[SEAL] After model_dump, org keys: {org_keys[:10]}")
                    logger.info(f"[SEAL] Has scaffold_state in org: {'scaffold_state' in pact_node.get('org', {})}")

                pact_regions.append(pact_node)
            else:
                # Fallback for components without model_dump method
                # This should not happen in normal operation
                pact_regions.append({
                    "id": getattr(component, 'id', 'unknown'),
                    "nodeType": "unknown",
                    "parent_id": None,
                    "offset": depth,
                    "ttl": None,
                    "cycle": 0,
                    "created_at_ns": 0,
                    "created_at_iso": "1970-01-01T00:00:00",
                    "creation_index": 0,
                    "children": []
                })
        
        return pact_regions
    
    def create_message_turn(self, depth: int = 0) -> 'MessageTurn':
        """
        Create MessageTurn with MessageContainer at offset 0 and add to specified depth.
        If depth is 0, shifts existing depths forward (d0 becomes d1, etc.).
        
        Args:
            depth: Depth to create at. 0 = active (default), 1+ = historical
            
        Returns:
            The created MessageTurn
        """
        from ..components.core import MessageTurn, MessageContainer
        
        # Create MessageTurn (MessageTurn.__init__ automatically creates MessageContainer at core)
        message_turn = MessageTurn(context=self._context)
        
        if depth == 0:
            # Shift all existing depths forward (d0 becomes d1, etc.)
            # Insert at index 1 (depth 0)
            self._depths.insert(1, message_turn)
            
            # Update depth attributes for all shifted components
            for i in range(2, len(self._depths)):
                comp = self._depths[i]
                comp.depth = i - 1
        else:
            # Insert at specific depth
            self.insert(depth, message_turn)
        
        # Set proper references
        assert hasattr(message_turn, '_context_ref'), f"MessageTurn {type(message_turn)} must have _context_ref attribute"
        message_turn._context_ref = self._context
        message_turn.depth = depth
            
        return message_turn