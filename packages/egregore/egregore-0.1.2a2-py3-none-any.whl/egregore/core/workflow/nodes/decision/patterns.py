"""
Pattern Matching Classes for Enhanced Decision Nodes

This module implements various pattern types that can be used in decision nodes
for sophisticated input matching, similar to Python's match statement.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Type, Union, Dict, List, Tuple, Optional
import inspect
from egregore.core.workflow.exceptions import AttributeMatchingError, PredicateEvaluationError, InvalidPatternError


class Pattern(ABC):
    """Base class for all pattern matching implementations

    Supports fully deferred instantiation: target_node can be:
    - BaseNode instance (legacy, immediate execution)
    - ChainBuilder (deferred, instantiated at execution time)
    """

    def __init__(self, target_node):
        """Initialize pattern with target node

        Args:
            target_node: BaseNode instance or ChainBuilder for deferred instantiation
        """
        from egregore.core.workflow.nodes.base import BaseNode
        from egregore.core.workflow.chain_builder import ChainBuilder

        # Accept both BaseNode instances and ChainBuilder for distributed execution
        if not isinstance(target_node, (BaseNode, ChainBuilder)):
            raise InvalidPatternError(
                target_node,
                "target_node must be a BaseNode instance or ChainBuilder"
            )

        self.target_node = target_node
    
    @abstractmethod
    def matches(self, input_value: Any, state: Any = None) -> bool:
        """Check if input value matches this pattern
        
        Args:
            input_value: The value to match against
            state: Optional workflow state for context
            
        Returns:
            True if pattern matches, False otherwise
        """
        pass
    
    @property
    @abstractmethod
    def priority(self) -> int:
        """Pattern matching priority (lower = higher priority)
        
        Returns:
            Integer priority value
        """
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(target={self.target_node.name if hasattr(self.target_node, 'name') else self.target_node})"


class ValuePattern(Pattern):
    """Pattern for matching exact values"""
    
    def __init__(self, value: Any, target_node):
        super().__init__(target_node)
        self.value = value
    
    def matches(self, input_value: Any, state: Any = None) -> bool:
        """Check exact value equality"""
        return input_value == self.value
    
    @property
    def priority(self) -> int:
        return 10  # High priority for exact matches
    
    def __repr__(self) -> str:
        return f"ValuePattern({self.value!r} -> {self.target_node.name if hasattr(self.target_node, 'name') else self.target_node})"


class ClassPattern(Pattern):
    """Pattern for matching class types with optional attribute constraints"""
    
    def __init__(self, class_type: Type, target_node, **attribute_constraints):
        super().__init__(target_node)
        if not isinstance(class_type, type):
            raise InvalidPatternError(class_type, "class_type must be a type")
        
        self.class_type = class_type
        self.attribute_constraints = attribute_constraints
        self._validate_constraints()
    
    def _validate_constraints(self):
        """Validate attribute constraint syntax"""
        for attr_name, expected_value in self.attribute_constraints.items():
            if not isinstance(attr_name, str):
                raise InvalidPatternError(attr_name, "attribute names must be strings")
    
    def matches(self, input_value: Any, state: Any = None) -> bool:
        """Check type match and attribute constraints"""
        # Check type match first
        if not isinstance(input_value, self.class_type):
            return False
        
        # Check attribute constraints
        try:
            return self._check_attributes(input_value)
        except Exception as e:
            # Attribute access failed - pattern doesn't match
            return False
    
    def _check_attributes(self, obj: Any) -> bool:
        """Check all attribute constraints against object"""
        for attr_name, expected_value in self.attribute_constraints.items():
            if '__' in attr_name:
                # Django-style lookup (e.g., status__gte=400)
                if not self._check_django_style_constraint(obj, attr_name, expected_value):
                    return False
            else:
                # Simple attribute match
                try:
                    actual_value = getattr(obj, attr_name)
                    if actual_value != expected_value:
                        return False
                except AttributeError:
                    return False  # Attribute doesn't exist
        
        return True
    
    def _check_django_style_constraint(self, obj: Any, constraint: str, expected: Any) -> bool:
        """Check Django-style attribute constraints (attr__operator=value)"""
        attr_path, operator = constraint.split('__', 1)
        
        try:
            actual_value = getattr(obj, attr_path)
        except AttributeError:
            return False
        
        return self._apply_operator(actual_value, operator, expected)
    
    def _apply_operator(self, actual: Any, operator: str, expected: Any) -> bool:
        """Apply Django-style operators"""
        try:
            match operator:
                case 'gte' | 'ge': return actual >= expected
                case 'gt': return actual > expected  
                case 'lte' | 'le': return actual <= expected
                case 'lt': return actual < expected
                case 'ne': return actual != expected
                case 'eq': return actual == expected
                case 'in': return actual in expected
                case 'contains': return expected in actual
                case 'isnull': return (actual is None) == expected
                case 'startswith': return str(actual).startswith(str(expected))
                case 'endswith': return str(actual).endswith(str(expected))
                case 'icontains': return str(expected).lower() in str(actual).lower()
                case _: return actual == expected  # Default to equality
        except (TypeError, AttributeError):
            return False
    
    @property
    def priority(self) -> int:
        # More specific patterns (with attributes) have higher priority
        base_priority = 100 - len(self.class_type.__mro__)  # Deeper inheritance = higher priority
        attribute_bonus = len(self.attribute_constraints) * 10
        return max(1, base_priority - attribute_bonus)
    
    def __repr__(self) -> str:
        constraints = f"({', '.join(f'{k}={v!r}' for k, v in self.attribute_constraints.items())})" if self.attribute_constraints else ""
        return f"ClassPattern({self.class_type.__name__}{constraints} -> {self.target_node.name if hasattr(self.target_node, 'name') else self.target_node})"


class InstancePattern(Pattern):
    """Pattern for matching against instance attributes"""
    
    def __init__(self, instance_template, target_node):
        super().__init__(target_node)
        self.instance_template = instance_template
        self.class_type = type(instance_template)
        
        # Extract non-None attributes as constraints
        self.attribute_constraints = {}
        for attr_name, attr_value in instance_template.__dict__.items():
            if attr_value is not None:  # Only check non-None attributes
                self.attribute_constraints[attr_name] = attr_value
    
    def matches(self, input_value: Any, state: Any = None) -> bool:
        """Check if input matches instance template"""
        # Must be same type
        if not isinstance(input_value, self.class_type):
            return False
        
        # Check all non-None attributes from template
        try:
            for attr_name, expected_value in self.attribute_constraints.items():
                actual_value = getattr(input_value, attr_name, None)
                if actual_value != expected_value:
                    return False
            return True
        except AttributeError:
            return False
    
    @property
    def priority(self) -> int:
        # Instance patterns are very specific
        base_priority = 5
        attribute_bonus = len(self.attribute_constraints) * 2
        return max(1, base_priority - attribute_bonus)
    
    def __repr__(self) -> str:
        attrs = ', '.join(f'{k}={v!r}' for k, v in self.attribute_constraints.items())
        return f"InstancePattern({self.class_type.__name__}({attrs}) -> {self.target_node.name if hasattr(self.target_node, 'name') else self.target_node})"


class PredicatePattern(Pattern):
    """Pattern for matching with custom predicates (lambda functions)"""
    
    def __init__(self, predicate: Callable[[Any], bool], target_node):
        super().__init__(target_node)
        if not callable(predicate):
            raise InvalidPatternError(predicate, "predicate must be callable")  # type: ignore[arg-type]

        self.predicate = predicate
        try:
            self._signature = inspect.signature(predicate)
            self._accepts_state = len(self._signature.parameters) > 1
        except (ValueError, TypeError):
            # Built-in functions may not have inspectable signatures
            self._accepts_state = False
    
    def matches(self, input_value: Any, state: Any = None) -> bool:
        """Evaluate predicate against input"""
        try:
            if self._accepts_state and state is not None:
                return bool(self.predicate(input_value, state))  # type: ignore[call-arg]
            else:
                return bool(self.predicate(input_value))
        except Exception as e:
            # Predicate failed - doesn't match
            return False
    
    @property
    def priority(self) -> int:
        return 1000  # Low priority for custom predicates
    
    def __repr__(self) -> str:
        func_name = getattr(self.predicate, '__name__', 'lambda')
        return f"PredicatePattern({func_name} -> {self.target_node.name if hasattr(self.target_node, 'name') else self.target_node})"


class DefaultPattern(Pattern):
    """Default pattern that matches anything (wildcard)"""
    
    def __init__(self, target_node):
        super().__init__(target_node)
    
    def matches(self, input_value: Any, state: Any = None) -> bool:
        """Always matches"""
        return True
    
    @property
    def priority(self) -> int:
        return 999999  # Lowest priority - always last
    
    def __repr__(self) -> str:
        return f"DefaultPattern(_ -> {self.target_node.name if hasattr(self.target_node, 'name') else self.target_node})"


class RangePattern(Pattern):
    """Pattern for matching values within a range"""
    
    def __init__(self, range_obj: range, target_node):
        super().__init__(target_node)
        if not isinstance(range_obj, range):
            raise InvalidPatternError(range_obj, "must be a range object")
        self.range_obj = range_obj
    
    def matches(self, input_value: Any, state: Any = None) -> bool:
        """Check if value is in range"""
        try:
            return input_value in self.range_obj
        except TypeError:
            return False
    
    @property
    def priority(self) -> int:
        return 50  # Medium priority
    
    def __repr__(self) -> str:
        return f"RangePattern({self.range_obj} -> {self.target_node.name if hasattr(self.target_node, 'name') else self.target_node})"


class ListPattern(Pattern):
    """Pattern for matching values within a list/tuple"""
    
    def __init__(self, values: Union[List, Tuple], target_node):
        super().__init__(target_node)
        if not isinstance(values, (list, tuple)):
            raise InvalidPatternError(values, "must be a list or tuple")
        self.values = values
    
    def matches(self, input_value: Any, state: Any = None) -> bool:
        """Check if value is in list"""
        return input_value in self.values
    
    @property
    def priority(self) -> int:
        return 30  # Medium-high priority
    
    def __repr__(self) -> str:
        return f"ListPattern({self.values} -> {self.target_node.name if hasattr(self.target_node, 'name') else self.target_node})"


class DictPattern(Pattern):
    """Pattern for matching dictionary contents"""
    
    def __init__(self, pattern_dict: Dict, target_node, match_all: bool = True):
        super().__init__(target_node)
        if not isinstance(pattern_dict, dict):
            raise InvalidPatternError(pattern_dict, "must be a dictionary")
        
        self.pattern_dict = pattern_dict
        self.match_all = match_all  # If True, all keys must match; if False, any key match
    
    def matches(self, input_value: Any, state: Any = None) -> bool:
        """Check dictionary pattern matching"""
        if not isinstance(input_value, dict):
            return False
        
        if self.match_all:
            # All pattern keys must match
            return all(
                input_value.get(key) == value
                for key, value in self.pattern_dict.items()
            )
        else:
            # Any pattern key can match
            return any(
                input_value.get(key) == value
                for key, value in self.pattern_dict.items()
            )
    
    @property
    def priority(self) -> int:
        # More keys = higher priority
        return max(1, 40 - len(self.pattern_dict) * 5)
    
    def __repr__(self) -> str:
        mode = "all" if self.match_all else "any"
        return f"DictPattern({self.pattern_dict}, {mode} -> {self.target_node.name if hasattr(self.target_node, 'name') else self.target_node})"