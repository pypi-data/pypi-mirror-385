"""
Standardized parameter types for provider interface.

This module defines the standardized parameters that agents pass to providers,
ensuring consistent parameter names across all providers while allowing
provider-specific extensions and translations.
"""

from typing import Dict, Any, Optional, Union, Literal
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class ReasoningEffort(str, Enum):
    """Standard reasoning effort levels for reasoning models."""
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"


class StandardParameters(BaseModel):
    """
    Standardized parameters that agents pass to providers.
    
    These parameters have consistent names across all providers, but each provider
    translates them to their native API parameter names in translate_to_native().
    """
    
    # Core generation parameters (universally supported)
    max_tokens: Optional[int] = Field(
        None,
        description="Maximum number of tokens to generate",
        ge=1,
        le=200000
    )
    
    temperature: Optional[float] = Field(
        None,
        description="Sampling temperature (0.0-2.0). Higher values = more random",
        ge=0.0,
        le=2.0
    )
    
    top_p: Optional[float] = Field(
        None,
        description="Nucleus sampling parameter (0.0-1.0)",
        ge=0.0,
        le=1.0
    )
    
    frequency_penalty: Optional[float] = Field(
        None,
        description="Frequency penalty (-2.0 to 2.0). Positive values discourage repetition",
        ge=-2.0,
        le=2.0
    )
    
    presence_penalty: Optional[float] = Field(
        None,
        description="Presence penalty (-2.0 to 2.0). Positive values encourage new topics",
        ge=-2.0,
        le=2.0
    )
    
    # Special parameters
    reasoning_effort: Optional[ReasoningEffort] = Field(
        None,
        description="Effort level for reasoning models (low/medium/high)"
    )
    
    stop: Optional[Union[str, list[str]]] = Field(
        None,
        description="Stop sequences to end generation"
    )
    
    seed: Optional[int] = Field(
        None,
        description="Random seed for reproducible outputs",
        ge=0
    )
    
    # Logit bias for token-level control
    logit_bias: Optional[Dict[str, float]] = Field(
        None,
        description="Token bias adjustments (token_id -> bias_value)"
    )
    
    @field_validator('stop')
    @classmethod
    def validate_stop_sequences(cls, v):
        """Validate stop sequences format."""
        if v is None:
            return v
        if isinstance(v, str):
            return v
        if isinstance(v, list) and all(isinstance(s, str) for s in v):
            return v
        raise ValueError("stop must be a string or list of strings")
    
    def model_dump_non_none(self) -> Dict[str, Any]:
        """Return only parameters that are not None."""
        return {k: v for k, v in self.model_dump().items() if v is not None}


class ProviderParameterDefaults(BaseModel):
    """Default parameter values for a specific provider."""
    
    # Provider name
    provider: str = Field(..., description="Provider identifier")
    
    # Default values for standard parameters
    max_tokens: int = Field(4096, description="Default max tokens")
    temperature: float = Field(0.7, description="Default temperature")
    top_p: float = Field(1.0, description="Default top_p")
    frequency_penalty: float = Field(0.0, description="Default frequency penalty")
    presence_penalty: float = Field(0.0, description="Default presence penalty")
    reasoning_effort: ReasoningEffort = Field(
        ReasoningEffort.MEDIUM, 
        description="Default reasoning effort"
    )
    
    # Provider-specific parameter mappings
    parameter_mappings: Dict[str, str] = Field(
        default_factory=dict,
        description="Map standard parameter names to provider-specific names"
    )
    
    # Parameters that should be excluded for this provider
    excluded_parameters: set[str] = Field(
        default_factory=set,
        description="Standard parameters this provider doesn't support"
    )


# Standard provider defaults
PROVIDER_DEFAULTS = {
    "openai": ProviderParameterDefaults(
        provider="openai",
        max_tokens=4096,
        temperature=0.7,
        parameter_mappings={
            # Most OpenAI parameters map directly, but reasoning models need special handling
            "max_tokens": "max_tokens",  # May become max_completion_tokens for o1 models
        },
        excluded_parameters=set()
    ),
    
    "anthropic": ProviderParameterDefaults(
        provider="anthropic",
        max_tokens=8000,  # Anthropic typical default
        temperature=0.5,
        parameter_mappings={
            "max_tokens": "max_tokens",
            "temperature": "temperature",
        },
        excluded_parameters=set()
    ),
    
    "google": ProviderParameterDefaults(
        provider="google",
        max_tokens=8192,
        temperature=0.9,
        parameter_mappings={
            "max_tokens": "max_output_tokens",  # Google uses different parameter name
            "temperature": "temperature",
        },
        excluded_parameters=set()
    ),
}


