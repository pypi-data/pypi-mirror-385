"""General Purpose model fetcher implementation for multi-provider support via any-llm."""

import asyncio
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

import logging
from .base_retriever import BaseModelFetcher
from .model_types import (
    ModelInfo, ModelCapabilities, ModelLimits, 
    ModelCostAndLimits, ModelMetadata
)
from egregore.providers.data.data_manager import data_manager
from .exceptions import GeneralPurposeError, GeneralPurposeModelError

logger = logging.getLogger(__name__)


class GeneralPurposeModelFetcher(BaseModelFetcher):
    """Fetches model information for any-llm supported providers."""
    
    def __init__(self, provider_name: str, config: Dict[str, Any]):
        """Initialize fetcher for specific provider backend.
        
        Args:
            provider_name: Name of the specific provider (e.g., 'anthropic', 'google')
            config: Provider configuration
        """
        super().__init__(provider_name)
        self.config = config
        
        # Provider-specific model mapping and litellm_provider mapping
        self.provider_mappings = {
            "anthropic": {
                "prefixes": ["claude"],
                "litellm_providers": ["anthropic"]
            },
            "google": {
                "prefixes": ["gemini", "models/gemini"],
                "litellm_providers": ["vertex_ai", "vertex_ai-language-models", "vertex_ai-vision-models", "google"]
            },
            "openrouter": {
                "prefixes": [],
                "litellm_providers": ["openrouter"]
            },
            "openai": {
                "prefixes": ["gpt", "o1"],
                "litellm_providers": ["openai"]
            },
            "cohere": {
                "prefixes": ["command"],
                "litellm_providers": ["cohere"]
            },
            "mistral": {
                "prefixes": ["mistral", "codestral"],
                "litellm_providers": ["mistral", "codestral"]
            },
            "together": {
                "prefixes": [],
                "litellm_providers": ["together_ai"]
            },
            "groq": {
                "prefixes": ["llama", "mixtral", "gemma"],
                "litellm_providers": ["groq"]
            },
        }
        
        # Get providers root directory
        self.providers_root = Path(__file__).parent.parent
    
    @classmethod
    async def auto_generate_provider_data_folders(cls) -> Dict[str, int]:
        """Auto-generate provider data folders for all supported providers.
        
        Returns:
            Dictionary mapping provider names to number of models extracted
        """
        logger.info("Auto-generating provider data folders for all supported providers")
        
        # Load supported providers from configuration
        providers_root = Path(__file__).parent.parent
        supported_providers_file = providers_root / "data" / "supported_providers.json"
        
        try:
            with open(supported_providers_file, 'r') as f:
                config = json.load(f)
            SUPPORTED_PROVIDERS = config["supported_providers"]
            PROVIDER_MAPPINGS = config.get("provider_mappings", {})
        except Exception as e:
            logger.error(f"Failed to load supported providers config: {e}")
            return {}
        
        # Get LiteLLM data
        try:
            litellm_data = await data_manager._get_litellm_data()
            if not litellm_data:
                logger.error("No LiteLLM data available")
                return {}
        except Exception as e:
            logger.error(f"Failed to get LiteLLM data: {e}")
            return {}
        
        # Determine providers root directory
        providers_root = Path(__file__).parent.parent
        
        results = {}
        
        # Group models by supported providers using direct LiteLLM provider matching
        for provider_name in SUPPORTED_PROVIDERS:
            # Skip providers that already have dedicated implementations
            if provider_name in ["openai", "anthropic"]:
                logger.debug(f"Skipping {provider_name} (has dedicated implementation)")
                continue
            
            provider_models = {}
            
            # Find models for this provider in LiteLLM data
            for model_name, model_data in litellm_data.items():
                if not isinstance(model_data, dict):
                    continue
                    
                litellm_provider = model_data.get("litellm_provider", "")
                
                # Direct provider name matching
                if provider_name == litellm_provider:
                    provider_models[model_name] = model_data
                # Use provider mappings for more complex matching
                elif provider_name in PROVIDER_MAPPINGS:
                    mappings = PROVIDER_MAPPINGS[provider_name]
                    if any(mapping in litellm_provider for mapping in mappings):
                        provider_models[model_name] = model_data
            
            # Create provider directory and models.json if models found
            if provider_models:
                try:
                    # Create provider data directory
                    provider_dir = providers_root / provider_name / "data"
                    provider_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Write models.json file
                    models_file = provider_dir / "models.json"
                    with open(models_file, 'w') as f:
                        json.dump(provider_models, f, indent=2, sort_keys=True)
                    
                    results[provider_name] = len(provider_models)
                    logger.info(f"Created {provider_name}/data/models.json with {len(provider_models)} models")
                    
                except Exception as e:
                    logger.error(f"Failed to create data folder for {provider_name}: {e}")
                    continue
            else:
                logger.debug(f"No models found for supported provider: {provider_name}")
        
        logger.info(f"Auto-generated data folders for {len(results)} providers")
        return results
    
    async def fetch_models(self) -> Dict[str, ModelInfo]:
        """Fetch model information using hierarchical data source strategy."""
        try:
            logger.info(f"Fetching models for provider: {self.provider_name}")
            
            # Get models from LiteLLM data (primary source)
            litellm_models = await self._get_litellm_models()
            
            # Get provider-specific models if available
            provider_models = await self._get_provider_specific_models()
            
            # Merge and filter models
            all_models = {**litellm_models, **provider_models}
            
            # Filter models for this specific provider
            filtered_models = self._filter_models_for_provider(all_models)
            
            logger.info(f"Found {len(filtered_models)} models for provider {self.provider_name}")
            return filtered_models
            
        except Exception as e:
            error_msg = f"Failed to fetch models for {self.provider_name}: {e}"
            logger.error(error_msg)
            raise GeneralPurposeModelError(error_msg) from e
    
    async def _get_litellm_models(self) -> Dict[str, ModelInfo]:
        """Get models from LiteLLM data manager."""
        try:
            # Get all LiteLLM data
            litellm_data = await data_manager._get_litellm_data()
            if not litellm_data:
                logger.warning("No LiteLLM data available")
                return {}
            
            models = {}
            for model_name, model_data in litellm_data.items():
                # Check if this model belongs to our provider
                if model_data.get("litellm_provider") == self.provider_name:
                    model_info = self._convert_litellm_to_model_info(model_name, model_data)
                    if model_info:
                        models[model_name] = model_info
            
            logger.debug(f"Found {len(models)} models from LiteLLM for {self.provider_name}")
            return models
            
        except Exception as e:
            logger.warning(f"Failed to get LiteLLM models: {e}")
            return {}
    
    async def _get_provider_specific_models(self) -> Dict[str, ModelInfo]:
        """Get provider-specific model data via unified data manager."""
        # Using unified GeneralPurposeProvider architecture - no provider-specific fetching needed
        # All provider model data is managed through the data_manager
        return {}
    
    def _filter_models_for_provider(self, models: Dict[str, ModelInfo]) -> Dict[str, ModelInfo]:
        """Filter models that belong to this provider."""
        if self.provider_name not in self.provider_mappings:
            # For unknown providers, return all models
            return models
        
        mapping = self.provider_mappings[self.provider_name]
        prefixes = mapping["prefixes"]
        
        if not prefixes:
            # If no prefixes defined (like openrouter), return all models
            return models
        
        filtered = {}
        for model_name, model_info in models.items():
            # Check if model name starts with any of the provider prefixes
            if any(model_name.startswith(prefix) for prefix in prefixes):
                filtered[model_name] = model_info
        
        return filtered
    
    def _convert_litellm_to_model_info(self, model_name: str, litellm_data: Dict[str, Any]) -> Optional[ModelInfo]:
        """Convert LiteLLM model data to ModelInfo following OpenAI fetcher pattern."""
        try:
            # Determine model capabilities based on LiteLLM data + name patterns
            is_reasoning = self._is_reasoning_model(model_name)
            
            # Get capabilities from LiteLLM data with smart defaults
            supports_tools = litellm_data.get("supports_function_calling", not is_reasoning)
            supports_streaming = not is_reasoning if is_reasoning else True  # Most models stream
            supports_vision = litellm_data.get("supports_vision", False)
            supports_audio = litellm_data.get("supports_audio_input", False) or litellm_data.get("supports_audio_output", False)
            structured_output_native = litellm_data.get("supports_response_schema", False)
            
            # Get token limits from LiteLLM data
            max_tokens = litellm_data.get("max_tokens", 4096)
            max_input = litellm_data.get("max_input_tokens", max_tokens)
            max_output = litellm_data.get("max_output_tokens", 4096)
            
            # Ensure context_tokens is at least max_input + max_output
            context_tokens = max(max_tokens, max_input + max_output)
            
            # Get pricing from LiteLLM (convert from per-token to per-1k)
            input_cost_per_1k = litellm_data.get("input_cost_per_token", 0.0) * 1000
            output_cost_per_1k = litellm_data.get("output_cost_per_token", 0.0) * 1000
            
            # Determine rate limits based on provider and model type
            if is_reasoning:
                rate_limit_rpm = 20
                rate_limit_tpm = 800000
            else:
                rate_limit_rpm = 10000
                rate_limit_tpm = 2000000
            
            # Build ModelInfo structure
            return ModelInfo(
                name=model_name,
                display_name=model_name.upper().replace('-', ' '),
                provider=self.provider_name,
                capabilities=ModelCapabilities(
                    reasoning=is_reasoning,
                    tools=supports_tools,
                    streaming=supports_streaming,
                    vision=supports_vision,
                    audio=supports_audio,
                    structured_output_native=structured_output_native
                ),
                limits=ModelLimits(
                    context_tokens=context_tokens,
                    max_input_tokens=max_input,
                    max_output_tokens=max_output,
                    knowledge_cutoff=litellm_data.get("knowledge_cutoff", "2024-04")
                ),
                cost_and_limits=ModelCostAndLimits(
                    cost_per_1k_input=input_cost_per_1k,
                    cost_per_1k_output=output_cost_per_1k,
                    rate_limit_rpm=rate_limit_rpm,
                    rate_limit_tpm=rate_limit_tpm
                ),
                metadata=ModelMetadata(
                    deprecated=False,
                    deprecation_date=None,
                    replacement_model=None,
                    oauth_ready=self._is_oauth_compatible(model_name),
                    special_features=self._get_special_features(model_name, litellm_data),
                    last_updated=datetime.now().isoformat()
                )
            )
            
        except Exception as e:
            logger.warning(f"Failed to convert LiteLLM data for {model_name}: {e}")
            return None
    
    def _is_reasoning_model(self, model_name: str) -> bool:
        """Check if model is a reasoning model."""
        reasoning_indicators = ["o1", "reasoning", "think"]
        return any(indicator in model_name.lower() for indicator in reasoning_indicators)
    
    def _get_model_family(self, model_name: str) -> Optional[str]:
        """Get model family from model name."""
        if "claude" in model_name:
            return "claude"
        elif "gemini" in model_name:
            return "gemini"
        elif "gpt" in model_name:
            return "gpt"
        elif "llama" in model_name:
            return "llama"
        elif "mistral" in model_name or "mixtral" in model_name:
            return "mistral"
        elif "command" in model_name:
            return "command"
        return None
    
    def _is_oauth_compatible(self, model_name: str) -> bool:
        """Check if model is OAuth-compatible."""
        # Define OAuth-compatible models per provider
        oauth_models = {
            "anthropic": ["claude-sonnet-4", "claude-opus-4"],
            "google": ["gemini-2.5"],
        }
        
        provider_oauth_models = oauth_models.get(self.provider_name, [])
        return any(oauth_model in model_name for oauth_model in provider_oauth_models)
    
    def _get_special_features(self, model_name: str, litellm_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get special features for model as a dictionary."""
        features = {}
        
        # Add capability-based features
        if litellm_data.get("supports_vision"):
            features["multimodal"] = True
        if litellm_data.get("supports_function_calling"):
            features["tools"] = True
        if self._is_reasoning_model(model_name):
            features["reasoning"] = True
        
        # Add provider-specific features
        if self.provider_name == "anthropic":
            if "claude-4" in model_name:
                features["oauth_supported"] = True
        elif self.provider_name == "google":
            if "gemini-2.5" in model_name:
                features["oauth_supported"] = True
        
        # Add size-based features
        if "large" in model_name or "xl" in model_name:
            features["model_size"] = "large"
        elif "small" in model_name or "mini" in model_name:
            features["model_size"] = "small"
        
        # Add speed-based features
        if "flash" in model_name or "turbo" in model_name or "fast" in model_name:
            features["optimized_for"] = "speed"
        
        return features
    
    def _get_model_tags(self, model_name: str, litellm_data: Dict[str, Any]) -> List[str]:
        """Get model tags based on name and capabilities."""
        tags = []
        
        # Add capability-based tags
        if litellm_data.get("supports_vision"):
            tags.append("multimodal")
        if litellm_data.get("supports_function_calling"):
            tags.append("tools")
        if self._is_reasoning_model(model_name):
            tags.append("reasoning")
        
        # Add size-based tags
        if "large" in model_name or "xl" in model_name:
            tags.append("large")
        elif "small" in model_name or "mini" in model_name:
            tags.append("small")
        
        # Add speed-based tags
        if "flash" in model_name or "turbo" in model_name or "fast" in model_name:
            tags.append("fast")
        
        return tags