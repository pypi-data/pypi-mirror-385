"""
Main ContextViewer class for PACT context tree inspection and analysis.

Provides comprehensive visualization and debugging capabilities for context structures.
"""

from typing import Optional, TYPE_CHECKING
from egregore.core.context_management import Context
from egregore.core.context_management.pact.components.core import (
    PactRoot,
    SystemHeader,
    MessageTurn,
    TextContent,
)

# Lazy imports for renderers to avoid circular dependencies
if TYPE_CHECKING:
    from .tree_renderer import TreeRenderer
    from .text_renderer import TextRenderer
    from .rich_text_renderer import RichTextRenderer
    from .xml_renderer import XMLRenderer
    from .provider_renderer import ProviderRenderer


class ContextViewer:
    """Main interface for context tree inspection and analysis"""
    
    def __init__(self, context: Optional[Context] = None):
        """Initialize ContextViewer with optional context
        
        Args:
            context: Context instance to view. If None, creates empty context.
        """
        self.context = context or Context()
        
        # Lazy initialization of renderers
        self._tree_renderer = None
        self._text_renderer = None
        self._rich_text_renderer = None
        self._xml_renderer = None
        self._provider_renderer = None
    
    @property
    def tree_renderer(self) -> 'TreeRenderer':
        """Lazy-load TreeRenderer"""
        if self._tree_renderer is None:
            from .tree_renderer import TreeRenderer
            self._tree_renderer = TreeRenderer()
        return self._tree_renderer
    
    @property
    def text_renderer(self) -> 'TextRenderer':
        """Lazy-load TextRenderer"""
        if self._text_renderer is None:
            from .text_renderer import TextRenderer
            self._text_renderer = TextRenderer()
        return self._text_renderer
    
    @property
    def rich_text_renderer(self) -> 'RichTextRenderer':
        """Lazy-load RichTextRenderer"""
        if self._rich_text_renderer is None:
            from .rich_text_renderer import RichTextRenderer
            self._rich_text_renderer = RichTextRenderer()
        return self._rich_text_renderer
    
    @property
    def xml_renderer(self) -> 'XMLRenderer':
        """Lazy-load XMLRenderer"""
        if self._xml_renderer is None:
            from .xml_renderer import XMLRenderer
            self._xml_renderer = XMLRenderer()
        return self._xml_renderer
    
    @property
    def provider_renderer(self) -> 'ProviderRenderer':
        """Lazy-load ProviderRenderer"""
        if self._provider_renderer is None:
            from .provider_renderer import ProviderRenderer
            self._provider_renderer = ProviderRenderer()
        return self._provider_renderer
    
    @classmethod
    def create_empty(cls) -> 'ContextViewer':
        """Create a ContextViewer with an empty context for testing"""
        return cls(Context())
    
    @classmethod
    def from_agent(cls, agent) -> 'ContextViewer':
        """Create a ContextViewer from an existing agent's context
        
        Args:
            agent: Agent instance with context attribute
        """
        return cls(agent.context)
    
    def view_tree(self, show_metadata: bool = True) -> str:
        """Display tree structure with component hierarchy
        
        Args:
            show_metadata: Include component metadata (TTL, positioning, etc.)
        
        Returns:
            Formatted tree structure as string
        
        Wiring: Uses context.root to traverse PactRoot hierarchy
        """
        return self.tree_renderer.render_tree(self.context, show_metadata)
    
    def view_text(self, mode: str = "full", include_metadata: bool = True, use_rich: bool = True) -> str:
        """Show rendered text content with configurable component rendering
        
        Args:
            mode: "full" (with component delimiters), "simple" (basic components), 
                  "provider" (exact format sent to provider - no delimiters)
            include_metadata: Show TTL, positioning, and component metadata
            use_rich: Use Rich library for beautiful formatting (default: True)
        
        Returns:
            Formatted text content as string
            
        Wiring: 
        - "provider" mode: Uses context.render() directly
        - Other modes: Rich or legacy rendering with component delimiters
        """
        if mode == "provider":
            # Use MessageScheduler to render exact provider format
            try:
                from egregore.core.agent.message_scheduler import MessageScheduler
                scheduler = MessageScheduler(self.context)
                provider_thread = scheduler.render()
                
                # Format the ProviderThread for display
                formatted_messages = []
                for msg in provider_thread.messages:
                    msg_type = getattr(msg, 'message_type', 'unknown')
                    content = getattr(msg, 'content', [])
                    
                    # Extract text from content list
                    if isinstance(content, list):
                        text_parts = []
                        for item in content:
                            if hasattr(item, 'content'):
                                text_parts.append(item.content)
                            else:
                                text_parts.append(str(item))
                        content_text = "\n".join(text_parts)
                    else:
                        content_text = str(content)
                    
                    formatted_messages.append(f"**{msg_type.upper().replace('_', ' ')}**:\n{content_text}")
                
                return "\n\n".join(formatted_messages)
            except Exception as e:
                # Fallback to context render if MessageScheduler fails
                return f"Error rendering provider format: {str(e)}\n\nFallback:\n{self.context.render()}"
        elif use_rich:
            # Use Rich for beautiful formatting
            return self.rich_text_renderer.render_with_delimiters(
                self.context, mode, include_metadata
            )
        else:
            # Legacy text renderer
            return self.text_renderer.render_with_delimiters(
                self.context, mode, include_metadata
            )
    
    def view_xml(self, validate: bool = True) -> str:
        """Display PACT-compliant XML structure
        
        Args:
            validate: Perform PACT specification validation
        
        Returns:
            Formatted XML structure as string
        
        Wiring: Uses context.model_dump() for PACT v0.1 compliant output
        """
        pact_data = self.context.model_dump()
        return self.xml_renderer.render_xml(pact_data, validate)
    
    def view_provider(self, provider_type: str, model: str, **kwargs):
        """Show provider-specific rendering with token counts
        
        Args:
            provider_type: Provider type (e.g., "openai", "anthropic")
            model: Model name (e.g., "gpt-4", "claude-3")
            **kwargs: Additional provider-specific options
        
        Returns:
            ProviderPreview object with formatted content and metadata
        
        Wiring: Uses context.render() + provider-specific formatting
        """
        return self.provider_renderer.render_provider_preview(
            self.context, provider_type, model, **kwargs
        )