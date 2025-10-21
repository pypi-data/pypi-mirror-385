"""
Tool Calling Context Components

ContextComponent types for tool calls and results that integrate with the V2 context tree.
These components represent both tool calls from LLM responses and tool execution outcomes.
"""

import json
from datetime import datetime
from typing import Optional, ClassVar, Dict, Any, TYPE_CHECKING

# RenderOptions removed - not needed in PACT
from egregore.core.context_management.pact.components.core import PACTNode


class ToolCall(PACTNode):
    """Context component for tool calls from LLM responses with PACT integration"""
    type: ClassVar[str] = "tool_call"
    description: ClassVar[str] = "Tool call from LLM response with parameters and metadata"

    # Tool call metadata
    tool_call_id: str
    tool_name: str
    parameters: Dict[str, Any]
    is_operation: bool = False

    @property
    def tool_id(self) -> str:
        """Convenience property that returns tool_call_id for easier querying"""
        return self.tool_call_id
    
    # content: str - inherited, automatically set to JSON of parameters
    # ttl: Optional[int] = None - inherited (for retention management)
    
    def __init__(self, **kwargs):
        """Initialize ToolCall with JSON content strategy."""
        # Set content to JSON representation of parameters for searchability
        if 'content' not in kwargs and 'parameters' in kwargs:
            kwargs['content'] = json.dumps(kwargs['parameters'], ensure_ascii=False)

        super().__init__(**kwargs)

        # Ensure universal +tool_call tag is set
        if "tool_call" not in self.tags:
            self.tags.append("tool_call")

        # Add tool_id tag for easy deletion (e.g., "tool_id:call_123")
        if hasattr(self, 'tool_call_id') and self.tool_call_id:
            tool_id_tag = f"tool_id:{self.tool_call_id}"
            if tool_id_tag not in self.tags:
                self.tags.append(tool_id_tag)
    
    def render(self, options: 'RenderOptions') -> str:
        """Render tool call with parameters visualization."""
        if not self.tool_name:
            return ""
        
        # Format parameters for display
        params_str = ""
        if self.parameters:
            # Pretty format parameters
            formatted_params = []
            for key, value in self.parameters.items():
                if isinstance(value, str) and len(value) > 50:
                    value = value[:47] + "..."
                formatted_params.append(f"{key}={repr(value)}")
            params_str = f"({', '.join(formatted_params)})"
        
        formatted = f"🔧 **{self.tool_name}**{params_str}"
        
        if hasattr(options, 'show_component_types') and options.show_component_types:
            formatted += f" *[{self.type}]*"
        
        if hasattr(options, 'show_metadata') and options.show_metadata:
            formatted += self._format_metadata(options)
        
        return formatted


class ScaffoldCall(ToolCall):
    """Context component for scaffold operation calls with scaffold metadata"""
    type: ClassVar[str] = "scaffold_call"
    description: ClassVar[str] = "Scaffold operation call from LLM response with scaffold metadata"
    
    # Override is_operation default
    is_operation: bool = True
    
    # Scaffold metadata
    scaffold_id: str
    scaffold_type: str  # e.g., "file_manager", "data_processor"  
    operation_name: str  # e.g., "create_file", "process_data"
    
    # Inherits: tool_call_id, tool_name, parameters from ToolCall
    # Inherits: content (JSON parameters), ttl for retention management
    
    def render(self, options: 'RenderOptions') -> str:
        """Render scaffold call with scaffold-specific display."""
        if not self.tool_name:
            return ""
        
        # Format parameters for display
        params_str = ""
        if self.parameters:
            # Pretty format parameters
            formatted_params = []
            for key, value in self.parameters.items():
                if isinstance(value, str) and len(value) > 40:
                    value = value[:37] + "..."
                formatted_params.append(f"{key}={repr(value)}")
            params_str = f"({', '.join(formatted_params)})"
        
        # Scaffold-specific formatting
        formatted = f"🏗️ **{self.scaffold_type}::{self.operation_name}**{params_str}"
        
        if hasattr(options, 'show_component_types') and options.show_component_types:
            formatted += f" *[{self.type}]*"
        
        if hasattr(options, 'show_metadata') and options.show_metadata:
            formatted += self._format_metadata(options)
        
        return formatted


class ToolResult(PACTNode):
    """Context component for tool execution results with pairing metadata"""
    type: ClassVar[str] = "tool_result"
    description: ClassVar[str] = "Tool execution result with pairing metadata"
    
    # Pairing integrity
    tool_call_id: str
    tool_name: str
    success: bool
    execution_time: Optional[datetime] = None
    error_message: Optional[str] = None
    
    # content: Union[str, List[ContextComponent]] - inherited
    # ttl: Optional[int] = None - inherited (for scaffold operations)
    
    def render(self, options: 'RenderOptions') -> str:
        """Render tool result with success/failure indicators"""
        if not self.content:
            return ""
        
        status = "✅" if self.success else "❌"
        content = self.content.strip() if isinstance(self.content, str) and self.content else str(self.content)
        
        if hasattr(options, 'max_content_length') and options.max_content_length and len(content) > options.max_content_length:
            content = content[:options.max_content_length] + "..."
        
        formatted = f"{status} **{self.tool_name}**\n```\n{content}\n```"
        
        if hasattr(options, 'show_component_types') and options.show_component_types:
            formatted += f" *[{self.type}]*"
        
        if hasattr(options, 'show_metadata') and options.show_metadata:
            formatted += self._format_metadata(options)
        
        return formatted


class ScaffoldResult(ToolResult):
    """Context component for scaffold operation results with scaffold tracking"""
    type: ClassVar[str] = "scaffold_result"
    description: ClassVar[str] = "Scaffold operation result with scaffold metadata"
    
    # Scaffold tracking
    scaffold_id: str
    scaffold_type: str  # e.g., "file_manager", "data_processor"
    operation_name: str  # e.g., "read_file", "process_data"
    
    # Inherited: tool_call_id, tool_name, success, etc.
    # ttl: Optional[int] = None - inherited (scaffolds manage their own TTL)
    
    def render(self, options: 'RenderOptions') -> str:
        """Render scaffold result with scaffold information"""
        if not self.content:
            return ""
        
        status = "✅" if self.success else "❌"
        content = self.content.strip() if isinstance(self.content, str) and self.content else str(self.content)
        
        if hasattr(options, 'max_content_length') and options.max_content_length and len(content) > options.max_content_length:
            content = content[:options.max_content_length] + "..."
        
        formatted = f"{status} **{self.scaffold_type}::{self.operation_name}**\n```\n{content}\n```"
        
        if hasattr(options, 'show_component_types') and options.show_component_types:
            formatted += f" *[{self.type}]*"
        
        if hasattr(options, 'show_metadata') and options.show_metadata:
            formatted += self._format_metadata(options)
        
        return formatted
