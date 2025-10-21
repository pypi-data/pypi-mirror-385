"""
Workflow Type Checking System

Provides compile-time type validation for workflow node chaining to catch type mismatches
when composing workflows with the >> operator.
"""

import inspect
from typing import Any, Dict, List, Optional, Type, Union, get_type_hints, get_origin, get_args
from dataclasses import dataclass


@dataclass
class TypeInfo:
    """Information about a parameter or return type"""
    type_annotation: object  # Can be any type, class, or type hint
    is_optional: bool = False
    is_any: bool = False
    origin_type: Optional[object] = None  # For generic types like List[str]
    args: tuple = ()  # Type arguments for generics
    
    def __str__(self):
        if self.is_any:
            return "Any"
        if self.is_optional:
            return f"Optional[{self.type_annotation}]"
        return str(self.type_annotation)

@dataclass
class NodeTypeSignature:
    """Type signature information for a workflow node"""
    node_name: str
    input_types: Dict[str, TypeInfo]  # parameter_name -> TypeInfo
    return_type: TypeInfo
    has_varargs: bool = False
    has_kwargs: bool = False
    
    def __str__(self):
        inputs = [f"{name}: {type_info}" for name, type_info in self.input_types.items()]
        if self.has_varargs:
            inputs.append("*args")
        if self.has_kwargs:
            inputs.append("**kwargs")
        
        return f"{self.node_name}({', '.join(inputs)}) -> {self.return_type}"

class TypeCompatibilityChecker:
    """Checks type compatibility between workflow nodes"""
    
    @staticmethod
    def is_compatible(output_type: TypeInfo, input_type: TypeInfo) -> bool:
        """Check if output_type can be assigned to input_type"""
        
        # Any is compatible with everything
        if output_type.is_any or input_type.is_any:
            return True
            
        # Optional types - if input is optional, anything can be assigned
        if input_type.is_optional:
            return True
            
        # Extract actual types from Optional
        actual_output = output_type.type_annotation
        actual_input = input_type.type_annotation
        
        if output_type.is_optional:
            # Optional output means it could be None
            actual_output = get_args(output_type.type_annotation)[0] if get_args(output_type.type_annotation) else actual_output
            
        # Direct type match
        if actual_output == actual_input:
            return True
            
        # Handle Union types
        if get_origin(actual_input) is Union:
            return actual_output in get_args(actual_input)
            
        if get_origin(actual_output) is Union:
            return actual_input in get_args(actual_output)
            
        # Inheritance check
        try:
            if inspect.isclass(actual_output) and inspect.isclass(actual_input):
                return issubclass(actual_output, actual_input)
        except TypeError:
            # Handle generic types or non-class types
            pass
            
        # Generic type compatibility (basic check)
        if get_origin(actual_output) and get_origin(actual_input):
            output_origin = get_origin(actual_output)
            input_origin = get_origin(actual_input)
            
            if output_origin == input_origin:
                # Same generic type, check args if available
                output_args = get_args(actual_output)
                input_args = get_args(actual_input)
                
                if not output_args or not input_args:
                    return True  # Generic without args
                    
                # For now, just check first arg (could be extended)
                if len(output_args) >= 1 and len(input_args) >= 1:
                    return TypeCompatibilityChecker.is_compatible(
                        TypeInfo(output_args[0]),
                        TypeInfo(input_args[0])
                    )
        
        return False

