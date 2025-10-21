"""Provider management system for Egregore v2."""

from .core.model_manager import BaseModelManager
from .core.interface import BaseProvider  
from .core.model_types import ModelInfo, PricingInfo, ProviderModelConfig

# Try to import Anthropic provider if available
try:
    from .anthropic import AnthropicProvider
    _anthropic_available = True
except ImportError:
    _anthropic_available = False

__all__ = [
    'BaseModelManager',
    'BaseProvider',
    'ModelInfo', 
    'PricingInfo',
    'ProviderModelConfig'
]

if _anthropic_available:
    __all__.append('AnthropicProvider')