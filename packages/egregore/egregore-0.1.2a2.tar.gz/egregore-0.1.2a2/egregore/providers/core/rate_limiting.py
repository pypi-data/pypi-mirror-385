"""
Universal rate limiting system for any provider.

Extracted from core/provider/provider_management/provider_manager.py
to be integrated directly into the GeneralPurposeProvider.
"""

from typing import Dict, Optional, List, Any
from enum import Enum
from dataclasses import dataclass
import asyncio
import time

from .exceptions import (
    RateLimitExceededError,
    CircuitBreakerOpenError,
)


class InteractionPattern(Enum):
    """Types of interactions with providers"""
    SYNC = "sync"
    ASYNC = "async" 
    STREAM = "stream"
    ASTREAM = "astream"


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting per provider"""
    requests_per_minute: int = 60
    requests_per_hour: int = 3600
    exponential_backoff_base: float = 2.0
    max_backoff_seconds: float = 300.0  # 5 minutes
    circuit_breaker_threshold: int = 5  # failures before opening circuit
    circuit_breaker_timeout: float = 60.0  # seconds before retry


class RateLimiter:
    """Generic rate limiter that wraps provider methods"""
    
    def __init__(self, provider_name: str, config: RateLimitConfig):
        self.provider_name = provider_name
        self.config = config
        self.request_timestamps: List[float] = []
        self.consecutive_failures = 0
        self.circuit_open_until: Optional[float] = None
        self.failure_timestamps: List[float] = []
        self.total_requests = 0
        self.successful_requests = 0
    
    async def check_rate_limits(self) -> None:
        """Check if request is allowed under current rate limits"""
        current_time = time.time()
        
        # Check circuit breaker
        if self.circuit_open_until and current_time < self.circuit_open_until:
            backoff_remaining = self.circuit_open_until - current_time
            raise CircuitBreakerOpenError(f"Circuit breaker open for {self.provider_name}, retry in {backoff_remaining:.1f}s")
        
        # Clean old timestamps
        minute_ago = current_time - 60
        self.request_timestamps = [ts for ts in self.request_timestamps if ts > minute_ago]
        
        # Check rate limits
        recent_requests = len(self.request_timestamps)
        if recent_requests >= self.config.requests_per_minute:
            wait_time = 60 - (current_time - self.request_timestamps[0])
            raise RateLimitExceededError(f"Rate limit exceeded for {self.provider_name}, retry in {wait_time:.1f}s")
        
        # Record this request attempt
        self.request_timestamps.append(current_time)
        self.total_requests += 1
    
    def record_success(self) -> None:
        """Record successful request"""
        self.consecutive_failures = 0
        self.successful_requests += 1
        # Clear circuit breaker
        self.circuit_open_until = None
    
    def record_failure(self, error: Exception) -> None:
        """Record failed request and update circuit breaker"""
        self.consecutive_failures += 1
        self.failure_timestamps.append(time.time())
        
        # Open circuit breaker after threshold failures
        if self.consecutive_failures >= self.config.circuit_breaker_threshold:
            backoff_time = min(
                self.config.max_backoff_seconds,
                self.config.exponential_backoff_base ** self.consecutive_failures
            )
            self.circuit_open_until = time.time() + backoff_time
            
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiter statistics"""
        success_rate = self.successful_requests / self.total_requests if self.total_requests > 0 else 0
        return {
            "provider": self.provider_name,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "success_rate": success_rate,
            "consecutive_failures": self.consecutive_failures,
            "circuit_open": self.circuit_open_until is not None and time.time() < self.circuit_open_until
        }


def get_default_rate_config(provider_name: str) -> RateLimitConfig:
    """Get default rate limit configuration for provider"""
    provider_configs = {
        "openai": RateLimitConfig(requests_per_minute=50, requests_per_hour=3000),
        "anthropic": RateLimitConfig(requests_per_minute=40, requests_per_hour=2400), 
        "google": RateLimitConfig(requests_per_minute=60, requests_per_hour=3600)
    }
    return provider_configs.get(provider_name.lower(), RateLimitConfig())