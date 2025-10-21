"""
Consolidated exception classes for universal provider system.

Combines exceptions from three sources:
1. core/provider/base/exceptions.py - Base provider exceptions
2. general_purpose/exceptions.py - General Purpose provider exceptions  
3. core/provider/provider_management/exceptions.py - Rate limiting exceptions
"""

from typing import Optional, List, Set

# ===========================================
# FROM core/provider/base/exceptions.py - Base Provider Exceptions
# ===========================================

class ProviderError(Exception):
    """Base exception for all provider-related errors"""
    
    def __init__(self, message: str, provider_name: str = "", original_error: Optional[Exception] = None):
        super().__init__(message)
        self.provider_name = provider_name
        self.original_error = original_error
        self.message = message


class ModelNotSupported(ProviderError):
    """Raised when a requested model is not available for this provider"""
    
    def __init__(self, model: str, provider_name: str = "", available_models: Optional[List[str]] = None):
        available_str = ""
        if available_models:
            available_str = f" Available models: {', '.join(available_models[:5])}"
            if len(available_models) > 5:
                available_str += f" and {len(available_models) - 5} more"
        
        message = f"Model '{model}' not supported by {provider_name}{available_str}"
        super().__init__(message, provider_name)
        self.model = model
        self.available_models = available_models or []


class ToolsNotSupported(ProviderError):
    """Raised when tools are requested but provider doesn't support them"""
    
    def __init__(self, provider_name: str = ""):
        message = f"Tool calling not supported by {provider_name}"
        super().__init__(message, provider_name)


class InvalidConfiguration(ProviderError):
    """Raised when invalid configuration parameters are provided"""
    
    def __init__(self, invalid_params: List[str], provider_name: str = "", supported_params: Optional[Set[str]] = None):
        params_str = ", ".join(invalid_params)
        message = f"Invalid parameters for {provider_name}: {params_str}"
        
        if supported_params:
            supported_str = ", ".join(sorted(supported_params))
            message += f". Supported parameters: {supported_str}"
        
        super().__init__(message, provider_name)
        self.invalid_params = invalid_params
        self.supported_params = supported_params or set()


class RateLimitError(ProviderError):
    """Raised when provider rate limits are exceeded"""
    
    def __init__(self, provider_name: str = "", retry_after: Optional[int] = None):
        message = f"Rate limit exceeded for {provider_name}"
        if retry_after:
            message += f". Retry after {retry_after} seconds"
        
        super().__init__(message, provider_name)
        self.retry_after = retry_after


class AuthenticationError(ProviderError):
    """Raised when provider authentication fails"""
    
    def __init__(self, provider_name: str = "", details: str = ""):
        message = f"Authentication failed for {provider_name}"
        if details:
            message += f": {details}"
        
        super().__init__(message, provider_name)
        self.details = details


class ProviderUnavailableError(ProviderError):
    """Raised when provider is temporarily unavailable (circuit breaker, maintenance, etc.)"""
    
    def __init__(self, provider_name: str = "", reason: str = ""):
        message = f"Provider {provider_name} is temporarily unavailable"
        if reason:
            message += f": {reason}"
        
        super().__init__(message, provider_name)
        self.reason = reason


class ProviderExecutionError(ProviderError):
    """Raised when provider execution fails after retries"""
    
    def __init__(self, provider_name: str = "", details: str = "", original_error: Optional[Exception] = None):
        message = f"Provider {provider_name} execution failed"
        if details:
            message += f": {details}"
        
        super().__init__(message, provider_name, original_error)
        self.details = details


class TranslationError(ProviderError):
    """Raised when provider translation (to/from native format) fails"""
    
    def __init__(self, direction: str, provider_name: str = "", details: str = ""):
        message = f"Translation error ({direction}) for {provider_name}"
        if details:
            message += f": {details}"
        
        super().__init__(message, provider_name)
        self.direction = direction
        self.details = details


class StreamingError(ProviderError):
    """Raised when streaming operations fail"""
    
    def __init__(self, provider_name: str = "", details: str = "", partial_content: str = ""):
        message = f"Streaming error for {provider_name}"
        if details:
            message += f": {details}"
        
        super().__init__(message, provider_name)
        self.details = details
        self.partial_content = partial_content


# Provider Manager specific exceptions

class NoCapableProviderError(Exception):
    """Raised when no provider can meet the specified requirements"""
    
    def __init__(self, requirements: dict, available_providers: Optional[List[str]] = None):
        req_str = ", ".join(f"{k}={v}" for k, v in requirements.items())
        message = f"No provider meets requirements: {req_str}"
        
        if available_providers:
            providers_str = ", ".join(available_providers)
            message += f". Available providers: {providers_str}"
        
        super().__init__(message)
        self.requirements = requirements
        self.available_providers = available_providers or []


