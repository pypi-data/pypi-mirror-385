"""
Scaffold Context Components

PACTCore types for scaffold operation results.
These components represent scaffold execution outcomes in the context tree.
"""

from egregore.core.context_management.pact.components.core import PACTCore
from datetime import datetime
from typing import Optional, ClassVar, TYPE_CHECKING

if TYPE_CHECKING:
    # RenderOptions removed - not needed in PACT architecture
    RenderOptions = None


class ScaffoldResult(PACTCore):
    """Context component for scaffold operation results with scaffold tracking"""
    type: ClassVar[str] = "scaffold_result"
    description: ClassVar[str] = "Scaffold operation result with scaffold metadata"
    
    # Tool result fields (following ToolResult pattern)
    tool_call_id: str
    tool_name: str
    success: bool
    execution_time: Optional[datetime] = None
    error_message: Optional[str] = None
    
    # Scaffold tracking
    scaffold_id: str
    scaffold_type: str  # e.g., "task_list", "file_manager"
    operation_name: str  # e.g., "add_task", "complete_task"
    
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