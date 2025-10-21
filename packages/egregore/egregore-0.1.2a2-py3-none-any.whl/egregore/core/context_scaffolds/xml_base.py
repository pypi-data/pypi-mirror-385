"""
BaseXMLScaffold - XML rendering capabilities for context scaffolds.

Provides automatic XML rendering capabilities for scaffolds with improved ergonomics.
"""

from typing import Union, List, Optional, Dict, Any, TYPE_CHECKING
from pydantic import Field, PrivateAttr
from .base import BaseContextScaffold
from ..context_management.pact.components.core import XMLComponent, XMLAttributeAccessor
from ..context_management.pact.components.core import PACTCore
# RenderOptions removed - not needed in PACT
from .data_types import ScaffoldState

if TYPE_CHECKING:
    from .data_types import StateChangeSource


class XMLAccessor:
    """Declarative XML attribute accessor for self.xml.attrs interface"""
    
    def __init__(self, component: 'BaseXMLScaffold'):
        self._component = component
    
    @property
    def attrs(self) -> 'XMLAttributeAccessor':
        """Access XML attributes stored in internal XMLComponent metadata.props"""
        return XMLAttributeAccessor(self._component._xml_component.metadata.props)
    
    def update_attrs(self, **attrs) -> None:
        """Bulk update XML attributes"""
        self.attrs.update(attrs)
    
    def clear_attrs(self) -> None:
        """Clear all custom XML attributes (preserve standard ones)"""
        standard_attrs = {'tokens', 'max_tokens', 'utilization'}
        to_remove = [k for k in self._component._xml_component.metadata.props.keys() 
                    if k not in standard_attrs]
        for key in to_remove:
            del self.attrs[key]


