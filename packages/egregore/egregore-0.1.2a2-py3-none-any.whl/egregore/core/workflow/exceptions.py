"""
Workflow-specific exception classes and error handling utilities.

This module provides a comprehensive error hierarchy for workflow execution,
enabling better error categorization, debugging, and recovery strategies.
"""

import traceback
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
from enum import Enum


class ErrorSeverity(Enum):
    """Error severity levels for workflow errors"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ErrorContext:
    """Comprehensive error context for workflow failures"""
    node_name: str
    node_type: str
    execution_phase: str  # "before_execute", "execute", "after_execute"
    attempt_number: int = 1
    workflow_state: Dict[str, Any] = field(default_factory=dict)
    stack_trace: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    severity: ErrorSeverity = ErrorSeverity.MEDIUM
    additional_info: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Capture stack trace if not provided"""
        if not self.stack_trace:
            self.stack_trace = traceback.format_exc()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/serialization"""
        return {
            "node_name": self.node_name,
            "node_type": self.node_type,
            "execution_phase": self.execution_phase,
            "attempt_number": self.attempt_number,
            "timestamp": self.timestamp.isoformat(),
            "severity": self.severity.value,
            "additional_info": self.additional_info,
            "stack_trace": self.stack_trace
        }


class WorkflowError(Exception):
    """Base exception for all workflow-related errors"""
    
    def __init__(self, message: str, context: Optional[ErrorContext] = None):
        super().__init__(message)
        self.context = context
        self.severity = context.severity if context else ErrorSeverity.MEDIUM
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.context:
            return f"{base_msg} [Node: {self.context.node_name}, Phase: {self.context.execution_phase}]"
        return base_msg


class NodeExecutionError(WorkflowError):
    """Raised when a node fails during execution"""
    
    def __init__(self, node_name: str, original_error: Exception, context: ErrorContext):
        message = f"Node '{node_name}' execution failed: {original_error}"
        super().__init__(message, context)
        self.node_name = node_name
        self.original_error = original_error


class StateValidationError(WorkflowError):
    """Raised when workflow state is invalid or corrupted"""
    
    def __init__(self, message: str, state_info: Optional[Dict[str, Any]] = None, context: Optional[ErrorContext] = None):
        super().__init__(message, context)
        self.state_info = state_info or {}


class RetryableError(WorkflowError):
    """Indicates an error that should be retried"""
    
    def __init__(self, message: str, retry_after: float = 1.0, max_retries: int = 3, context: Optional[ErrorContext] = None):
        super().__init__(message, context)
        self.retry_after = retry_after
        self.max_retries = max_retries


class FatalError(WorkflowError):
    """Indicates an error that should stop workflow execution immediately"""
    
    def __init__(self, message: str, context: Optional[ErrorContext] = None):
        # Fatal errors are always high severity
        if context:
            context.severity = ErrorSeverity.CRITICAL
        super().__init__(message, context)


class TimeoutError(RetryableError):
    """Specific error for timeout scenarios"""
    
    def __init__(self, node_name: str, timeout_duration: float, context: Optional[ErrorContext] = None):
        message = f"Node '{node_name}' timed out after {timeout_duration}s"
        super().__init__(message, retry_after=min(timeout_duration * 0.5, 10.0), context=context)
        self.timeout_duration = timeout_duration


class ResourceExhaustionError(RetryableError):
    """Error when system resources are exhausted"""
    
    def __init__(self, resource_type: str, context: Optional[ErrorContext] = None):
        message = f"Resource exhausted: {resource_type}"
        super().__init__(message, retry_after=5.0, max_retries=2, context=context)
        self.resource_type = resource_type


class ValidationError(FatalError):
    """Error when input validation fails"""
    
    def __init__(self, field_name: str, value: Any, expected_type: str, context: Optional[ErrorContext] = None):
        message = f"Validation failed for field '{field_name}': expected {expected_type}, got {type(value).__name__}"
        super().__init__(message, context)
        self.field_name = field_name
        self.invalid_value = value
        self.expected_type = expected_type


class DependencyError(RetryableError):
    """Error when external dependencies are unavailable"""
    
    def __init__(self, dependency_name: str, context: Optional[ErrorContext] = None):
        message = f"Dependency unavailable: {dependency_name}"
        super().__init__(message, retry_after=2.0, max_retries=5, context=context)
        self.dependency_name = dependency_name


def categorize_generic_error(error: Exception, context: ErrorContext) -> WorkflowError:
    """
    Categorize a generic exception into a workflow-specific error type.
    
    Args:
        error: The original exception
        context: Error context information
        
    Returns:
        Categorized workflow error
    """
    import asyncio
    
    # Network and connection errors (usually retryable)
    if isinstance(error, ConnectionError):
        return DependencyError("network connection", context)
    if isinstance(error, OSError) and "connection" in str(error).lower():
        return DependencyError("network connection", context)
    
    # Timeout errors (retryable)
    if isinstance(error, asyncio.TimeoutError):
        return TimeoutError(context.node_name, 30.0, context)  # Default 30s timeout
    
    # Memory errors (retryable with longer delay)
    if isinstance(error, MemoryError):
        return ResourceExhaustionError("memory", context)
    
    # Value errors (usually fatal - bad input)
    if isinstance(error, ValueError):
        return ValidationError("input", str(error), "valid value", context)
    
    # Type errors (fatal - programming error)
    if isinstance(error, TypeError):
        return FatalError(f"Type error: {error}", context)
    
    # KeyError/AttributeError (usually fatal - programming error)
    if isinstance(error, (KeyError, AttributeError)):
        return FatalError(f"Access error: {error}", context)
    
    # FileNotFoundError (could be retryable if temporary)
    if isinstance(error, FileNotFoundError):
        return DependencyError("file system", context)
    
    # Permission errors (usually fatal)
    if isinstance(error, PermissionError):
        return FatalError(f"Permission denied: {error}", context)
    
    # Default to node execution error (retryable with low retry count)
    return NodeExecutionError(context.node_name, error, context)

class ParallelExecutionError(Exception):
    """Raised when a node fails during parallel execution"""
    pass


class ParallelTimeoutError(Exception):
    """Raised when parallel execution times out"""
    pass


# ============================================================================
# Decision Pattern Matching Exceptions
# ============================================================================

class PatternMatchingError(Exception):
    """Base exception for pattern matching errors"""

    def __init__(self, message: str, pattern: Any = None, input_value: Any = None):
        super().__init__(message)
        self.pattern = pattern
        self.input_value = input_value
        self.message = message

    def __str__(self) -> str:
        if self.pattern is not None and self.input_value is not None:
            return f"{self.message} (pattern: {self.pattern}, input: {self.input_value})"
        return self.message


class MaxIterationsExceededError(PatternMatchingError):
    """Raised when decision exceeds max_iter without finding a default pattern"""

    def __init__(self, max_iter: int, iterations: int, decision_name: str = "Decision"):
        message = f"{decision_name} exceeded max_iter={max_iter} after {iterations} iterations with no default pattern"
        super().__init__(message)
        self.max_iter = max_iter
        self.iterations = iterations
        self.decision_name = decision_name


class InvalidPatternError(PatternMatchingError):
    """Raised when a pattern is malformed or invalid"""

    def __init__(self, pattern: Any, reason: str):
        message = f"Invalid pattern: {reason}"
        super().__init__(message, pattern=pattern)
        self.reason = reason


class AttributeMatchingError(PatternMatchingError):
    """Raised when attribute matching fails unexpectedly"""

    def __init__(self, attribute_name: str, pattern_value: Any, actual_value: Any, obj: Any):
        message = f"Attribute '{attribute_name}' mismatch: expected {pattern_value}, got {actual_value}"
        super().__init__(message, pattern=pattern_value, input_value=actual_value)
        self.attribute_name = attribute_name
        self.pattern_value = pattern_value
        self.actual_value = actual_value
        self.obj = obj


class PredicateEvaluationError(PatternMatchingError):
    """Raised when predicate evaluation fails"""

    def __init__(self, predicate, input_value: Any, original_error: Exception):
        message = f"Predicate evaluation failed: {original_error}"
        super().__init__(message, pattern=predicate, input_value=input_value)
        self.predicate = predicate
        self.original_error = original_error


def create_error_context(
    node_name: str,
    node_type: str,
    execution_phase: str,
    attempt_number: int = 1,
    workflow_state: Optional[Dict[str, Any]] = None,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    **additional_info
) -> ErrorContext:
    """
    Factory function to create error context with optional state sanitization.
    
    Args:
        node_name: Name of the failing node
        node_type: Type/class of the failing node
        execution_phase: Phase where error occurred
        attempt_number: Current attempt number
        workflow_state: Current workflow state (will be sanitized)
        severity: Error severity level
        **additional_info: Additional context information
        
    Returns:
        ErrorContext instance
    """
    # Sanitize workflow state to avoid circular references or large objects
    sanitized_state = {}
    if workflow_state:
        for key, value in workflow_state.items():
            try:
                # Try to convert to string, limit size
                str_value = str(value)
                if len(str_value) > 1000:
                    str_value = str_value[:1000] + "... [truncated]"
                sanitized_state[key] = str_value
            except Exception:
                sanitized_state[key] = f"<{type(value).__name__} object>"
    
    return ErrorContext(
        node_name=node_name,
        node_type=node_type,
        execution_phase=execution_phase,
        attempt_number=attempt_number,
        workflow_state=sanitized_state,
        severity=severity,
        additional_info=additional_info
    )