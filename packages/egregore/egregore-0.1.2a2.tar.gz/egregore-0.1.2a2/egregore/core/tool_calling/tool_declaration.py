"""
Tool Declaration System

ToolDeclaration class for V2 tool system with ContextComponent integration.
Enhanced from V1 with context tree support and ScaffoldManager compatibility.
"""

from pydantic import BaseModel, Field, PrivateAttr
from typing import Optional, Dict, Any, Callable
import inspect
from egregore.core.tool_calling.schema import Schema, SchemaType
from egregore.core.tool_calling.context_components import ToolResult, ScaffoldResult
from egregore.core.messaging import ProviderToolCall
from egregore.core.context_scaffolds.data_types import StateOperatorResult
from datetime import datetime


class ToolDeclaration(BaseModel):
    """
    V2 tool declaration with ContextComponent integration.
    
    Represents a callable tool that can be executed by the V2 tool system.
    Provides automatic parameter extraction from function signatures,
    schema generation for provider integration, and ContextComponent output.
    
    Attributes:
        name: Unique tool identifier used for registration and calling
        description: Human-readable description of tool functionality  
        parameters: Optional Schema for input parameter validation
        response: Optional Schema for output response validation
        always_succeeds: If True, wraps exceptions in success responses
        provider_hints: Provider-specific configuration hints
        
    Example:
        ```python
        from egregore.core.tool_calling import ToolDeclaration
        
        # Create from callable
        def my_tool(text: str, count: int = 1) -> str:
            return text * count
        
        tool = ToolDeclaration.from_callable(my_tool)
        
        # Execute tool
        call = ProviderToolCall(
            tool_name="my_tool",
            tool_call_id="call_123", 
            parameters={"text": "hello", "count": 2}
        )
        result = tool.execute(call)
        assert result.success
        assert result.content == "hellohello"
        ```
    """
    name: str = Field(..., description="Unique tool identifier")
    description: str = Field(..., description="Human-readable tool description")
    parameters: Optional[Schema] = Field(None, description="Input parameter schema (auto-extracted from callable)")
    response: Optional[Schema] = Field(None, description="Output response schema for validation")
    
    # V2 context integration
    always_succeeds: bool = Field(False, description="If True, wraps exceptions in success responses")
    
    # Provider integration
    provider_hints: Dict[str, Any] = Field(default_factory=dict, description="Provider-specific configuration hints")
    
    # Execution callable
    _callable: Optional[Callable] = PrivateAttr(default=None)
    _is_async: bool = PrivateAttr(default=False)
    
    @classmethod
    def from_callable(cls, callable: Callable, **kwargs) -> 'ToolDeclaration':
        """
        Create tool declaration from callable with automatic parameter extraction.
        
        Analyzes the callable's signature to extract parameter information including:
        - Parameter names and types
        - Required vs optional parameters (Optional[T] or default values)  
        - Basic type validation schema
        
        Args:
            callable: Function to convert to tool declaration
            **kwargs: Additional ToolDeclaration attributes to override
            
        Returns:
            ToolDeclaration with extracted parameters and attached callable
            
        Example:
            ```python
            def greet(name: str, greeting: str = "Hello") -> str:
                return f"{greeting}, {name}!"
            
            tool = ToolDeclaration.from_callable(greet)
            assert tool.name == "greet"
            assert "name" in tool.parameters.required
            assert "greeting" not in tool.parameters.required  # Has default
            ```
        """
        # Extract basic metadata
        tool_name = kwargs.get('name', callable.__name__)
        tool_description = kwargs.get('description', callable.__doc__ or f"Execute {tool_name}")
        
        # Extract parameters from function signature
        parameters = cls._extract_parameters_from_callable(callable)
        
        declaration = cls(
            name=tool_name,
            description=tool_description,
            parameters=parameters,
            **{k: v for k, v in kwargs.items() if k not in ['name', 'description']}
        )
        
        # Store callable reference
        declaration._callable = callable
        declaration._is_async = kwargs.get('is_async', False)
        
        return declaration
    
    @classmethod
    def _extract_parameters_from_callable(cls, callable: Callable) -> Optional[Schema]:
        """Extract parameters from callable signature and create Schema"""
        try:
            sig = inspect.signature(callable)
            properties = {}
            required = []
            
            for param_name, param in sig.parameters.items():
                # Skip *args and **kwargs
                if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
                    continue
                
                # Use Schema.from_parameter to extract parameter schema
                param_schema = Schema.from_parameter(param)
                properties[param_name] = param_schema.model_dump(exclude_none=True)
                
                # Parameter is required if it has no default value and is not Optional
                if param.default is param.empty and not getattr(param_schema, 'nullable', False):
                    required.append(param_name)
            
            # If no parameters, return None
            if not properties:
                return None
                
            # Create Schema for all parameters
            return Schema(
                type=SchemaType.OBJECT,
                properties=properties,
                required=required
            )
            
        except Exception as e:
            # If parameter extraction fails, return None and log
            print(f"Warning: Failed to extract parameters from {callable.__name__}: {e}")
            return None
        
    def execute(self, tool_call: ProviderToolCall) -> ToolResult:
        """Execute tool with scaffold detection and TTL application."""
        try:
            if self._is_async:
                raise RuntimeError("Use execute_async for async tools")
            
            if not self._callable:
                raise RuntimeError("No callable attached to ToolDeclaration")
            
            result = self._callable(**tool_call.parameters)
            
            # Check if result is StateOperatorResult (scaffold operation detection)
            if isinstance(result, StateOperatorResult):
                # This WAS a scaffold operation - result type tells us everything!
                scaffold = self._callable.__self__  # Get scaffold instance
                operation_name = self._callable.__name__
                
                # Get TTL config from scaffold (retention handled by MessageScheduler)
                operation_ttl = scaffold._get_operation_ttl(operation_name)
                synchronized_ttl = operation_ttl - 1 if operation_ttl > 0 else None
                
                # Return ScaffoldResult with TTL
                return ScaffoldResult(
                    tool_call_id=tool_call.tool_call_id,
                    tool_name=tool_call.tool_name,
                    scaffold_id=scaffold.metadata.id,  # Use component ID
                    scaffold_type=scaffold.type,  # Use scaffold.type field
                    operation_name=operation_name,
                    content=result.message,  # Use StateOperatorResult.message
                    success=result.success,  # Use StateOperatorResult.success
                    execution_time=datetime.now(),
                    ttl=synchronized_ttl  # TTL applied, retention handled by MessageScheduler
                )
            else:
                # Regular tool - existing behavior
                return ToolResult(
                    tool_call_id=tool_call.tool_call_id,
                    tool_name=tool_call.tool_name,
                    content=str(result),
                    success=True,
                    execution_time=datetime.now()
                    # No TTL for regular tools
                )
                
        except Exception as e:
            # Handle errors with proper scaffold vs regular tool detection
            if (hasattr(self._callable, '__self__') and 
                hasattr(self._callable.__self__, '_get_operation_ttl')):
                # Scaffold operation failed - return ScaffoldResult
                scaffold = self._callable.__self__
                return ScaffoldResult(
                    tool_call_id=tool_call.tool_call_id,
                    tool_name=tool_call.tool_name,
                    scaffold_id=scaffold.metadata.id,  # Use component ID
                    scaffold_type=scaffold.type,  # Use scaffold.type field
                    operation_name=self._callable.__name__,
                    content=f"Scaffold operation failed: {str(e)}",
                    success=False,
                    execution_time=datetime.now(),
                    error_message=str(e)
                    # No TTL for failed operations - they should be visible
                )
            else:
                # Regular tool failed - return standard ToolResult
                if self.always_succeeds:
                    return ToolResult(
                        tool_call_id=tool_call.tool_call_id,
                        tool_name=tool_call.tool_name,
                        content=f"Tool execution completed with warning: {str(e)}",
                        success=True,
                        execution_time=datetime.now(),
                        error_message=str(e)
                    )
                else:
                    return ToolResult(
                        tool_call_id=tool_call.tool_call_id,
                        tool_name=tool_call.tool_name,
                        content=f"Error executing tool: {str(e)}",
                        success=False,
                        execution_time=datetime.now(),
                        error_message=str(e)
                    )


