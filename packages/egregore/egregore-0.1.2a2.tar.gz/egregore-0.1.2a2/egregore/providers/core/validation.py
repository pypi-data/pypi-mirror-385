"""
Validation utilities for provider interface.

This module provides helper functions for validating provider parameters,
capabilities, and configurations.
"""

from typing import Dict, Any, List, Set, Optional, Type, Union
from .exceptions import InvalidConfiguration, ModelNotSupported, ToolsNotSupported


def validate_provider_params(params: Dict[str, Any], supported_params: Set[str]) -> List[str]:
    """
    Validate provider-specific parameters.
    
    Args:
        params: Dictionary of parameters to validate
        supported_params: Set of parameter names supported by the provider
        
    Returns:
        List of invalid parameter names (empty if all valid)
    """
    # Exclude manager-level parameters that shouldn't be validated
    manager_params = {'cost_priority', 'provider_name', 'fallback_provider'}
    
    invalid_params = []
    for param_name in params.keys():
        if param_name not in supported_params and param_name not in manager_params:
            invalid_params.append(param_name)
    
    return invalid_params


def validate_model_support(model: str, available_models: List[str], provider_name: str) -> None:
    """
    Validate that a model is supported by the provider.
    
    Args:
        model: Model name to validate
        available_models: List of models supported by the provider
        provider_name: Name of the provider for error messages
        
    Raises:
        ModelNotSupported: If model is not in available_models list
    """
    if model not in available_models:
        raise ModelNotSupported(model, provider_name, available_models)


def validate_tools_support(tools_requested: bool, tools_supported: bool, provider_name: str) -> None:
    """
    Validate that tools are supported if requested.
    
    Args:
        tools_requested: Whether tools were requested
        tools_supported: Whether provider supports tools
        provider_name: Name of the provider for error messages
        
    Raises:
        ToolsNotSupported: If tools requested but not supported
    """
    if tools_requested and not tools_supported:
        raise ToolsNotSupported(provider_name)


def validate_configuration_params(params: Dict[str, Any], provider_name: str, supported_params: Set[str]) -> None:
    """
    Validate configuration parameters and raise exception if invalid.
    
    Args:
        params: Dictionary of parameters to validate
        provider_name: Name of the provider for error messages
        supported_params: Set of parameter names supported by the provider
        
    Raises:
        InvalidConfiguration: If any parameters are invalid
    """
    invalid_params = validate_provider_params(params, supported_params)
    if invalid_params:
        raise InvalidConfiguration(invalid_params, provider_name, supported_params)


def validate_required_fields(data: Dict[str, Any], required_fields: List[str], context: str = "data") -> None:
    """
    Validate that required fields are present in data dictionary.
    
    Args:
        data: Dictionary to validate
        required_fields: List of required field names
        context: Context description for error messages
        
    Raises:
        ValueError: If any required fields are missing
    """
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None:
            missing_fields.append(field)
    
    if missing_fields:
        fields_str = ", ".join(missing_fields)
        raise ValueError(f"Missing required fields in {context}: {fields_str}")


def validate_response_format(response: Any, required_attributes: List[str]) -> bool:
    """
    Validate that a response object has required attributes.
    
    Args:
        response: Response object to validate
        required_attributes: List of required attribute names
        
    Returns:
        True if valid, False otherwise
    """
    if response is None:
        return False
    
    for attr in required_attributes:
        # Check if the attribute exists on the response object
        if not hasattr(response, attr):
            return False
    
    return True


def sanitize_model_name(model_name: str) -> str:
    """
    Sanitize model name to ensure it's valid.
    
    Args:
        model_name: Raw model name
        
    Returns:
        Sanitized model name
    """
    if not isinstance(model_name, str):
        return str(model_name)
    
    # Remove any whitespace and convert to lowercase for consistency
    sanitized = model_name.strip().lower()
    
    # Ensure it's not empty
    if not sanitized:
        raise ValueError("Model name cannot be empty")
    
    return sanitized


