from typing import Type, Callable, TYPE_CHECKING, List, Dict, Any, get_type_hints, Union
from egregore.core.workflow.nodes.base import BaseNode
import inspect
import weakref

if TYPE_CHECKING:
    from egregore.core.workflow.nodes.node import Node, NodeMapper

def _analyze_function_signature(callable_func: Callable) -> Dict[str, Any]:
    """Analyze function signature for intelligent parameter mapping
    
    Args:
        callable_func: Function to analyze
        
    Returns:
        Dict containing:
        - sig: Function signature
        - type_hints: Type hints dictionary  
        - state_param: Name of SharedState parameter (if any)
        - input_params: List of input parameter objects
        - param_names: List of input parameter names
        
    Raises:
        ValueError: If multiple SharedState parameters found
    """
    sig = inspect.signature(callable_func)
    type_hints = get_type_hints(callable_func)
    
    state_param = None
    input_params = []
    param_names = []
    
    for name, param in sig.parameters.items():
        # Check if this parameter is annotated with SharedState
        param_type = type_hints.get(name)
        if param_type is not None and getattr(param_type, '__name__', None) == 'SharedState':
            if state_param is not None:
                raise ValueError(f"Only one SharedState parameter allowed, found: {state_param}, {name}")
            state_param = name
        elif param.default is inspect.Parameter.empty and param.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            # This is an input parameter (non-default, non-state, not *args or **kwargs)
            input_params.append(param)
            param_names.append(name)
    
    return {
        'sig': sig,
        'type_hints': type_hints,
        'state_param': state_param,
        'input_params': input_params,
        'param_names': param_names
    }


def map_outputs_to_parameters(previous_output: Any, input_params: List, param_names: List[str]) -> List[Any]:
    """Map node output to function parameters based on output types and parameter structure
    
    This is the core intelligence of the parameter mapping system. It automatically
    maps previous node outputs to current node input parameters using these rules:
    
    1. Single parameter: Gets entire output (no unpacking)
    2. Multiple params + tuple/list output: Positional mapping
    3. Multiple params + dict output: Named mapping by parameter names
    4. Fallback: Replicate single output to all parameters
    
    Args:
        previous_output: Output from the previous workflow node
        input_params: List of parameter objects (from inspect.signature)
        param_names: List of parameter names for dict mapping
        
    Returns:
        List of arguments to pass to the function (*args style)
    """
    # Case 1: Single parameter - gets entire output (no unpacking)
    if len(input_params) == 1:
        return [previous_output]
    
    # Case 2: Multiple params + tuple/list output - positional mapping
    if isinstance(previous_output, (tuple, list)) and len(previous_output) >= len(input_params):
        return list(previous_output)[:len(input_params)]
    
    # Case 3: Multiple params + dict output - named mapping by parameter names
    if isinstance(previous_output, dict):
        return [previous_output.get(name) for name in param_names]
    
    # Fallback for other cases
    return [previous_output] * len(input_params) if input_params else []


# Performance optimization: Cache signature analysis results
# Uses WeakKeyDictionary to automatically clean up when functions are garbage collected
# This prevents cache pollution when different functions reuse the same memory address
# Provides ~6x speedup for repeated wrapper creation of the same function
_signature_analysis_cache: 'weakref.WeakKeyDictionary[Callable, Dict[str, Any]]' = weakref.WeakKeyDictionary()


