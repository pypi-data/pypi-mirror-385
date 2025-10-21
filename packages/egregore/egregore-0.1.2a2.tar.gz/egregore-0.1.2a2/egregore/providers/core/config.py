"""Universal configuration validation for General Purpose provider."""

from typing import TypedDict, Optional, Union, List, Dict, Any


class GeneralPurposeProviderConfig(TypedDict, total=False):
    """Provider-level configuration for General Purpose provider (Agent initialization)."""
    api_key: str                    # Provider API key
    organization: Optional[str]     # Organization ID (provider-specific)
    base_url: Optional[str]         # Custom API endpoint
    timeout: Optional[float]        # Request timeout in seconds (default: 120)
    max_retries: Optional[int]      # Maximum retry attempts (default: 3)
    default_model: Optional[str]    # Default model when none specified


class GeneralPurposeModelConfig(TypedDict, total=False):
    """Model-level configuration for General Purpose provider (per request)."""
    temperature: Optional[float]                    # Sampling temperature (0.0-2.0)
    max_tokens: Optional[int]                       # Response length limit
    top_p: Optional[float]                          # Nucleus sampling (0.0-1.0)
    frequency_penalty: Optional[float]              # Frequency penalty (-2.0 to 2.0)
    presence_penalty: Optional[float]               # Presence penalty (-2.0 to 2.0)
    stop: Optional[Union[str, List[str]]]           # Stop sequences
    seed: Optional[int]                             # Reproducibility seed
    stream: Optional[bool]                          # Streaming response


def validate_provider_config(provider_name: str, config: Dict[str, Any]) -> None:
    """Validate provider-specific configuration.
    
    Args:
        provider_name: Name of the specific provider backend
        config: Configuration dictionary to validate
        
    Raises:
        ValueError: If configuration is invalid
    """
    errors = _validate_provider_config_dict(provider_name, config)
    if errors:
        error_messages = [f"{key}: {msg}" for key, msg in errors.items()]
        raise ValueError(f"Invalid {provider_name} provider config: {'; '.join(error_messages)}")


def validate_model_config(provider_name: str, config: Dict[str, Any]) -> None:
    """Validate model-specific configuration.
    
    Args:
        provider_name: Name of the specific provider backend  
        config: Configuration dictionary to validate
        
    Raises:
        ValueError: If configuration is invalid
    """
    errors = _validate_model_config_dict(provider_name, config)
    if errors:
        error_messages = [f"{key}: {msg}" for key, msg in errors.items()]
        raise ValueError(f"Invalid {provider_name} model config: {'; '.join(error_messages)}")


def _validate_provider_config_dict(provider_name: str, config: Dict[str, Any]) -> Dict[str, str]:
    """Validate provider configuration and return error messages."""
    errors = {}
    
    if not config:
        return errors
    
    # Validate API key (universal)
    api_key = config.get("api_key")
    if api_key is not None:
        if not isinstance(api_key, str):
            errors["api_key"] = "API key must be a string"
        elif not api_key.strip():
            errors["api_key"] = "API key cannot be empty"
        else:
            # Provider-specific API key validation
            errors.update(_validate_provider_specific_api_key(provider_name, api_key))
    
    # Validate base_url (universal)
    base_url = config.get("base_url")
    if base_url is not None:
        if not isinstance(base_url, str):
            errors["base_url"] = "Base URL must be a string"
        elif not base_url.strip():
            errors["base_url"] = "Base URL cannot be empty"
        elif not (base_url.startswith("http://") or base_url.startswith("https://")):
            errors["base_url"] = "Base URL must start with http:// or https://"
    
    # Validate timeout (universal)
    timeout = config.get("timeout")
    if timeout is not None:
        if not isinstance(timeout, (int, float)):
            errors["timeout"] = "Timeout must be a number"
        elif timeout <= 0:
            errors["timeout"] = "Timeout must be positive"
        elif timeout > 600:
            errors["timeout"] = "Timeout cannot exceed 600 seconds"
    
    # Validate max_retries (universal)
    max_retries = config.get("max_retries")
    if max_retries is not None:
        if not isinstance(max_retries, int):
            errors["max_retries"] = "Max retries must be an integer"
        elif max_retries < 0:
            errors["max_retries"] = "Max retries cannot be negative"
        elif max_retries > 10:
            errors["max_retries"] = "Max retries cannot exceed 10"
    
    return errors


def _validate_model_config_dict(provider_name: str, config: Dict[str, Any]) -> Dict[str, str]:
    """Validate model configuration and return error messages."""
    errors = {}
    
    if not config:
        return errors
    
    # Validate temperature (universal)
    temperature = config.get("temperature")
    if temperature is not None:
        if not isinstance(temperature, (int, float)):
            errors["temperature"] = "Temperature must be a number"
        elif temperature < 0.0 or temperature > 2.0:
            errors["temperature"] = "Temperature must be between 0.0 and 2.0"
    
    # Validate max_tokens (universal)
    max_tokens = config.get("max_tokens")
    if max_tokens is not None:
        if not isinstance(max_tokens, int):
            errors["max_tokens"] = "Max tokens must be an integer"
        elif max_tokens <= 0:
            errors["max_tokens"] = "Max tokens must be positive"
        elif max_tokens > 200000:
            errors["max_tokens"] = "Max tokens cannot exceed 200,000"
    
    # Validate top_p (universal)
    top_p = config.get("top_p")
    if top_p is not None:
        if not isinstance(top_p, (int, float)):
            errors["top_p"] = "Top-p must be a number"
        elif top_p < 0.0 or top_p > 1.0:
            errors["top_p"] = "Top-p must be between 0.0 and 1.0"
    
    return errors


def _validate_provider_specific_api_key(provider_name: str, api_key: str) -> Dict[str, str]:
    """Validate provider-specific API key formats."""
    errors = {}
    
    if provider_name == "openai":
        if not api_key.startswith("sk-"):
            errors["api_key"] = "OpenAI API key must start with 'sk-'"
    elif provider_name == "anthropic":
        if not api_key.startswith("sk-ant-"):
            errors["api_key"] = "Anthropic API key must start with 'sk-ant-'"
    elif provider_name == "google":
        # Google API keys can have various formats, less strict validation
        if len(api_key) < 10:
            errors["api_key"] = "Google API key appears too short"
    # Add more provider-specific validations as needed
    
    return errors