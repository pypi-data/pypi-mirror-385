from typing import Any, Iterator, Tuple, TypedDict, TypeVar, Optional, Union, Dict
from typing import TYPE_CHECKING
import json
import pickle
from pathlib import Path
from contextvars import ContextVar


if TYPE_CHECKING:
    from egregore.core.workflow.nodes.base import BaseNode

# Execution-scoped state isolation for concurrent executions
# Hybrid approach: contextvars for async context + thread-local for sync executor threads
import asyncio
import threading
from contextvars import ContextVar

# Thread-local storage for execution ID (set before run_in_executor, read during execution)
_thread_local = threading.local()

# Contextvar to store execution ID in async context
_execution_id_var: ContextVar[Optional[int]] = ContextVar('_execution_id', default=None)

# Dict mapping execution ID -> execution state
_execution_state_by_id: Dict[int, Dict[str, Any]] = {}


def _set_thread_execution_context():
    """Set thread-local execution ID before running in executor.

    Call this from a wrapper function that's passed to run_in_executor() to ensure
    the execution ID from the contextvar is available in the thread-local for sync code.
    """
    execution_id = _execution_id_var.get(None)
    if execution_id is not None:
        _thread_local.execution_id = execution_id


def _wrap_for_executor(func):
    """Wrap a sync function to propagate execution context to thread pool.

    Captures execution ID from contextvar BEFORE entering thread pool,
    then sets it in thread-local DURING execution in the thread pool.
    """
    # Capture execution ID NOW (in async context) before entering thread pool
    execution_id = _execution_id_var.get(None)

    def wrapper(*args, **kwargs):
        # Set thread-local execution ID (in thread pool context)
        if execution_id is not None:
            _thread_local.execution_id = execution_id
        return func(*args, **kwargs)
    return wrapper


class InitialInput(TypedDict):
    args: tuple
    kwargs: dict


class NotImplemented:
    pass
 
NOT_IMPLEMENTED = TypeVar("NOT_IMPLEMENTED", bound=NotImplemented)

class NodeOutput:
    """Enhanced node execution tracker with input/output separation.

    Provides access to:
    - .input: What the node received as input
    - .output: What the node produced as output
    - .before_execute, .execute, .after_execute: Legacy hook outputs
    - .latest: Most recent value (backward compatibility)
    """
    before_execute_output: Any = NOT_IMPLEMENTED
    execute_output: Any = NOT_IMPLEMENTED
    after_execute_output: Any = NOT_IMPLEMENTED

    def __init__(self, name: Optional[str] = None, input_value: Any = None, output_value: Any = None, **kwargs):
        self.name = name
        self._input = input_value
        self._output = output_value

        self._execution_sequence = [NOT_IMPLEMENTED, NOT_IMPLEMENTED, NOT_IMPLEMENTED]

    @property
    def input(self) -> Any:
        """Get the input value received by this node"""
        return self._input

    @input.setter
    def input(self, value: Any):
        """Set the input value received by this node"""
        self._input = value

    @property
    def output(self) -> Any:
        """Get the output value produced by this node"""
        return self._output

    @output.setter
    def output(self, value: Any):
        """Set the output value produced by this node"""
        self._output = value

    @property
    def before_execute(self):
        if hasattr(self, "_before_execute_output"):
            return self._before_execute_output
        else:
            return None

    @before_execute.setter
    def before_execute(self, value: Any):
        self._before_execute_output = value
        self._execution_sequence[0] = value
        return self

    @property
    def execute(self):
        if hasattr(self, "_execute_output"):
            return self._execute_output
        else:
            return None

    @execute.setter
    def execute(self, value: Any):
        self._execute_output = value
        self._execution_sequence[1] = value
        return self

    @property
    def after_execute(self):
        if hasattr(self, "_after_execute_output"):
            return self._after_execute_output
        else:
            return None

    @after_execute.setter
    def after_execute(self, value: Any):
        self._after_execute_output = value
        self._execution_sequence[2] = value
        return self

    @property
    def latest(self):
        """Get most recent value - prioritizes output, then execution sequence

        For backward compatibility with code that expects raw values.
        """
        # First check if we have an output value (new system)
        if self._output is not None and self._output is not NOT_IMPLEMENTED:
            return self._output

        # Fall back to execution sequence (legacy system)
        for output in self._execution_sequence[::-1]:
            if output is not NOT_IMPLEMENTED and output is not None:
                return output

        # Finally check input if nothing else is available
        if self._input is not None and self._input is not NOT_IMPLEMENTED:
            return self._input

        return None

    def __repr__(self) -> str:
        return f"NodeOutput(name={self.name}, input={self._input}, output={self._output})"

    def __eq__(self, other: Any) -> bool:
        """Enable comparison with raw values for backward compatibility.

        When compared to a raw value, compares against the output value.
        This allows existing tests like `assert state['node'] == 20` to work.
        """
        if isinstance(other, NodeOutput):
            # Comparing two NodeOutput objects
            return (self._input == other._input and
                    self._output == other._output and
                    self.name == other.name)
        else:
            # Comparing NodeOutput to raw value - compare against output
            return self._output == other

    def __hash__(self) -> int:
        """Make NodeOutput hashable"""
        return hash((self.name, self._input, self._output))



