"""
Exception classes for V2 Context Scaffolds.

Provides specialized exception hierarchy for scaffold-related errors
with helpful context and error messages.
"""

from typing import Optional, Any, Dict, List


class ScaffoldError(Exception):
    """
    Base exception for all scaffold-related errors.
    
    Provides common functionality and context for scaffold errors.
    """
    
    def __init__(
        self, 
        message: str, 
        scaffold_name: Optional[str] = None,
        scaffold_type: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize scaffold error.
        
        Args:
            message: Error message
            scaffold_name: Name of scaffold that caused the error
            scaffold_type: Type of scaffold that caused the error
            context: Additional context information
        """
        super().__init__(message)
        self.scaffold_name = scaffold_name
        self.scaffold_type = scaffold_type
        self.context = context or {}
        
        # Enhance message with scaffold context if available
        if scaffold_name or scaffold_type:
            context_parts = []
            if scaffold_name:
                context_parts.append(f"scaffold '{scaffold_name}'")
            if scaffold_type:
                context_parts.append(f"type '{scaffold_type}'")
            
            context_str = " (" + ", ".join(context_parts) + ")"
            self.args = (message + context_str,)
    
    def __str__(self) -> str:
        """Enhanced string representation with context."""
        base_msg = super().__str__()
        
        if self.context:
            context_items = []
            for key, value in self.context.items():
                context_items.append(f"{key}={value}")
            
            if context_items:
                context_str = " [Context: " + ", ".join(context_items) + "]"
                return base_msg + context_str
        
        return base_msg


class ScaffoldStateError(ScaffoldError):
    """
    Exception for scaffold state-related errors.
    
    Raised when there are issues with scaffold state management,
    initialization, or state transitions.
    """
    
    def __init__(
        self,
        message: str,
        scaffold_name: Optional[str] = None,
        state_key: Optional[str] = None,
        state_value: Optional[Any] = None,
        **kwargs
    ):
        """
        Initialize scaffold state error.
        
        Args:
            message: Error message
            scaffold_name: Name of scaffold with state error
            state_key: Specific state key that caused the error
            state_value: Value that caused the error
            **kwargs: Additional context passed to parent
        """
        # Build context with state information
        context = kwargs.pop('context', {})
        if state_key is not None:
            context['state_key'] = state_key
        if state_value is not None:
            context['state_value'] = str(state_value)[:100]  # Limit length
        
        super().__init__(
            message=message,
            scaffold_name=scaffold_name,
            context=context,
            **kwargs
        )
        
        self.state_key = state_key
        self.state_value = state_value


class ScaffoldOperationError(ScaffoldError):
    """
    Exception for scaffold operation execution errors.
    
    Raised when scaffold operations fail during execution,
    parameter validation, or method invocation.
    """
    
    def __init__(
        self,
        message: str,
        scaffold_name: Optional[str] = None,
        operation_name: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
        **kwargs
    ):
        """
        Initialize scaffold operation error.
        
        Args:
            message: Error message
            scaffold_name: Name of scaffold with operation error
            operation_name: Name of operation that failed
            parameters: Parameters passed to the operation
            original_error: Original exception that caused this error
            **kwargs: Additional context passed to parent
        """
        # Build context with operation information
        context = kwargs.pop('context', {})
        if operation_name:
            context['operation'] = operation_name
        if parameters:
            # Limit parameter representation for readability
            param_strs = []
            for key, value in parameters.items():
                value_str = str(value)[:50]  # Limit length
                param_strs.append(f"{key}={value_str}")
            context['parameters'] = ", ".join(param_strs[:5])  # Limit count
        if original_error:
            context['original_error'] = f"{type(original_error).__name__}: {str(original_error)[:100]}"
        
        super().__init__(
            message=message,
            scaffold_name=scaffold_name,
            context=context,
            **kwargs
        )
        
        self.operation_name = operation_name
        self.parameters = parameters
        self.original_error = original_error
    
    @classmethod
    def from_exception(
        cls,
        original_error: Exception,
        scaffold_name: Optional[str] = None,
        operation_name: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> "ScaffoldOperationError":
        """
        Create ScaffoldOperationError from another exception.
        
        Args:
            original_error: Original exception
            scaffold_name: Name of scaffold
            operation_name: Name of operation
            parameters: Operation parameters
            
        Returns:
            ScaffoldOperationError wrapping the original error
        """
        message = f"Operation failed: {str(original_error)}"
        return cls(
            message=message,
            scaffold_name=scaffold_name,
            operation_name=operation_name,
            parameters=parameters,
            original_error=original_error
        )


class ScaffoldRegistrationError(ScaffoldError):
    """
    Exception for scaffold registration and management errors.
    
    Raised when scaffolds cannot be registered, retrieved, or managed
    through the SystemInterface or ScaffoldAccessor.
    """
    
    def __init__(
        self,
        message: str,
        scaffold_name: Optional[str] = None,
        available_scaffolds: Optional[List[str]] = None,
        **kwargs
    ):
        """
        Initialize scaffold registration error.
        
        Args:
            message: Error message
            scaffold_name: Name of scaffold causing registration error
            available_scaffolds: List of currently available scaffold names
            **kwargs: Additional context passed to parent
        """
        # Build context with registration information
        context = kwargs.pop('context', {})
        if available_scaffolds:
            context['available_scaffolds'] = ", ".join(available_scaffolds[:10])  # Limit count
        
        super().__init__(
            message=message,
            scaffold_name=scaffold_name,
            context=context,
            **kwargs
        )
        
        self.available_scaffolds = available_scaffolds or []


class ScaffoldConfigurationError(ScaffoldError):
    """
    Exception for scaffold configuration and setup errors.
    
    Raised when scaffolds are misconfigured, have invalid parameters,
    or cannot be properly initialized.
    """
    
    def __init__(
        self,
        message: str,
        scaffold_name: Optional[str] = None,
        config_key: Optional[str] = None,
        config_value: Optional[Any] = None,
        valid_values: Optional[List[str]] = None,
        **kwargs
    ):
        """
        Initialize scaffold configuration error.
        
        Args:
            message: Error message
            scaffold_name: Name of misconfigured scaffold
            config_key: Configuration key that is invalid
            config_value: Invalid configuration value
            valid_values: List of valid values for the configuration
            **kwargs: Additional context passed to parent
        """
        # Build context with configuration information
        context = kwargs.pop('context', {})
        if config_key:
            context['config_key'] = config_key
        if config_value is not None:
            context['config_value'] = str(config_value)[:100]
        if valid_values:
            context['valid_values'] = ", ".join(str(v) for v in valid_values[:10])
        
        super().__init__(
            message=message,
            scaffold_name=scaffold_name,
            context=context,
            **kwargs
        )
        
        self.config_key = config_key
        self.config_value = config_value
        self.valid_values = valid_values or []


class ScaffoldAccessError(ScaffoldError):
    """
    Exception for scaffold access and proxy errors.
    
    Raised when scaffolds cannot be accessed through the ScaffoldAccessor
    or when proxy operations fail.
    """
    
    def __init__(
        self,
        message: str,
        scaffold_name: Optional[str] = None,
        access_path: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize scaffold access error.
        
        Args:
            message: Error message
            scaffold_name: Name of scaffold being accessed
            access_path: Full access path (e.g., "agent.scaffolds.task_manager.add_task")
            **kwargs: Additional context passed to parent
        """
        # Build context with access information
        context = kwargs.pop('context', {})
        if access_path:
            context['access_path'] = access_path
        
        super().__init__(
            message=message,
            scaffold_name=scaffold_name,
            context=context,
            **kwargs
        )
        
        self.access_path = access_path


class ScaffoldValidationError(ScaffoldError):
    """
    Exception for scaffold validation errors.
    
    Raised when scaffold implementations don't meet required interfaces,
    have invalid operations, or fail validation checks.
    """
    
    def __init__(
        self,
        message: str,
        scaffold_name: Optional[str] = None,
        validation_failures: Optional[List[str]] = None,
        **kwargs
    ):
        """
        Initialize scaffold validation error.
        
        Args:
            message: Error message
            scaffold_name: Name of scaffold that failed validation
            validation_failures: List of specific validation failures
            **kwargs: Additional context passed to parent
        """
        # Build context with validation information
        context = kwargs.pop('context', {})
        if validation_failures:
            context['validation_failures'] = "; ".join(validation_failures[:5])
        
        super().__init__(
            message=message,
            scaffold_name=scaffold_name,
            context=context,
            **kwargs
        )
        
        self.validation_failures = validation_failures or []


class ScaffoldDefinitionError(ScaffoldError):
    """
    Exception for scaffold class definition errors.
    
    Raised when scaffold classes are defined incorrectly or are missing
    required properties like 'type' and 'state'.
    """
    
    def __init__(
        self,
        message: str,
        scaffold_name: str,
        missing_properties: Optional[List[str]] = None,
        invalid_properties: Optional[Dict[str, str]] = None,
        **kwargs
    ):
        """
        Initialize scaffold definition error.
        
        Args:
            message: Error message
            scaffold_name: Name of scaffold class that failed definition validation
            missing_properties: List of required properties that are missing
            invalid_properties: Dict mapping property names to validation failure reasons
            **kwargs: Additional context passed to parent
        """
        # Build helpful error message with hints
        error_parts = [message]
        
        if missing_properties:
            error_parts.append("\nMissing required properties:")
            for prop in missing_properties:
                if prop == 'type':
                    error_parts.append(f"  - Add: type: str = 'my_scaffold_name'")
                elif prop == 'state':
                    error_parts.append(f"  - Add: state: MyState = MyState()  # where MyState inherits from ScaffoldState")
                else:
                    error_parts.append(f"  - Add: {prop}")
        
        if invalid_properties:
            error_parts.append("\nInvalid property definitions:")
            for prop, reason in invalid_properties.items():
                error_parts.append(f"  - {prop}: {reason}")
        
        # Add example
        error_parts.append("\nExample valid scaffold:")
        error_parts.append("  class MyScaffold(BaseContextScaffold):")
        error_parts.append("      type: str = 'my_scaffold'")
        error_parts.append("      state: MyState = MyState()")
        error_parts.append("      def render(self) -> str: ...")
        
        enhanced_message = "\n".join(error_parts)
        
        # Build context
        context = kwargs.pop('context', {})
        if missing_properties:
            context['missing_properties'] = ", ".join(missing_properties)
        if invalid_properties:
            context['invalid_properties'] = ", ".join(invalid_properties.keys())
        
        super().__init__(
            message=enhanced_message,
            scaffold_name=scaffold_name,
            context=context,
            **kwargs
        )
        
        self.missing_properties = missing_properties or []
        self.invalid_properties = invalid_properties or {}


# Convenience functions for creating common errors

def scaffold_not_found_error(
    scaffold_name: str, 
    available_scaffolds: Optional[List[str]] = None
) -> ScaffoldRegistrationError:
    """
    Create a standard 'scaffold not found' error.
    
    Args:
        scaffold_name: Name of missing scaffold
        available_scaffolds: List of available scaffold names
        
    Returns:
        ScaffoldRegistrationError with appropriate message
    """
    if available_scaffolds:
        message = f"Scaffold '{scaffold_name}' not found. Available scaffolds: {', '.join(available_scaffolds)}"
    else:
        message = f"Scaffold '{scaffold_name}' not found"
    
    return ScaffoldRegistrationError(
        message=message,
        scaffold_name=scaffold_name,
        available_scaffolds=available_scaffolds
    )


def operation_not_found_error(
    scaffold_name: str,
    operation_name: str,
    available_operations: Optional[List[str]] = None
) -> ScaffoldOperationError:
    """
    Create a standard 'operation not found' error.
    
    Args:
        scaffold_name: Name of scaffold
        operation_name: Name of missing operation
        available_operations: List of available operation names
        
    Returns:
        ScaffoldOperationError with appropriate message
    """
    if available_operations:
        message = f"Operation '{operation_name}' not found on scaffold '{scaffold_name}'. Available operations: {', '.join(available_operations)}"
    else:
        message = f"Operation '{operation_name}' not found on scaffold '{scaffold_name}'"
    
    return ScaffoldOperationError(
        message=message,
        scaffold_name=scaffold_name,
        operation_name=operation_name,
        context={'available_operations': ', '.join(available_operations or [])}
    )


def invalid_state_error(
    scaffold_name: str,
    state_key: str,
    state_value: Any,
    reason: str
) -> ScaffoldStateError:
    """
    Create a standard 'invalid state' error.
    
    Args:
        scaffold_name: Name of scaffold
        state_key: Invalid state key
        state_value: Invalid state value
        reason: Reason why the state is invalid
        
    Returns:
        ScaffoldStateError with appropriate message
    """
    message = f"Invalid state for key '{state_key}': {reason}"
    
    return ScaffoldStateError(
        message=message,
        scaffold_name=scaffold_name,
        state_key=state_key,
        state_value=state_value
    )