def create_intelligent_wrapper(callable_func: Callable) -> Callable:
    """Create wrapper with intelligent parameter mapping and advanced system integration
    
    This is the core wrapper that enables the new input-first workflow design pattern.
    It automatically maps previous node outputs to current node input parameters using
    intelligent type-based mapping rules.
    
    Supported Parameter Patterns:
        Single parameter:
            @node('processor') def func(input_data): ...
            -> Gets entire previous output
            
        Multiple parameters with tuple/list input:
            @node('processor') def func(a, b, c): ... 
            -> Positional mapping: (val1, val2, val3) -> a=val1, b=val2, c=val3
            
        Multiple parameters with dict input:
            @node('processor') def func(name, age): ...
            -> Named mapping: {"name": "Alice", "age": 30} -> name="Alice", age=30
            
        State parameter injection:
            @node('processor') def func(input_data, state: SharedState): ...
            -> Automatically injects workflow state as keyword argument
            
        Mixed patterns:
            @node('processor') def func(a, b, state: SharedState, debug=False): ...
            -> Combines positional mapping + state injection + default parameters
    
    Args:
        callable_func: Original function to wrap with intelligent parameter mapping
        
    Returns:
        Wrapped function with parameter mapping capabilities
        
    Raises:
        ValueError: If function has multiple SharedState parameters
    """
    # Performance optimization: Use cached signature analysis
    # WeakKeyDictionary uses the function object itself as key (not id())
    if callable_func in _signature_analysis_cache:
        sig_analysis = _signature_analysis_cache[callable_func]
    else:
        sig_analysis = _analyze_function_signature(callable_func)
        _signature_analysis_cache[callable_func] = sig_analysis
    
    def wrapper(*args, **kwargs):
        """The actual wrapper that gets called when the node executes"""
        instance = args[0]  # First arg is always the node instance
        previous_output = instance.state.get_previous_output()
        
        # Use our intelligent parameter mapping system
        input_params = sig_analysis['input_params']
        param_names = sig_analysis['param_names']
        state_param = sig_analysis['state_param']
        
        # Map previous output to function parameters
        mapped_args = map_outputs_to_parameters(previous_output, input_params, param_names)
        
        # Prepare function call arguments
        call_kwargs = {}
        if state_param:
            call_kwargs[state_param] = instance.state
            
        # Merge any additional kwargs passed to the wrapper
        call_kwargs.update(kwargs)
        
        # If we have a state parameter, use keyword arguments for all parameters
        # to avoid positional conflicts
        if state_param:
            # Convert positional mapped_args to keyword arguments
            for i, param_name in enumerate(param_names):
                if i < len(mapped_args):
                    call_kwargs[param_name] = mapped_args[i]
            # Call with kwargs only
            result = callable_func(**call_kwargs)
        else:
            # No state parameter, use positional arguments
            result = callable_func(*mapped_args, **call_kwargs)
        
        # Advanced system integration (if available)
        if hasattr(instance, 'name') and instance.name:
            # Store both INPUT and OUTPUT for complete execution tracking
            if hasattr(instance.state, 'set_node_execution'):
                instance.state.set_node_execution(instance, previous_output, result)
            elif hasattr(instance.state, 'set_node_output'):
                # Fallback to legacy method (stores output only)
                instance.state.set_node_output(instance, result)
            else:
                # Fallback to name-based storage (raw output value)
                instance.state[instance.name] = result
        
        return result
    
    return wrapper

node_registry = {}


