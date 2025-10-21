"""
Pydantic models for LLM model management.

This module provides structured data models for managing LLM model information,
capabilities, limits, and metadata across different providers.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path
import json
import threading
import asyncio
from abc import ABC, abstractmethod


class ModelCapabilities(BaseModel):
    """Model capability information"""
    reasoning: bool = Field(False, description="Reasoning/thinking capabilities")
    tools: bool = Field(True, description="Function calling support")
    streaming: bool = Field(True, description="Stream responses")
    vision: bool = Field(False, description="Image input support")
    audio: bool = Field(False, description="Audio input/output")
    structured_output_native: bool = Field(False, description="Native structured output support")


class ModelLimits(BaseModel):
    """Model limits and constraints"""
    context_tokens: int = Field(..., description="Total context window (input + output)", gt=0)
    max_input_tokens: int = Field(..., description="Maximum input tokens", gt=0)
    max_output_tokens: int = Field(..., description="Maximum output tokens", gt=0)
    knowledge_cutoff: str = Field(..., description="Training data cutoff")


class ModelCostAndLimits(BaseModel):
    """Model cost and rate limiting information"""
    cost_per_1k_input: float = Field(..., description="USD per 1K input tokens", ge=0)
    cost_per_1k_output: float = Field(..., description="USD per 1K output tokens", ge=0)
    rate_limit_rpm: int = Field(..., description="Requests per minute", ge=0)
    rate_limit_tpm: int = Field(..., description="Tokens per minute", ge=0)


class ModelMetadata(BaseModel):
    """Model metadata and lifecycle information"""
    deprecated: bool = Field(False, description="Model is deprecated")
    deprecation_date: Optional[str] = Field(None, description="Deprecation date")
    replacement_model: Optional[str] = Field(None, description="Replacement model")
    oauth_ready: bool = Field(False, description="OAuth authentication support")
    special_features: Dict[str, Any] = Field(default_factory=dict, description="Provider-specific features")
    last_updated: str = Field(
        default_factory=lambda: datetime.now().isoformat(), 
        description="Last update timestamp"
    )


class ModelInfo(BaseModel):
    """Comprehensive model information - ported to Pydantic"""
    
    # Basic info
    name: str = Field(..., description="Model identifier")
    display_name: str = Field(..., description="Human-readable name")
    provider: str = Field(..., description="Provider name")
    
    # Structured components
    capabilities: ModelCapabilities = Field(..., description="Model capabilities")
    limits: ModelLimits = Field(..., description="Model limits and constraints")
    cost_and_limits: Optional[ModelCostAndLimits] = Field(None, description="Cost and rate limiting")
    metadata: ModelMetadata = Field(default_factory=ModelMetadata, description="Metadata and lifecycle info")

    model_config = ConfigDict(arbitrary_types_allowed=True)


class BaseModelRetriever(ABC):
    """Abstract base class for model retrievers that fetch from provider APIs"""
    
    def __init__(self, provider_name: str):
        """Initialize retriever for a specific provider"""
        self.provider_name = provider_name
    
    @abstractmethod
    async def fetch_models(self) -> Dict[str, ModelInfo]:
        """Fetch current models from provider API
        
        Returns:
            Dictionary mapping model names to ModelInfo objects
        """
        pass
    
    @abstractmethod
    async def retrieve_and_save(self, storage_path: Path) -> None:
        """Fetch models from API and save to storage
        
        Args:
            storage_path: Path to save the model data JSON file
        """
        pass


class ModelList(BaseModel):
    """Container for managing a provider's models with refresh capabilities"""
    provider: str = Field(..., description="Provider name")
    models: Dict[str, ModelInfo] = Field(default_factory=dict, description="Model definitions")
    last_updated: str = Field(
        default_factory=lambda: datetime.now().isoformat(), 
        description="Last update timestamp"
    )
    update_frequency_hours: int = Field(6, description="Update frequency", gt=0)
    egregore_version: Optional[str] = Field(None, description="Egregore version")
    fetcher_fingerprint: Optional[str] = Field(None, description="Fetcher fingerprint")
    
    # Non-pydantic fields for storage and retrieval
    _storage_path: Optional[Path] = None
    _retriever: Optional[BaseModelRetriever] = None
    _lock: threading.RLock = None
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    def __init__(self, **data):
        """Initialize ModelList with storage capabilities"""
        super().__init__(**data)
        self._lock = threading.RLock()
        self._storage_path = None
        self._retriever = None
    
    def __contains__(self, model_name: str) -> bool:
        """Check if model exists: 'gpt-4o' in model_list"""
        return model_name in self.models
    
    def __getitem__(self, model_name: str) -> ModelInfo:
        """Get model info: model_list['gpt-4o']"""
        if model_name not in self.models:
            available = list(self.models.keys())[:5]
            raise KeyError(f"Model '{model_name}' not found. Available: {available}")
        return self.models[model_name]
    
    def __iter__(self):
        """Iterate over model names"""
        return iter(self.models.keys())
    
    def __len__(self) -> int:
        """Get number of models"""
        return len(self.models)
    
    
    async def refresh(self) -> bool:
        """Manually refresh model list from provider API
        
        Returns:
            True if refresh succeeded, False otherwise
        """
        return await self.refresh_from_api()
    
    
    def set_storage_path(self, storage_path: Path) -> None:
        """Set the path for JSON storage"""
        with self._lock:
            self._storage_path = storage_path
            # Try to load existing data
            if storage_path.exists():
                self.load_from_storage()
    
    def set_retriever(self, retriever: BaseModelRetriever) -> None:
        """Set the model retriever for API updates"""
        with self._lock:
            self._retriever = retriever
    
    def save_to_storage(self) -> None:
        """Save current model list to JSON storage"""
        if not self._storage_path:
            return
        
        with self._lock:
            # Ensure directory exists
            self._storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert to JSON-serializable format
            data = {
                "provider": self.provider,
                "last_updated": self.last_updated,
                "update_frequency_hours": self.update_frequency_hours,
                "egregore_version": self.egregore_version,
                "fetcher_fingerprint": self.fetcher_fingerprint,
                "models": {}
            }
            
            # Serialize each model
            for model_name, model_info in self.models.items():
                data["models"][model_name] = model_info.model_dump()
            
            # Write to file
            with open(self._storage_path, 'w') as f:
                json.dump(data, f, indent=2, sort_keys=True)
    
    def load_from_storage(self) -> bool:
        """Load model list from JSON storage
        
        Returns:
            True if loaded successfully, False otherwise
        """
        if not self._storage_path or not self._storage_path.exists():
            return False
        
        try:
            with self._lock:
                with open(self._storage_path, 'r') as f:
                    data = json.load(f)
                
                # Update basic fields
                self.provider = data.get("provider", self.provider)
                self.last_updated = data.get("last_updated", self.last_updated)
                self.update_frequency_hours = data.get("update_frequency_hours", self.update_frequency_hours)
                self.egregore_version = data.get("egregore_version")
                self.fetcher_fingerprint = data.get("fetcher_fingerprint")
                
                # Load models
                self.models.clear()
                for model_name, model_data in data.get("models", {}).items():
                    try:
                        model_info = ModelInfo(**model_data)
                        self.models[model_name] = model_info
                    except Exception as e:
                        # Skip invalid model data but continue loading others
                        continue
                
                return True
                
        except Exception as e:
            return False
    
    async def refresh_from_api(self) -> bool:
        """Refresh models from API using the configured retriever
        
        Returns:
            True if refresh succeeded, False otherwise
        """
        if not self._retriever:
            return False
        
        try:
            # Fetch new models from API
            new_models = await self._retriever.fetch_models()
            
            with self._lock:
                # Update models
                self.models.clear()
                self.models.update(new_models)
                
                # Update timestamp
                self.last_updated = datetime.now().isoformat()
                
                # Save to storage
                self.save_to_storage()
                
            return True
            
        except Exception as e:
            return False
    
    def needs_refresh(self) -> bool:
        """Check if models need refreshing based on age"""
        if not self.last_updated:
            return True
        
        try:
            last_updated = datetime.fromisoformat(self.last_updated.replace('Z', '+00:00'))
            age_hours = (datetime.now() - last_updated.replace(tzinfo=None)).total_seconds() / 3600
            return age_hours >= self.update_frequency_hours
        except Exception:
            return True  # If parsing fails, assume refresh needed
    
    async def refresh_if_needed(self) -> bool:
        """Refresh models only if they are stale
        
        Returns:
            True if refresh was performed or not needed, False if refresh failed
        """
        if not self.needs_refresh():
            return True  # No refresh needed
        
        if not self._retriever:
            return False  # Can't refresh without retriever
        
        return await self.refresh_from_api()
    
    async def _reload_from_storage(self) -> None:
        """Reload models from storage after refresh"""
        self.load_from_storage()


class PricingInfo(BaseModel):
    """Pricing information for a model."""
    input_cost_per_1k: float = Field(..., description="USD per 1K input tokens", ge=0)
    output_cost_per_1k: float = Field(..., description="USD per 1K output tokens", ge=0)
    currency: str = Field(default="USD", description="Currency code")
    free_tier_limit: Optional[int] = Field(None, description="Free tier token limit")
    notes: Optional[str] = Field(None, description="Additional pricing notes")


class ProviderModelConfig(BaseModel):
    """Complete configuration for a provider's models."""
    provider: str = Field(..., description="Provider name")
    last_updated: str = Field(..., description="Last update timestamp")
    update_frequency_hours: int = Field(default=6, description="Update frequency in hours")
    models: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Model configurations")
    egregore_version: Optional[str] = Field(None, description="Egregore version")
    fetcher_fingerprint: Optional[str] = Field(None, description="Fetcher version fingerprint")
    
