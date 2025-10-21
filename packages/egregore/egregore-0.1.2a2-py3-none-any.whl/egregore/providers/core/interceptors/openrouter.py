"""OpenRouter interceptor for custom routing and optimization logic."""

from typing import Dict, Any, Optional, List
import logging

from .base import BaseInterceptor

logger = logging.getLogger(__name__)


class OpenRouterInterceptor(BaseInterceptor):
    """Interceptor to handle OpenRouter custom routing and optimization.
    
    OpenRouter provides advanced routing capabilities including:
    - Cost optimization
    - Fallback model selection
    - Provider preference management
    - Rate limit aware routing
    """
    
    def __init__(self, provider_name: str = "openrouter", **config):
        """Initialize OpenRouter interceptor.
        
        Args:
            provider_name: Should be "openrouter" for this interceptor
            **config: OpenRouter-specific configuration including:
                - cost_optimization: Enable cost-based routing (default: False)
                - fallback_enabled: Enable fallback routing (default: True)
                - preferred_providers: List of preferred provider names
                - max_cost_per_token: Maximum cost per token threshold
                - routing_strategy: 'cost', 'speed', 'quality', 'balanced'
        """
        super().__init__(provider_name, **config)
        
        # Routing configuration
        self.cost_optimization = config.get('cost_optimization', False)
        self.fallback_enabled = config.get('fallback_enabled', True)
        self.preferred_providers = config.get('preferred_providers', [])
        self.max_cost_per_token = config.get('max_cost_per_token', None)
        self.routing_strategy = config.get('routing_strategy', 'balanced')
        
        # OpenRouter-specific headers
        self.site_url = config.get('site_url', 'https://egregore.ai')
        self.app_name = config.get('app_name', 'Egregore')
        
        logger.info(f"Initialized OpenRouter interceptor with strategy: {self.routing_strategy}")
    
    def applies_to_request(self, request_payload: Dict[str, Any]) -> bool:
        """Check if this interceptor should be applied to the request.
        
        This interceptor applies to:
        1. OpenRouter provider requests
        2. Requests that can benefit from routing optimization
        
        Args:
            request_payload: The request payload to check
            
        Returns:
            True if this interceptor should process the request
        """
        try:
            # Check if provider is OpenRouter
            provider = request_payload.get('provider', '').lower()
            return provider == 'openrouter'
            
        except Exception as e:
            logger.warning(f"Error checking OpenRouter interceptor applicability: {e}")
            return False
    
    def intercept_request(self, request_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Apply OpenRouter routing optimizations to the request.
        
        Args:
            request_payload: The request payload to modify
            
        Returns:
            Modified request payload with OpenRouter routing enhancements
        """
        try:
            modified_payload = request_payload.copy()
            modifications_made = False
            
            # Add OpenRouter-specific headers
            if 'headers' not in modified_payload:
                modified_payload['headers'] = {}
            
            # Add application identification headers
            headers = modified_payload['headers']
            if 'HTTP-Referer' not in headers:
                headers['HTTP-Referer'] = self.site_url
                modifications_made = True
            
            if 'X-Title' not in headers:
                headers['X-Title'] = self.app_name
                modifications_made = True
            
            # Apply routing preferences
            routing_applied = self._apply_routing_preferences(modified_payload)
            if routing_applied:
                modifications_made = True
            
            # Apply cost optimization if enabled
            if self.cost_optimization:
                cost_applied = self._apply_cost_optimization(modified_payload)
                if cost_applied:
                    modifications_made = True
            
            # Apply fallback configuration if enabled
            if self.fallback_enabled:
                fallback_applied = self._apply_fallback_configuration(modified_payload)
                if fallback_applied:
                    modifications_made = True
            
            if modifications_made:
                logger.info("Applied OpenRouter routing optimizations")
            
            return modified_payload
            
        except Exception as e:
            logger.error(f"Error applying OpenRouter routing optimizations: {e}")
            # Return original payload if optimization fails
            return request_payload
    
    def _apply_routing_preferences(self, payload: Dict[str, Any]) -> bool:
        """Apply routing strategy preferences to the request.
        
        Args:
            payload: The request payload to modify
            
        Returns:
            True if modifications were made
        """
        modifications_made = False
        
        # Add routing strategy parameter
        if self.routing_strategy:
            if 'route' not in payload:
                payload['route'] = {}
            
            payload['route']['strategy'] = self.routing_strategy
            modifications_made = True
            logger.debug(f"Applied routing strategy: {self.routing_strategy}")
        
        # Add preferred providers if configured
        if self.preferred_providers:
            if 'route' not in payload:
                payload['route'] = {}
            
            payload['route']['preferred_providers'] = self.preferred_providers
            modifications_made = True
            logger.debug(f"Applied preferred providers: {self.preferred_providers}")
        
        return modifications_made
    
    def _apply_cost_optimization(self, payload: Dict[str, Any]) -> bool:
        """Apply cost optimization parameters to the request.
        
        Args:
            payload: The request payload to modify
            
        Returns:
            True if modifications were made
        """
        modifications_made = False
        
        # Add cost optimization flag
        if 'route' not in payload:
            payload['route'] = {}
        
        payload['route']['cost_optimization'] = True
        modifications_made = True
        
        # Add max cost threshold if configured
        if self.max_cost_per_token is not None:
            payload['route']['max_cost_per_token'] = self.max_cost_per_token
            logger.debug(f"Applied max cost per token: {self.max_cost_per_token}")
        
        logger.debug("Applied cost optimization settings")
        return modifications_made
    
    def _apply_fallback_configuration(self, payload: Dict[str, Any]) -> bool:
        """Apply fallback routing configuration to the request.
        
        Args:
            payload: The request payload to modify
            
        Returns:
            True if modifications were made
        """
        modifications_made = False
        
        # Enable fallback routing
        if 'route' not in payload:
            payload['route'] = {}
        
        payload['route']['fallback_enabled'] = True
        modifications_made = True
        
        # Configure fallback behavior based on routing strategy
        if self.routing_strategy == 'cost':
            # For cost strategy, fallback to next cheapest
            payload['route']['fallback_strategy'] = 'cost_ascending'
        elif self.routing_strategy == 'speed':
            # For speed strategy, fallback to next fastest
            payload['route']['fallback_strategy'] = 'speed_descending'
        elif self.routing_strategy == 'quality':
            # For quality strategy, fallback to next highest quality
            payload['route']['fallback_strategy'] = 'quality_descending'
        else:
            # Balanced strategy fallback
            payload['route']['fallback_strategy'] = 'balanced'
        
        logger.debug(f"Applied fallback configuration with strategy: {payload['route']['fallback_strategy']}")
        return modifications_made
    
    def intercept_response(self, response_data: Any, original_request: Dict[str, Any]) -> Any:
        """Intercept and potentially modify an OpenRouter response.
        
        Args:
            response_data: The response data to potentially modify
            original_request: The original request that generated this response
            
        Returns:
            Modified response data with OpenRouter routing metadata
        """
        try:
            # Add OpenRouter routing metadata to response if available
            if isinstance(response_data, dict):
                modified_response = response_data.copy()
                
                # Add routing metadata if not present
                if 'routing' not in modified_response:
                    modified_response['routing'] = {
                        'interceptor': 'OpenRouterInterceptor',
                        'strategy': self.routing_strategy,
                        'cost_optimization': self.cost_optimization,
                        'fallback_enabled': self.fallback_enabled
                    }
                
                return modified_response
            
            return response_data
            
        except Exception as e:
            logger.warning(f"Error intercepting OpenRouter response: {e}")
            return response_data
    
    def __str__(self) -> str:
        """String representation of the interceptor."""
        return (f"OpenRouterInterceptor(strategy={self.routing_strategy}, "
                f"cost_opt={self.cost_optimization}, fallback={self.fallback_enabled})")