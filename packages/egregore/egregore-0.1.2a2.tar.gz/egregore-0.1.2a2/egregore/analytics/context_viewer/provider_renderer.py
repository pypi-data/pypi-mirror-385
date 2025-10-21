"""
ProviderRenderer for provider-specific content formatting and analysis.

Provides provider-specific rendering with token estimation and cost analysis.
Integrates with the existing egregore provider system.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path
import json
import logging

from egregore.core.context_management import Context

logger = logging.getLogger(__name__)


@dataclass
class TokenEstimate:
    """Token count estimation result"""
    total_tokens: int
    system_tokens: int
    conversation_tokens: int
    active_tokens: int
    model: str
    input_cost_per_token: float = 0.01
    output_cost_per_token: float = 0.02
    
    @property
    def estimated_cost(self) -> float:
        """Estimate cost based on real pricing data"""
        # Assume 70% input, 30% output tokens
        input_tokens = int(self.total_tokens * 0.7)
        output_tokens = int(self.total_tokens * 0.3)
        
        return (input_tokens * self.input_cost_per_token) + (output_tokens * self.output_cost_per_token)


@dataclass
class ProviderPreview:
    """Complete provider preview with content and metadata"""
    provider_type: str
    model: str
    formatted_content: str
    token_estimate: TokenEstimate
    provider_thread: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __str__(self) -> str:
        """Format provider preview for display"""
        lines = []
        lines.append(f"=== {self.provider_type.upper()} PROVIDER PREVIEW ===")
        lines.append(f"Model: {self.model}")
        lines.append(f"Estimated Tokens: {self.token_estimate.total_tokens}")
        lines.append(f"Estimated Cost: ${self.token_estimate.estimated_cost:.3f}")
        lines.append("")
        lines.append("PROVIDER THREAD:")
        lines.append(self.formatted_content)
        lines.append("")
        lines.append("=== TOKEN BREAKDOWN ===")
        lines.append(f"System Context: {self.token_estimate.system_tokens} tokens")
        lines.append(f"Conversation History: {self.token_estimate.conversation_tokens} tokens")
        lines.append(f"Active Message: {self.token_estimate.active_tokens} tokens")
        lines.append(f"Total: {self.token_estimate.total_tokens} tokens")
        
        return '\n'.join(lines)


class ProviderRenderer:
    """Handles provider-specific content formatting and token estimation"""
    
    def __init__(self):
        """Initialize ProviderRenderer with real provider data"""
        self._provider_data = None
        self._model_data = None
        self._load_provider_data()
    
    def _load_provider_data(self):
        """Load provider data from the egregore provider system"""
        try:
            # Find egregore root directory
            egregore_root = Path(__file__).resolve().parents[3]
            if egregore_root.name != "egregore":
                # Search upwards for egregore package
                for p in Path(__file__).resolve().parents:
                    if (p / "__init__.py").exists() and p.name == "egregore":
                        egregore_root = p
                        break
            
            # Load LiteLLM models data
            models_path = egregore_root / "providers" / "data" / "litellm_models.json"
            if models_path.exists():
                with open(models_path, 'r') as f:
                    self._model_data = json.load(f)
                logger.debug(f"Loaded model data from {models_path}")
            else:
                logger.warning(f"Model data not found at {models_path}")
                self._model_data = {}
            
            # Load supported providers
            supported_dir = egregore_root / "providers" / "data" / "supported"
            self._provider_data = {}
            
            if supported_dir.exists():
                for provider_dir in supported_dir.iterdir():
                    if provider_dir.is_dir():
                        models_file = provider_dir / "models.json"
                        if models_file.exists():
                            with open(models_file, 'r') as f:
                                provider_models = json.load(f)
                                self._provider_data[provider_dir.name] = provider_models
                
                logger.debug(f"Loaded {len(self._provider_data)} provider configurations")
        except Exception as e:
            logger.error(f"Failed to load provider data: {e}")
            self._provider_data = {}
            self._model_data = {}
    
    def _get_provider_config(self, provider_type: str, model: str) -> Dict[str, Any]:
        """Get provider configuration from real data"""
        # First try to find model in main model data
        if self._model_data and model in self._model_data:
            model_info = self._model_data[model]
            return {
                'provider_type': provider_type,
                'model': model,
                'supports_functions': model_info.get('supports_function_calling', False),
                'max_tokens': model_info.get('max_tokens', 4096),
                'input_cost_per_token': model_info.get('input_cost_per_token', 0.0),
                'output_cost_per_token': model_info.get('output_cost_per_token', 0.0),
                'litellm_provider': model_info.get('litellm_provider', provider_type),
                'mode': model_info.get('mode', 'chat')
            }
        
        # Try provider-specific data
        if self._provider_data and provider_type in self._provider_data:
            provider_models = self._provider_data[provider_type]
            if model in provider_models:
                model_info = provider_models[model]
                return {
                    'provider_type': provider_type,
                    'model': model,
                    'supports_functions': model_info.get('supports_function_calling', False),
                    'max_tokens': model_info.get('max_tokens', 4096),
                    'input_cost_per_token': model_info.get('input_cost_per_token', 0.0),
                    'output_cost_per_token': model_info.get('output_cost_per_token', 0.0)
                }
        
        # Fallback for unknown models
        return {
            'provider_type': provider_type,
            'model': model,
            'supports_functions': False,
            'max_tokens': 4096,
            'input_cost_per_token': 0.01,
            'output_cost_per_token': 0.02
        }
    
    def render_provider_preview(
        self,
        context: Context,
        provider_type: str,
        model: str,
        include_costs: bool = True,
        **kwargs
    ) -> ProviderPreview:
        """Generate provider-specific rendering with token estimates
        
        Args:
            context: Context to render
            provider_type: Provider type (e.g., "openai", "anthropic")
            model: Model name (e.g., "gpt-4", "claude-3")
            include_costs: Include cost estimation
            **kwargs: Additional provider-specific options
        
        Returns:
            ProviderPreview with formatted content and metadata
        
        Wiring: Uses context.render() + provider-specific formatting
        """
        # Get raw content from context
        raw_content = context.render()
        
        # Get provider configuration from real data
        provider_config = self._get_provider_config(provider_type, model)
        
        # Format for specific provider
        formatted_content = self._format_for_provider(
            raw_content, provider_type, provider_config, **kwargs
        )
        
        # Estimate tokens
        token_estimate = self.estimate_tokens(raw_content, model, provider_type)
        
        # Create provider thread representation
        provider_thread = self._create_provider_thread(
            context, provider_type, provider_config
        )
        
        return ProviderPreview(
            provider_type=provider_type,
            model=model,
            formatted_content=formatted_content,
            token_estimate=token_estimate,
            provider_thread=provider_thread,
            metadata={
                'provider_config': provider_config,
                'render_options': kwargs
            }
        )
    
    def _format_for_provider(
        self,
        content: str,
        provider_type: str,
        provider_config: Dict[str, Any],
        **kwargs
    ) -> str:
        """Format content for specific provider"""
        if provider_type.lower() == 'openai':
            return self._format_for_openai(content, provider_config, **kwargs)
        elif provider_type.lower() == 'anthropic':
            return self._format_for_anthropic(content, provider_config, **kwargs)
        elif provider_type.lower() == 'cohere':
            return self._format_for_cohere(content, provider_config, **kwargs)
        else:
            return self._format_generic(content, provider_config, **kwargs)
    
    def _format_for_openai(self, content: str, config: Dict[str, Any], **kwargs) -> str:
        """Format content for OpenAI API"""
        # Simulate OpenAI message format
        return f'{{\n  "model": "{kwargs.get("model", "gpt-4")}",\n  "messages": [\n    {{\n      "role": "user",\n      "content": "{content[:100]}..."\n    }}\n  ]\n}}'
    
    def _format_for_anthropic(self, content: str, config: Dict[str, Any], **kwargs) -> str:
        """Format content for Anthropic API"""
        # Simulate Anthropic message format
        return f'{{\n  "model": "{kwargs.get("model", "claude-3-sonnet")}",\n  "messages": [\n    {{\n      "role": "user",\n      "content": "{content[:100]}..."\n    }}\n  ]\n}}'
    
    def _format_for_cohere(self, content: str, config: Dict[str, Any], **kwargs) -> str:
        """Format content for Cohere API"""
        return f'{{\n  "model": "{kwargs.get("model", "command-r-plus")}",\n  "message": "{content[:100]}..."\n}}'
    
    def _format_generic(self, content: str, config: Dict[str, Any], **kwargs) -> str:
        """Generic formatting fallback"""
        return f"Provider Content:\n{content}"
    
    def _create_provider_thread(
        self,
        context: Context,
        provider_type: str,
        provider_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create provider thread representation"""
        # This is a simplified representation
        # In a real implementation, this would use the actual provider formatting logic
        content = context.render()
        return {
            'provider_type': provider_type,
            'model': provider_config.get('model', 'unknown'),
            'content_preview': content[:200] + '...' if len(content) > 200 else content,
            'supports_functions': provider_config.get('supports_functions', False),
            'max_tokens': provider_config.get('max_tokens', 4096)
        }
    
    def estimate_tokens(self, content: str, model: str, provider_type: str = 'generic') -> TokenEstimate:
        """Estimate token count for provider content
        
        Args:
            content: Content to analyze
            model: Model name for tokenization
            provider_type: Provider type for pricing
        
        Returns:
            TokenEstimate with breakdown
        """
        # TODO: Integrate with egregore's token counting system
        # For now, use simple estimation (~4 characters per token)
        total_chars = len(content)
        estimated_tokens = max(1, total_chars // 4)
        
        # Rough breakdown (would need real section analysis)
        system_tokens = max(0, estimated_tokens // 4)
        conversation_tokens = max(0, estimated_tokens // 2)
        active_tokens = estimated_tokens - system_tokens - conversation_tokens
        
        # Get real pricing data
        provider_config = self._get_provider_config(provider_type, model)
        
        return TokenEstimate(
            total_tokens=estimated_tokens,
            system_tokens=system_tokens,
            conversation_tokens=conversation_tokens,
            active_tokens=active_tokens,
            model=model,
            input_cost_per_token=provider_config.get('input_cost_per_token', 0.01),
            output_cost_per_token=provider_config.get('output_cost_per_token', 0.02)
        )
    
    def get_supported_providers(self) -> List[str]:
        """Get list of supported provider types from real data"""
        providers = set()
        
        # Add providers from loaded data
        if self._provider_data:
            providers.update(self._provider_data.keys())
        
        # Add providers from model data (litellm_provider field)
        if self._model_data:
            for model_info in self._model_data.values():
                if isinstance(model_info, dict) and 'litellm_provider' in model_info:
                    providers.add(model_info['litellm_provider'])
        
        return sorted(list(providers))
    
    def get_provider_info(self, provider_type: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific provider from real data"""
        if self._provider_data and provider_type in self._provider_data:
            return self._provider_data[provider_type]
        return None
    
    def estimate_cost_breakdown(self, token_estimate: TokenEstimate, provider_type: str, model: str = None) -> Dict[str, float]:
        """Estimate cost breakdown using real provider pricing data
        
        Args:
            token_estimate: Token count estimate
            provider_type: Provider type for pricing
            model: Specific model for accurate pricing
        
        Returns:
            Dictionary with cost breakdown
        """
        # Get real pricing from provider config
        provider_config = self._get_provider_config(provider_type, model or 'default')
        
        input_cost_per_token = provider_config.get('input_cost_per_token', 0.01)
        output_cost_per_token = provider_config.get('output_cost_per_token', 0.02)
        
        # Assume 70% input, 30% output (rough estimate)
        input_tokens = int(token_estimate.total_tokens * 0.7)
        output_tokens = int(token_estimate.total_tokens * 0.3)
        
        input_cost = input_tokens * input_cost_per_token
        output_cost = output_tokens * output_cost_per_token
        
        return {
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'input_cost': input_cost,
            'output_cost': output_cost,
            'total_cost': input_cost + output_cost,
            'provider_type': provider_type,
            'model': model,
            'input_cost_per_token': input_cost_per_token,
            'output_cost_per_token': output_cost_per_token
        }