import inspect
from collections import OrderedDict
from typing import Callable, Optional, Literal
from egregore.core.workflow.nodes.node import Node
from egregore.core.workflow.nodes.node_types import NodeType, node_registry


def get_default_params(func: Callable):
    """Extract default parameters from a function signature.

    Args:
        func: Function to analyze

    Returns:
        OrderedDict of parameter names to default values
    """
    params = inspect.signature(func).parameters
    return OrderedDict((k, v.default) for k, v in params.items() if v.default is not inspect.Parameter.empty)


class NodeFactory:
    """Factory class for creating nodes.
    typically imported as N

    @N.register("A")
    def test_n(t=0):
        if t is not None:
            return t
    """
    def __init__(self):
        self.registry = node_registry

    def register(self, name: str, method: Optional[Literal["execute"]] = None, node_type: type[Node] = Node ):
        """Decorator to register a node type with the factory. By default the method is 'execute'."""
        if name not in self.registry:
            def __init__(self, *args, **kwargs):
                self.name = name
                Node.__init__(self, *args, **kwargs)

            class_attrs = {
                "__init__": __init__,

            }
            NewNodeClass = type(name, (Node,), class_attrs)
            self.registry[name] = NewNodeClass
            n = NodeType(self.registry[name])


        else:
            n = NodeType(self.registry[name])

        if method is None:
            return n

        if method == "execute":
            # Return a decorator that binds the function to the node's execute
            return n.__call__
        # Lifecycle methods removed in Plan 16: Lifecycle Simplification
        else:
            raise ValueError(f"Unknown method: {method}. Only 'execute' is supported.")


    def __getitem__(self, name: str):
        return self.registry[name]

    def __call__(self, name: str):
        """Create or retrieve a node type, supporting decorator syntax @node('name')"""
        if name not in self.registry:
            # Auto-register the node if it doesn't exist (enables @node('name') syntax)
            return self.register(name)
        else:
            return NodeType(self.registry[name])


node_factory = NodeFactory()