class BaseXMLScaffold(BaseContextScaffold):
    """
    Base scaffold class with automatic XML rendering capabilities.
    
    Combines BaseContextScaffold's state management and tool generation
    with XMLComponent's automatic XML rendering and attribute handling.
    
    Key Features:
    - Multiple inheritance from BaseContextScaffold + XMLComponent
    - Declarative XML attribute management via self.xml.attrs
    - Component-based render() return values
    - Automatic token calculation and utilization tracking
    - Proper XML escaping and formatting
    """
    
    # Concrete values required by metaclass - subclasses will override
    type: str = "base_xml_scaffold"  # Must be overridden by subclasses  
    state: ScaffoldState = ScaffoldState()  # Must be overridden by subclasses
    
    # XML functionality - using private attributes to avoid validation issues
    _xml_component: Optional[XMLComponent] = PrivateAttr(default=None)
    _xml: Optional['XMLAccessor'] = PrivateAttr(default=None)
    
    def __init__(self, *, position: str = "system", scaffold_op_fmt=None, operation_ttl=None, operation_retention=None, operation_config=None, **kwargs):
        """
        Initialize BaseXMLScaffold with XML rendering capabilities.
        """
        # Create internal XMLComponent for rendering functionality FIRST
        self._xml_component = XMLComponent(type=self.type, content="[Initializing...]")
        
        # Initialize declarative XML interface
        self._xml = XMLAccessor(self)
        
        # We need to handle the BaseContextScaffold init differently
        # because it calls self.render() which should return components, not strings
        
        # Call parent init methods manually to avoid the render() call
        from .base import BaseContextScaffold
        from ..context_management.pact.components.core import PACTCore
        
        # Initialize PACTCore first
        PACTCore.__init__(self, **kwargs)
        
        # Set BaseContextScaffold attributes manually
        self.position = position  
        self.scaffold_op_fmt = scaffold_op_fmt or 'distinct'
        self.operation_ttl = operation_ttl
        self.operation_retention = operation_retention
        self.operation_config = operation_config or {}
        self.agent_state = None
        
        # Initialize state (from BaseContextScaffold._init_state)
        BaseContextScaffold._init_state(self)
        
        # Now do our XML rendering for content
        self.content = self._system_render()
    
    def on_state_change(self, old_state: Dict[str, Any], new_state: Dict[str, Any], 
                       source: 'StateChangeSource', metadata: Dict[str, Any]) -> None:
        """
        Override state change handling to mark scaffold as needing re-render.
        
        Instead of immediately re-rendering on every state change (which causes 
        infinite recursion), we mark the scaffold as dirty and defer rendering
        until it's actually needed before provider calls.
        """
        # Call parent implementation
        super().on_state_change(old_state, new_state, source, metadata)
        
        # Mark as needing re-render instead of immediate render
        self._needs_render = True
    
    def _ensure_rendered(self) -> None:
        """
        Ensure content is up-to-date by rendering if needed.
        
        Should be called before scaffold content is accessed by agents
        or before provider calls to ensure LLM sees current state.
        """
        if getattr(self, '_needs_render', True):  # Default to True for initial render
            self.content = self._system_render()
            self._needs_render = False
    
    @property
    def xml(self) -> 'XMLAccessor':
        """Access the XML interface"""
        # Ensure initialization on first access
        if not hasattr(self, '_xml') or self._xml is None:
            self._ensure_xml_init()
        return self._xml
    
    def render(self):
        """
        Override this method in subclasses to return your content.
        
        Return:
        - str: Plain text content
        - PACTCore: Single component  
        - List[PACTCore]: Multiple components
        
        Set XML attributes via: self.xml.attrs['key'] = 'value'
        
        Example:
            def render(self):
                self.xml.attrs['count'] = str(len(self.state.items))
                return self.state.items  # Return components directly!
        """
        # Default implementation - return state content
        if hasattr(self.state, 'content'):
            return getattr(self.state, 'content', '') or "[No content]"
        return str(self.state)
    
    def _system_render(self) -> str:
        """
        System method that calls user's render() and converts result to XML string.
        """
        # Call user's render() method to get components/content
        user_content = self.render()
        
        # Process it and return XML string
        return self._render_with_content(user_content)
    
    def _render_with_content(self, content: Union[str, PACTCore, List[PACTCore]]) -> str:
        """
        Helper method to render XML with given content.
        Call this from your render() override after setting attributes.
        """
        # Ensure initialization
        if not hasattr(self, '_xml_component') or self._xml_component is None:
            self._ensure_xml_init()
        
        # Process the content
        self._process_content(content)
        self._update_standard_attrs()
        
        # Use internal XMLComponent's render method for proper XML output
        return self._xml_component.render()
    
    def _process_content(self, content_result: Union[str, PACTCore, List[PACTCore]]) -> None:
        """Process content and set it on the internal XML component."""
        try:
            
            # Process different return types
            if isinstance(content_result, list):
                # List of components - check if they're XMLComponents
                xml_components = []
                text_parts = []
                
                for component in content_result:
                    try:
                        # Check if it's XMLComponent or has XMLComponent-like behavior
                        is_xml_component = (
                            isinstance(component, XMLComponent) or
                            (hasattr(component, '_wrapped') and isinstance(component._wrapped, XMLComponent))  # Change tracking proxy
                        )
                        
                        if is_xml_component:
                            # XMLComponent (or proxy) - add directly to avoid double escaping
                            xml_components.append(component)
                        elif hasattr(component, 'render'):
                            # Other component - render to text
                            # RenderOptions not needed in PACT
                            text_parts.append(component.render())
                        else:
                            # Fallback for non-component items
                            text_parts.append(str(component))
                    except Exception as e:
                        # Include error info but continue processing
                        text_parts.append(f"[Component Error: {type(component).__name__}]")
                
                # If we have XMLComponents, use them directly
                if xml_components and not text_parts:
                    # Pure XMLComponent list - set as content list for no escaping
                    self._xml_component.content = xml_components
                elif xml_components and text_parts:
                    # Mixed content - we need to merge (complex case)
                    # For now, render XMLComponents to text and join
                    # RenderOptions not needed in PACT
                    all_parts = []
                    for comp in xml_components:
                        all_parts.append(comp.render())
                    all_parts.extend(text_parts)
                    self._xml_component.content = '\n'.join(all_parts)
                else:
                    # Pure text parts
                    self._xml_component.content = '\n'.join(text_parts) if text_parts else "[No content]"
                
            elif hasattr(content_result, 'render'):
                # Single component - render it
                # RenderOptions not needed in PACT
                rendered_content = content_result.render()
                # If the component is an XMLComponent, treat as raw XML content
                if isinstance(content_result, XMLComponent):
                    # For XMLComponents, set as list so XMLComponent doesn't escape it
                    self._xml_component.content = [content_result]
                else:
                    self._xml_component.content = rendered_content
                
            elif content_result is None:
                # Handle None return
                self._xml_component.content = "[No content]"
                
            else:
                # String or other type - convert to string
                self._xml_component.content = str(content_result) if content_result else "[No content]"
                
        except Exception as e:
            # Fallback to error content
            self._xml_component.content = f"[Render Error: {str(e)}]"
            self.xml.attrs['error'] = 'true'
    
    def _update_standard_attrs(self) -> None:
        """
        Update standard XML attributes automatically.
        
        Standard attributes:
        - tokens: Current token count of content
        - max_tokens: Maximum tokens allowed for this scaffold
        - utilization: Percentage utilization (0.0% - 100.0%)
        """
        # Only calculate if scaffold has token-counting capabilities
        if hasattr(self, 'count_tokens') and hasattr(self, 'get_token_limit'):
            # Calculate current token usage
            content_str = str(self._xml_component.content) if self._xml_component.content else ""
            current_tokens = self.count_tokens(content_str)
            max_tokens = self.get_token_limit()
            
            # Update XML attributes
            self.xml.attrs['tokens'] = str(current_tokens)
            self.xml.attrs['max_tokens'] = str(max_tokens)
            
            # Calculate utilization percentage
            if max_tokens > 0:
                utilization = (current_tokens / max_tokens) * 100
                self.xml.attrs['utilization'] = f"{utilization:.1f}%"
            else:
                self.xml.attrs['utilization'] = "0.0%"
    
    def _finalize_xml_render(self) -> str:
        """
        Legacy method - now just returns a basic render.
        This is kept for compatibility but should not be used directly.
        """
        # Just return default render
        return self._render_with_content("[No content - override render()]")
    
    
    def _ensure_xml_init(self) -> None:
        """Ensure XML components are initialized (handles metaclass init bypass)"""
        if not hasattr(self, '_xml_component') or self._xml_component is None:
            self._xml_component = XMLComponent(type=self.type, content="[Initializing...]")
        if not hasattr(self, '_xml') or self._xml is None:
            self._xml = XMLAccessor(self)