class ProviderCapabilityError(Exception):
    """Raised when provider doesn't support requested capability"""
    
    def __init__(self, capability: str, provider_name: str = ""):
        message = f"Capability '{capability}' not supported by {provider_name}"
        super().__init__(message)
        self.capability = capability
        self.provider_name = provider_name


class StructuredOutputError(ProviderError):
    """Raised when structured output processing fails"""
    
    def __init__(self, result_type: str, provider_name: str = "", details: str = "", fallback_failed: bool = False):
        message = f"Structured output failed for type '{result_type}'"
        if provider_name:
            message += f" with {provider_name}"
        if details:
            message += f": {details}"
        if fallback_failed:
            message += " (fallback also failed)"
        
        super().__init__(message, provider_name)
        self.result_type = result_type
        self.details = details
        self.fallback_failed = fallback_failed


class UnsupportedMediaTypeError(ProviderError):
    """Raised when a media type is not supported by the model or provider"""
    
    def __init__(self, media_type: str, model: str = "", provider_name: str = "", supported_types: Optional[List[str]] = None):
        message = f"Media type '{media_type}' not supported"
        if model:
            message += f" by model '{model}'"
        if provider_name:
            message += f" with {provider_name}"
            
        if supported_types:
            types_str = ", ".join(supported_types)
            message += f". Supported types: {types_str}"
        
        super().__init__(message, provider_name)
        self.media_type = media_type
        self.model = model
        self.supported_types = supported_types or []


class InvalidMediaFormatError(ProviderError):
    """Raised when media format is invalid or corrupted"""
    
    def __init__(self, media_type: str, format_error: str = "", provider_name: str = ""):
        message = f"Invalid {media_type} format"
        if format_error:
            message += f": {format_error}"
        if provider_name:
            message += f" for {provider_name}"
            
        super().__init__(message, provider_name)
        self.media_type = media_type
        self.format_error = format_error

# ===========================================
# FROM general_purpose/exceptions.py - General Purpose Provider Exceptions
# ===========================================

class GeneralPurposeError(ProviderError):
    """Base exception for General Purpose provider errors."""
    pass


class GeneralPurposeModelError(GeneralPurposeError):
    """Exception for model-related errors in General Purpose provider."""
    pass


class GeneralPurposeConfigError(GeneralPurposeError):
    """Exception for configuration errors in General Purpose provider."""
    pass


class GeneralPurposeAuthError(GeneralPurposeError):
    """Exception for authentication errors in General Purpose provider."""
    pass


def map_anyllm_error(error: Exception, provider_name: str) -> GeneralPurposeError:
    """Map any-llm errors to General Purpose provider errors.
    
    Args:
        error: The original any-llm error
        provider_name: Name of the specific provider backend
        
    Returns:
        Mapped GeneralPurposeError
    """
    error_str = str(error).lower()
    
    # Check for authentication errors
    if any(auth_term in error_str for auth_term in ['auth', 'unauthorized', 'api key', 'token']):
        return GeneralPurposeAuthError(f"Authentication error for {provider_name}: {str(error)}")
    
    # Check for model errors
    if any(model_term in error_str for model_term in ['model', 'not found', 'invalid model']):
        return GeneralPurposeModelError(f"Model error for {provider_name}: {str(error)}")
    
    # Check for configuration errors
    if any(config_term in error_str for config_term in ['config', 'parameter', 'invalid']):
        return GeneralPurposeConfigError(f"Configuration error for {provider_name}: {str(error)}")
    
    # Default to base error
    return GeneralPurposeError(f"AnyLLM error for {provider_name}: {str(error)}")

# ===========================================
# FROM core/provider/provider_management/exceptions.py - Rate Limiting Exceptions
# ===========================================

class ProviderManagerError(Exception):
    """Base provider manager error"""


class RateLimitExceededError(ProviderManagerError):
    """Rate limit exceeded for provider"""


class CircuitBreakerOpenError(ProviderManagerError):
    """Circuit breaker is open for provider"""


class MaxRetriesExceededError(ProviderManagerError):
    """Maximum retry attempts exceeded"""

# ===========================================
# CONSOLIDATED EXPORTS
# ===========================================

__all__ = [
    # Base provider exceptions
    'ProviderError', 'ModelNotSupported', 'ToolsNotSupported', 'InvalidConfiguration',
    'RateLimitError', 'AuthenticationError', 'ProviderUnavailableError', 'ProviderExecutionError',
    'TranslationError', 'StreamingError', 'NoCapableProviderError', 'ProviderCapabilityError',
    'StructuredOutputError', 'UnsupportedMediaTypeError', 'InvalidMediaFormatError',
    
    # General purpose provider exceptions
    'GeneralPurposeError', 'GeneralPurposeModelError', 'GeneralPurposeConfigError', 
    'GeneralPurposeAuthError', 'map_anyllm_error',
    
    # Rate limiting exceptions
    'ProviderManagerError', 'RateLimitExceededError', 'CircuitBreakerOpenError', 
    'MaxRetriesExceededError'
]