def validate_stream_chunk(chunk: Any, required_fields: List[str] = None) -> bool:
    """
    Validate that a stream chunk has required structure.
    
    Args:
        chunk: Stream chunk to validate
        required_fields: List of required field names (defaults to ['delta'])
        
    Returns:
        True if valid, False otherwise
    """
    if required_fields is None:
        required_fields = ['delta']
    
    if chunk is None:
        return False
    
    # Check if it has the required fields
    for field in required_fields:
        if not hasattr(chunk, field):
            return False
    
    return True


def validate_content_blocks(content: Any) -> bool:
    """
    Validate that content follows ContentBlock structure.
    
    This is a placeholder until ContentBlock types are implemented.
    
    Args:
        content: Content to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Placeholder validation - will be updated when ContentBlock types are available
    if content is None:
        return False
    
    # For now, accept either string content or list of content blocks
    if isinstance(content, str):
        return len(content.strip()) > 0
    
    if isinstance(content, list):
        return len(content) > 0
    
    return False


class ParameterValidator:
    """
    Reusable parameter validator for providers.
    
    This class can be instantiated by providers to validate their specific
    parameter requirements.
    """
    
    def __init__(self, provider_name: str, supported_params: Set[str]):
        """
        Initialize validator for a specific provider.
        
        Args:
            provider_name: Name of the provider
            supported_params: Set of parameter names supported by this provider
        """
        self.provider_name = provider_name
        self.supported_params = supported_params
    
    def validate(self, params: Dict[str, Any]) -> None:
        """
        Validate parameters for this provider.
        
        Args:
            params: Parameters to validate
            
        Raises:
            InvalidConfiguration: If parameters are invalid
        """
        validate_configuration_params(params, self.provider_name, self.supported_params)
    
    def is_valid(self, params: Dict[str, Any]) -> bool:
        """
        Check if parameters are valid without raising exception.
        
        Args:
            params: Parameters to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            self.validate(params)
            return True
        except InvalidConfiguration:
            return False
    
    def get_invalid_params(self, params: Dict[str, Any]) -> List[str]:
        """
        Get list of invalid parameter names.
        
        Args:
            params: Parameters to validate
            
        Returns:
            List of invalid parameter names
        """
        return validate_provider_params(params, self.supported_params)


# Structured Output Validation Functions

def validate_result_type(result_type: Optional[Type[Any]]) -> bool:
    """
    Validate that a result_type is acceptable for structured output.
    
    Checks if the provided type can be used for structured output generation.
    Supports dict, dataclass, Pydantic BaseModel, and native Python types.
    
    Args:
        result_type: The type to validate for structured output
        
    Returns:
        True if valid, False otherwise
        
    Examples:
        >>> validate_result_type(dict)
        True
        >>> validate_result_type(str)
        True
        >>> from typing import List
        >>> validate_result_type(List[str])
        True
        >>> validate_result_type(None)
        True
    """
    if result_type is None:
        return True
    
    # Import here to avoid circular imports
    from .structured_output import _classify_result_type
    
    try:
        # If we can classify it, it's valid
        category = _classify_result_type(result_type)
        return category in ["dict", "dataclass", "pydantic", "native"]
    except Exception:
        return False


