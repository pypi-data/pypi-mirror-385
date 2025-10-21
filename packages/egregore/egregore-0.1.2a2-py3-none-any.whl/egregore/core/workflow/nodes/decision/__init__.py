"""
Enhanced Decision Module for Workflow Pattern Matching

This module provides sophisticated pattern matching capabilities for workflow decisions,
similar to Python's match statement but optimized for workflow execution.

Features:
- Class type matching (str, int, custom classes)
- Instance pattern matching (HTTPResponse(status_code=200))
- Value matching (exact values, ranges, lists)
- Lambda predicate matching
- Default case handling
- Loop control with max_iter
- Inheritance hierarchy matching
"""

from .patterns import (
    Pattern,
    ValuePattern,
    ClassPattern,
    InstancePattern,
    PredicatePattern,
    DefaultPattern,
    RangePattern,
    ListPattern,
    DictPattern
)

from .decision import Decision, decision, _, create_type_pattern, create_range_pattern
from egregore.core.workflow.exceptions import (
    PatternMatchingError,
    MaxIterationsExceededError,
    InvalidPatternError
)
__all__ = [
    # Core decision functionality
    "Decision",
    "decision", 
    "_",
    "create_type_pattern",
    "create_range_pattern",
    
    # Pattern types
    "Pattern",
    "ValuePattern", 
    "ClassPattern",
    "InstancePattern",
    "PredicatePattern",
    "DefaultPattern",
    "RangePattern",
    "ListPattern",
    "DictPattern",
    
    # Exceptions
    "PatternMatchingError",
    "MaxIterationsExceededError", 
    "InvalidPatternError"
]