def get_provider_defaults(provider_name: str) -> ProviderParameterDefaults:
    """Get parameter defaults for a specific provider."""
    if provider_name not in PROVIDER_DEFAULTS:
        # Return generic defaults for unknown providers
        return ProviderParameterDefaults(
            provider=provider_name,
            parameter_mappings={},
            excluded_parameters=set()
        )
    return PROVIDER_DEFAULTS[provider_name]


def merge_parameters(
    standard_params: StandardParameters,
    provider_specific: Dict[str, Any],
    provider_defaults: ProviderParameterDefaults,
    model_config_standard: Optional[StandardParameters] = None,
    model_config_specific: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Merge parameters with 3-tier priority system.
    
    Priority (highest to lowest):
    1. standard_params + provider_specific (from agent.call(**kwargs))
    2. model_config_standard + model_config_specific (from provider_config.model_config)  
    3. provider_defaults (built-in provider defaults)
    
    Args:
        standard_params: Standardized parameters from agent.call()
        provider_specific: Provider-specific parameters from agent.call()
        provider_defaults: Default values for this provider
        model_config_standard: Standardized parameters from provider_config.model_config
        model_config_specific: Provider-specific parameters from provider_config.model_config
        
    Returns:
        Merged parameter dictionary with 3-tier priority applied
    """
    # Start with provider defaults (lowest priority)
    result = {}
    
    # Add non-excluded defaults
    if "max_tokens" not in provider_defaults.excluded_parameters:
        result["max_tokens"] = provider_defaults.max_tokens
    if "temperature" not in provider_defaults.excluded_parameters:
        result["temperature"] = provider_defaults.temperature
    if "top_p" not in provider_defaults.excluded_parameters:
        result["top_p"] = provider_defaults.top_p
    if "frequency_penalty" not in provider_defaults.excluded_parameters:
        result["frequency_penalty"] = provider_defaults.frequency_penalty
    if "presence_penalty" not in provider_defaults.excluded_parameters:
        result["presence_penalty"] = provider_defaults.presence_penalty
    if "reasoning_effort" not in provider_defaults.excluded_parameters:
        result["reasoning_effort"] = provider_defaults.reasoning_effort.value
    
    # Apply model_config from provider_config (middle priority)
    if model_config_standard:
        model_config_dict = model_config_standard.model_dump_non_none()
        for key, value in model_config_dict.items():
            if key not in provider_defaults.excluded_parameters:
                if isinstance(value, ReasoningEffort):
                    result[key] = value.value
                else:
                    result[key] = value
    
    if model_config_specific:
        result.update(model_config_specific)
    
    # Apply call parameters (highest priority) - override everything
    standard_dict = standard_params.model_dump_non_none()
    for key, value in standard_dict.items():
        if key not in provider_defaults.excluded_parameters:
            if isinstance(value, ReasoningEffort):
                result[key] = value.value
            else:
                result[key] = value
    
    # Add provider-specific parameters from call
    result.update(provider_specific)
    
    return result


def extract_standard_and_specific_params(
    kwargs: Dict[str, Any]
) -> tuple[StandardParameters, Dict[str, Any]]:
    """
    Extract standard parameters from kwargs, leaving provider-specific ones.
    
    Args:
        kwargs: All parameters passed to provider
        
    Returns:
        Tuple of (standard_parameters, provider_specific_parameters)
    """
    # Standard parameter names
    standard_names = set(StandardParameters.model_fields.keys())
    
    # Extract standard parameters
    standard_dict = {}
    provider_specific = {}
    
    for key, value in kwargs.items():
        if key in standard_names:
            standard_dict[key] = value
        else:
            provider_specific[key] = value
    
    # Create StandardParameters instance (will validate)
    standard_params = StandardParameters(**standard_dict)
    
    return standard_params, provider_specific