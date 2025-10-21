"""Base interceptor framework for provider-specific features."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging
import asyncio
import inspect

logger = logging.getLogger(__name__)


class BaseInterceptor(ABC):
    """Base class for provider-specific interceptors."""
    
    def __init__(self, provider_name: str, **config):
        """Initialize interceptor with provider-specific configuration.
        
        Args:
            provider_name: Name of the provider this interceptor applies to
            **config: Provider-specific configuration parameters
        """
        self.provider_name = provider_name
        self.config = config
        self.enabled = config.get('enabled', True)
    
    @abstractmethod
    def applies_to_request(self, request_payload: Dict[str, Any]) -> bool:
        """Check if this interceptor should be applied to the given request.
        
        Args:
            request_payload: The request payload to potentially intercept
            
        Returns:
            True if this interceptor should process the request
        """
        pass
    
    @abstractmethod
    def intercept_request(self, request_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Intercept and potentially modify an outgoing request.
        
        Args:
            request_payload: The request payload to potentially modify
            
        Returns:
            Modified request payload (can be same as input if no changes needed)
        """
        pass
    
    def intercept_response(self, response_data: Any, original_request: Dict[str, Any]) -> Any:
        """Intercept and potentially modify an incoming response.
        
        Args:
            response_data: The response data to potentially modify
            original_request: The original request that generated this response
            
        Returns:
            Modified response data (can be same as input if no changes needed)
        """
        # Default implementation: no response modification
        return response_data
    
    def __str__(self) -> str:
        """String representation of interceptor."""
        return f"{self.__class__.__name__}(provider={self.provider_name}, enabled={self.enabled})"


class InterceptorRegistry:
    """Registry for managing provider interceptors with chaining logic."""
    
    def __init__(self):
        """Initialize empty interceptor registry."""
        self._interceptors: List[BaseInterceptor] = []
        logger.debug("Initialized InterceptorRegistry")
    
    def register(self, interceptor: BaseInterceptor) -> None:
        """Register a new interceptor.
        
        Args:
            interceptor: The interceptor to register
        """
        if not isinstance(interceptor, BaseInterceptor):
            raise TypeError(f"Expected BaseInterceptor, got {type(interceptor)}")
        
        self._interceptors.append(interceptor)
        logger.info(f"Registered interceptor: {interceptor}")
    
    def unregister(self, interceptor: BaseInterceptor) -> None:
        """Unregister an existing interceptor.
        
        Args:
            interceptor: The interceptor to unregister
        """
        if interceptor in self._interceptors:
            self._interceptors.remove(interceptor)
            logger.info(f"Unregistered interceptor: {interceptor}")
        else:
            logger.warning(f"Attempted to unregister non-registered interceptor: {interceptor}")
    
    def get_applicable_interceptors(self, request_payload: Dict[str, Any]) -> List[BaseInterceptor]:
        """Get all interceptors that apply to the given request.

        Args:
            request_payload: The request payload to check

        Returns:
            List of interceptors that should process this request
        """
        applicable = []
        for interceptor in self._interceptors:
            if not interceptor.enabled:
                continue

            # Check if applies_to_request is async
            applies_method = interceptor.applies_to_request
            if inspect.iscoroutinefunction(applies_method):
                # Handle async method - run in event loop if available, else skip
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # Cannot await in running loop - skip this interceptor
                        logger.warning(f"Skipping async interceptor {interceptor} in running event loop")
                        continue
                    else:
                        applies = loop.run_until_complete(applies_method(request_payload))
                except RuntimeError:
                    # No event loop - create one temporarily
                    applies = asyncio.run(applies_method(request_payload))
            else:
                # Sync method - call directly
                applies = applies_method(request_payload)

            if applies:
                applicable.append(interceptor)
                logger.debug(f"Interceptor {interceptor} applies to request")

        return applicable
    
    def apply_request_interceptors(self, request_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Apply all applicable request interceptors in sequence.

        Args:
            request_payload: The request payload to process

        Returns:
            Modified request payload after all applicable interceptors
        """
        applicable_interceptors = self.get_applicable_interceptors(request_payload)

        if not applicable_interceptors:
            logger.debug("No applicable request interceptors found")
            return request_payload

        # Apply interceptors in registration order
        modified_payload = request_payload.copy()
        for interceptor in applicable_interceptors:
            try:
                logger.debug(f"Applying request interceptor: {interceptor}")

                # Check if intercept_request is async
                intercept_method = interceptor.intercept_request
                if inspect.iscoroutinefunction(intercept_method):
                    # Handle async method
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            # Cannot await in running loop - skip
                            logger.warning(f"Skipping async interceptor {interceptor} in running event loop")
                            continue
                        else:
                            modified_payload = loop.run_until_complete(intercept_method(modified_payload))
                    except RuntimeError:
                        # No event loop - create one temporarily
                        modified_payload = asyncio.run(intercept_method(modified_payload))
                else:
                    # Sync method - call directly
                    modified_payload = intercept_method(modified_payload)

            except Exception as e:
                logger.error(f"Error in request interceptor {interceptor}: {e}")
                # Continue with other interceptors - don't let one failure break the chain
                continue

        logger.info(f"Applied {len(applicable_interceptors)} request interceptors")
        return modified_payload
    
    def apply_response_interceptors(self, response_data: Any, original_request: Dict[str, Any]) -> Any:
        """Apply all applicable response interceptors in reverse order.
        
        Args:
            response_data: The response data to process
            original_request: The original request that generated this response
            
        Returns:
            Modified response data after all applicable interceptors
        """
        applicable_interceptors = self.get_applicable_interceptors(original_request)
        
        if not applicable_interceptors:
            logger.debug("No applicable response interceptors found")
            return response_data
        
        # Apply interceptors in reverse registration order for response processing
        modified_response = response_data
        for interceptor in reversed(applicable_interceptors):
            try:
                logger.debug(f"Applying response interceptor: {interceptor}")
                modified_response = interceptor.intercept_response(modified_response, original_request)
            except Exception as e:
                logger.error(f"Error in response interceptor {interceptor}: {e}")
                # Continue with other interceptors - don't let one failure break the chain
                continue
        
        logger.info(f"Applied {len(applicable_interceptors)} response interceptors")
        return modified_response
    
    def clear(self) -> None:
        """Clear all registered interceptors."""
        count = len(self._interceptors)
        self._interceptors.clear()
        logger.info(f"Cleared {count} interceptors from registry")
    
    def list_interceptors(self) -> List[BaseInterceptor]:
        """Get a copy of all registered interceptors.
        
        Returns:
            List of all registered interceptors
        """
        return self._interceptors.copy()
    
    def __len__(self) -> int:
        """Get number of registered interceptors."""
        return len(self._interceptors)


# Global interceptor registry instance
_global_registry: Optional[InterceptorRegistry] = None


def get_global_interceptor_registry() -> InterceptorRegistry:
    """Get the global interceptor registry instance.
    
    Returns:
        The global InterceptorRegistry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = InterceptorRegistry()
        logger.debug("Created global InterceptorRegistry")
    return _global_registry


def register_interceptor(interceptor: BaseInterceptor) -> None:
    """Register an interceptor with the global registry.
    
    Args:
        interceptor: The interceptor to register globally
    """
    get_global_interceptor_registry().register(interceptor)


def unregister_interceptor(interceptor: BaseInterceptor) -> None:
    """Unregister an interceptor from the global registry.
    
    Args:
        interceptor: The interceptor to unregister globally
    """
    get_global_interceptor_registry().unregister(interceptor)