def validate_structured_response(response: Any, expected_type: Type[Any]) -> bool:
    """
    Validate that a structured response matches the expected type.
    
    Performs type checking to ensure the parsed result matches what was
    requested. Provides confidence scoring for the match quality.
    
    Args:
        response: The response to validate
        expected_type: The expected type of the response
        
    Returns:
        True if response matches expected type, False otherwise
        
    Examples:
        >>> validate_structured_response({"name": "test"}, dict)
        True
        >>> validate_structured_response("hello", str)
        True
        >>> validate_structured_response(42, str)
        False
    """
    if response is None:
        return False
    
    try:
        # Import here to avoid circular imports
        from .structured_output import _classify_result_type
        
        category = _classify_result_type(expected_type)
        
        if category == "dict":
            return isinstance(response, dict)
        elif category == "native":
            if expected_type == str:
                return isinstance(response, str)
            elif expected_type == int:
                return isinstance(response, int)
            elif expected_type == float:
                return isinstance(response, (int, float))
            elif expected_type == bool:
                return isinstance(response, bool)
            else:
                # For complex types like List[str], try isinstance check
                try:
                    return isinstance(response, expected_type)
                except TypeError:
                    # Some generic types can't be used with isinstance
                    return True  # Assume valid for complex generic types
        elif category == "dataclass":
            return isinstance(response, expected_type)
        elif category == "pydantic":
            return isinstance(response, expected_type)
        
        return False
        
    except Exception:
        return False


def validate_outlines_availability() -> bool:
    """
    Check if JSON parsing is available (always True as json is stdlib).

    Legacy function name kept for backwards compatibility.
    JSON parsing is always available as it uses Python's built-in json module.

    Returns:
        True (json module is always available in Python)

    Examples:
        >>> validate_outlines_availability()  # doctest: +SKIP
        True
    """
    return True


def validate_streaming_structured_output(
    result_type: Optional[Type[Any]], 
    model_capabilities: Optional[Any] = None
) -> Union[bool, str]:
    """
    Validate that streaming structured output is supported for the given configuration.
    
    Streaming structured output requires native provider support since no fallback
    mechanisms are available for streaming. This function validates the configuration.
    
    Args:
        result_type: The requested result type
        model_capabilities: Model capabilities object (optional)
        
    Returns:
        True if valid, error message string if invalid
        
    Examples:
        >>> validate_streaming_structured_output(None)
        True
        >>> validate_streaming_structured_output(dict, None)
        'Streaming structured output requires native model support'
    """
    # No result_type means no structured output - always valid
    if result_type is None:
        return True
    
    # If we don't have capabilities info, we can't validate native support
    if model_capabilities is None:
        return "Streaming structured output requires native model support"
    
    # Check if model supports native structured output
    try:
        if hasattr(model_capabilities, 'structured_output_native'):
            if model_capabilities.structured_output_native:
                return True
            else:
                return "Model does not support native structured output required for streaming"
        else:
            return "Cannot determine model structured output capabilities"
    except Exception:
        return "Error accessing model capabilities"


def validate_structured_output_request(
    result_type: Optional[Type[Any]], 
    is_streaming: bool = False,
    model_capabilities: Optional[Any] = None
) -> Union[bool, str]:
    """
    Comprehensive validation for structured output requests.
    
    Validates all aspects of a structured output request including type validity,
    streaming compatibility, and model capabilities.
    
    Args:
        result_type: The requested result type
        is_streaming: Whether this is for a streaming operation
        model_capabilities: Model capabilities object (optional)
        
    Returns:
        True if valid, error message string if invalid
        
    Examples:
        >>> validate_structured_output_request(dict, False)
        True
        >>> validate_structured_output_request(dict, True, None)
        'Streaming structured output requires native model support'
    """
    # Validate the result type itself
    if not validate_result_type(result_type):
        return f"Invalid result type: {result_type}"
    
    # No result_type means no structured output - always valid
    if result_type is None:
        return True
    
    # For streaming operations, check native support
    if is_streaming:
        streaming_validation = validate_streaming_structured_output(result_type, model_capabilities)
        if streaming_validation is not True:
            return streaming_validation
    
    # For non-streaming, check if JSON parsing is available as fallback
    if not is_streaming:
        if not validate_outlines_availability():
            # Check if model has native support
            if model_capabilities and hasattr(model_capabilities, 'structured_output_native'):
                if not model_capabilities.structured_output_native:
                    return "Neither native structured output nor JSON parsing fallback available"
            else:
                return "JSON parsing not available for structured output fallback"
    
    return True