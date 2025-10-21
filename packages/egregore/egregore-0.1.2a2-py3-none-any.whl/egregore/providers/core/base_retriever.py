"""Base class for model retrieval implementations in corev2."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import json
from datetime import datetime, timezone
from pathlib import Path

import logging
from .model_types import ModelInfo, PricingInfo, ProviderModelConfig, BaseModelRetriever


logger = logging.getLogger(__name__)


class BaseModelFetcher(BaseModelRetriever):
    """Base class for retrieving model information from providers in corev2.
    
    Provider-Specific Resolution Override Pattern:
    ============================================
    
    Providers can implement custom model resolution logic by defining this method:
    
    resolve_latest(self, model_prefix: str, available_models: Dict[str, Any]) -> str:
       Custom logic for resolving model aliases (e.g. gpt-4o -> gpt-4o-2024-05-13)
    
    Example implementation in OpenAI fetcher:
    
    ```python
    def resolve_latest(self, model_prefix: str, available_models: Dict[str, Any]) -> str:
        # OpenAI-specific logic for date-versioned models
        if model_prefix == 'gpt-4o':
            # Custom logic to prefer specific versions
            candidates = [m for m in available_models.keys() if m.startswith('gpt-4o-')]
            if 'gpt-4o-2024-05-13' in candidates:
                return 'gpt-4o-2024-05-13'  # Prefer stable version
        return self._resolve_model_alias_universal(model_prefix, available_models)
    ```
    
    If this method is not implemented, the universal resolution algorithm is used.
    """
    
    def __init__(self, provider_name: str):
        super().__init__(provider_name)
        # Use corev2 structure for data storage - point to egregore/providers
        self.cache_dir = Path(__file__).parent.parent.parent.parent / "providers" / provider_name / "data"
        self.config_path = self.cache_dir / "models.json"
        self.bundled_config_path = self.cache_dir / "bundled_models.json"
    
    # Implement required abstract methods from BaseModelRetriever
    
    @abstractmethod
    async def fetch_models(self) -> Dict[str, ModelInfo]:
        """Fetch model information from the provider's API.
        
        Returns:
            Dictionary mapping model names to ModelInfo objects with corev2 structure
        """
        pass
    
    async def retrieve_and_save(self, storage_path: Path) -> None:
        """Fetch models from API and save to storage."""
        try:
            models_dict = await self.fetch_models()
            
            # Convert to JSON format and save
            data = {
                "provider": self.provider_name,
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "models": {}
            }
            
            for model_name, model_info in models_dict.items():
                data["models"][model_name] = model_info.model_dump()
            
            # Ensure directory exists
            storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save to specified path
            with open(storage_path, 'w') as f:
                json.dump(data, f, indent=2, sort_keys=True)
            
            logger.info(f"Saved {len(models_dict)} models to {storage_path}")
            
        except Exception as e:
            logger.error(f"Failed to retrieve and save models: {e}")
            raise
    
    # Additional helper methods for provider implementations
    
    def _detect_structured_output_support(self, model_name: str) -> bool:
        """Detect if model supports native structured output. Override in subclasses."""
        return False
    
    def _resolve_model_alias(self, model_prefix: str, available_models: Dict[str, Any]) -> str:
        """Resolve model prefix to latest version with provider-specific override support.
        
        This method provides a standard pattern where providers can override resolution logic:
        1. Check if provider has custom resolver method
        2. Use custom resolver if available  
        3. Fall back to universal resolution algorithm
        """
        # Check if provider implements custom resolution
        custom_resolver = getattr(self, 'resolve_latest', None)
        if custom_resolver and callable(custom_resolver):
            try:
                resolved = custom_resolver(model_prefix, available_models)
                logger.debug(f"Used provider-specific resolver: {model_prefix} -> {resolved}")
                return resolved
            except Exception as e:
                logger.warning(f"Provider-specific resolver failed, using default: {e}")
                # Fall through to default resolution
        
        # Default universal resolution algorithm
        return self._resolve_model_alias_universal(model_prefix, available_models)
    
    def _resolve_model_alias_universal(self, model_prefix: str, available_models: Dict[str, Any]) -> str:
        """Universal model resolution algorithm supporting multiple provider patterns."""
        # Find all models matching the prefix
        matching_models = []
        for model_name in available_models.keys():
            if model_name.startswith(model_prefix):
                matching_models.append(model_name)
        
        if not matching_models:
            return model_prefix  # No matches, return as-is
        
        # If exact match exists, prefer it
        if model_prefix in matching_models:
            return model_prefix
        
        # Universal resolution logic supporting different naming patterns:
        # 1. OpenAI: gpt-4o-2024-05-13 (date-versioned)
        # 2. Anthropic: claude-3-5-sonnet-20241022 (date-suffixed)  
        # 3. Google: gemini-1.5-pro-002, gemini-1.5-pro-latest (version + latest)
        
        # Separate models with different suffixes
        dated_models = []
        version_models = []
        latest_models = []
        
        for model in matching_models:
            suffix = model[len(model_prefix):].lstrip('-')
            if suffix.startswith('202') and len(suffix) >= 8:  # Date pattern (2024, 20241022, etc.)
                dated_models.append(model)
            elif suffix in ['latest', 'preview']:  # Latest/preview indicators
                latest_models.append(model)
            elif suffix.replace('.', '').replace('-', '').isdigit():  # Version numbers
                version_models.append(model)
            else:
                # Fallback for other patterns
                version_models.append(model)
        
        # Priority: latest > newest date > highest version
        if latest_models:
            # Prefer 'latest' over 'preview'
            if any('latest' in m for m in latest_models):
                return next(m for m in latest_models if 'latest' in m)
            return latest_models[0]
        
        if dated_models:
            # Sort by date (lexicographically works for YYYY-MM-DD and YYYYMMDD)
            return sorted(dated_models)[-1]
        
        if version_models:
            # Sort lexicographically (works for most version patterns)
            return sorted(version_models)[-1]
        
        # Fallback: return the last model lexicographically among matches
        return sorted(matching_models)[-1]
    
    def _build_model_aliases(self, models: Dict[str, ModelInfo]) -> Dict[str, str]:
        """Build mapping of model prefixes to their latest versions using resolve_latest method."""
        return self._build_model_aliases_universal(models)
    
    def _build_model_aliases_universal(self, models: Dict[str, ModelInfo]) -> Dict[str, str]:
        """Universal model alias building supporting multiple provider patterns."""
        aliases = {}
        
        # Auto-detect prefixes by analyzing model names
        model_names = set(models.keys()) if isinstance(models, dict) else set(models)
        detected_prefixes = set()
        
        # Common patterns across providers
        known_patterns = [
            # OpenAI patterns
            'gpt-4o', 'gpt-4', 'gpt-3.5-turbo', 'o1', 'o1-mini', 'o1-preview',
            # Anthropic patterns  
            'claude-3-5-sonnet', 'claude-3-5-haiku', 'claude-3-opus',
            'claude-sonnet-4', 'claude-opus-4', 'claude-3-7-sonnet',
            # Google patterns
            'gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-2.0-flash'
        ]
        
        # Find prefixes that have multiple versions
        for pattern in known_patterns:
            matches = [name for name in model_names if name.startswith(pattern)]
            if len(matches) > 1 or (len(matches) == 1 and matches[0] != pattern):
                detected_prefixes.add(pattern)
        
        # Build aliases for detected prefixes using the same resolution logic
        for prefix in detected_prefixes:
            resolved = self._resolve_model_alias(prefix, models)
            if resolved != prefix:  # Only add if there's an actual resolution
                aliases[prefix] = resolved
        
        return aliases
    
    def _save_config_with_fallback(self, config_dict: dict):
        """Save configuration with fallback bundled copy."""
        # Ensure directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Save main config
        with open(self.config_path, 'w') as f:
            json.dump(config_dict, f, indent=2)
        
        logger.debug(f"Saved model configuration to {self.config_path}")
        
        # Also save as bundled fallback (fresh data from successful API calls)
        try:
            with open(self.bundled_config_path, 'w') as f:
                json.dump(config_dict, f, indent=2)
            logger.info(f"Updated bundled fallback: {self.bundled_config_path}")
        except Exception as e:
            logger.warning(f"Failed to update bundled fallback: {e}")
    
    def _load_fallback_config(self) -> dict:
        """Load fallback configuration from bundled or cached files."""
        # Try cached config first
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                logger.info(f"Loaded cached config for {self.provider_name}")
                return data
            except Exception as e:
                logger.warning(f"Failed to load cached config: {e}")
        
        # Try bundled config
        if self.bundled_config_path.exists():
            try:
                with open(self.bundled_config_path, 'r') as f:
                    data = json.load(f)
                logger.info(f"Loaded bundled config for {self.provider_name}")
                return data
            except Exception as e:
                logger.warning(f"Failed to load bundled config: {e}")
        
        # Return empty config as last resort
        logger.warning(f"No fallback config available for {self.provider_name}")
        return {
            "provider": self.provider_name,
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "models": {}
        }