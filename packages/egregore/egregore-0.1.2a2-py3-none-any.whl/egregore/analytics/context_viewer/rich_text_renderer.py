"""
Rich-based TextRenderer for clean, professional context visualization.

Uses Rich library for consistent, beautiful formatting.
"""

from typing import Optional, List
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich.rule import Rule
from rich.tree import Tree
from rich.syntax import Syntax
import io

from egregore.core.context_management import Context
from egregore.core.context_management.pact.components.core import PACTCore as PACTCore


class RichTextRenderer:
    """Handles text content visualization using Rich library"""
    
    def __init__(self, width: Optional[int] = None):
        """Initialize RichTextRenderer
        
        Args:
            width: Console width (auto-detect if None)
        """
        self.console = Console(width=width, file=io.StringIO())
    
    def render_with_delimiters(
        self, 
        context: Context, 
        mode: str = "full", 
        include_metadata: bool = True
    ) -> str:
        """Render context with Rich-based visual delimiters
        
        Args:
            context: Context to render
            mode: "full" (with panels) or "simple" (basic format)
            include_metadata: Include TTL and positioning metadata
        
        Returns:
            Formatted text with Rich components
        """
        # Clear console buffer
        self.console.file = io.StringIO()
        
        if mode == "simple":
            return self._render_simple(context, include_metadata)
        else:
            return self._render_full(context, include_metadata)
    
    def _render_full(self, context: Context, include_metadata: bool) -> str:
        """Render full format with Rich panels and formatting"""
        
        # Access components through DepthArray structure
        components_to_render = []
        
        # System header (depth -1)
        if hasattr(context, '_depths') and hasattr(context._depths, 'system_header'):
            system_header = context._depths.system_header
            if system_header:
                components_to_render.append(('system', system_header))
        
        # Active message (depth 0)  
        if hasattr(context, '_depths') and hasattr(context._depths, 'active_message'):
            active_message = context._depths.active_message
            if active_message:
                components_to_render.append(('active', active_message))
        
        # Historical messages (depths 1+)
        if hasattr(context, '_depths') and hasattr(context._depths, '_conversation_segments'):
            for depth in range(1, len(context._depths._conversation_segments) + 1):
                try:
                    segment = context._depths[depth]
                    if segment:
                        components_to_render.append(('history', segment))
                except (KeyError, IndexError):
                    continue
        
        # Render each component based on its type
        for i, (section_type, component) in enumerate(components_to_render):
            if section_type == 'system':
                self._render_system_section(component, include_metadata)
            elif section_type == 'history':
                self._render_conversation_history(component, include_metadata)
            elif section_type == 'active':
                self._render_active_message(component, include_metadata)
            else:
                self._render_generic_component(component, include_metadata)
            
            # Add spacing between sections
            if i < len(components_to_render) - 1:
                self.console.print()
        
        return self.console.file.getvalue()
    
    def _render_simple(self, context: Context, include_metadata: bool) -> str:
        """Render simple format with minimal Rich styling"""
        if hasattr(context, 'content') and context.content:
            for component in context.content:
                content_text = self._extract_component_content(component)
                if content_text:
                    if include_metadata:
                        metadata = self._get_component_metadata(component)
                        self.console.print(f"[dim]\\[{metadata}][/dim] {content_text}")
                    else:
                        self.console.print(content_text)
        
        return self.console.file.getvalue()
    
    def _render_system_section(self, component: PACTCore, include_metadata: bool) -> None:
        """Render system header section with Rich panels"""
        # System section title
        self.console.print(Rule("[bold blue]SYSTEM SECTION[/bold blue]", style="blue"))
        
        # Render the SystemHeader as a container (if it has children) or its children directly
        if hasattr(component, 'content') and component.content:
            # Convert CoreOffsetArray to list
            content_items = self._extract_content_items(component.content)
            if len(content_items) > 1:
                # Multiple children - show the container structure
                self._render_container_with_nested_panels(component, include_metadata, "blue")
            elif len(content_items) == 1:
                # Single child - render directly for cleaner display
                self._render_component_panel(content_items[0], include_metadata, "blue")
        else:
            # Empty system section
            panel = Panel(
                "[dim]No system components[/dim]",
                title="System",
                border_style="blue"
            )
            self.console.print(panel)
    
    def _render_conversation_history(self, component: PACTCore, include_metadata: bool) -> None:
        """Render conversation history section"""
        self.console.print(Rule("[bold green]CONVERSATION HISTORY[/bold green]", style="green"))
        
        if hasattr(component, 'content') and component.content:
            if len(component.content) > 1:
                # Multiple children - show the container structure
                self._render_container_with_nested_panels(component, include_metadata, "green")
            else:
                # Single child - render directly for cleaner display
                for child in component.content:
                    # Check if this is actually a MessageContainer or a leaf component
                    if 'messagecontainer' in child.__class__.__name__.lower():
                        self._render_message_container(child, include_metadata, "green")
                    else:
                        # This is a leaf component like TextPACTCore
                        self._render_component_panel(child, include_metadata, "green")
        else:
            # Empty conversation history
            panel = Panel(
                "[dim]No conversation history[/dim]",
                title="History",
                border_style="green"
            )
            self.console.print(panel)
    
    def _render_active_message(self, component: PACTCore, include_metadata: bool) -> None:
        """Render active message section"""
        self.console.print(Rule("[bold yellow]ACTIVE MESSAGE[/bold yellow]", style="yellow"))
        
        # Render components in active message
        if hasattr(component, 'content') and component.content:
            content_items = self._extract_content_items(component.content)
            for child in content_items:
                if 'messagecontainer' in child.__class__.__name__.lower():
                    self._render_message_container(child, include_metadata, "yellow")
                else:
                    self._render_component_panel(child, include_metadata, "yellow")
        else:
            # Empty active message
            panel = Panel(
                "[dim]No active message content[/dim]",
                title="Active",
                border_style="yellow"
            )
            self.console.print(panel)
    
    def _render_message_container(self, component: PACTCore, include_metadata: bool, border_color: str) -> None:
        """Render a message container with Rich panel"""
        # Use the shared container rendering logic
        self._render_container_with_nested_panels(component, include_metadata, border_color)
    
    def _render_component_panel(
        self, 
        component: PACTCore, 
        include_metadata: bool, 
        border_color: str = "white"
    ) -> None:
        """Render a component as a Rich panel with nested containers"""
        # Check if this is a container component (has child components)
        if hasattr(component, 'content') and isinstance(component.content, list) and component.content:
            # This is a container - render with nested panels
            self._render_container_with_nested_panels(component, include_metadata, border_color)
        else:
            # This is a leaf component - render as simple panel
            self._render_leaf_component_panel(component, include_metadata, border_color)
    
    def _render_container_with_nested_panels(
        self,
        component: PACTCore,
        include_metadata: bool,
        border_color: str
    ) -> None:
        """Render a container component with nested child panels"""
        # Component title with position information
        component_type = component.__class__.__name__
        component_id = getattr(component, 'id', 'unknown')
        
        # Get position from coordinates (more accurate than offset)
        position_info = self._get_position_info(component)
        
        # Build title with position
        if position_info:
            title_base = f"{component_type} [{component_id}] {position_info}"
        else:
            title_base = f"{component_type} [{component_id}]"
        
        if include_metadata:
            metadata = self._get_component_metadata(component)
            title = f"{title_base} ({metadata})"
        else:
            title = title_base
        
        # Create nested panels for each child component
        from rich.console import Group
        
        child_panels = []
        content_items = self._extract_content_items(component.content)
        for child in content_items:
            # Create a panel for each child component
            child_content = self._extract_component_content(child)
            if child_content:
                # Build child title with position
                child_position_info = self._get_position_info(child)
                if child_position_info:
                    child_title_base = f"{child.__class__.__name__} [{getattr(child, 'id', 'unknown')}] {child_position_info}"
                else:
                    child_title_base = f"{child.__class__.__name__} [{getattr(child, 'id', 'unknown')}]"
                
                if include_metadata:
                    metadata = self._get_component_metadata(child)
                    child_title = f"{child_title_base} ({metadata})"
                else:
                    child_title = child_title_base
                
                # Apply syntax highlighting if it looks like code
                if self._looks_like_code(child_content):
                    try:
                        child_content = Syntax(child_content, "python", theme="monokai", line_numbers=True)
                    except:
                        pass
                
                # Create a smaller nested panel for the child
                child_panel = Panel(
                    child_content,
                    title=child_title,
                    border_style="dim " + border_color,
                    padding=(0, 1)
                )
                child_panels.append(child_panel)
        
        if child_panels:
            # Group all child panels together
            content_group = Group(*child_panels)
            panel_content = content_group
        else:
            panel_content = "[dim]Empty container[/dim]"
        
        # Create the main container panel
        panel = Panel(
            panel_content,
            title=title,
            border_style=border_color,
            padding=(1, 1)
        )
        self.console.print(panel)
    
    def _render_leaf_component_panel(
        self,
        component: PACTCore,
        include_metadata: bool,
        border_color: str
    ) -> None:
        """Render a leaf component as a simple panel"""
        # Component title with position information
        component_type = component.__class__.__name__
        component_id = getattr(component, 'id', 'unknown')
        
        # Get position from coordinates (more accurate than offset)
        position_info = self._get_position_info(component)
        
        # Build title with position
        if position_info:
            title_base = f"{component_type} [{component_id}] {position_info}"
        else:
            title_base = f"{component_type} [{component_id}]"
        
        if include_metadata:
            metadata = self._get_component_metadata(component)
            title = f"{title_base} ({metadata})"
        else:
            title = title_base
        
        # Component content
        content_text = self._extract_component_content(component)
        
        if not content_text:
            content_text = "[dim]No content[/dim]"
        elif self._looks_like_code(content_text):
            # Syntax highlight code
            try:
                content_text = Syntax(content_text, "python", theme="monokai", line_numbers=True)
            except:
                # Fallback if syntax highlighting fails
                pass
        
        # Create panel
        panel = Panel(
            content_text,
            title=title,
            border_style=border_color,
            padding=(1, 2)
        )
        self.console.print(panel)
    
    def _render_generic_component(self, component: PACTCore, include_metadata: bool) -> None:
        """Render a generic component"""
        self._render_component_panel(component, include_metadata, "white")
    
    def _extract_component_content(self, component: PACTCore) -> Optional[str]:
        """Extract text content from a component"""
        # Try different content attributes
        if hasattr(component, 'text') and component.text:
            return component.text
        elif hasattr(component, 'content') and isinstance(component.content, str):
            return component.content
        elif hasattr(component, 'content') and component.content:
            # If content is a container, try to extract text from children
            content_items = self._extract_content_items(component.content)
            if content_items:
                texts = []
                for child in content_items:
                    child_text = self._extract_component_content(child)
                    if child_text:
                        texts.append(child_text)
                return '\\n'.join(texts) if texts else None
        
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
    
    def _get_position_info(self, component: PACTCore) -> str:
        """Get position information from component coordinates"""
        if hasattr(component, 'metadata') and hasattr(component.metadata, 'coordinates'):
            coords = component.metadata.coordinates
            if hasattr(coords, 'coords') and coords.coords:
                # Show the full coordinate path
                coord_str = ','.join(map(str, coords.coords))
                return f"({coord_str})"
        
        # Fallback to offset if coordinates not available
        offset = getattr(component, 'offset', None)
        if offset is not None:
            return f"{offset}"
        
        return ""
    
    def _extract_content_items(self, content):
        """Extract items from CoreOffsetArray or other content structures"""
        if content is None:
            return []
        
        # Handle CoreOffsetArray (has __iter__ and __getitem__)
        if hasattr(content, '__iter__') and hasattr(content, '__getitem__'):
            try:
                items = []
                for offset in content:  # This gives us the indices
                    items.append(content[offset])
                return items
            except:
                pass
        
        # Handle regular list
        if isinstance(content, list):
            return content
        
        # Single item (string content)
        return [content] if content else []
    
    def _looks_like_code(self, text: str) -> bool:
        """Heuristic to detect if text looks like code"""
        code_indicators = [
            'def ', 'class ', 'import ', 'from ',  # Python
            'function ', 'var ', 'const ', 'let ',  # JavaScript
            '{}', '[]', '()', '=>', '->', '::',  # Common programming symbols
            '    '  # Indentation suggests code
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in code_indicators)