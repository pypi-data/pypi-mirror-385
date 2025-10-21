"""Registry context management for workflow-scoped node isolation.

This module provides contextvars-based registry scoping to prevent node pollution
across different workflows. Each workflow can operate with its own registry scope,
ensuring that node copies created during workflow compilation are isolated.
"""

from contextvars import ContextVar
from typing import Optional
from egregore.core.workflow.nodes.registry import NodeRegistry


# Context variable to store the active registry for the current execution context
_active_registry: ContextVar[Optional[NodeRegistry]] = ContextVar('active_registry', default=None)


def get_active_registry() -> NodeRegistry:
    """Get the currently active registry, or global fallback.

    Returns:
        The registry from current context if set, otherwise the global registry.
    """
    from egregore.core.workflow.nodes.base import _global_node_registry

    registry = _active_registry.get()
    return registry if registry is not None else _global_node_registry


def set_active_registry(registry: Optional[NodeRegistry]) -> None:
    """Set the active registry for current context.

    Args:
        registry: Registry to use, or None to clear context
    """
    _active_registry.set(registry)


class RegistryScope:
    """Context manager for workflow-scoped registry.

    Usage:
        with RegistryScope(workflow._local_node_registry):
            # All node operations within this block use the scoped registry
            self.start = self._build_chain(chain_result)

    This ensures that any nodes created or registered during workflow compilation
    use the workflow's local registry instead of the global one.
    """

    def __init__(self, registry: NodeRegistry):
        """Initialize registry scope.

        Args:
            registry: The registry to activate for this scope
        """
        self.registry = registry
        self.token = None

    def __enter__(self) -> NodeRegistry:
        """Enter the registry scope.

        Returns:
            The activated registry
        """
        self.token = _active_registry.set(self.registry)
        return self.registry

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the registry scope and restore previous context.

        Args:
            exc_type: Exception type if raised
            exc_val: Exception value if raised
            exc_tb: Exception traceback if raised
        """
        if self.token is not None:
            _active_registry.reset(self.token)
