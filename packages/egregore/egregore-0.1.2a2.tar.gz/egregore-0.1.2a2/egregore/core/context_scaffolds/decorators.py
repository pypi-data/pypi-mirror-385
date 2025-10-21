"""
Decorators for V2 Context Scaffolds.

Provides the @operation decorator for marking scaffold methods
that should be exposed as agent operations.
"""

import inspect
import functools
from typing import Any, Callable, Dict, Optional, List, get_type_hints, Union, Protocol, runtime_checkable, cast, TypeVar, overload
from dataclasses import dataclass

# Import StateOperatorResult for type checking
from .data_types import StateOperatorResult


@dataclass
class ScaffoldOperationMetadata:
    """
    Metadata for scaffold operations.
    
    Stores information about a decorated scaffold method for later
    introspection and tool generation.
    """
    name: str
    description: str
    original_func: Callable
    parameters: Dict[str, Dict[str, Any]]  # param_name -> {type, description, default, required}
    return_type: Optional[type] = None
    is_async: bool = False
    desc_path: Optional[str] = None  # Path to description file or external resource


@runtime_checkable
class _ScaffoldWrapped(Protocol):
    _scaffold_operation_metadata: "ScaffoldOperationMetadata"
    _is_scaffold_operation: bool
    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...


F = TypeVar("F", bound=Callable[..., Any])


def get_operation_description(metadata: ScaffoldOperationMetadata) -> str:
    """
    Get the current description for a scaffold operation.
    
    Follows the description hierarchy:
    1. desc_path file (if exists and readable)
    2. Stored description from decorator
    3. Function docstring (from original_func)
    4. Default "Execute {operation_name}"
    
    Args:
        metadata: ScaffoldOperationMetadata instance
        
    Returns:
        Current description string following the hierarchy
    """
    # Try to load from desc_path file first
    if metadata.desc_path:
        try:
            import os
            if os.path.exists(metadata.desc_path):
                with open(metadata.desc_path, 'r', encoding='utf-8') as f:
                    file_description = f.read().strip()
                if file_description:
                    return file_description
        except Exception:
            # Silently fall back to next option
            pass
    
    # Fallback hierarchy: stored description > docstring > default
    return metadata.description or getattr(metadata.original_func, '__doc__', None) or f"Execute {metadata.name}"


@overload
def operation(func: F, /) -> F: ...


@overload
def operation(*, name: Optional[str] = ..., description: Optional[str] = ..., desc_path: Optional[str] = ...) -> Callable[[F], F]: ...


def operation(
    func: Optional[F] = None,
    /,
    *,
    name: Optional[str] = None,
    description: Optional[str] = None,
    desc_path: Optional[str] = None
) -> Union[F, Callable[[F], F]]:
    """
    Decorator to mark scaffold methods as operations available to agents.
    
    This decorator is for INTERNAL discovery only. External access to scaffold
    operations should use the agent.scaffolds.<scaffold_name>.<method>() pattern
    via ScaffoldAccessor.
    
    Args:
        name: Override name for the operation (defaults to function name)
        description: Description of what the operation does
        desc_path: Path to description file or external resource for detailed documentation
        
    Description Resolution Hierarchy:
        1. desc_path file (if exists and readable) - highest priority
        2. description parameter
        3. function docstring
        4. default "Execute {operation_name}" - lowest priority
    Returns:
        Decorated function with scaffold operation metadata
        
    Examples:
        ```python
        class TaskScaffold(BaseContextScaffold):
            @operation()  # Uses docstring
            def add_task(self, title: str) -> StateOperatorResult:
                '''Add a new task to the system'''
                return StateOperatorResult(success=True, message="Task added")
            
            @operation(description="Quick task creation")  # Overrides docstring
            def quick_add(self, title: str) -> StateOperatorResult:
                '''This docstring will be ignored'''
                return StateOperatorResult(success=True, message="Quick add done")
            
            @operation(
                description="Fallback description",  # Used if file doesn't exist
                desc_path="docs/scaffolds/task_analysis.md"  # Highest priority
            )
            def analyze_tasks(self, criteria: str) -> StateOperatorResult:
                '''This docstring ignored if file exists'''
                return StateOperatorResult(success=True, message="Analysis complete")
        ```
    """
    def decorator(func: F) -> F:
        # Auto-resolve name
        operation_name = name or func.__name__
        
        # Build description hierarchy: desc_path file > provided description > docstring > default
        operation_description = None
        
        # Try to load from desc_path file first
        if desc_path:
            try:
                import os
                if os.path.exists(desc_path):
                    with open(desc_path, 'r', encoding='utf-8') as f:
                        file_description = f.read().strip()
                    if file_description:
                        operation_description = file_description
            except Exception as e:
                # If file loading fails, log warning and continue to fallbacks
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to load description from {desc_path}: {e}")
        
        # Fallback hierarchy: provided description > docstring > default
        if not operation_description:
            operation_description = description or func.__doc__ or f"Execute {operation_name}"
        
        # Extract parameter information
        parameters = _extract_parameter_info(func)
        
        # Get return type and validate it's StateOperatorResult
        type_hints = get_type_hints(func)
        return_type = type_hints.get('return', None)
        
        # Enforce StateOperatorResult return type
        if return_type is None:
            raise ValueError(f"Scaffold operation '{operation_name}' must have a return type annotation of StateOperatorResult")
        
        if return_type != StateOperatorResult:
            raise ValueError(f"Scaffold operation '{operation_name}' must return StateOperatorResult, got {return_type}")
        
        # Check if function is async
        is_async = inspect.iscoroutinefunction(func)
        
        # Create metadata
        metadata = ScaffoldOperationMetadata(
            name=operation_name,
            description=operation_description,
            original_func=func,
            parameters=parameters,
            return_type=return_type,
            is_async=is_async,
            desc_path=desc_path
        )
        
        # Create wrapper function
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Validate parameters before calling
            _validate_parameters(func, parameters, args, kwargs)
            
            # Call the function
            result = func(*args, **kwargs)
            
            # Validate return type at runtime
            if not isinstance(result, StateOperatorResult):
                raise ValueError(f"Scaffold operation '{operation_name}' must return StateOperatorResult instance, got {type(result)}")
            
            return result
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Validate parameters before calling
            _validate_parameters(func, parameters, args, kwargs)
            
            # Call the function
            result = await func(*args, **kwargs)
            
            # Validate return type at runtime
            if not isinstance(result, StateOperatorResult):
                raise ValueError(f"Scaffold operation '{operation_name}' must return StateOperatorResult instance, got {type(result)}")
            
            return result
        
        # Use appropriate wrapper
        final_wrapper = async_wrapper if is_async else wrapper
        
        # Attach metadata to the wrapper (cast for type checkers)
        wrapped = cast(_ScaffoldWrapped, final_wrapper)
        wrapped._scaffold_operation_metadata = metadata
        wrapped._is_scaffold_operation = True
        
        return cast(F, wrapped)
    
    if func is None:
        return decorator
    else:
        return decorator(func)


