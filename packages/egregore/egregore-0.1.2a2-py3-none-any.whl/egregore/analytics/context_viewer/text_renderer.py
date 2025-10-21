"""
TextRenderer for raw text output with visual delimiters.

Provides formatted text rendering with component boundaries and metadata display.
"""

from typing import Optional, List, Any
from egregore.core.context_management import Context
from egregore.core.context_management.pact.components.core import PACTCore as PACTCore


class TextRenderer:
    """Handles text content visualization with component delimiters"""
    
    # Visual delimiter characters for different component types
    DELIMITERS = {
        'system_header': {
            'top': '╔═══',
            'bottom': '╚═══',
            'side': '║',
            'fill': '═',
            'title': 'SYSTEM SECTION'
        },
        'conversation_history': {
            'top': '═══',
            'bottom': '═══',
            'side': '',
            'fill': '═',
            'title': 'CONVERSATION HISTORY'
        },
        'message_container': {
            'top': '╔═══',
            'bottom': '╚═══',
            'side': '║',
            'fill': '═',
        },
        'active_message': {
            'top': '═══',
            'bottom': '═══',
            'side': '',
            'fill': '═',
            'title': 'ACTIVE MESSAGE'
        },
        'component': {
            'top': '┌─',
            'bottom': '└─',
            'side': '│',
            'fill': '─',
        }
    }
    
    def __init__(self):
        """Initialize TextRenderer"""
        pass
    
    def render_with_delimiters(
        self, 
        context: Context, 
        mode: str = "full", 
        include_metadata: bool = True
    ) -> str:
        """Render context with visual component delimiters
        
        Args:
            context: Context to render
            mode: "full" (with delimiters) or "simple" (basic format)
            include_metadata: Include TTL and positioning metadata
        
        Returns:
            Formatted text with component boundaries
        """
        if mode == "simple":
            return self._render_simple(context, include_metadata)
        else:
            return self._render_full(context, include_metadata)
    
    def _render_full(self, context: Context, include_metadata: bool) -> str:
        """Render full format with all visual delimiters"""
        lines = []
        
        # Calculate consistent viewport width for all components
        viewport_width = self._calculate_viewport_width(context, include_metadata)
        
        # Render each major section
        if hasattr(context, 'content') and context.content:
            for component in context.content:
                component_type = component.__class__.__name__.lower()
                
                if 'systemheader' in component_type:
                    lines.extend(self._render_system_section(component, include_metadata, viewport_width))
                elif 'conversationsegements' in component_type or 'history' in component_type:
                    lines.extend(self._render_conversation_history(component, include_metadata, viewport_width))
                elif 'activemessage' in component_type:
                    lines.extend(self._render_active_message(component, include_metadata, viewport_width))
                else:
                    lines.extend(self._render_generic_component(component, include_metadata, viewport_width))
                
                lines.append('')  # Add spacing between sections
        
        return '\n'.join(lines).strip()
    
    def _render_simple(self, context: Context, include_metadata: bool) -> str:
        """Render simple format with minimal delimiters"""
        lines = []
        
        if hasattr(context, 'content') and context.content:
            for component in context.content:
                content_text = self._extract_component_content(component)
                if content_text:
                    if include_metadata:
                        metadata = self._get_component_metadata(component)
                        lines.append(f"[{metadata}] {content_text}")
                    else:
                        lines.append(content_text)
        
        return '\n'.join(lines)
    
    def _calculate_viewport_width(self, context: Context, include_metadata: bool) -> int:
        """Calculate consistent viewport width for all components"""
        max_width = 60  # Minimum width
        
        # Scan all components to find the maximum content width needed
        if hasattr(context, 'content') and context.content:
            for component in context.content:
                max_width = max(max_width, self._calculate_component_width(component, include_metadata))
        
        return min(max_width, 120)  # Cap at reasonable terminal width
    
    def _calculate_component_width(self, component: PACTCore, include_metadata: bool) -> int:
        """Calculate width needed for a single component"""
        # Component title width
        component_type = component.__class__.__name__
        component_id = getattr(component, 'id', 'unknown')
        title = f"{component_type} [{component_id}]"
        
        if include_metadata:
            metadata = self._get_component_metadata(component)
            title += f" ({metadata})"
        
        title_width = len(title) + 10  # Add padding
        
        # Content width
        content_width = 0
        content_text = self._extract_component_content(component)
        if content_text:
            content_lines = content_text.split('\n')
            content_width = max(len(line) for line in content_lines) + 10  # Add padding
        
        # Check child components recursively
        child_width = 0
        if hasattr(component, 'content') and isinstance(component.content, list):
            for child in component.content:
                child_width = max(child_width, self._calculate_component_width(child, include_metadata))
        
        return max(title_width, content_width, child_width)
    
    def _render_system_section(self, component: PACTCore, include_metadata: bool, viewport_width: int = None) -> List[str]:
        """Render system header section with delimiters"""
        if viewport_width is None:
            viewport_width = 80
            
        lines = []
        delim = self.DELIMITERS['system_header']
        
        # Top border with consistent width
        title_line = f"{delim['top']} {delim['title']} "
        remaining = viewport_width - len(title_line) - 1
        lines.append(title_line + delim['fill'] * remaining + delim['top'][::-1])
        
        # Content
        if hasattr(component, 'content') and component.content:
            for child in component.content:
                child_lines = self._render_component_with_box(child, include_metadata, "", viewport_width)
                lines.extend(child_lines)
        
        # Bottom border with consistent width
        lines.append(delim['bottom'] + delim['fill'] * (viewport_width - 2) + delim['bottom'][::-1])
        
        return lines
    
    def _render_conversation_history(self, component: PACTCore, include_metadata: bool, viewport_width: int = None) -> List[str]:
        """Render conversation history section"""
        if viewport_width is None:
            viewport_width = 80
            
        lines = []
        delim = self.DELIMITERS['conversation_history']
        
        title_line = f"{delim['top']} {delim['title']} "
        remaining = viewport_width - len(title_line)
        lines.append(title_line + delim['fill'] * remaining)
        
        if hasattr(component, 'content') and component.content:
            for child in component.content:
                # Check if this is actually a MessageContainer or a leaf component
                if 'messagecontainer' in child.__class__.__name__.lower():
                    lines.extend(self._render_message_container(child, include_metadata, viewport_width))
                else:
                    # This is a leaf component like TextPACTCore
                    lines.extend(self._render_component_with_box(child, include_metadata, "", viewport_width))
                lines.append('')  # Spacing between messages
        
        return lines
    
    def _render_active_message(self, component: PACTCore, include_metadata: bool, viewport_width: int = None) -> List[str]:
        """Render active message section"""
        if viewport_width is None:
            viewport_width = 80
            
        lines = []
        delim = self.DELIMITERS['active_message']
        
        title_line = f"{delim['top']} {delim['title']} "
        remaining = viewport_width - len(title_line)
        lines.append(title_line + delim['fill'] * remaining)
        
        # Render components around the message container
        if hasattr(component, 'content') and component.content:
            for child in component.content:
                if 'messagecontainer' in child.__class__.__name__.lower():
                    lines.extend(self._render_message_container(child, include_metadata, viewport_width))
                else:
                    lines.extend(self._render_component_with_box(child, include_metadata, "", viewport_width))
        
        return lines
    
    def _render_message_container(self, component: PACTCore, include_metadata: bool, viewport_width: int = None) -> List[str]:
        """Render a message container with delimiters"""
        if viewport_width is None:
            viewport_width = 80
            
        lines = []
        delim = self.DELIMITERS['message_container']
        
        # Get component ID for title
        component_id = getattr(component, 'id', 'unknown')
        title = f"MessageContainer [{component_id}]"
        
        # Top border with consistent width
        title_line = f"{delim['top']} {title} "
        remaining = viewport_width - len(title_line) - 1
        lines.append(title_line + delim['fill'] * remaining + delim['top'][::-1])
        
        # Child components (containers should only render their children, not direct content)
        if hasattr(component, 'content') and component.content:
            for child in component.content:
                child_lines = self._render_component_with_box(child, include_metadata, "  ", viewport_width - 4)
                for child_line in child_lines:
                    # Wrap child lines within container
                    container_line = f"{delim['side']} {child_line}"
                    padding_needed = viewport_width - len(container_line) - 1
                    lines.append(container_line + " " * max(0, padding_needed) + delim['side'])
        
        # Bottom border with consistent width
        lines.append(delim['bottom'] + delim['fill'] * (viewport_width - 2) + delim['bottom'][::-1])
        
        return lines
    
    def _render_component_with_box(
        self, 
        component: PACTCore, 
        include_metadata: bool, 
        indent: str = "",
        viewport_width: int = None
    ) -> List[str]:
        """Render a component with a box delimiter"""
        if viewport_width is None:
            viewport_width = 80
            
        lines = []
        delim = self.DELIMITERS['component']
        
        # Component title
        component_type = component.__class__.__name__
        component_id = getattr(component, 'id', 'unknown')
        
        title = f"{component_type} [{component_id}]"
        if include_metadata:
            metadata = self._get_component_metadata(component)
            title += f" ({metadata})"
        
        # Calculate available width for this component
        available_width = viewport_width - len(indent)
        
        # Top border with consistent width
        title_line = f"{indent}{delim['top']} {title} "
        remaining = available_width - len(title_line) + len(indent) - 1
        lines.append(title_line + delim['fill'] * max(0, remaining) + "┐")
        
        # Content
        content_text = self._extract_component_content(component)
        if content_text:
            content_lines = content_text.split('\n')
            for line in content_lines:
                # Ensure content fits within available width
                max_content_width = available_width - 4  # Account for borders and padding
                if len(line) > max_content_width:
                    line = line[:max_content_width - 3] + "..."
                
                content_line = f"{indent}{delim['side']} {line}"
                padding_needed = available_width - len(content_line) + len(indent) - 1
                lines.append(content_line + " " * max(0, padding_needed) + delim['side'])
        
        # Bottom border with consistent width
        lines.append(f"{indent}{delim['bottom']}{delim['fill'] * (available_width - len(indent) - 2)}┘")
        
        return lines
    
    def _render_generic_component(self, component: PACTCore, include_metadata: bool, viewport_width: int = None) -> List[str]:
        """Render a generic component"""
        return self._render_component_with_box(component, include_metadata, "", viewport_width)
    
    def _extract_component_content(self, component: PACTCore) -> Optional[str]:
        """Extract text content from a component"""
        # Try different content attributes
        if hasattr(component, 'text') and component.text:
            return component.text
        elif hasattr(component, 'content') and isinstance(component.content, str):
            return component.content
        elif hasattr(component, 'content') and component.content:
            # If content is a list, try to extract text from children
            if isinstance(component.content, list):
                texts = []
                for child in component.content:
                    child_text = self._extract_component_content(child)
                    if child_text:
                        texts.append(child_text)
                return '\n'.join(texts) if texts else None
        
        return None
    
    def _get_component_metadata(self, component: PACTCore) -> str:
        """Get component metadata string"""
        metadata_parts = []
        
        # TTL information
        if hasattr(component, 'ttl'):
            if component.ttl is None:
                metadata_parts.append("ttl: permanent")
            else:
                metadata_parts.append(f"ttl: {component.ttl}")
        
        # Relative offset
        if hasattr(component, 'relative_offset') and component.relative_offset is not None:
            metadata_parts.append(f"offset: {component.relative_offset}")
        
        return ", ".join(metadata_parts) if metadata_parts else "no metadata"