class ScaffoldOpDeclaration(ToolDeclaration):
    """
    Specialized ToolDeclaration for scaffold operations with type-based detection.
    
    Inherits all functionality from ToolDeclaration but guarantees scaffold-specific
    behavior and metadata. Eliminates the need for pattern-based detection by
    providing type-safe scaffold operation handling.
    
    Attributes:
        scaffold_id: Unique identifier of the scaffold instance
        scaffold_type: Type of scaffold (matches scaffold.type field)
        operation_name: Name of the scaffold operation method
        
    Benefits:
        - Type-based detection replaces pattern matching
        - Early scaffold identification at tool creation time
        - Guaranteed ScaffoldResult return type
        - Backward compatible through inheritance
    """
    scaffold_id: str = Field(..., description="Unique identifier of the scaffold instance")
    scaffold_type: str = Field(..., description="Type of scaffold (matches scaffold.type field)")
    operation_name: str = Field(..., description="Name of the scaffold operation method")
    
    @classmethod
    def from_scaffold_method(cls, scaffold_instance, method_callable: Callable, **kwargs) -> 'ScaffoldOpDeclaration':
        """
        Create scaffold operation declaration from scaffold method.
        
        Extracts scaffold metadata and creates properly named tool declaration
        using the standard scaffold tool naming format.
        
        Args:
            scaffold_instance: The scaffold instance containing the method
            method_callable: The bound method to convert to tool declaration
            **kwargs: Additional ToolDeclaration attributes to override
            
        Returns:
            ScaffoldOpDeclaration with scaffold metadata and proper tool naming
        """
        operation_name = method_callable.__name__
        scaffold_id = scaffold_instance.id
        scaffold_type = scaffold_instance.type
        
        # Generate tool name using standard format: scaffold_type_operation_name
        tool_name = f"{scaffold_type}_{operation_name}"
        
        # Extract description from method docstring or generate default
        tool_description = (method_callable.__doc__ or 
                          f"Execute {operation_name} operation on {scaffold_type} scaffold")
        
        # Extract parameters using parent method
        parameters = cls._extract_parameters_from_callable(method_callable)
        
        declaration = cls(
            name=tool_name,
            description=tool_description,
            parameters=parameters,
            scaffold_id=scaffold_id,
            scaffold_type=scaffold_type,
            operation_name=operation_name,
            **{k: v for k, v in kwargs.items() if k not in ['name', 'description']}
        )
        
        # Store callable reference
        declaration._callable = method_callable
        declaration._is_async = kwargs.get('is_async', False)
        
        return declaration
    
    def execute(self, tool_call: ProviderToolCall) -> ScaffoldResult:
        """
        Execute scaffold operation with guaranteed ScaffoldResult return.
        
        Overrides parent execute() method to ensure scaffold operations always
        return ScaffoldResult, eliminating the need for runtime detection.
        
        Args:
            tool_call: Provider tool call containing parameters
            
        Returns:
            ScaffoldResult with scaffold metadata and execution results
        """
        try:
            if self._is_async:
                raise RuntimeError("Use execute_async for async scaffold operations")
            
            if not self._callable:
                raise RuntimeError("No callable attached to ScaffoldOpDeclaration")
            
            # Execute the scaffold operation
            result = self._callable(**tool_call.parameters)
            
            # For scaffold operations, we expect StateOperatorResult but handle other types gracefully
            if isinstance(result, StateOperatorResult):
                # Standard scaffold operation result
                scaffold = self._callable.__self__  # Get scaffold instance
                
                # Get TTL config from scaffold (retention handled by MessageScheduler)
                operation_ttl = scaffold._get_operation_ttl(self.operation_name)
                synchronized_ttl = operation_ttl - 1 if operation_ttl > 0 else None
                
                return ScaffoldResult(
                    tool_call_id=tool_call.tool_call_id,
                    tool_name=tool_call.tool_name,
                    scaffold_id=self.scaffold_id,
                    scaffold_type=self.scaffold_type,
                    operation_name=self.operation_name,
                    content=result.message,  # Use StateOperatorResult.message
                    success=result.success,  # Use StateOperatorResult.success
                    execution_time=datetime.now(),
                    ttl=synchronized_ttl  # TTL applied, retention handled by MessageScheduler
                )
            else:
                # Non-standard result from scaffold operation - handle gracefully
                return ScaffoldResult(
                    tool_call_id=tool_call.tool_call_id,
                    tool_name=tool_call.tool_name,
                    scaffold_id=self.scaffold_id,
                    scaffold_type=self.scaffold_type,
                    operation_name=self.operation_name,
                    content=str(result),
                    success=True,
                    execution_time=datetime.now()
                    # No TTL for non-standard results
                )
                
        except Exception as e:
            # Scaffold operation failed - return ScaffoldResult with error
            return ScaffoldResult(
                tool_call_id=tool_call.tool_call_id,
                tool_name=tool_call.tool_name,
                scaffold_id=self.scaffold_id,
                scaffold_type=self.scaffold_type,
                operation_name=self.operation_name,
                content=f"Scaffold operation failed: {str(e)}",
                success=False,
                execution_time=datetime.now(),
                error_message=str(e)
                # No TTL for failed operations - they should be visible
            )