def _extract_parameter_info(func: Callable) -> Dict[str, Dict[str, Any]]:
    """
    Extract parameter information from function signature.
    
    Args:
        func: Function to inspect
        
    Returns:
        Dictionary mapping parameter names to their metadata
    """
    sig = inspect.signature(func)
    type_hints = get_type_hints(func)
    parameters = {}
    
    for param_name, param in sig.parameters.items():
        # Skip 'self' parameter
        if param_name == 'self':
            continue
            
        param_info = {
            'required': param.default == inspect.Parameter.empty,
            'default': param.default if param.default != inspect.Parameter.empty else None,
            'type': type_hints.get(param_name, Any),
            'description': f"Parameter {param_name}"  # Could be enhanced with docstring parsing
        }
        
        parameters[param_name] = param_info
    
    return parameters


def _validate_parameters(
    func: Callable, 
    parameters: Dict[str, Dict[str, Any]], 
    args: tuple, 
    kwargs: dict
) -> None:
    """
    Validate parameters before calling scaffold operation.
    
    Args:
        func: Original function
        parameters: Parameter metadata
        args: Positional arguments
        kwargs: Keyword arguments
        
    Raises:
        ValueError: If parameter validation fails
    """
    sig = inspect.signature(func)
    
    try:
        # Use inspect.signature to validate the call
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
    except TypeError as e:
        raise ValueError(f"Parameter validation failed for {func.__name__}: {e}")
    
    # Additional type checking could be added here if needed
    # For now, we rely on Python's built-in type checking


def get_scaffold_operations(obj: Any) -> Dict[str, ScaffoldOperationMetadata]:
    """
    Get all scaffold operations from an object.
    
    Args:
        obj: Object to inspect for scaffold operations
        
    Returns:
        Dictionary mapping operation names to their metadata
    """
    operations = {}
    
    # Inspect all methods/attributes of the object
    for attr_name in dir(obj):
        try:
            attr = getattr(obj, attr_name)
            
            # Check if this is a scaffold operation
            if hasattr(attr, '_is_scaffold_operation') and attr._is_scaffold_operation:
                metadata = getattr(attr, '_scaffold_operation_metadata')
                operations[metadata.name] = metadata
                
        except (AttributeError, TypeError):
            # Skip attributes that can't be accessed or aren't callable
            continue
    
    return operations


def is_scaffold_operation(func: Any) -> bool:
    """
    Check if a function/method is decorated with @operation.
    
    Args:
        func: Function or method to check
        
    Returns:
        True if it's a scaffold operation, False otherwise
    """
    return hasattr(func, '_is_scaffold_operation') and func._is_scaffold_operation


def get_operation_metadata(func: Any) -> Optional[ScaffoldOperationMetadata]:
    """
    Get metadata for a scaffold operation.
    
    Args:
        func: Function or method to get metadata for
        
    Returns:
        ScaffoldOperationMetadata if it's a scaffold operation, None otherwise
    """
    if is_scaffold_operation(func):
        return getattr(func, '_scaffold_operation_metadata', None)
    return None


__all__ = [
    'operation',
    'ScaffoldOperationMetadata',
    'get_scaffold_operations',
    'is_scaffold_operation', 
    'get_operation_metadata'
]