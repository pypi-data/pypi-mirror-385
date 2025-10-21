"""Base model management extending BaseModelRetriever pattern."""

import json
import asyncio
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional, Mapping
from datetime import datetime

import logging
from .model_types import (
    ModelInfo,
    PricingInfo,
    ProviderModelConfig,
    ModelCapabilities,
    ModelLimits,
    ModelCostAndLimits,
    ModelMetadata,
)

logger = logging.getLogger(__name__)


class BaseModelManager(ABC):
    """Base class for provider model management - extends BaseModelRetriever pattern"""
    
    def __init__(self, provider_name: str):
        self.provider_name: str = provider_name
        # Automatically determine provider-specific data path
        # Locate the egregore package root robustly, then providers/{provider_name}/data/models.json
        try:
            egregore_root = Path(__file__).resolve().parents[3]  # .../egregore
            if egregore_root.name != "egregore":
                # Fallback: search upwards for the 'egregore' package dir
                for p in Path(__file__).resolve().parents:
                    if (p / "__init__.py").exists() and p.name == "egregore":
                        egregore_root = p
                        break
            self.config_path: Path = egregore_root / "providers" / provider_name / "data" / "models.json"
        except Exception:
            # Final fallback to previous relative approach (may be incorrect but prevents crashes)
            self.config_path = Path(__file__).parent.parent.parent / "providers" / provider_name / "data" / "models.json"
        self._config: Optional[ProviderModelConfig] = None
        # Cache for model name resolution (e.g., "gpt-4o" -> "gpt-4o-2024-05-13")
        self._model_aliases: Dict[str, str] = {}
    
    # Core model discovery methods (what we actually need)
    def list_models(self) -> List[ModelInfo]:
        """List all available models for this provider"""
        config = self._get_config()
        
        # Auto-populate if cache is empty
        if not config.models:
            logger.info(f"No cached models found for {self.provider_name}, attempting to fetch from API...")
            try:
                import asyncio
                # Check if we're in an async context
                try:
                    loop = asyncio.get_running_loop()
                    # We're in an async context, we can't block here
                    logger.warning(f"Cannot auto-populate models in async context for {self.provider_name}. Use refresh_models() first.")
                except RuntimeError:
                    # No event loop running, safe to create one
                    asyncio.run(self.refresh_models())
                    config = self._get_config()  # Reload after refresh
            except Exception as e:
                logger.warning(f"Failed to auto-populate models for {self.provider_name}: {e}")
        
        return [self._convert_to_model_info(model_data) for model_data in config.models.values()]
    
    def get_model(self, model_name: str) -> ModelInfo:
        """Get detailed information about a specific model with automatic name resolution and dynamic API lookup"""
        resolved_model = self._resolve_model_name(model_name)
        config = self._get_config()
        
        # First try cached data
        if resolved_model in config.models:
            return self._convert_to_model_info(config.models[resolved_model])
        
        # Model not found in cache - try dynamic lookup from API
        return self._dynamic_model_lookup(model_name, resolved_model)
    
    def _dynamic_model_lookup(self, original_model: str, resolved_model: str) -> ModelInfo:
        """Dynamic model lookup: check API if model not found in cache, update cache if found.
        Always returns a ModelInfo or raises ValueError; never returns None.
        """
        logger.info(
            "Model %s (resolved: %s) not found in cache, checking API...",
            original_model,
            resolved_model,
        )

        # Get fresh models from API (handle async/sync uniformly)
        fetcher = self._get_fetcher()
        try:
            if asyncio.iscoroutinefunction(fetcher.fetch_models):
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        import concurrent.futures
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(asyncio.run, fetcher.fetch_models())
                            fresh_models = future.result(timeout=30)
                    else:
                        fresh_models = asyncio.run(fetcher.fetch_models())
                except RuntimeError:
                    fresh_models = asyncio.run(fetcher.fetch_models())
            else:
                fresh_models = fetcher.fetch_models()
        except Exception as e:
            logger.error("Dynamic model fetch failed for %s: %s", original_model, e)
            raise ValueError(
                f"Model {original_model} (resolved to: {resolved_model}) not found for provider {self.provider_name}. API lookup failed: {e}"
            )

        # If found in fresh data, cache and return
        if resolved_model in fresh_models:
            logger.info("Found %s in API, updating cache...", resolved_model)
            config = self._get_config()
            model_info = fresh_models[resolved_model]

            # Convert to dict for storage
            if hasattr(model_info, 'model_dump'):
                model_dict = model_info.model_dump()
            elif hasattr(model_info, 'dict'):
                model_dict = model_info.dict()
            else:
                model_dict = model_info if isinstance(model_info, dict) else model_info.__dict__

            config.models[resolved_model] = model_dict
            config.last_updated = datetime.now().isoformat()
            self._save_config(config)
            self._config = config

            final_resolved = self._resolve_model_name_with_models(original_model, fresh_models)
            if final_resolved in fresh_models:
                mi = fresh_models[final_resolved]
                return mi if isinstance(mi, ModelInfo) else self._convert_to_model_info(mi)
            mi = fresh_models[resolved_model]
            return mi if isinstance(mi, ModelInfo) else self._convert_to_model_info(mi)

        # Not found: raise with sample
        sample = list(fresh_models.keys())[:5]
        raise ValueError(
            f"Model {original_model} (resolved to: {resolved_model}) not found in {self.provider_name} API. Available models: {sample}"
        )
        
        try:
            # Get fresh models from API
            fetcher = self._get_fetcher()
            
            # Run async fetch_models in sync context
            if asyncio.iscoroutinefunction(fetcher.fetch_models):
                try:
                    # Try to get the current event loop
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # We're in an async context, but need sync behavior
                        # Create a new thread to run the coroutine
                        import concurrent.futures
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(asyncio.run, fetcher.fetch_models())
                            fresh_models = future.result(timeout=30)  # 30 second timeout
                    else:
                        # No running loop, we can use asyncio.run
                        fresh_models = asyncio.run(fetcher.fetch_models())
                except RuntimeError:
                    # No event loop, use asyncio.run
                    fresh_models = asyncio.run(fetcher.fetch_models())
            else:
                # Not async, call directly
                fresh_models = fetcher.fetch_models()
            
            # Check if our model exists in fresh data
            if resolved_model in fresh_models:
                logger.info("Found %s in API, updating cache...", resolved_model)
                
                # Add the new model to our config
                config = self._get_config()
                model_info = fresh_models[resolved_model]
                
                # Convert ModelInfo to dict for storage
                if hasattr(model_info, 'model_dump'):
                    model_dict = model_info.model_dump()
                elif hasattr(model_info, 'dict'):
                    model_dict = model_info.dict()
                else:
                    # Assume it's already a dict
                    model_dict = model_info if isinstance(model_info, dict) else model_info.__dict__
                
                config.models[resolved_model] = model_dict
                config.last_updated = datetime.now().isoformat()
                
                # Save updated config to disk
                self._save_config(config)
                
                # Update our cached config
                self._config = config
                
                # Re-resolve model name with fresh data (in case alias changed)
                final_resolved = self._resolve_model_name_with_models(original_model, fresh_models)
                if final_resolved in fresh_models:
                    logger.info(f"Successfully added {final_resolved} to cache")
                    return fresh_models[final_resolved] if isinstance(fresh_models[final_resolved], ModelInfo) else self._convert_to_model_info(fresh_models[final_resolved])
                else:
                    # Return the originally found model
                    return fresh_models[resolved_model] if isinstance(fresh_models[resolved_model], ModelInfo) else self._convert_to_model_info(fresh_models[resolved_model])
            
            # Model not found in API either
                sample = list(fresh_models.keys())[:5]  # Show first 5 for brevity
                raise ValueError(
                    f"Model {original_model} (resolved to: {resolved_model}) not found in {self.provider_name} API. Available models: {sample}"
                )            
        except Exception as e:
            # API lookup failed - this is the final error
            logger.error("Dynamic model lookup failed for %s: %s", original_model, e)
            # Ensure function never returns None when annotated as ModelInfo
            raise ValueError(
                f"Model {original_model} (resolved to: {resolved_model}) not found for provider {self.provider_name}. API lookup also failed: {e}"
            )
    
    def _resolve_model_name_with_models(self, model_name: str, models_dict: Mapping[str, Any]) -> str:
        """Resolve model name using a specific models dictionary (for dynamic lookup)."""
        try:
            fetcher = self._get_fetcher()
            return fetcher._resolve_model_alias(model_name, dict(models_dict))
        except Exception:
            return model_name
    
    def _save_config(self, config: ProviderModelConfig) -> None:
        """Save configuration to JSON file"""
        try:
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save to file
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config.model_dump(exclude_none=True), f, indent=2, sort_keys=True, ensure_ascii=False)
                
            logger.debug(f"Saved updated config for {self.provider_name} to {self.config_path}")
            
        except Exception as e:
            logger.warning(f"Failed to save config for {self.provider_name}: {e}")
    
    def validate(self, model_name: str) -> bool:
        """Validate that a model exists and is available with automatic name resolution and dynamic lookup"""
        try:
            # Try to get the model - this will use dynamic lookup if needed
            model_info = self.get_model(model_name)
            
            # Check if model is deprecated
            return not model_info.metadata.deprecated
            
        except Exception as e:
            logger.debug(f"Model validation failed for {model_name}: {e}")
            return False
    
    # Cost calculation methods (automatically use resolved model names)
    def calculate_request_cost(self, input_tokens: int, output_tokens: int, model_name: str) -> float:
        """Calculate cost for a request with automatic name resolution"""
        model_info = self.get_model(model_name)  # get_model() already resolves the name
        if model_info.cost_and_limits is None:
            return 0.0
        return (input_tokens * model_info.cost_and_limits.cost_per_1k_input / 1000 + 
                output_tokens * model_info.cost_and_limits.cost_per_1k_output / 1000)
    
    def get_pricing_info(self, model_name: str) -> Optional[PricingInfo]:
        """Get pricing information for model with automatic name resolution"""
        model_info = self.get_model(model_name)  # get_model() already resolves the name
        if model_info.cost_and_limits is None:
            return None
        return PricingInfo(
            input_cost_per_1k=model_info.cost_and_limits.cost_per_1k_input,
            output_cost_per_1k=model_info.cost_and_limits.cost_per_1k_output,
            currency="USD",
            free_tier_limit=None,
            notes=None,
        )
    
    # Configuration management (reuse existing pattern)
    def _get_config(self) -> ProviderModelConfig:
        """Load model configuration from cache"""
        if self._config is None:
            self._config = self._load_config()
        return self._config
    
    def _load_config(self) -> ProviderModelConfig:
        """Load configuration from JSON file"""
        # Reuse existing logic from BaseModelRetriever
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return ProviderModelConfig.model_validate(data)
            except (json.JSONDecodeError, Exception) as e:
                logger.warning(f"Failed to load config from {self.config_path}: {e}. Using default config.")
                return ProviderModelConfig(provider=self.provider_name, last_updated="never", egregore_version=None, fetcher_fingerprint=None)
        else:
            # Return empty config if file doesn't exist
            return ProviderModelConfig(provider=self.provider_name, last_updated="never", egregore_version=None, fetcher_fingerprint=None)
    
    async def refresh_models(self) -> None:
        """Refresh model data from provider API"""
        # Delegates to provider-specific fetcher
        fetcher = self._get_fetcher()
        await fetcher.retrieve_and_save(self.config_path)
        # Reload the config after fetcher saved it
        self._config = self._load_config()
        # Refresh model aliases after getting new model data
        self._refresh_model_aliases()
    
    def _convert_to_model_info(self, model_data: Dict[str, Any]) -> ModelInfo:
        """Convert flat model data to nested ModelInfo structure"""
        # Handle both flat and already-nested data
        if isinstance(model_data.get("capabilities"), dict):
            # Already nested structure - but ensure max_input_tokens exists
            if "limits" in model_data and "max_input_tokens" not in model_data["limits"]:
                # Fix missing max_input_tokens in nested structure
                limits = model_data["limits"]
                context_tokens = limits.get("context_tokens", 4096)
                max_output_tokens = limits.get("max_output_tokens", 4096)
                limits["max_input_tokens"] = max(context_tokens - max_output_tokens, context_tokens // 2)
            # Ensure required identity fields exist
            model_data.setdefault("name", model_data.get("name", ""))
            model_data.setdefault("display_name", model_data.get("display_name", model_data.get("name", "")))
            model_data.setdefault("provider", model_data.get("provider", self.provider_name))
            return ModelInfo(**model_data)
        
        # Convert flat structure to nested Pydantic models
        capabilities = ModelCapabilities(
            reasoning=bool(model_data.get("reasoning", False)),
            tools=bool(model_data.get("tools", True)),
            streaming=bool(model_data.get("streaming", True)),
            vision=bool(model_data.get("vision", False)),
            audio=bool(model_data.get("audio", False)),
            structured_output_native=bool(model_data.get("structured_output_native", False)),
        )
        
        # Calculate max_input_tokens if not present (for legacy data)
        context_tokens = model_data.get("context_tokens", 4096)
        max_output_tokens = model_data.get("max_output_tokens", 4096)
        max_input_tokens = model_data.get("max_input_tokens")
        
        # If max_input_tokens is not set, calculate it as context - output
        if max_input_tokens is None:
            max_input_tokens = max(context_tokens - max_output_tokens, context_tokens // 2)  # Ensure positive
        
        limits = ModelLimits(
            context_tokens=context_tokens,
            max_input_tokens=max_input_tokens,
            max_output_tokens=max_output_tokens,
            knowledge_cutoff=model_data.get("knowledge_cutoff", "2024-04")
        )
        
        # Handle cost_and_limits - check both nested structure and flat structure
        cost_and_limits_data = model_data.get("cost_and_limits")
        if cost_and_limits_data is None:
            # For flat structure, check if individual cost fields exist
            if any(field in model_data for field in ["cost_per_1k_input", "cost_per_1k_output", "rate_limit_rpm", "rate_limit_tpm"]):
                cost_and_limits = ModelCostAndLimits(
                    cost_per_1k_input=model_data.get("cost_per_1k_input", 0.0),
                    cost_per_1k_output=model_data.get("cost_per_1k_output", 0.0),
                    rate_limit_rpm=model_data.get("rate_limit_rpm", 1000),
                    rate_limit_tpm=model_data.get("rate_limit_tpm", 60000)
                )
            else:
                cost_and_limits = None
        else:
            # Nested structure - use the data from cost_and_limits field
            cost_and_limits = ModelCostAndLimits(
                cost_per_1k_input=cost_and_limits_data.get("cost_per_1k_input", 0.0),
                cost_per_1k_output=cost_and_limits_data.get("cost_per_1k_output", 0.0),
                rate_limit_rpm=cost_and_limits_data.get("rate_limit_rpm", 1000),
                rate_limit_tpm=cost_and_limits_data.get("rate_limit_tpm", 60000)
            )
        
        metadata = ModelMetadata(
            deprecated=model_data.get("deprecated", False),
            deprecation_date=model_data.get("deprecation_date"),
            replacement_model=model_data.get("replacement_model"),
            oauth_ready=model_data.get("oauth_ready", False),
            special_features=model_data.get("special_features", {}),
            last_updated=model_data.get("last_updated", "2024-08-14")
        )
        
        return ModelInfo(
            name=model_data.get("name", ""),
            display_name=model_data.get("display_name", ""),
            provider=model_data.get("provider", self.provider_name),
            capabilities=capabilities,
            limits=limits,
            cost_and_limits=cost_and_limits,
            metadata=metadata
        )
    
    @abstractmethod
    def _get_fetcher(self) -> Any:
        """Get provider-specific fetcher implementation."""
        raise NotImplementedError
    
    # Generic Model Resolution Methods
    
    def _resolve_model_name(self, model_name: str) -> str:
        """Resolve model prefix to actual model name (e.g., gpt-4o -> gpt-4o-2024-05-07)."""
        # First, try direct alias lookup
        if model_name in self._model_aliases:
            resolved = self._model_aliases[model_name]
            logger.debug(f"Resolved {model_name} -> {resolved} via cached alias")
            return resolved
        
        # If no cached alias, try to resolve from available models
        try:
            config = self._get_config()
            available_models = config.models
            
            # Use the fetcher's resolution logic
            fetcher = self._get_fetcher()
            resolved = fetcher._resolve_model_alias(model_name, available_models)
            
            # Cache the resolution for future use
            if resolved != model_name:
                self._model_aliases[model_name] = resolved
                logger.debug(f"Resolved and cached {model_name} -> {resolved}")
            
            return resolved
            
        except Exception as e:
            logger.warning(f"Failed to resolve model name {model_name}: {e}")
            return model_name  # Return original if resolution fails
    
    def _refresh_model_aliases(self):
        """Refresh cached model aliases."""
        try:
            fetcher = self._get_fetcher()
            config = self._get_config()
            
            # Rebuild aliases from current model list
            self._model_aliases = fetcher._build_model_aliases(config.models)
            logger.info(f"Refreshed {len(self._model_aliases)} model aliases for {self.provider_name}")
            
        except Exception as e:
            logger.warning(f"Failed to refresh model aliases for {self.provider_name}: {e}")


class GeneralPurposeModelManager(BaseModelManager):
    """Model manager for General Purpose provider with multi-provider support."""
    
    def __init__(self, provider_name: str, config: Dict[str, Any]):
        """Initialize model manager for specific provider backend.
        
        Args:
            provider_name: Name of the specific provider backend (e.g., 'anthropic', 'google')
            config: Provider configuration
        """
        super().__init__(provider_name)
        self.config = config
        self._fetcher_instance: Optional['GeneralPurposeModelFetcher'] = None
    
    def _get_fetcher(self) -> 'GeneralPurposeModelFetcher':
        """Get provider-specific fetcher implementation."""
        if self._fetcher_instance is None:
            from .fetcher import GeneralPurposeModelFetcher
            self._fetcher_instance = GeneralPurposeModelFetcher(
                provider_name=self.provider_name,
                config=self.config
            )
        return self._fetcher_instance
    
    async def resolve_model_name(self, model_name: str) -> str:
        """Resolve user-friendly model name to canonical LiteLLM name.
        
        Args:
            model_name: User-provided model name (e.g., 'claude-sonnet-4')
            
        Returns:
            Canonical model name (e.g., 'claude-sonnet-4-20250514')
        """
        from ..data.data_manager import data_manager
        return await data_manager.resolve_model_name(self.provider_name, model_name)
    
    async def get_model_async(self, model_name: str) -> ModelInfo:
        """Get model info with async alias resolution."""
        # Resolve alias first
        canonical_name = await self.resolve_model_name(model_name)
        
        # Use BaseModelManager's get_model with canonical name
        try:
            return super().get_model(canonical_name)
        except Exception as e:
            # If canonical name fails, try original name as fallback
            if canonical_name != model_name:
                logger.debug(f"Canonical name {canonical_name} failed, trying original {model_name}")
                return super().get_model(model_name)
            raise
    
    def supports_structured_output(self, model_name: str) -> bool:
        """Check if model supports native structured output."""
        try:
            model_info = self.get_model(model_name)  # get_model() handles resolution automatically
            return model_info.capabilities.structured_output_native
        except Exception as e:
            logger.warning(f"Failed to check structured output support for {model_name}: {e}")
            return False
    
    def supports_multimodal(self, model_name: str) -> bool:
        """Check if model supports multimodal input."""
        try:
            model_info = self.get_model(model_name)  # get_model() handles resolution automatically
            return model_info.capabilities.vision
        except Exception as e:
            logger.warning(f"Failed to check multimodal support for {model_name}: {e}")
            return False
    
    def supports_tools(self, model_name: str) -> bool:
        """Check if model supports tool calling."""
        try:
            model_info = self.get_model(model_name)  # get_model() handles resolution automatically
            return model_info.capabilities.tools
        except Exception as e:
            logger.warning(f"Failed to check tool support for {model_name}: {e}")
            return False
    
    def get_provider_specific_constraints(self, model_name: str) -> Dict[str, Any]:
        """Get provider-specific constraints for the model from data, not hardcoded."""
        try:
            model_info = self.get_model(model_name)
            
            # Base constraints from model data
            constraints = {
                "max_tokens": model_info.limits.max_output_tokens,
                "context_tokens": model_info.limits.context_tokens,
                "supports_system_message": True,  # Default assumption for chat models
            }
            
            # Add any provider-specific features from model metadata
            if model_info.metadata.special_features:
                # Provider-specific features should be stored in special_features
                constraints.update(model_info.metadata.special_features)
            
            # Add capabilities-based constraints
            constraints.update({
                "supports_tools": model_info.capabilities.tools,
                "supports_vision": model_info.capabilities.vision, 
                "supports_audio": model_info.capabilities.audio,
                "supports_streaming": model_info.capabilities.streaming,
                "supports_structured_output": model_info.capabilities.structured_output_native,
            })
            
            return constraints
            
        except Exception as e:
            logger.warning(f"Failed to get constraints for {model_name}: {e}")
            return {
                "max_tokens": 4096,  # Safe default
                "context_tokens": 4096,
                "supports_system_message": True,
                "supports_tools": True,  # Conservative defaults
                "supports_vision": False,
                "supports_audio": False, 
                "supports_streaming": True,
                "supports_structured_output": False,
            }