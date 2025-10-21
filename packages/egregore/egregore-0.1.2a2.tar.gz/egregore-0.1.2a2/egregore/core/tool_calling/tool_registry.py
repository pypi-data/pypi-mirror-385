"""
Tool Registry System

ToolRegistry for provider-agnostic tool storage with clean lookup capabilities.
Manages tool declarations and provides access for tool execution.
"""

from pydantic import BaseModel, Field
from typing import Dict, Optional, List
from egregore.core.tool_calling.tool_declaration import ToolDeclaration


class ToolRegistry(BaseModel):
    """
    Centralized tool registry for provider-agnostic tool storage.
    
    Manages ToolDeclaration instances and provides efficient lookup capabilities.
    Thread-safe for read operations, use external synchronization for writes
    in multi-threaded environments.
    
    Attributes:
        tools: Dictionary mapping tool names to ToolDeclaration instances
        
    Example:
        ```python
        from egregore.core.tool_calling import ToolRegistry, ToolDeclaration
        
        # Create registry
        registry = ToolRegistry()
        
        # Register tool
        def my_tool(param: str) -> str:
            return f"Processed: {param}"
            
        tool = ToolDeclaration.from_callable(my_tool)
        registry.register_tool(tool)
        
        # Use registry
        assert registry.tool_exists("my_tool")
        found_tool = registry.get_tool("my_tool")
        assert found_tool.name == "my_tool"
        ```
        
    Thread Safety:
        - Read operations (get_tool, tool_exists, etc.) are thread-safe
        - Write operations (register_tool, unregister_tool) require external
          synchronization in multi-threaded environments
    """
    tools: Dict[str, ToolDeclaration] = Field(default_factory=dict, description="Mapping of tool names to declarations")
    
    def register_tool(self, tool: ToolDeclaration) -> None:
        """
        Register tool in registry.
        
        If a tool with the same name already exists, it will be replaced.
        
        Args:
            tool: ToolDeclaration to register
            
        Example:
            ```python
            tool = ToolDeclaration.from_callable(my_function)
            registry.register_tool(tool)
            ```
        """
        self.tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Optional[ToolDeclaration]:
        """
        Get tool by name.
        
        Args:
            name: Tool name to lookup
            
        Returns:
            ToolDeclaration if found, None otherwise
            
        Example:
            ```python
            tool = registry.get_tool("my_tool")
            if tool:
                result = tool.execute(call)
            ```
        """
        return self.tools.get(name)
    
    def get_all_tools(self) -> List[ToolDeclaration]:
        """
        Get all registered tools.
        
        Returns:
            List of all ToolDeclaration instances in registry
            
        Example:
            ```python
            all_tools = registry.get_all_tools()
            for tool in all_tools:
                print(f"Tool: {tool.name}")
            ```
        """
        return list(self.tools.values())
    
    def unregister_tool(self, name: str) -> bool:
        """Remove tool from registry, returns True if tool was found and removed"""
        if name in self.tools:
            del self.tools[name]
            return True
        return False
    
    def list_tool_names(self) -> List[str]:
        """Get list of all registered tool names"""
        return list(self.tools.keys())
    
    def tool_exists(self, name: str) -> bool:
        """Check if tool exists in registry"""
        return name in self.tools
    
    def clear(self) -> None:
        """Clear all tools from registry"""
        self.tools.clear()
    
    def count(self) -> int:
        """Get number of registered tools"""
        return len(self.tools)