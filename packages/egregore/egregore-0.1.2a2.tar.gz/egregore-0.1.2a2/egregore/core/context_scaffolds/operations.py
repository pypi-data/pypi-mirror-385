"""
OperationsAccessor - Clean interface for scaffold operation management.

Provides declarative (initialization) and imperative (runtime) control over
which scaffold operations are available, following the same accessor pattern
as agent.hooks.
"""

from typing import TYPE_CHECKING, List, Dict, Any, Literal, Set

if TYPE_CHECKING:
    from .base import BaseContextScaffold

from .decorators import get_scaffold_operations


class OperationsAccessor:
    """
    Accessor for scaffold operation management.

    Provides clean interface for querying and controlling scaffold operations,
    following the same pattern as agent.hooks.

    Usage:
        # Query operations
        scaffold.operations.disabled  # List[str]
        scaffold.operations.enabled   # Dict[str, metadata]
        scaffold.operations.format    # 'unified' | 'distinct' | 'custom'

        # Runtime control
        scaffold.operations.disable("op1", "op2")
        scaffold.operations.enable("op1")
    """

    def __init__(self, scaffold: 'BaseContextScaffold'):
        """
        Initialize operations accessor.

        Args:
            scaffold: Parent scaffold instance
        """
        self._scaffold = scaffold
        self._runtime_disabled: Set[str] = set()
        self._runtime_enabled: Set[str] = set()  # Override constructor/config disabling
        self._validated = False  # Track if we've validated

    @property
    def format(self) -> Literal['unified', 'distinct', 'custom']:
        """Get tool generation format."""
        return self._scaffold._scaffold_op_fmt

    @property
    def disabled(self) -> List[str]:
        """
        Get list of all disabled operations from all sources.

        Returns sorted list of operation names that are currently disabled,
        combining operations disabled via:
        - Constructor parameter (disabled_operations=[...])
        - operation_config ({"op": {"enabled": False}})
        - Runtime methods (scaffold.operations.disable(...))

        Runtime enable() calls override constructor/config disabling.

        Returns:
            Sorted list of disabled operation names
        """
        disabled = set()

        # From constructor parameter
        if self._scaffold.disabled_operations:
            disabled.update(self._scaffold.disabled_operations)

        # From operation_config
        for op_name, config in self._scaffold.operation_config.items():
            if not config.get("enabled", True):
                disabled.add(op_name)

        # From runtime modifications
        disabled.update(self._runtime_disabled)

        # Runtime enable() overrides other sources
        disabled -= self._runtime_enabled

        return sorted(disabled)

    @property
    def enabled(self) -> Dict[str, Any]:
        """
        Get enabled operations with metadata (filtered).

        Returns dictionary of operation names to their metadata,
        excluding any operations that are disabled.

        Returns:
            Dictionary mapping operation names to metadata

        Raises:
            ValueError: If disabled operations are invalid (first access only)
        """
        # Validate on first access
        if not self._validated:
            self._validate_disabled_operations()
            self._validated = True

        all_ops = get_scaffold_operations(self._scaffold)
        disabled_set = set(self.disabled)
        return {k: v for k, v in all_ops.items() if k not in disabled_set}

    def enable(self, *operation_names: str) -> None:
        """
        Enable operations at runtime.

        Removes operations from the runtime disabled set and adds to runtime enabled set,
        making them available. This overrides constructor/config disabling.

        Args:
            *operation_names: Names of operations to enable

        Example:
            scaffold.operations.enable("create", "update")
        """
        for op_name in operation_names:
            self._runtime_disabled.discard(op_name)
            self._runtime_enabled.add(op_name)

        # Trigger re-render if scaffold is reactive
        if self._scaffold._reactive:
            self._scaffold.content = self._scaffold.render()

    def disable(self, *operation_names: str) -> None:
        """
        Disable operations at runtime.

        Adds operations to the runtime disabled set, making them unavailable
        for tool generation and execution.

        Args:
            *operation_names: Names of operations to disable

        Raises:
            ValueError: If operation names don't exist or if disabling would
                       result in no enabled operations

        Example:
            scaffold.operations.disable("delete", "clear")
        """
        all_ops = get_scaffold_operations(self._scaffold)

        # Validate operations exist
        invalid = set(operation_names) - set(all_ops.keys())
        if invalid:
            raise ValueError(
                f"Cannot disable non-existent operations: {sorted(invalid)}. "
                f"Available: {sorted(all_ops.keys())}"
            )

        # Validate not disabling all operations
        new_disabled = set(self.disabled) | set(operation_names)
        if new_disabled >= set(all_ops.keys()):
            raise ValueError(
                f"Cannot disable all scaffold operations. "
                f"At least one must remain enabled."
            )

        self._runtime_disabled.update(operation_names)

        # Remove from runtime enabled (in case it was previously enabled)
        self._runtime_enabled -= set(operation_names)

        # Trigger re-render if scaffold is reactive
        if self._scaffold._reactive:
            self._scaffold.content = self._scaffold.render()

    def _validate_disabled_operations(self) -> None:
        """
        Validate disabled operations from all sources.

        Called lazily on first access to enabled property.

        Raises:
            ValueError: If disabled operations are invalid or would disable all operations
        """
        all_ops = get_scaffold_operations(self._scaffold)
        disabled_set = set(self.disabled)  # Collect from all sources

        if not disabled_set:
            return  # Nothing to validate

        # Validate operations exist
        invalid = disabled_set - set(all_ops.keys())
        if invalid:
            raise ValueError(
                f"Cannot disable non-existent operations: {sorted(invalid)}. "
                f"Available: {sorted(all_ops.keys())}"
            )

        # Validate not disabling all operations
        if disabled_set >= set(all_ops.keys()):
            raise ValueError(
                f"Cannot disable all scaffold operations. "
                f"At least one must remain enabled."
            )
