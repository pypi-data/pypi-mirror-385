"""
Unified Data Manager for Provider Data Management

Consolidates functionality from:
- LiteLLMDataManager: LiteLLM model data with hierarchical fallback
- ModelAliasManager: Model alias resolution for user-friendly names
- supported_providers.py: Provider validation and discovery utilities
"""

import json
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Set
import aiohttp
from any_llm import LLMProvider

import logging

logger = logging.getLogger(__name__)


class DataManager:
    """
    Unified manager for all provider data including:
    - LiteLLM model data with automatic refresh and hierarchical fallback
    - Model alias resolution for user-friendly names  
    - Provider validation and discovery utilities
    """
    
    def __init__(self):
        self.data_dir = Path(__file__).parent
        
        # LiteLLM data paths (updated for new structure)
        self.litellm_json_path = self.data_dir / "shared" / "litellm_models.json"
        self.litellm_url = "https://raw.githubusercontent.com/BerriAI/litellm/refs/heads/main/model_prices_and_context_window.json"
        self.refresh_interval_days = 7
        self._cached_litellm_data: Optional[Dict[str, Any]] = None
        
        # Model alias paths (updated for new structure)
        self.aliases_json_path = self.data_dir / "shared" / "model_aliases.json"
        self._cached_aliases: Optional[Dict[str, Dict[str, str]]] = None
        
        # Provider data structure (new centralized structure)
        self.supported_data_dir = self.data_dir / "supported"
        
        # Supported providers (any-llm integration)
        self.provider_names = LLMProvider.__members__.values()
    
    # ===========================================
    # FROM LiteLLMDataManager - Model Data Management
    # ===========================================
    
    async def get_model_data(self, provider: str, model_name: str) -> Optional[Dict[str, Any]]:
        """Get model data using hierarchical fallback strategy."""
        
        # 1. Try LiteLLM data (primary source)
        litellm_data = await self._get_litellm_data()
        if litellm_data and model_name in litellm_data:
            model_info = litellm_data[model_name]
            # Check if this model is for the correct provider
            if model_info.get("litellm_provider") == provider:
                logger.debug(f"Found {model_name} in LiteLLM data")
                return model_info
        
        # 2. Try provider-specific data (secondary source)
        provider_data = await self._get_provider_data(provider, model_name)
        if provider_data:
            logger.debug(f"Found {model_name} in {provider} provider data")
            return provider_data
        
        # 3. Model not found in any cached source
        logger.debug(f"Model {model_name} not found in cached data sources")
        return None
    
    async def update_model_data(self, provider: str, model_name: str, model_info: Dict[str, Any]):
        """Update both LiteLLM and provider JSON when model found via API."""
        
        # Update LiteLLM JSON
        await self._update_litellm_data(model_name, model_info)
        
        # Update provider JSON  
        await self._update_provider_data(provider, model_name, model_info)
        
        # Clear cached data to force reload
        self._cached_litellm_data = None
        
        logger.info(f"Updated model data for {model_name} in both LiteLLM and {provider} data")
    
    async def _refresh_litellm_data(self) -> bool:
        """Download fresh LiteLLM data."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.litellm_url) as response:
                    if response.status == 200:
                        # Get text content and parse as JSON manually to handle MIME type issues
                        text_content = await response.text()
                        data = json.loads(text_content)
                        
                        # Ensure shared directory exists
                        self.litellm_json_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Save to file with timestamp
                        with open(self.litellm_json_path, 'w') as f:
                            json.dump(data, f, indent=2)
                        
                        logger.info(f"Successfully refreshed LiteLLM data from {self.litellm_url}")
                        return True
                    else:
                        logger.warning(f"Failed to refresh LiteLLM data: HTTP {response.status}")
                        return False
        
        except Exception as e:
            logger.error(f"Error refreshing LiteLLM data: {e}")
            return False
    
    async def _get_litellm_data(self) -> Optional[Dict[str, Any]]:
        """Get LiteLLM data with automatic refresh."""
        
        # Check if refresh is needed
        if await self._needs_refresh():
            logger.info("LiteLLM data is stale, refreshing...")
            await self._refresh_litellm_data()
        
        # Load cached data
        if self._cached_litellm_data is None:
            self._cached_litellm_data = await self._load_litellm_data()
        
        return self._cached_litellm_data
    
    async def _needs_refresh(self) -> bool:
        """Check if LiteLLM data needs refresh (older than 1 week)."""
        if not self.litellm_json_path.exists():
            return True
        
        file_modified = datetime.fromtimestamp(self.litellm_json_path.stat().st_mtime)
        age = datetime.now() - file_modified
        
        return age > timedelta(days=self.refresh_interval_days)
    
    async def _load_litellm_data(self) -> Optional[Dict[str, Any]]:
        """Load LiteLLM data from local file."""
        try:
            if self.litellm_json_path.exists():
                with open(self.litellm_json_path, 'r') as f:
                    data = json.load(f)
                logger.debug(f"Loaded LiteLLM data with {len(data)} entries")
                return data
        except Exception as e:
            logger.error(f"Error loading LiteLLM data: {e}")
        
        return None
    
    async def _get_provider_data(self, provider: str, model_name: str) -> Optional[Dict[str, Any]]:
        """Get data from provider-specific JSON file (updated for new structure)."""
        try:
            # Updated path for new centralized structure
            provider_data_path = self.supported_data_dir / provider / "models.json"
            
            if provider_data_path.exists():
                with open(provider_data_path, 'r') as f:
                    data = json.load(f)
                
                models = data.get("models", {})
                if model_name in models:
                    return models[model_name]
        
        except Exception as e:
            logger.debug(f"Error loading {provider} provider data: {e}")
        
        return None
    
    async def _update_litellm_data(self, model_name: str, model_info: Dict[str, Any]):
        """Update LiteLLM JSON with new model info."""
        try:
            # Load current data
            litellm_data = await self._load_litellm_data() or {}
            
            # Convert our ModelInfo format to LiteLLM format
            litellm_entry = self._convert_to_litellm_format(model_info)
            
            # Add to data
            litellm_data[model_name] = litellm_entry
            
            # Ensure directory exists
            self.litellm_json_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save back to file
            with open(self.litellm_json_path, 'w') as f:
                json.dump(litellm_data, f, indent=2)
            
            logger.debug(f"Updated LiteLLM data with {model_name}")
            
        except Exception as e:
            logger.error(f"Error updating LiteLLM data: {e}")
    
    async def _update_provider_data(self, provider: str, model_name: str, model_info: Dict[str, Any]):
        """Update provider JSON with new model info (updated for new structure)."""
        try:
            # Updated path for new centralized structure  
            provider_data_path = self.supported_data_dir / provider / "models.json"
            
            # Load current provider data
            if provider_data_path.exists():
                with open(provider_data_path, 'r') as f:
                    data = json.load(f)
            else:
                data = {"provider": provider, "models": {}, "last_updated": datetime.now().isoformat()}
            
            # Add model
            data["models"][model_name] = model_info
            data["last_updated"] = datetime.now().isoformat()
            
            # Ensure directory exists
            provider_data_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save back to file
            with open(provider_data_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.debug(f"Updated {provider} provider data with {model_name}")
            
        except Exception as e:
            logger.error(f"Error updating {provider} provider data: {e}")
    
    def _convert_to_litellm_format(self, model_info: Dict[str, Any]) -> Dict[str, Any]:
        """Convert our ModelInfo format to LiteLLM format."""
        
        # Extract from our nested structure
        capabilities = model_info.get("capabilities", {})
        limits = model_info.get("limits", {})
        costs = model_info.get("cost_and_limits", {})
        
        # Convert to LiteLLM format
        return {
            "max_tokens": limits.get("context_tokens", 4096),
            "max_input_tokens": limits.get("max_input_tokens", 4096),
            "max_output_tokens": limits.get("max_output_tokens", 4096),
            "input_cost_per_token": costs.get("cost_per_1k_input", 0.0) / 1000.0,  # Convert per-1k to per-token
            "output_cost_per_token": costs.get("cost_per_1k_output", 0.0) / 1000.0,
            "litellm_provider": model_info.get("provider", "openai"),
            "mode": "chat",
            "supports_function_calling": capabilities.get("tools", False),
            "supports_parallel_function_calling": capabilities.get("tools", False),
            "supports_vision": capabilities.get("vision", False),
            "supports_audio_input": capabilities.get("audio", False),
            "supports_audio_output": capabilities.get("audio", False),
            "supports_response_schema": capabilities.get("structured_output_native", False),
            "supports_system_messages": True,  # Assume true for chat models
            "supports_reasoning": capabilities.get("reasoning", False),
        }
    
    # ===========================================
    # FROM ModelAliasManager - Model Alias Resolution  
    # ===========================================
    
    async def resolve_model_name(self, provider: str, user_model_name: str) -> str:
        """Resolve user-friendly model name to canonical LiteLLM name.
        
        Args:
            provider: Provider name (e.g., 'anthropic', 'google')
            user_model_name: User-provided model name (e.g., 'claude-sonnet-4')
            
        Returns:
            Canonical model name (e.g., 'claude-sonnet-4-20250514') or original if no alias
        """
        try:
            aliases = await self._get_aliases()
            provider_aliases = aliases.get(provider, {})
            
            # Try exact alias match first
            if user_model_name in provider_aliases:
                canonical = provider_aliases[user_model_name]
                logger.debug(f"Resolved {provider}:{user_model_name} → {canonical}")
                return canonical
            
            # If no alias found, return original name
            logger.debug(f"No alias for {provider}:{user_model_name}, using as-is")
            return user_model_name
            
        except Exception as e:
            logger.warning(f"Failed to resolve model name {provider}:{user_model_name}: {e}")
            return user_model_name
    
    async def get_provider_aliases(self, provider: str) -> Dict[str, str]:
        """Get all aliases for a specific provider.
        
        Args:
            provider: Provider name
            
        Returns:
            Dict mapping user-friendly names to canonical names
        """
        try:
            aliases = await self._get_aliases()
            return aliases.get(provider, {})
        except Exception as e:
            logger.warning(f"Failed to get aliases for provider {provider}: {e}")
            return {}
    
    async def get_all_aliases(self) -> Dict[str, Dict[str, str]]:
        """Get all provider aliases.
        
        Returns:
            Dict mapping provider names to their alias mappings
        """
        return await self._get_aliases()
    
    async def _get_aliases(self) -> Dict[str, Dict[str, str]]:
        """Get alias data with caching."""
        if self._cached_aliases is None:
            await self._load_aliases()
        return self._cached_aliases or {}
    
    async def _load_aliases(self):
        """Load aliases from JSON file."""
        try:
            if not self.aliases_json_path.exists():
                logger.warning(f"Model aliases file not found: {self.aliases_json_path}")
                self._cached_aliases = {}
                return
            
            with open(self.aliases_json_path, 'r') as f:
                data = json.load(f)
            
            # Remove metadata fields
            aliases = {k: v for k, v in data.items() if not k.startswith('_')}
            self._cached_aliases = aliases
            
            total_aliases = sum(len(provider_aliases) for provider_aliases in aliases.values())
            logger.info(f"Loaded {total_aliases} model aliases for {len(aliases)} providers")
            
        except Exception as e:
            logger.error(f"Failed to load model aliases: {e}")
            self._cached_aliases = {}
    
    def invalidate_alias_cache(self):
        """Invalidate cached aliases (for reloading)."""
        self._cached_aliases = None
    
    # ===========================================
    # FROM supported_providers.py - Provider Validation & Discovery
    # ===========================================
    
    def get_all_supported_providers(self) -> List[str]:
        """Get list of all providers supported by any-llm.
        
        Returns:
            List of provider names as strings
        """
        return [provider.value for provider in self.provider_names]
    
    def is_provider_supported(self, provider_name: str) -> bool:
        """Check if a provider is supported by any-llm.
        
        Args:
            provider_name: Name of the provider to check
            
        Returns:
            True if provider is supported, False otherwise
        """
        supported_providers = self.get_supported_provider_set()
        return provider_name.lower() in supported_providers
    
    def get_supported_provider_set(self) -> Set[str]:
        """Get set of supported provider names (lowercase) for fast lookup.
        
        Returns:
            Set of lowercase provider names
        """
        return {provider.value.lower() for provider in self.provider_names}
    
    def validate_provider_name(self, provider_name: str) -> str:
        """Validate and normalize provider name.
        
        Args:
            provider_name: Provider name to validate
            
        Returns:
            Normalized provider name
            
        Raises:
            ValueError: If provider is not supported
        """
        if not self.is_provider_supported(provider_name):
            supported = self.get_all_supported_providers()
            raise ValueError(
                f"Provider '{provider_name}' is not supported by any-llm. "
                f"Supported providers: {', '.join(sorted(supported))}"
            )
        
        # Find exact case match
        provider_set = {provider.value: provider.value for provider in self.provider_names}
        for exact_name in provider_set:
            if exact_name.lower() == provider_name.lower():
                return exact_name
        
        # Fallback (should not reach here if is_provider_supported worked correctly)
        return provider_name
    
    # ===========================================
    # NEW COMBINED METHODS
    # ===========================================
    
    async def get_resolved_model_data(self, provider: str, user_model_name: str) -> Optional[Dict[str, Any]]:
        """Get model data after resolving user-friendly name to canonical name.
        
        Combines alias resolution with model data lookup.
        
        Args:
            provider: Provider name
            user_model_name: User-provided model name (may be alias)
            
        Returns:
            Model data dict or None if not found
        """
        # First resolve the model name using aliases
        canonical_name = await self.resolve_model_name(provider, user_model_name)
        
        # Then get the model data
        return await self.get_model_data(provider, canonical_name)
    
    def invalidate_all_caches(self):
        """Invalidate all cached data for reloading."""
        self._cached_litellm_data = None
        self._cached_aliases = None
    
    def get_data_directory_info(self) -> Dict[str, Any]:
        """Get information about data directory structure and file counts."""
        info = {
            "data_dir": str(self.data_dir),
            "shared_dir": str(self.data_dir / "shared"),
            "supported_dir": str(self.supported_data_dir),
            "files": {
                "litellm_json_exists": self.litellm_json_path.exists(),
                "aliases_json_exists": self.aliases_json_path.exists(),
                "supported_providers": []
            }
        }
        
        # Count provider data directories
        if self.supported_data_dir.exists():
            for provider_dir in self.supported_data_dir.iterdir():
                if provider_dir.is_dir():
                    models_file = provider_dir / "models.json"
                    info["files"]["supported_providers"].append({
                        "provider": provider_dir.name,
                        "models_file_exists": models_file.exists()
                    })
        
        return info


# Global instance
data_manager = DataManager()