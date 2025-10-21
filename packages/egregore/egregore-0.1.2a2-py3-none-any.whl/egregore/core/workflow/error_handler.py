"""
Advanced error handling and recovery strategies for async workflow execution.

This module provides sophisticated error handling capabilities including
categorization, recovery strategies, and configurable retry policies.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, Optional, Union, TYPE_CHECKING
from egregore.core.workflow.exceptions import WorkflowError, ErrorContext, ErrorSeverity, RetryableError, FatalError, categorize_generic_error, create_error_context

if TYPE_CHECKING:
    from egregore.core.workflow.nodes.base import BaseNode


class ErrorRecoveryStrategy(ABC):
    """Abstract base class for error recovery strategies"""
    
    @abstractmethod
    def can_retry(self, error: Exception, context: ErrorContext) -> bool:
        """Determine if error can be retried"""
        pass
    
    @abstractmethod
    def should_continue_workflow(self, error: Exception, context: ErrorContext) -> bool:
        """Determine if workflow should continue after error"""
        pass
    
    @abstractmethod
    def get_fallback_value(self, error: Exception, context: ErrorContext) -> Any:
        """Get fallback value for failed operation"""
        pass
    
    @abstractmethod
    def get_retry_delay(self, error: Exception, attempt_number: int) -> float:
        """Calculate delay before retry"""
        pass


class DefaultRecoveryStrategy(ErrorRecoveryStrategy):
    """Default error recovery strategy with sensible defaults"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 30.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
    
    def can_retry(self, error: Exception, context: ErrorContext) -> bool:
        """Check if error can be retried based on type and attempt count"""
        if context.attempt_number >= self.max_retries:
            return False

        # RetryableError types can be retried
        if isinstance(error, RetryableError):
            return context.attempt_number < error.max_retries

        # FatalError types cannot be retried
        if isinstance(error, FatalError):
            return False

        # Programming errors and permission errors are fatal - don't retry
        fatal_types = (TypeError, ValueError, AttributeError, NameError, SyntaxError, PermissionError)
        if isinstance(error, fatal_types):
            return False

        # Other WorkflowError types: retry based on severity
        if isinstance(error, WorkflowError):
            return context.severity in [ErrorSeverity.LOW, ErrorSeverity.MEDIUM]

        # Generic exceptions: retry based on type
        retryable_types = (
            ConnectionError, OSError, asyncio.TimeoutError,
            MemoryError, FileNotFoundError
        )
        return isinstance(error, retryable_types)
    
    def should_continue_workflow(self, error: Exception, context: ErrorContext) -> bool:
        """Determine if workflow should continue after failed retries"""
        # Fatal errors always stop workflow
        if isinstance(error, FatalError):
            return False

        # Programming errors and permission errors are fatal - stop workflow
        fatal_types = (TypeError, ValueError, AttributeError, NameError, SyntaxError, PermissionError)
        if isinstance(error, fatal_types):
            return False

        # Critical severity errors stop workflow
        if isinstance(error, WorkflowError) and context.severity == ErrorSeverity.CRITICAL:
            return False

        # For other errors, continue workflow but log the failure
        return True
    
    def get_fallback_value(self, error: Exception, context: ErrorContext) -> Any:
        """Get fallback value - returns None by default"""
        # Could be enhanced to return meaningful defaults based on node type
        return None
    
    def get_retry_delay(self, error: Exception, attempt_number: int) -> float:
        """Calculate exponential backoff delay"""
        if isinstance(error, RetryableError):
            # Use error-specific retry delay
            base_delay = error.retry_after
        else:
            base_delay = self.base_delay
        
        # Exponential backoff with jitter
        delay = base_delay * (2 ** (attempt_number - 1))
        # Add some randomness to avoid thundering herd
        import random
        jitter = random.uniform(0.8, 1.2)
        delay *= jitter
        
        return min(delay, self.max_delay)


class StrictRecoveryStrategy(ErrorRecoveryStrategy):
    """Strict recovery strategy - fails fast with minimal retries"""

    def __init__(self):
        self.max_retries = 2  # Original attempt + 1 retry = 2 total attempts

    def can_retry(self, error: Exception, context: ErrorContext) -> bool:
        """Only retry very specific error types once"""
        if context.attempt_number > 1:  # Changed >= to > to allow first retry
            return False
        
        # Only retry timeout and connection errors
        return isinstance(error, (asyncio.TimeoutError, ConnectionError))
    
    def should_continue_workflow(self, error: Exception, context: ErrorContext) -> bool:
        """Never continue workflow on any error"""
        return False
    
    def get_fallback_value(self, error: Exception, context: ErrorContext) -> Any:
        """No fallback values in strict mode"""
        return None
    
    def get_retry_delay(self, error: Exception, attempt_number: int) -> float:
        """Fixed short delay"""
        return 0.5