class NodeNotFoundError(Exception):
    """Raised when requested node is not found in execution history"""
    pass


class SharedState:
    def __init__(self, instance_name: str, **kwargs):
        self.instance_name = instance_name
        self.state = {}
        for k,v in kwargs.items():
            self.state[k] = v
        
        self._legacy_initial_input = NodeOutput('initial_input')
        
        self.execution_sequence = []
        self.executions = []
        
        # Performance optimization: cache for frequently accessed nodes
        self._node_output_cache = {}
        
        # Store initial workflow input separately for helper property
        self._initial_workflow_input = None
        
        # Reference to workflow for controller access (set by workflow)
        self.workflow: Optional[Any] = None  # TYPE_CHECKING import would create circular dependency
        
        # Simple loop control system (Plan 21 enhancement)
        self._node_execution_counts = {}  # Track executions per node name
        self.default_max_node_executions = 10  # Default limit for any single node
        
        # Phase 2: GUID-based storage and alias support
        self.node_outputs_by_guid: Dict[str, Any] = {}  # GUID-based storage
        self.node_outputs_by_alias: Dict[str, str] = {} # alias -> guid mapping
        self.node_guid_mapping: Dict[str, str] = {}     # node_name -> guid (for latest)
        
        # Generic state store for arbitrary workflow data
        self.store: Dict[str, Any] = {}

        
    def set_current(self, node: "BaseNode") -> "NodeOutput":
        self.current = NodeOutput(name=node.name)
        return self.current
    
    def set_node_execution(self, node: "BaseNode", input_value: Any, output_value: Any) -> None:
        """Store node execution with input and output tracking

        Args:
            node: The node instance that executed
            input_value: What the node received as input
            output_value: What the node produced as output
        """
        # Create NodeOutput object with input/output
        node_output = NodeOutput(
            name=node.effective_name,
            input_value=input_value,
            output_value=output_value
        )

        # Store by GUID (primary)
        self.node_outputs_by_guid[node.guid] = node_output

        # Store by effective name for easy access
        effective_name = node.effective_name
        self.state[effective_name] = node_output

        # Handle canonical name mapping carefully
        canonical_name = node.canonical_name or node.name

        # If this is an aliased node, don't overwrite the canonical mapping
        if node.alias_name:
            # Store alias-specific mapping
            self.node_outputs_by_alias[node.alias_name] = node.guid
            self.node_guid_mapping[node.alias_name] = node.guid
        else:
            # This is the original node, update canonical mapping
            self.node_guid_mapping[canonical_name] = node.guid

    def set_node_output(self, node: "BaseNode", output: Any) -> None:
        """Store node output with proper aliasing support (legacy compatibility)

        DEPRECATED: Use set_node_execution() instead for input/output tracking.
        This method stores output-only for backward compatibility.
        """
        # Get input from previous output for backward compatibility
        input_value = self.get_previous_output()

        # Use new set_node_execution method
        self.set_node_execution(node, input_value, output)
        

    def __setattr__(self, name: str, value: Any) -> None:
        self.__dict__[name] = value
    
    def __getattr__(self, name: str) -> Any:
        return self.__dict__[name]
    
    def __delattr__(self, name: str) -> None:
        del self.__dict__[name]
    
    def get(self, name: str, default: Any = None) -> Any:
        return self.state.get(name, default)

    
    # def __setattr__(self, name: str, value: Any) -> None:
        # self.state[name] = value

    # def __getattr__(self, name: str) -> Any:
        # return self.state[name]

    # def __delattr__(self, name: str) -> None:
        # del self.state[name]

    def __contains__(self, name: str) -> bool:
        return name in self.state
    
    def __iter__(self) -> Iterator[Tuple[str, Any]]:
        for k,v in self.state.items():
            yield k,v

    def __len__(self) -> int:
        return len(self.state)
    
    
    def __getitem__(self, key) -> Any:
        """Enable state[key] access with int/str indexing"""
        if isinstance(key, int):
            return self._get_by_index(key)
        elif isinstance(key, str):
            return self._get_by_name(key)
        else:
            raise TypeError(f"State key must be int or str, got {type(key).__name__}")
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Enable state[key] = value assignment"""
        if not isinstance(key, str):
            raise TypeError(f"State assignment key must be str, got {type(key).__name__}")
        self.state[key] = value
        self._notify_state_change('assignment', key, value)
    
    def extend(self, other: "SharedState") -> None:
        if other.instance_name != self.instance_name:
            self.state[other.instance_name] = other.state
        else:
            self.state.update(other.state)
        
    def __str__(self) -> str:
        return f"SharedState(instance_name={self.instance_name}, state={self.state})"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    @property
    def previous_output(self) -> Any:
        if len(self.executions) > 0:
            return self.executions[-1].latest
        elif len(self.executions) == 0:
            return self._legacy_initial_input.latest
        else:
            return None
    
    def get_previous_output(self) -> Any:
        """Standardized method to get previous output with manual override priority"""

        # PRIORITY 1: Check for execution-scoped override (hybrid isolation for concurrent execution)
        # Try thread-local first (for sync code in thread pool), then contextvar (for async code)
        execution_id = getattr(_thread_local, 'execution_id', None) or _execution_id_var.get(None)

        if execution_id is not None and execution_id in _execution_state_by_id:
            ctx = _execution_state_by_id[execution_id]
            if '_manual_previous_output' in ctx:
                return ctx['_manual_previous_output']

        # PRIORITY 2: Check for manual override in instance dict (backward compatibility)
        # Use direct __dict__ access to avoid triggering __getattr__
        # Manual override takes precedence to allow Decision and other controllers to inject data
        if '_manual_previous_output' in self.__dict__:
            return self._manual_previous_output

        # PRIORITY 3: Use controller execution history if available (Plan 21)
        if (self.workflow and
            hasattr(self.workflow, 'controller') and
            self.workflow.controller.execution_history):

            last_completed = self.workflow.controller.execution_history.get_last_completed()
            if last_completed:
                return last_completed.output_value

        # PRIORITY 4: Fallback to legacy previous_output property
        return self.previous_output

    def set_previous_output(self, value: Any) -> None:
        """Standardized method to set previous output with execution-scoped isolation"""
        # Use hybrid isolation: contextvar for async, thread-local for thread pool
        # Get or create execution ID from contextvar
        execution_id = _execution_id_var.get(None)
        if execution_id is None:
            # First call in this execution - create new ID
            try:
                task = asyncio.current_task()
                if task:
                    execution_id = id(task)  # Use task ID as execution ID
                    _execution_id_var.set(execution_id)
            except RuntimeError:
                # Not in async context - use thread ID as fallback
                execution_id = id(threading.current_thread())

        if execution_id is not None:
            if execution_id not in _execution_state_by_id:
                _execution_state_by_id[execution_id] = {}
            _execution_state_by_id[execution_id]['_manual_previous_output'] = value
            return

        # Fallback to instance attribute for non-async execution
        self._manual_previous_output = value
    
    def clear_manual_override(self) -> None:
        """Clear manual previous output override"""
        # Clear execution-scoped override
        execution_id = getattr(_thread_local, 'execution_id', None) or _execution_id_var.get(None)
        if execution_id is not None and execution_id in _execution_state_by_id:
            ctx = _execution_state_by_id[execution_id]
            if '_manual_previous_output' in ctx:
                del ctx['_manual_previous_output']
            # Clean up empty execution state
            if not ctx:
                del _execution_state_by_id[execution_id]

        # Clear instance-level override (backward compatibility)
        if '_manual_previous_output' in self.__dict__:
            delattr(self, '_manual_previous_output')
    
    def clear_store(self) -> None:
        """Clear the generic state store"""
        self.store.clear()
    
    # Enhanced execution history methods for Plan 21
    def get_execution_history(self, node_name: Optional[str] = None, limit: Optional[int] = None):
        """Get execution history from controller, optionally filtered"""
        if not (self.workflow and hasattr(self.workflow, 'controller')):
            return []
        
        history = self.workflow.controller.execution_history.entries
        
        if node_name:
            history = [entry for entry in history if entry.node_name == node_name]
        
        if limit:
            history = history[-limit:]
        
        return history
    
    def get_node_execution_count(self, node_name: str) -> int:
        """Count executions of a specific node via controller"""
        if not (self.workflow and hasattr(self.workflow, 'controller')):
            return 0
        
        return self.workflow.controller.execution_history.get_node_execution_count(node_name)
    
    def detect_execution_loop(self, target_node_name: str, pattern_length: int = 3) -> bool:
        """Detect if selecting target would create a repetitive execution pattern"""
        if not (self.workflow and hasattr(self.workflow, 'controller')):
            return False
        
        return self.workflow.controller.execution_history.detect_repetitive_pattern(
            target_node_name, pattern_length
        )
    
    def get_execution_sequence(self, limit: int = None):
        """Get sequence of executed node names"""
        if not (self.workflow and hasattr(self.workflow, 'controller')):
            return []
        
        return self.workflow.controller.execution_history.get_execution_sequence(limit)
    
    # Simple per-node execution counting for loop control
    def increment_node_execution(self, node_name: str) -> int:
        """Increment execution count for a node and return new count"""
        current_count = self._node_execution_counts.get(node_name, 0) + 1
        self._node_execution_counts[node_name] = current_count
        return current_count
    
    def get_node_execution_count_local(self, node_name: str) -> int:
        """Get local execution count for a node (separate from controller)"""
        return self._node_execution_counts.get(node_name, 0)
    
    def check_node_execution_limit(self, node_name: str, max_executions: int = None) -> dict:
        """Check if node has exceeded execution limit"""
        current_count = self.get_node_execution_count_local(node_name)
        limit = max_executions or self.default_max_node_executions
        
        if current_count >= limit:
            return {
                'allowed': False,
                'reason': 'max_executions_exceeded',
                'node': node_name,
                'current_count': current_count,
                'limit': limit
            }
        
        return {
            'allowed': True,
            'reason': 'within_limit',
            'node': node_name,
            'current_count': current_count,
            'limit': limit
        }
    
    def reset_node_execution_counts(self):
        """Reset all node execution counts"""
        self._node_execution_counts.clear()
    
    def get_execution_summary(self) -> dict:
        """Get summary of all node execution counts"""
        return {
            'node_counts': self._node_execution_counts.copy(),
            'total_executions': sum(self._node_execution_counts.values()),
            'unique_nodes': len(self._node_execution_counts),
            'default_limit': self.default_max_node_executions
        }
    
    # NEW: Enhanced State Access Helper Properties (Plan 18)
    @property
    def initial_input(self) -> Any:
        """Get the very first input to the workflow"""
        if self._initial_workflow_input is not None:
            return self._initial_workflow_input
        elif hasattr(self, '_legacy_initial_input') and self._legacy_initial_input.latest is not None:
            # Fallback to legacy initial_input NodeOutput
            return self._legacy_initial_input.latest
        elif self.executions:
            # Fallback to first execution's input if available
            return getattr(self.executions[0], 'input', None)
        return None

    @initial_input.setter
    def initial_input(self, value: Any) -> None:
        """Set the initial workflow input"""
        self._initial_workflow_input = value

    @property
    def final_output(self) -> Any:
        """Get the final output from the last executed node

        Returns the output value (not input) from the most recent execution.
        Updated after each successful node execution.
        """
        # Try controller execution history first (most reliable)
        if (self.workflow and
            hasattr(self.workflow, 'controller') and
            self.workflow.controller.execution_history):
            last_completed = self.workflow.controller.execution_history.get_last_completed()
            if last_completed:
                return last_completed.output_value

        # Fallback to executions list
        if self.executions:
            last_exec = self.executions[-1]
            # Try to get output attribute first
            if hasattr(last_exec, 'output') and last_exec.output is not None:
                return last_exec.output
            # Fall back to latest
            return last_exec.latest

        return None
    
    @property
    def current_input(self) -> Any:
        """Get the input being processed by current node"""
        if hasattr(self, 'current') and hasattr(self.current, 'input'):
            return self.current.input
        elif self.executions:
            return getattr(self.executions[-1], 'input', None)
        return self._initial_workflow_input
    
    @property
    def execution_count(self) -> int:
        """Get total number of executed nodes"""
        return len(self.executions)
    
    @property
    def last_node(self) -> Optional["BaseNode"]:
        """Get reference to the last executed node"""
        if self.execution_sequence:
            return self.execution_sequence[-1]
        return None
    
    def _get_by_index(self, index: int) -> Any:
        """Get execution result by integer index"""
        if not self.executions:
            raise IndexError("No executions in state history")
        
        try:
            if index == -1:
                # Optimize most common case
                result = self.executions[-1].latest
            else:
                result = self.executions[index].latest
            self._notify_state_change('access', index, result)
            return result
        except IndexError:
            raise IndexError(f"Execution index {index} out of range (0 to {len(self.executions)-1})")
    
    def _get_by_name(self, name: str) -> Any:
        """Get result by string name (parallel results priority)"""
        # Check parallel results first (stored in state dict)
        if name in self.state:
            result = self.state[name]
            self._notify_state_change('access', name, result)
            return result
        
        # Then check execution history by node name (latest wins)
        for execution in reversed(self.executions):  # Latest first
            if hasattr(execution, 'name') and execution.name == name:
                result = execution.latest
                self._notify_state_change('access', name, result)
                return result
        
        # Return None if not found (dict-like behavior)
        self._notify_state_change('access', name, None)
        return None
    
    def _notify_state_change(self, operation: str, key: Any, value: Any) -> None:
        """Notify attached observers of state changes"""
        # Only notify if observer is attached and method exists - optimize hot path
        observer = self.__dict__.get('_observer_hook')
        if observer and hasattr(observer, 'capture_state_change'):
            # Skip access notifications if disabled for performance
            if operation == 'access' and not self.__dict__.get('_notify_access', True):
                return
            try:
                observer.capture_state_change(
                    timestamp=__import__('time').time(),
                    operation=operation,  # 'access' or 'assignment'
                    key=key,
                    value=value,
                    state_snapshot=self._create_lightweight_snapshot()
                )
            except Exception:
                # Don't let observer errors break workflow execution
                pass
    
    def _create_lightweight_snapshot(self) -> dict:
        """Create minimal state snapshot for observers"""
        return {
            'instance_name': self.instance_name,
            'execution_count': len(self.executions),
            'state_keys': list(self.state.keys()),
            'last_execution': self.executions[-1].name if self.executions else None
        }
    
    def attach_observer(self, observer, notify_access: bool = True) -> None:
        """Attach an observer for state changes and workflow control
        
        Args:
            observer: Observer object with capture_state_change and/or check_workflow_control methods
            notify_access: If False, only notify on assignments, not access (for performance)
        """
        self._observer_hook = observer
        self._notify_access = notify_access
    
    def _check_workflow_control(self) -> bool:
        """Check if observer wants to control workflow execution (pause/stop)"""
        observer = self.__dict__.get('_observer_hook')
        if observer:
            if hasattr(observer, 'check_workflow_control'):
                try:
                    control_action = observer.check_workflow_control(
                        instance_name=self.instance_name,
                        current_state=self._create_lightweight_snapshot()
                    )
                    return control_action != 'continue'  # pause/stop/resume
                except Exception:
                    # Don't let observer errors break workflow execution
                    return False
        return False
    
    # NEW: Enhanced State Navigation Methods (Plan 18)
    def get_node_output(self, node_identifier: str, index: int = -1) -> Any:
        """Get node output by name, alias, or GUID with enhanced Phase 2 support
        
        Args:
            node_identifier: Node name, alias, or GUID
            index: Which execution if node ran multiple times (-1 for last)
        """
        # Phase 2: Try GUID-based lookup first (fast path)
        if node_identifier in self.node_outputs_by_guid:
            return self.node_outputs_by_guid[node_identifier]
        
        # Phase 2: Try alias resolution
        if node_identifier in self.node_outputs_by_alias:
            guid = self.node_outputs_by_alias[node_identifier]
            return self.node_outputs_by_guid[guid]
        
        # Phase 2: Try node name to GUID mapping
        if node_identifier in self.node_guid_mapping:
            guid = self.node_guid_mapping[node_identifier]
            return self.node_outputs_by_guid[guid]
        
        # Phase 2: Try direct state access (backward compatibility)
        if node_identifier in self.state:
            return self.state[node_identifier]
        
        # Legacy fallback: Check cache first
        cache_key = f"{node_identifier}:{index}"
        if cache_key in self._node_output_cache:
            return self._node_output_cache[cache_key]
        
        # Legacy fallback: Find matching executions by node name
        matching_executions = []
        for i, execution in enumerate(self.executions):
            if execution.name == node_identifier:
                matching_executions.append((i, execution))
        
        if not matching_executions:
            # Also check execution_sequence for node names
            for i, node in enumerate(self.execution_sequence):
                node_name_attr = getattr(node, 'name', None)
                if node_name_attr == node_identifier and i < len(self.executions):
                    matching_executions.append((i, self.executions[i]))
        
        if not matching_executions:
            raise NodeNotFoundError(f"Node '{node_identifier}' not found in execution history")
        
        try:
            exec_index, execution = matching_executions[index]
            result = execution.latest
            
            # Cache result
            self._node_output_cache[cache_key] = result
            return result
            
        except IndexError:
            raise NodeNotFoundError(
                f"Node '{node_identifier}' index {index} not found. "
                f"Found {len(matching_executions)} executions."
            )
    
    def get_all_outputs_for_canonical(self, canonical_name: str) -> Dict[str, Any]:
        """Get all outputs for a canonical component (all aliases)

        Args:
            canonical_name: The original component name

        Returns:
            Dictionary mapping effective_name -> output for all instances
        """
        from egregore.core.workflow.nodes.base import _global_node_registry

        results = {}

        # Use workflow's local registry if available, otherwise global
        registry = _global_node_registry
        if hasattr(self, 'workflow') and self.workflow and hasattr(self.workflow, '_local_node_registry'):
            registry = self.workflow._local_node_registry

        # Get all nodes for this canonical component from registry
        nodes = registry.get_nodes_by_canonical(canonical_name)

        for node in nodes:
            guid = node.guid
            if guid in self.node_outputs_by_guid:
                effective_name = node.effective_name
                results[effective_name] = self.node_outputs_by_guid[guid]

        return results
    
    def get_node_attribute(self, node_name: str, attribute_path: str) -> Any:
        """Get specific attribute from node output using dot notation
        
        Args:
            node_name: Name of the node
            attribute_path: Dot-separated path like "data.items.count"
        """
        output = self.get_node_output(node_name)
        
        # Navigate attribute path
        current = output
        for attr in attribute_path.split('.'):
            if isinstance(current, dict):
                current = current.get(attr)
            else:
                current = getattr(current, attr, None)
            
            if current is None:
                break
        
        return current
    
    def get_execution_by_name(self, node_name: str, index: int = -1) -> Optional["NodeOutput"]:
        """Get execution object by node name"""
        matching_executions = []
        for execution in self.executions:
            if execution.name == node_name:
                matching_executions.append(execution)
        
        if not matching_executions:
            return None
        
        try:
            return matching_executions[index]
        except IndexError:
            return None
    
    def get_parallel_outputs(self, parallel_node_name: str) -> Dict[str, Any]:
        """Get all outputs from parallel child nodes
        
        Args:
            parallel_node_name: Name of the parallel coordinator node
            
        Returns:
            Dict mapping child node names to their outputs
        """
        parallel_outputs = {}
        
        # Find parallel execution in execution_sequence
        for i, node in enumerate(self.execution_sequence):
            node_name_attr = getattr(node, 'name', None)
            if (node_name_attr == parallel_node_name and
                hasattr(node, 'parallel_nodes')):
                
                # Get outputs from all parallel children
                for child_node in node.parallel_nodes:
                    child_name = getattr(child_node, 'name', str(child_node))
                    try:
                        child_output = self.get_node_output(child_name)
                        parallel_outputs[child_name] = child_output
                    except NodeNotFoundError:
                        # Child might not have executed yet or failed
                        parallel_outputs[child_name] = None
                break
        
        return parallel_outputs
    
    def find_last_execution_of(self, node_name: str) -> Optional["NodeOutput"]:
        """Find the last execution of a node by name"""
        return self.get_execution_by_name(node_name, -1)
    
    # Phase 2: State Serialization for GUID/alias persistence
    def to_dict(self, include_outputs: bool = True) -> Dict[str, Any]:
        """Serialize state to dictionary with GUID/alias persistence
        
        Args:
            include_outputs: Whether to include actual output values (may be large)
            
        Returns:
            Dictionary containing all state data including GUID mappings
        """
        serialized = {
            'instance_name': self.instance_name,
            'state': self.state.copy() if include_outputs else {},
            'default_max_node_executions': self.default_max_node_executions,
            
            # Phase 2: GUID-based storage persistence
            'node_outputs_by_guid': self.node_outputs_by_guid.copy() if include_outputs else {},
            'node_outputs_by_alias': self.node_outputs_by_alias.copy(),
            'node_guid_mapping': self.node_guid_mapping.copy(),
            
            # Execution tracking
            'node_execution_counts': self._node_execution_counts.copy(),
            
            # Metadata
            'serialization_version': '1.0',
            'serialized_with_outputs': include_outputs
        }
        
        # Handle executions (convert to serializable format)
        if include_outputs and self.executions:
            serialized['executions'] = []
            for execution in self.executions:
                exec_data = {
                    'name': execution.name,
                    'before_execute': getattr(execution, '_before_execute_output', None),
                    'execute': getattr(execution, '_execute_output', None),
                    'after_execute': getattr(execution, '_after_execute_output', None)
                }
                serialized['executions'].append(exec_data)
        
        return serialized
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Restore state from dictionary with GUID/alias persistence
        
        Args:
            data: Dictionary containing serialized state data
        """
        # Validate serialization version
        version = data.get('serialization_version', '1.0')
        if version != '1.0':
            pass
        
        # Restore basic state
        self.instance_name = data.get('instance_name', self.instance_name)
        self.state = data.get('state', {})
        self.default_max_node_executions = data.get('default_max_node_executions', 10)
        
        # Phase 2: Restore GUID-based storage
        self.node_outputs_by_guid = data.get('node_outputs_by_guid', {})
        self.node_outputs_by_alias = data.get('node_outputs_by_alias', {})
        self.node_guid_mapping = data.get('node_guid_mapping', {})
        
        # Restore execution tracking
        self._node_execution_counts = data.get('node_execution_counts', {})
        
        # Restore executions if present
        if 'executions' in data:
            self.executions = []
            for exec_data in data['executions']:
                execution = NodeOutput(name=exec_data['name'])
                if 'before_execute' in exec_data:
                    execution.before_execute = exec_data['before_execute']
                if 'execute' in exec_data:
                    execution.execute = exec_data['execute']
                if 'after_execute' in exec_data:
                    execution.after_execute = exec_data['after_execute']
                self.executions.append(execution)
        
        # Clear caches after restore
        self._node_output_cache.clear()
        
    
    def save(self, file_path: Union[str, Path], format: str = 'json', include_outputs: bool = True) -> None:
        """Save state to file with GUID/alias persistence
        
        Args:
            file_path: Path to save file
            format: 'json' or 'pickle' 
            include_outputs: Whether to include actual output values
        """
        file_path = Path(file_path)
        
        if format == 'json':
            # JSON serialization (human-readable, but limited data types)
            data = self.to_dict(include_outputs=include_outputs)
            
            # Convert non-JSON serializable objects to strings
            def json_serializer(obj):
                if hasattr(obj, '__dict__'):
                    return {'__type__': obj.__class__.__name__, '__data__': str(obj)}
                return str(obj)
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=json_serializer)
                
        elif format == 'pickle':
            # Pickle serialization (preserves all Python objects)
            data = self.to_dict(include_outputs=include_outputs)
            with open(file_path, 'wb') as f:
                pickle.dump(data, f)
                
        else:
            raise ValueError(f"Unsupported format: {format}. Use 'json' or 'pickle'")
        
    
    def load(self, file_path: Union[str, Path], format: str = 'json') -> None:
        """Load state from file with GUID/alias persistence
        
        Args:
            file_path: Path to load file
            format: 'json' or 'pickle'
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"State file not found: {file_path}")
        
        if format == 'json':
            with open(file_path, 'r') as f:
                data = json.load(f)
        elif format == 'pickle':
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
        else:
            raise ValueError(f"Unsupported format: {format}. Use 'json' or 'pickle'")
        
        self.from_dict(data)
    
    @classmethod
    def load_from_file(cls, file_path: Union[str, Path], format: str = 'json') -> 'SharedState':
        """Create new SharedState instance from saved file
        
        Args:
            file_path: Path to load file
            format: 'json' or 'pickle'
            
        Returns:
            New SharedState instance with loaded data
        """
        file_path = Path(file_path)
        
        if format == 'json':
            with open(file_path, 'r') as f:
                data = json.load(f)
        elif format == 'pickle':
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
        else:
            raise ValueError(f"Unsupported format: {format}. Use 'json' or 'pickle'")
        
        instance_name = data.get('instance_name', 'loaded_state')
        state = cls(instance_name)
        state.from_dict(data)
        
        return state


# NEW: Global workflow_state() Function and Context Management (Plan 18)

# Global variable to track current workflow state during execution
_current_workflow_state: Optional[SharedState] = None


def workflow_state(node_identifier: Union[str, int], attribute: str = None) -> Any:
    """Access workflow state from decision functions and node code
    
    Args:
        node_identifier: Node name (str) or execution index (int)
        attribute: Optional dot-separated attribute path
        
    Returns:
        Node output or specific attribute value
        
    Examples:
        workflow_state("validator")  # Get validator output
        workflow_state("data_processor", "result.count")  # Get nested attribute
        workflow_state(-1)  # Get previous output (same as state.previous_output)
        workflow_state(0)   # Get first node output
    """
    if _current_workflow_state is None:
        raise RuntimeError("workflow_state() can only be called during workflow execution")
    
    state = _current_workflow_state
    
    if isinstance(node_identifier, str):
        # Access by node name
        if attribute:
            return state.get_node_attribute(node_identifier, attribute)
        else:
            return state.get_node_output(node_identifier)
    
    elif isinstance(node_identifier, int):
        # Access by execution index
        if node_identifier >= len(state.executions) or node_identifier < -len(state.executions):
            raise IndexError(f"Execution index {node_identifier} out of range")
        
        output = state.executions[node_identifier].latest
        
        if attribute:
            # Navigate attribute path
            current = output
            for attr in attribute.split('.'):
                if isinstance(current, dict):
                    current = current.get(attr)
                else:
                    current = getattr(current, attr, None)
                if current is None:
                    break
            return current
        
        return output
    
    else:
        raise TypeError(f"node_identifier must be str or int, got {type(node_identifier)}")


class WorkflowStateContext:
    """Context manager for setting current workflow state"""
    
    def __init__(self, state: SharedState):
        self.state = state
        self.previous_state = None
    
    def __enter__(self):
        global _current_workflow_state
        self.previous_state = _current_workflow_state
        _current_workflow_state = self.state
        return self.state
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        global _current_workflow_state
        _current_workflow_state = self.previous_state
 