"""
Tool Decorator System

@tool decorator for auto-registration system with function signature extraction.
Provides clean API for declaring tools with automatic ToolDeclaration creation.
"""

from typing import Optional, Callable, Any
from egregore.core.tool_calling.tool_declaration import ToolDeclaration
from egregore.core.tool_calling.tool_registry import ToolRegistry


# Global tool registry instance
tool_registry = ToolRegistry()


def tool(
    func: Optional[Callable] = None,
    *,
    name: Optional[str] = None,
    description: Optional[str] = None,
    always_succeeds: bool = False,
    **kwargs
) -> Callable:
    """
    Decorator to register a function as a tool with automatic parameter extraction.
    
    Analyzes function signature to extract parameters, types, and requirements.
    Automatically registers the tool in the global registry for immediate use.
    Supports both @tool and @tool(...) decorator patterns.
    
    Args:
        func: The function being decorated (when used as @tool)
        name: Custom tool name (defaults to function name)
        description: Tool description (defaults to function docstring)
        always_succeeds: If True, wraps exceptions in success responses
        **kwargs: Additional ToolDeclaration parameters
    
    Returns:
        Decorated function with attached ToolDeclaration and _is_tool marker
    
    Auto-Registration:
        Decorated functions are automatically registered in the global tool
        registry accessible via get_tool_registry().
    
    Parameter Extraction:
        - Required parameters: No default value and not Optional[T]
        - Optional parameters: Has default value OR Optional[T] type hint
        - Supported types: str, int, float, bool, list, dict, Optional, List
    
    Examples:
        ```python
        # Simple usage
        @tool
        def greet(name: str, greeting: str = "Hello") -> str:
            '''Greet someone with a custom greeting'''
            return f"{greeting}, {name}!"
        
        # With parameters
        @tool(name="file_reader", always_succeeds=True)
        def read_file(path: str, encoding: str = "utf-8") -> str:
            '''Read file contents safely'''
            try:
                with open(path, encoding=encoding) as f:
                    return f.read()
            except Exception as e:
                return f"Error reading file: {e}"
                
        # Complex parameters
        @tool
        def process_items(
            items: List[str], 
            filter_empty: bool = True,
            max_items: Optional[int] = None
        ) -> str:
            '''Process list of items with filtering'''
            if filter_empty:
                items = [item for item in items if item.strip()]
            if max_items:
                items = items[:max_items]
            return f"Processed {len(items)} items"
        ```
    """
    def decorator(func: Callable) -> Callable:
        # Extract metadata from function
        tool_name = name or func.__name__
        tool_description = description or func.__doc__ or f"Execute {tool_name}"
        
        # Create ToolDeclaration from function signature
        tool_declaration = ToolDeclaration.from_callable(
            func,
            name=tool_name,
            description=tool_description,
            always_succeeds=always_succeeds,
            **kwargs
        )
        
        # Attach declaration to function for registry access
        func._tool_declaration = tool_declaration
        func._is_tool = True
        
        # Auto-register in global registry
        tool_registry.register_tool(tool_declaration)
        
        return func
    
    # Handle both @tool and @tool(...) usage patterns
    if func is None:
        # Called as @tool(...)
        return decorator
    else:
        # Called as @tool
        return decorator(func)


def get_tool_registry() -> ToolRegistry:
    """
    Get the global tool registry instance.
    
    Returns:
        ToolRegistry containing all @tool decorated functions
        
    Example:
        ```python
        registry = get_tool_registry()
        my_tool = registry.get_tool("my_function")
        ```
    """
    return tool_registry


def reset_tool_registry() -> None:
    """
    Reset the global tool registry (useful for testing).
    
    Clears all registered tools and creates a fresh registry instance.
    Primarily used in test environments to ensure clean state.
    
    Example:
        ```python
        # In test setup
        reset_tool_registry()
        
        @tool
        def test_tool():
            return "test"
            
        assert len(get_tool_registry().tools) == 1
        ```
    """
    global tool_registry
    tool_registry = ToolRegistry()


def list_registered_tools() -> list[str]:
    """
    Get list of all registered tool names.
    
    Returns:
        List of tool names currently in the global registry
        
    Example:
        ```python
        tools = list_registered_tools()
        print(f"Available tools: {', '.join(tools)}")
        ```
    """
    return tool_registry.list_tool_names()


def is_tool_function(func: Callable) -> bool:
    """
    Check if a function has been decorated with @tool.
    
    Args:
        func: Function to check
        
    Returns:
        True if function has been decorated with @tool, False otherwise
        
    Example:
        ```python
        @tool
        def my_tool():
            return "result"
        
        def regular_function():
            return "result"
            
        assert is_tool_function(my_tool) == True
        assert is_tool_function(regular_function) == False
        ```
    """
    return hasattr(func, '_is_tool') and func._is_tool


def get_tool_declaration(func: Callable) -> Optional[ToolDeclaration]:
    """
    Get the ToolDeclaration attached to a @tool decorated function.
    
    Args:
        func: Function to extract ToolDeclaration from
        
    Returns:
        ToolDeclaration if function is decorated with @tool, None otherwise
        
    Example:
        ```python
        @tool
        def my_tool(param: str) -> str:
            return param.upper()
        
        declaration = get_tool_declaration(my_tool)
        assert declaration.name == "my_tool"
        assert "param" in declaration.parameters.required
        ```
    """
    return getattr(func, '_tool_declaration', None)