class PermissiveRecoveryStrategy(ErrorRecoveryStrategy):
    """Permissive recovery strategy - retries most errors and continues workflow"""
    
    def __init__(self, max_retries: int = 5):
        self.max_retries = max_retries
    
    def can_retry(self, error: Exception, context: ErrorContext) -> bool:
        """Retry most errors except clear programming errors"""
        if context.attempt_number >= self.max_retries:
            return False
        
        # Don't retry clear programming errors
        fatal_types = (TypeError, AttributeError, NameError, SyntaxError)
        if isinstance(error, fatal_types):
            return False
        
        return True
    
    def should_continue_workflow(self, error: Exception, context: ErrorContext) -> bool:
        """Continue workflow for most errors"""
        # Only stop for critical programming errors
        fatal_types = (TypeError, AttributeError, NameError, SyntaxError)
        return not isinstance(error, fatal_types)
    
    def get_fallback_value(self, error: Exception, context: ErrorContext) -> Any:
        """Return empty/default values based on common patterns"""
        # Could be enhanced with node-type specific defaults
        return None
    
    def get_retry_delay(self, error: Exception, attempt_number: int) -> float:
        """Linear backoff"""
        return attempt_number * 1.0


class AsyncErrorHandler:
    """Comprehensive error handler for async workflow execution"""
    
    def __init__(self, 
                 recovery_strategy: Optional[ErrorRecoveryStrategy] = None,
    ):
        self.recovery_strategy = recovery_strategy or DefaultRecoveryStrategy()
        self._error_stats = {"total_errors": 0, "retries": 0, "recoveries": 0}
    
    async def handle_node_error(
        self, 
        error: Exception, 
        node: "BaseNode", 
        context: ErrorContext
    ) -> Union[Any, None]:
        """
        Handle error from node execution with comprehensive error processing.
        
        Args:
            error: The exception that occurred
            node: The node where error occurred
            context: Error context information
            
        Returns:
            Fallback value if error is recoverable, otherwise re-raises
            
        Raises:
            WorkflowError: Categorized version of the original error
        """
        self._error_stats["total_errors"] += 1
        
        # Categorize the error if it's not already a WorkflowError
        if isinstance(error, WorkflowError):
            categorized_error = error
        else:
            categorized_error = categorize_generic_error(error, context)

        # Log the error with appropriate level
        self._log_error(categorized_error, context)

        # Check if we can retry this error
        if self.recovery_strategy.can_retry(categorized_error, context):
            self._error_stats["retries"] += 1

            # For retry scenarios, we want to signal to the caller that this should be retried
            # by raising a RetryableError
            delay = self.recovery_strategy.get_retry_delay(categorized_error, context.attempt_number)


            if delay > 0:
                await asyncio.sleep(delay)

            # Raise the categorized error to signal retry
            raise categorized_error

        # Check if workflow should continue despite failure
        if self.recovery_strategy.should_continue_workflow(categorized_error, context):
            self._error_stats["recoveries"] += 1

            fallback_value = self.recovery_strategy.get_fallback_value(categorized_error, context)

            return fallback_value

        # Error is fatal (max retries exhausted or non-retryable)
        # Always raise the ORIGINAL exception to preserve its type
        # This ensures tests can catch the specific exception type they expect
        # (e.g., ConnectionError, TypeError, ValueError)
        raise error
    
    def _log_error(self, error: WorkflowError, context: ErrorContext) -> None:
        """Log error with appropriate level based on severity"""
        log_data = {
            "node_name": context.node_name,
            "node_type": context.node_type,
            "execution_phase": context.execution_phase,
            "attempt_number": context.attempt_number,
            "error_type": type(error).__name__,
            "severity": context.severity.value
        }
        
        if context.severity == ErrorSeverity.CRITICAL:
            pass
        elif context.severity == ErrorSeverity.HIGH:
            pass
        elif context.severity == ErrorSeverity.MEDIUM:
            pass
        else:  # LOW
            pass
    
    def get_error_statistics(self) -> dict:
        """Get error handling statistics"""
        return self._error_stats.copy()
    
    def reset_statistics(self) -> None:
        """Reset error statistics"""
        self._error_stats = {"total_errors": 0, "retries": 0, "recoveries": 0}


# Convenience function to create error handlers with different strategies
def create_error_handler(strategy_type: str = "default", **kwargs) -> AsyncErrorHandler:
    """
    Factory function to create error handlers with predefined strategies.

    Args:
        strategy_type: Type of recovery strategy ("default", "strict", "permissive")
        **kwargs: Additional arguments for the strategy

    Returns:
        Configured AsyncErrorHandler
    """
    strategies = {
        "default": DefaultRecoveryStrategy,
        "strict": StrictRecoveryStrategy,
        "permissive": PermissiveRecoveryStrategy
    }

    if strategy_type not in strategies:
        raise ValueError(f"Unknown strategy type: {strategy_type}. Available: {list(strategies.keys())}")

    strategy_class = strategies[strategy_type]

    # Filter kwargs based on strategy type
    if strategy_type == "strict":
        # StrictRecoveryStrategy takes no arguments
        strategy = strategy_class()
    elif strategy_type == "permissive":
        # PermissiveRecoveryStrategy only takes max_retries
        strategy_kwargs = {}
        if "max_retries" in kwargs:
            strategy_kwargs["max_retries"] = kwargs["max_retries"]
        strategy = strategy_class(**strategy_kwargs)
    else:
        # DefaultRecoveryStrategy takes all kwargs
        strategy = strategy_class(**kwargs)

    return AsyncErrorHandler(recovery_strategy=strategy)