class NodeType:
    def __init__(self, node: Type["Node"], original_name: str = None):
        # Store internal attributes first (before __setattr__ override)
        object.__setattr__(self, '_custom_attrs', {})
        self.node: Type["Node"] = node
        self._original_name: str = original_name  # Store for serialization
        # No instance caching - always create fresh instances

    def __setattr__(self, name: str, value: Any) -> None:
        """Capture custom attributes for inheritance by node instances.

        Internal attributes (starting with underscore or core attributes) are
        set normally. Custom attributes (like max_retries, fallback_value) are
        stored in _custom_attrs dict for inheritance by instances.
        """
        # Internal attributes - set normally
        if name in ('node', '_original_name', '_custom_attrs', 'exec', '_is_router'):
            object.__setattr__(self, name, value)
        # Custom attributes - store for instance inheritance
        else:
            if hasattr(self, '_custom_attrs'):
                self._custom_attrs[name] = value
            else:
                # Fallback during initialization
                object.__setattr__(self, name, value)

    def __getattr__(self, name: str) -> Any:
        """Allow reading custom attributes from _custom_attrs.

        This enables reading attributes that were set via __setattr__.
        """
        if '_custom_attrs' in object.__getattribute__(self, '__dict__'):
            custom_attrs = object.__getattribute__(self, '_custom_attrs')
            if name in custom_attrs:
                return custom_attrs[name]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def _assign_method(self, method_name:str, callable_func: Callable) -> Callable:
        """Assign method with intelligent parameter mapping"""
        
        # Use new intelligent wrapper for parameter mapping
        wrapper = create_intelligent_wrapper(callable_func)
            
        setattr(self.node, method_name, wrapper)
        method = getattr(self.node, method_name)
        method.__doc__ = callable_func.__doc__
        
        # Store original function for testing access
        self.exec = callable_func
        
        return callable_func # Return the original function

    def __call__(self, callable_func: Callable):
        """Direct decorator usage: @node('name') - function becomes the node"""
        self._assign_method('_execute_impl', callable_func)
        return self  # Return NodeType instance to maintain .node_instance access
    
    def __repr__(self):
        name = getattr(self.node, "__name__", None) or getattr(self.node, "__class__", type(self.node)).__name__
        return f"<NodeType: [{name}] >"
    
    @property
    def node_instance(self) -> "Node":
        """Always return FRESH instance - no caching.

        Creates new instance on every access to ensure complete isolation
        between sequences and executions.

        Custom attributes (like max_retries, fallback_value) set on the NodeType
        are automatically inherited by each instance.
        """
        import logging
        import uuid
        logger = logging.getLogger(__name__)

        # Always create fresh instance (no caching)
        instance = self.node()

        # Store reference to node class for reuse detection
        # The CLASS is still singleton, instances are not
        instance.node_class = self.node

        # Store reference to NodeType for type hint extraction
        instance._source_node_type = self

        # Copy custom attributes to instance (e.g., max_retries, fallback_value)
        if hasattr(self, '_custom_attrs'):
            for attr_name, attr_value in self._custom_attrs.items():
                setattr(instance, attr_name, attr_value)

        logger.debug(f"[NodeType.node_instance] Created FRESH instance: {instance.name} (guid={instance.guid[:8]})")
        return instance
    
    def alias(self, alias_name: str) -> 'ChainBuilder':
        """Create aliased reference for reused nodes.

        In deferred architecture, this returns a ChainBuilder with alias metadata.
        No instance is created until execute() time.

        Alias conflict detection happens during graph building (per-workflow scope).

        Raises:
            ValueError: If alias name is empty
        """
        from egregore.core.workflow.chain_builder import ChainBuilder

        # Validate alias name
        if not alias_name or not alias_name.strip():
            raise ValueError("Alias name cannot be empty")

        # Create ChainBuilder with alias metadata
        # Conflict detection happens during graph building, not here
        return ChainBuilder.from_single(self, alias_name=alias_name)
    
    def __rrshift__(self, other: Any):
        from egregore.core.workflow.nodes.node import NodeMapper

        if isinstance(other, bool):
            return NodeMapper(other, self.node_instance)
        if isinstance(other, str):
            return NodeMapper(other, self.node_instance)
        if isinstance(other, NodeType):
            return NodeMapper(other.node_instance, self)
        else:
            return NodeMapper(other, self.node_instance)


    def __rshift__(self, other: Union["BaseNode", "NodeType", "ChainBuilder"]):
        """Chain nodes together: left >> right

        Full deferred instantiation: Returns ChainBuilder metadata.
        NO instances created during >> operations - only at execute() time.
        This enables serialization and distributed execution.
        """
        from egregore.core.workflow.chain_builder import ChainBuilder
        from egregore.core.workflow.sequence import Sequence

        # Convert self to ChainBuilder
        left_builder = ChainBuilder.from_single(self)

        # Convert other to ChainBuilder based on type
        if isinstance(other, NodeType):
            # Another NodeType - straightforward
            right_builder = ChainBuilder.from_single(other)
        elif isinstance(other, ChainBuilder):
            # Already a ChainBuilder
            right_builder = other
        elif isinstance(other, (Sequence, BaseNode)):
            # BaseNode instance (includes Sequence, Decision, etc.)
            # Wrap in ChainBuilder to preserve as-is for legacy compatibility
            # This includes Decision nodes, custom nodes, etc.
            right_builder = ChainBuilder(
                node_types=[other],  # Store instance as-is
                edges=[],
                alias_map={}
            )
        else:
            # Unexpected type
            raise TypeError(
                f"Cannot chain NodeType with {type(other).__name__}. "
                f"Full deferred instantiation requires NodeType, ChainBuilder, or BaseNode. "
                f"Received: {other}"
            )

        # Chain builders together
        return left_builder >> right_builder

class NodeDecorator:
    """Wrapper that provides both @node('name') and @node.router('name') syntax."""

    @staticmethod
    def __call__(name: str):
        """Standard node creation: @node('name')"""
        return NodeDecorator._create_node(name, is_router=False)

    @staticmethod
    def router(name: str):
        """Router node creation: @node.router('name')"""
        return NodeDecorator._create_node(name, is_router=True)

    @staticmethod
    def _create_node(name: str, is_router: bool = False):
        """Internal: Create a NodeType with optional router flag.

        IMPORTANT: Each call creates a FRESH node class to prevent test isolation issues.
        Tests often reuse node names like @node('check') with different implementations.
        Creating a fresh class each time ensures implementations don't interfere.
        """
        from egregore.core.workflow.nodes.node import Node
        import uuid

        # Always create a fresh class - use UUID to ensure uniqueness
        # This prevents signature conflicts when tests reuse node names
        unique_class_name = f"{name}_{uuid.uuid4().hex[:8]}"

        def __init__(self, *args, **kwargs):
            Node.__init__(self, *args, **kwargs)
            self.name = name  # User-facing name stays the same (set AFTER parent init)
            self._is_router = is_router  # Set router flag

        class_attrs = {
            "__init__": __init__,
        }
        NewNodeClass = type(unique_class_name, (Node,), class_attrs)

        # Create NodeType and mark as router if needed
        node_type = NodeType(NewNodeClass, original_name=name)
        if is_router:
            node_type._is_router = True

        return node_type


# Create singleton instance for decorator usage
node = NodeDecorator()