class NodeTypeExtractor:
    """Extracts type information from workflow nodes"""
    
    @staticmethod
    def extract_signature(node) -> Optional[NodeTypeSignature]:
        """Extract type signature from a workflow node"""
        try:
            # Get the actual function from different node types
            func = NodeTypeExtractor._get_node_function(node)
            if not func:
                return None
                
            # Get function signature and type hints
            sig = inspect.signature(func)
            type_hints = get_type_hints(func)
            
            # Extract input types
            input_types = {}
            has_varargs = False
            has_kwargs = False
            
            for param_name, param in sig.parameters.items():
                if param.kind == param.VAR_POSITIONAL:
                    has_varargs = True
                    continue
                elif param.kind == param.VAR_KEYWORD:
                    has_kwargs = True
                    continue
                    
                # Skip special workflow parameters
                if param_name in ['state', 'context', 'workflow']:
                    continue
                    
                param_type = type_hints.get(param_name, Any)
                input_types[param_name] = NodeTypeExtractor._create_type_info(param_type)
            
            # Extract return type
            return_annotation = type_hints.get('return', Any)
            return_type = NodeTypeExtractor._create_type_info(return_annotation)
            
            node_name = getattr(node, 'name', str(node))
            
            return NodeTypeSignature(
                node_name=node_name,
                input_types=input_types,
                return_type=return_type,
                has_varargs=has_varargs,
                has_kwargs=has_kwargs
            )

        except Exception as e:
            return None
    
    @staticmethod
    def _get_node_function(node):
        """Extract the actual function from different node types"""
        # FIRST: Check if this is a node created by @node decorator
        # These nodes store _execute_impl in their class which wraps the original function
        if hasattr(node, '__class__') and hasattr(node.__class__, '_execute_impl'):
            # Get the wrapper from the class
            wrapper = node.__class__.__dict__.get('_execute_impl')
            if wrapper and callable(wrapper):
                # The wrapper is created by create_intelligent_wrapper
                # Check if it has __wrapped__ or closure with the original function
                if hasattr(wrapper, '__wrapped__'):
                    return wrapper.__wrapped__
                # Check closure for the original function
                if hasattr(wrapper, '__closure__') and wrapper.__closure__:
                    for cell in wrapper.__closure__:
                        try:
                            val = cell.cell_contents
                            if callable(val) and hasattr(val, '__annotations__'):
                                return val
                        except (AttributeError, ValueError):
                            continue

        # Handle semantic functions
        if hasattr(node, 'func'):
            return node.func

        # Handle decorated functions with execute method
        if hasattr(node, 'execute') and callable(node.execute):
            # Check if execute method has the original function signature
            if hasattr(node.execute, '__wrapped__'):
                return node.execute.__wrapped__

            # For semantic functions and other wrapped nodes
            if hasattr(node, '_original_func'):
                return node._original_func

            # Try to get the original function from various attributes
            for attr in ['_func', 'func', '_original_function', 'original_function']:
                if hasattr(node, attr):
                    return getattr(node, attr)

            # As a last resort, return the execute method itself
            return node.execute

        # Handle regular functions
        if callable(node):
            return node

        return None
    
    @staticmethod
    def _create_type_info(type_annotation) -> TypeInfo:
        """Create TypeInfo from a type annotation"""
        if type_annotation is Any or type_annotation == Any:
            return TypeInfo(type_annotation=Any, is_any=True)
            
        origin = get_origin(type_annotation)
        args = get_args(type_annotation)
        
        # Handle Optional types (Union[T, None])
        if origin is Union:
            # Check if it's Optional (Union with None)
            if len(args) == 2 and type(None) in args:
                non_none_type = args[0] if args[1] is type(None) else args[1]
                return TypeInfo(
                    type_annotation=non_none_type,
                    is_optional=True,
                    origin_type=origin,
                    args=args
                )

        return TypeInfo(
            type_annotation=type_annotation,
            origin_type=origin,
            args=args
        )

class WorkflowTypeChecker:
    """Main class for workflow type checking"""
    
    def __init__(self, strict_mode: bool = False):
        """
        Initialize type checker
        
        Args:
            strict_mode: If True, raises exceptions on type mismatches.
                        If False, logs warnings.
        """
        self.strict_mode = strict_mode
        self.type_cache: Dict[int, Optional[NodeTypeSignature]] = {}
    
    def check_node_compatibility(self, output_node, input_node) -> bool:
        """Check if two nodes can be chained together"""
        
        # Extract signatures (with caching)
        output_sig = self._get_cached_signature(output_node)
        input_sig = self._get_cached_signature(input_node)
        
        # If we can't extract signatures, assume compatible (fail open)
        if not output_sig or not input_sig:
            return True
        
        # Get the return type from output node
        output_type = output_sig.return_type
        
        # Check compatibility with input node parameters
        compatibility_results = []
        
        # If input node accepts varargs or kwargs, it's flexible
        if input_sig.has_varargs or input_sig.has_kwargs:
            return True
            
        # If input node has no required parameters, it's compatible
        if not input_sig.input_types:
            return True
            
        # Check if output type is compatible with first input parameter
        # (workflow nodes typically take one main input)
        first_param = next(iter(input_sig.input_types.values()))
        is_compatible = TypeCompatibilityChecker.is_compatible(output_type, first_param)
        
        if not is_compatible:
            error_msg = f"Type mismatch: {output_sig.node_name} returns {output_type} but {input_sig.node_name} expects {first_param}"

            if self.strict_mode:
                raise TypeError(error_msg)
            else:
                import warnings
                warnings.warn(error_msg, UserWarning, stacklevel=3)

        return is_compatible
    
    def _get_cached_signature(self, node) -> Optional[NodeTypeSignature]:
        """Get signature with caching"""
        node_id = id(node)
        if node_id not in self.type_cache:
            self.type_cache[node_id] = NodeTypeExtractor.extract_signature(node)
        return self.type_cache[node_id]

# Global type checker instance
_global_type_checker = None

def get_type_checker() -> WorkflowTypeChecker:
    """Get or create global type checker instance"""
    global _global_type_checker
    if _global_type_checker is None:
        _global_type_checker = WorkflowTypeChecker(strict_mode=False)  # Default: warnings only
    return _global_type_checker

def set_type_checking_mode(strict: bool = False):
    """Configure global type checking behavior"""
    global _global_type_checker
    _global_type_checker = WorkflowTypeChecker(strict_mode=strict)

def check_node_chain_types(left_node, right_node) -> bool:
    """Public API for checking node compatibility in >> operations"""
    checker = get_type_checker()
    return checker.check_node_compatibility(left_node, right_node)