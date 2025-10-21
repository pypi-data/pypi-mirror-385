"""
TreeRenderer for hierarchical context tree visualization.

Provides tree structure display with proper indentation and component metadata.
"""

from typing import Optional, List, Any, Union
from egregore.core.context_management import (
    Context,
    PactRoot,
    SystemHeader,
    MessageTurn,
    PACTCore,
)


class TreeRenderer:
    """Handles tree structure visualization with proper indentation"""
    
    # Tree formatting characters
    TREE_CHARS = {
        'branch': '├── ',
        'last_branch': '└── ',
        'vertical': '│   ',
        'space': '    '
    }
    
    def __init__(self):
        """Initialize TreeRenderer"""
        pass
    
    def render_tree(self, context: Context, show_metadata: bool = True) -> str:
        """Render complete tree structure with proper hierarchy
        
        Args:
            context: Context instance to render
            show_metadata: Include component metadata (TTL, positioning, etc.)
        
        Returns:
            Formatted tree structure as string
        """
        lines = []
        
        # Start with root component
        lines.append(self._render_component(context, 0, True, [], show_metadata))
        
        # Build proper hierarchy by traversing depths and positions
        self._render_context_hierarchy(context, lines, show_metadata)
        
        return '\n'.join(lines)
    
    def _render_context_hierarchy(self, context: Context, lines: List[str], show_metadata: bool):
        """Render the actual hierarchical structure of the context"""
        # Get all depths in the context
        depths = []
        try:
            # Access depths directly from the DepthArray
            for depth in range(-1, 10):  # Check common depth range
                if depth in context.content:
                    depths.append(depth)
        except:
            pass
        
        for i, depth in enumerate(depths):
            is_last_depth = (i == len(depths) - 1)
            depth_component = context.content[depth]
            
            # Render the depth component (SystemHeader, MessageTurn)
            prefix = self.TREE_CHARS['last_branch'] if is_last_depth else self.TREE_CHARS['branch']
            depth_line = f"{prefix}{type(depth_component).__name__} [depth: {depth}, id: {depth_component.id}]"
            if show_metadata:
                depth_line += f" ttl: {getattr(depth_component, 'ttl', 'N/A')}"
            lines.append(depth_line)
            
            # Render positions within this depth
            if hasattr(depth_component, 'content') and hasattr(depth_component.content, 'get_offsets'):
                positions = depth_component.content.get_offsets()
                for j, pos in enumerate(positions):
                    is_last_pos = (j == len(positions) - 1)
                    depth_prefix = self.TREE_CHARS['space'] if is_last_depth else self.TREE_CHARS['vertical']
                    pos_prefix = self.TREE_CHARS['last_branch'] if is_last_pos else self.TREE_CHARS['branch']
                    
                    pos_component = depth_component.content[pos]

                    # Add content preview for leaf nodes (TextContent, etc.)
                    content_preview = ""
                    if hasattr(pos_component, 'content') and isinstance(getattr(pos_component, 'content', None), str):
                        content_text = str(pos_component.content)[:50]
                        if content_text:
                            content_preview = f' "{content_text}"'

                    pos_line = f"{depth_prefix}{pos_prefix}Position {pos}: {type(pos_component).__name__}{content_preview} [id: {pos_component.id}]"
                    if show_metadata:
                        pos_line += f" ttl: {getattr(pos_component, 'ttl', 'N/A')}"
                    lines.append(pos_line)
                    
                    # Render offsets within MessageContainers
                    if hasattr(pos_component, 'content') and hasattr(pos_component.content, 'get_offsets'):
                        offsets = pos_component.content.get_offsets()
                        for k, offset in enumerate(offsets):
                            is_last_offset = (k == len(offsets) - 1)
                            pos_space = self.TREE_CHARS['space'] if is_last_pos else self.TREE_CHARS['vertical']
                            depth_space = self.TREE_CHARS['space'] if is_last_depth else self.TREE_CHARS['vertical']
                            offset_prefix = self.TREE_CHARS['last_branch'] if is_last_offset else self.TREE_CHARS['branch']
                            
                            offset_component = pos_component.content[offset]
                            content_preview = str(getattr(offset_component, 'content', ''))[:30]
                            if content_preview:
                                content_preview = f' "{content_preview}"'
                            
                            offset_line = f"{depth_space}{pos_space}{offset_prefix}Offset {offset}: {type(offset_component).__name__}{content_preview}"
                            if show_metadata:
                                offset_line += f" [id: {offset_component.id}]"
                            lines.append(offset_line)
    
    def _render_component(
        self, 
        component: Union[Context, PACTCore], 
        depth: int, 
        is_last: bool, 
        prefix_stack: List[bool], 
        show_metadata: bool
    ) -> str:
        """Render individual component with tree formatting
        
        Args:
            component: Component to render
            depth: Current nesting depth
            is_last: Whether this is the last child at this level
            prefix_stack: Stack of prefix states for parent levels
            show_metadata: Include metadata in output
        
        Returns:
            Formatted component line
            
        Wiring: Uses component properties:
        - component.id: Component identifier
        - component.ttl: Lifecycle information
        - component.relative_offset: Positioning
        - component.__class__.__name__: Component type
        """
        # Build prefix from stack
        prefix = ''
        for is_last_at_level in prefix_stack:
            if is_last_at_level:
                prefix += self.TREE_CHARS['space']
            else:
                prefix += self.TREE_CHARS['vertical']
        
        # Add branch character
        if depth > 0:
            if is_last:
                prefix += self.TREE_CHARS['last_branch']
            else:
                prefix += self.TREE_CHARS['branch']
        
        # Component name and type
        component_type = component.__class__.__name__
        component_info = f"{component_type}"
        
        # Add positioning context for special components (always shown)
        if isinstance(component, Context):
            component_info += " (position: ROOT)"
        elif isinstance(component, SystemHeader):
            component_info += " (position: SYSTEM)"
        elif isinstance(component, MessageTurn):
            component_info += " (position: ACTIVE)"
        elif isinstance(component, MessageTurn):
            component_info += " (position: TURN)"
        
        # Add metadata if requested
        if show_metadata:
            metadata_parts = []
            
            # Component ID
            if hasattr(component, 'id') and component.id:
                metadata_parts.append(f"id: {component.id}")
            
            # TTL information
            if hasattr(component, 'ttl'):
                if component.ttl is None:
                    metadata_parts.append("ttl: permanent")
                else:
                    metadata_parts.append(f"ttl: {component.ttl}")
            
            # Relative offset
            if hasattr(component, 'relative_offset') and getattr(component, 'relative_offset', None) is not None:
                metadata_parts.append(f"offset: {getattr(component, 'relative_offset')}")
            
            # Position information for special components (exclude ContextPosition.SEQUENCE)
            if hasattr(component, 'position') and getattr(component, 'position', None):
                position_val = getattr(component, 'position')
                if str(position_val) != "ContextPosition.SEQUENCE":
                    metadata_parts.append(f"position: {position_val}")
            
            if metadata_parts:
                component_info += f" [{', '.join(metadata_parts)}]"
        
        return f"{prefix}{component_info}"
    
    def _render_children(
        self, 
        children: List[PACTCore], 
        lines: List[str], 
        prefix_stack: List[bool], 
        show_metadata: bool
    ) -> None:
        """Render child components recursively
        
        Args:
            children: List of child components
            lines: Output lines to append to
            prefix_stack: Current prefix state stack
            show_metadata: Include metadata in output
        """
        if not children:
            return
        
        # Filter children by TTL expiry status
        visible_children = []
        for child in children:
            if hasattr(child, '_is_expired'):
                if not child._is_expired():
                    visible_children.append(child)
            elif hasattr(child, 'ttl') and child.ttl is not None:
                # Check if TTL-based component has expired
                # For now, assume visible (proper TTL checking would need cycle info)
                visible_children.append(child)
            else:
                # If no TTL info, assume visible
                visible_children.append(child)
        
        for i, child in enumerate(visible_children):
            is_last = i == len(visible_children) - 1
            
            # Render this child
            child_line = self._render_component(
                child, 
                len(prefix_stack) + 1, 
                is_last, 
                prefix_stack, 
                show_metadata
            )
            lines.append(child_line)
            
            # Render grandchildren if any - handle CoreOffsetArray properly
            if hasattr(child, 'content') and child.content:
                # Check if this is string content (leaf node) first
                if isinstance(child.content, str) and child.content.strip():
                    # For string content, show the actual text as a child
                    new_prefix_stack = prefix_stack + [is_last]
                    content_prefix = ''
                    for is_last_at_level in new_prefix_stack:
                        if is_last_at_level:
                            content_prefix += self.TREE_CHARS['space']
                        else:
                            content_prefix += self.TREE_CHARS['vertical']
                    content_prefix += self.TREE_CHARS['last_branch']
                    lines.append(f"{content_prefix}\"{child.content}\"")
                else:
                    # Extract items from CoreOffsetArray or other structures
                    content_items = self._extract_content_items(child.content)
                    
                    if content_items:
                        new_prefix_stack = prefix_stack + [is_last]
                        self._render_children(content_items, lines, new_prefix_stack, show_metadata)
    
    def get_component_count(self, context: Context) -> dict:
        """Get count of components by type
        
        Args:
            context: Context to analyze
        
        Returns:
            Dictionary with component type counts
        """
        counts = {}
        
        def count_recursive(component):
            component_type = component.__class__.__name__
            counts[component_type] = counts.get(component_type, 0) + 1
            
            if hasattr(component, 'content') and component.content:
                for child in component.content:
                    count_recursive(child)
        
        count_recursive(context)
        return counts
    
    def _extract_content_items(self, content):
        """Extract items from CoreOffsetArray using proper iteration"""
        if content is None:
            return []
        
        # Handle CoreOffsetArray using get_offsets method
        from egregore.core.context_management.data_structures.core_offset_array import CoreOffsetArray
        if isinstance(content, CoreOffsetArray):
            try:
                items = []
                # Use get_offsets for proper iteration order
                for offset in content.get_offsets():
                    items.append(content[offset])
                return items
            except Exception:
                return []
        
        # Handle string content (leaf nodes)
        if isinstance(content, str):
            return []
        
        # Handle regular list (legacy fallback)
        if isinstance(content, list):
            return content
        
        # No items to extract
        return []