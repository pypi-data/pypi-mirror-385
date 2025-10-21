from typing import Optional, Union, Any, TYPE_CHECKING
import copy
import uuid
from egregore.core.workflow.state import SharedState
from egregore.core.workflow.nodes.registry import NodeRegistry

if TYPE_CHECKING:
    from egregore.core.workflow.nodes.node import NodeMapper
    from egregore.core.workflow.nodes.node_types import NodeType


_global_node_registry = NodeRegistry()


def _get_active_registry() -> NodeRegistry:
    """Get the active registry from context, or global fallback.

    This function is defined here to avoid circular imports while still
    providing access to the registry context system.
    """
    try:
        from egregore.core.workflow.nodes.registry_context import get_active_registry
        return get_active_registry()
    except ImportError:
        # Fallback if registry_context not available
        return _global_node_registry

# Legacy dict for backward compatibility
node_registry = {}


class BaseNode:

    """The base class for all nodes in the action graph."""

    def __init__(self, **kwargs):
        self.name = kwargs.get("name", self.__class__.__name__)
        self.next_node = None
        self._first_node: "BaseNode" = self
        self._prev_shift: Optional["NodeMapper"] = None

        self._chain_start: Optional["BaseNode"] = None
        self.guid = str(uuid.uuid4())
        self.alias_name = None
        self.canonical_name = None

        self._is_router = False
        self._produces_data = True
        registry = _get_active_registry()
        registry.register_node(self)
    
    @property
    def effective_name(self) -> str:
        """Name used in state management and references"""
        return self.alias_name if self.alias_name else self.name
    
    def set(self, shared_state: SharedState):
        self.state = shared_state

    def __rrshift__(self, other: Any):
        """Handle reverse right shift for Decision patterns: condition >> node

        This is used for Decision branches with Sequence/Decision/ParallelNode instances:
        - 'condition' >> sequence_instance
        - 'condition' >> decision_instance

        For NodeType instances, NodeType.__rrshift__() is called instead.
        """
        from egregore.core.workflow.nodes.node import NodeMapper
        from egregore.core.workflow.nodes.node_types import NodeType

        if isinstance(other, bool):
            first_node = getattr(self, '_chain_start', None) or self._get_first_node_in_chain()
            return NodeMapper(other, first_node)
        if isinstance(other, str):
            first_node = getattr(self, '_chain_start', None) or self._get_first_node_in_chain()
            return NodeMapper(other, first_node)
        if isinstance(other, NodeType):
            first_node = getattr(self, '_chain_start', self._get_first_node_in_chain())
            return NodeMapper(other.node_instance, first_node)

    def _get_first_node_in_chain(self):
        """Get the first node in a chain when this node is the result of >> operations"""
        if hasattr(self, '_first_node') and self._first_node is not None:
            return self._first_node
        return self

    def execute(self, *args, **kwargs):
        from egregore.core.workflow.agent_interceptor import workflow_node_context
        from egregore.core.workflow.agent_discovery import get_agent_registry
        
        with workflow_node_context(self.name):
            try:
                registry = get_agent_registry()
                registry._notify_observers("node_execution_started", self.name, {
                    "node": self,
                    "args": str(args)[:100] if args else "",
                    "kwargs": {k: str(v)[:50] for k, v in kwargs.items()}
                })
                
                result = self._execute_impl(*args, **kwargs)
                
                registry._notify_observers("node_execution_completed", self.name, {
                    "node": self,
                    "result": str(result)[:100] if result else None
                })
                
                return result
                
            except Exception as e:
                get_agent_registry()._notify_observers("node_execution_failed", self.name, {
                    "node": self,
                    "error": str(e)
                })
                raise
    
    def _execute_impl(self, *args, **kwargs):
        raise NotImplementedError(f"Execute is not implemented for {self.name}")