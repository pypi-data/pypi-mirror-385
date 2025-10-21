"""Interceptors for provider-specific features like OAuth and custom routing."""

from .base import (
    BaseInterceptor,
    InterceptorRegistry, 
    get_global_interceptor_registry,
    register_interceptor,
    unregister_interceptor
)
from .anthropic_oauth import AnthropicOAuthInterceptor
from .google_oauth import GoogleOAuthInterceptor
from .openrouter import OpenRouterInterceptor

__all__ = [
    'BaseInterceptor',
    'InterceptorRegistry',
    'get_global_interceptor_registry', 
    'register_interceptor',
    'unregister_interceptor',
    'AnthropicOAuthInterceptor',
    'GoogleOAuthInterceptor',
    'OpenRouterInterceptor'
]