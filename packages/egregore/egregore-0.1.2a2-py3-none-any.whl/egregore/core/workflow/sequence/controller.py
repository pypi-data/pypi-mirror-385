"""
Workflow Controller for execution management.

Provides external control, monitoring, and checkpoint management for workflow execution.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from egregore.core.workflow.sequence.base import Sequence
    from egregore.core.workflow.nodes.base import BaseNode
    from egregore.core.workflow.execution import ExecutionEntry

from egregore.core.workflow.state import SharedState


class WorkflowStoppedException(Exception):
    """Raised when workflow is stopped via controller"""
    pass


class WorkflowController:
    """External controller for workflow execution management with execution tracking"""

    def __init__(self, workflow: 'Sequence'):
        self.workflow = workflow
        self._state = 'ready'  # ready, running, paused, stopped, completed, error
        self._control_event = asyncio.Event()
        self._control_event.set()  # Start unpaused
        self._stop_requested = False

        # Track current execution location for nested sequences
        self.current_execution_path = []  # e.g., ["main_workflow", "seq1", "node_e"]
        self.execution_depth = 0

        # Execution tracking
        from egregore.core.workflow.execution import ExecutionHistory
        self.execution_history = ExecutionHistory()
        self.current_execution = None
        self.execution_counter = 0

        # Phase 3: Position tracking for workflow traversal
        self.execution_position = 0  # Track position in workflow sequence

        # Performance metrics
        self.total_execution_time = 0.0
        self.node_execution_counts = {}

        # Phase 6: Node Registry for GUID-based tracking
        from egregore.core.workflow.nodes.registry import NodeRegistry
        self.node_registry = NodeRegistry()
        self._register_workflow_nodes(workflow)

        # Reporting system
        from egregore.core.workflow.reporting import WorkflowReportingSystem
        self.reporting = WorkflowReportingSystem(self)

        # Plan 7: Checkpoint management
        self.auto_checkpoint_enabled = True
        self.checkpoint_dir = Path(".checkpoints")
        self.checkpoint_retention_days = 7
        self.auto_checkpoint_interval = 1  # Every N successful nodes
        self._auto_checkpoint_counter = 0

        # Hook system registry
        self._hook_registry = {
            "pre_sequence": [],           # [(hook_func, target_name), ...]
            "post_sequence": [],
            "on_sequence_error": [],
            "pre_execution": [],
            "post_execution": [],
            "on_error": [],
        }

        # Callback subscribers (new clean API)
        self._callback_subscribers = []   # For controller.subscribe()
        self._subscription_counter = 0    # For unique subscription IDs

    def pause(self) -> None:
        """Pause workflow execution"""
        if self._state == 'running':
            self._state = 'paused'
            self._control_event.clear()

            # Notify observers with execution location
            if hasattr(self.workflow.state, '_notify_state_change'):
                self.workflow.state._notify_state_change('workflow_paused', self.workflow.name, {
                    'timestamp': time.time(),
                    'controller_state': self._state,
                    'current_execution_path': self.current_execution_path.copy(),
                    'execution_depth': self.execution_depth
                })

    def resume(self) -> None:
        """Resume paused workflow execution"""
        if self._state == 'paused':
            self._state = 'running'
            self._control_event.set()

            # Notify observers
            if hasattr(self.workflow.state, '_notify_state_change'):
                self.workflow.state._notify_state_change('workflow_resumed', self.workflow.name, {
                    'timestamp': time.time(),
                    'controller_state': self._state
                })

    def stop(self) -> None:
        """Stop workflow execution"""
        if self._state in ['running', 'paused']:
            self._state = 'stopped'
            self._stop_requested = True
            self._control_event.set()  # Unblock if paused

            # Notify observers
            if hasattr(self.workflow.state, '_notify_state_change'):
                self.workflow.state._notify_state_change('workflow_stopped', self.workflow.name, {
                    'timestamp': time.time(),
                    'controller_state': self._state
                })

    def restart(self) -> None:
        """Restart workflow from beginning"""
        self._state = 'ready'
        self._stop_requested = False
        self._control_event.set()

        # Reset workflow state
        self.workflow.state = SharedState(self.workflow.state.instance_name)

        # Restore workflow reference
        self.workflow.state.workflow = self.workflow

        # Notify observers
        if hasattr(self.workflow.state, '_notify_state_change'):
            self.workflow.state._notify_state_change('workflow_restarted', self.workflow.name, {
                'timestamp': time.time(),
                'controller_state': self._state
            })

    @property
    def state(self) -> str:
        """Get current controller state"""
        return self._state

    @property
    def is_running(self) -> bool:
        """Check if workflow is currently running"""
        return self._state == 'running'

    @property
    def is_paused(self) -> bool:
        """Check if workflow is paused"""
        return self._state == 'paused'

    @property
    def is_stopped(self) -> bool:
        """Check if workflow is stopped"""
        return self._state == 'stopped'

    async def _check_control_state(self) -> None:
        """Internal method to check for pause/stop during execution"""
        # Wait if paused
        await self._control_event.wait()

        # Check if stop was requested
        if self._stop_requested:
            raise WorkflowStoppedException("Workflow execution was stopped")

    # Execution tracking methods
    def start_node_execution(self, node: 'BaseNode', input_value: Any) -> 'ExecutionEntry':
        """Phase 3: Record the start of node execution with enhanced identity tracking"""
        from egregore.core.workflow.execution import ExecutionEntry

        # Phase 3: Use factory method with position tracking
        entry = ExecutionEntry.from_node(node, input_value, self.execution_position)

        self.current_execution = entry
        self.execution_history.add_entry(entry)
        self.execution_counter += 1

        # Phase 3: Increment position for next node
        self.execution_position += 1

        # Update metrics (legacy support)
        self.node_execution_counts[entry.node_name] = \
            self.node_execution_counts.get(entry.node_name, 0) + 1

        # Phase 3: Notify event subscribers of node execution start
        if hasattr(self, 'reporting') and self.reporting:
            self.reporting._notify_subscribers('node_execution_started', {
                'node_name': entry.effective_name,
                'node_guid': entry.node_guid,
                'execution_id': entry.execution_id,
                'input_value': str(input_value)[:100] if input_value else None,
                'timestamp': entry.start_time.isoformat() if entry.start_time else None
            })

        return entry

    def complete_node_execution(self, entry: 'ExecutionEntry', output_value: Any) -> None:
        """Record the completion of node execution with automatic checkpointing"""
        entry.complete(output_value)

        if entry.duration:
            self.total_execution_time += entry.duration

        # Plan 7: Automatic checkpoint after successful node execution
        if self.auto_checkpoint_enabled:
            self._auto_checkpoint(entry.effective_name)

        # Phase 4: Check performance thresholds after completion
        if hasattr(self, 'reporting') and self.reporting:
            self.reporting.check_performance_thresholds(entry)

            # Phase 3: Notify event subscribers
            self.reporting._notify_subscribers('node_execution_completed', {
                'node_name': entry.effective_name,
                'node_guid': entry.node_guid,
                'execution_id': entry.execution_id,
                'duration': entry.duration,
                'output_value': str(output_value)[:100] if output_value else None,
                'timestamp': entry.end_time.isoformat() if entry.end_time else None
            })

        self.current_execution = None

    def error_node_execution(self, entry: 'ExecutionEntry', error: Exception) -> None:
        """Record an error during node execution"""
        entry.fail(error)
        self.current_execution = None

    def get_execution_summary(self) -> dict:
        """Get summary of execution metrics"""
        return {
            'total_executions': len(self.execution_history),
            'total_execution_time': self.total_execution_time,
            'node_execution_counts': self.node_execution_counts.copy(),
            'unique_nodes': len(self.node_execution_counts),
            'current_execution': self.current_execution.node_name if self.current_execution else None
        }

    def _register_workflow_nodes(self, workflow: 'Sequence') -> None:
        """Phase 6: Register all nodes in workflow with registry"""
        def register_recursive(node):
            if node and node not in visited:
                # Register node with registry
                self.node_registry.register_node(node)
                visited.add(node)

                # Follow next_node chain
                if hasattr(node, 'next_node') and node.next_node:
                    register_recursive(node.next_node)

                # For Decision nodes, register both branches
                if hasattr(node, 'true_node') and node.true_node:
                    register_recursive(node.true_node)
                if hasattr(node, 'false_node') and node.false_node:
                    register_recursive(node.false_node)

                # For Sequence nodes, register their internal chain
                if hasattr(node, 'start') and node.start:
                    register_recursive(node.start)

        visited = set()
        if workflow.start:
            register_recursive(workflow.start)

    # Plan 7: Checkpoint Management Methods
    def _auto_checkpoint(self, node_name: str) -> Optional[str]:
        """Create automatic checkpoint after successful node execution"""
        if not self.auto_checkpoint_enabled:
            return None

        self._auto_checkpoint_counter += 1

        # Only checkpoint every N successful nodes
        if self._auto_checkpoint_counter % self.auto_checkpoint_interval != 0:
            return None

        checkpoint_id = f"auto_{node_name}_{self.execution_counter}_{int(time.time())}"
        return self._create_checkpoint(checkpoint_id, checkpoint_type="auto")

    def _create_checkpoint(self, checkpoint_id: str, checkpoint_type: str = "manual") -> Optional[str]:
        """Create a checkpoint with workflow state and controller data"""
        try:
            # Ensure checkpoint directory exists
            self.checkpoint_dir.mkdir(exist_ok=True)

            # Create checkpoint data
            checkpoint_data = {
                "checkpoint_id": checkpoint_id,
                "checkpoint_type": checkpoint_type,
                "timestamp": datetime.now().isoformat(),
                "workflow_name": self.workflow.name,
                "workflow_id": self.workflow.workflow_id,

                # Workflow serialization using Plan 15 JSON
                "workflow_json": self.workflow.to_json(),

                # Workflow state (separate from JSON structure)
                "workflow_state": {
                    "state_dict": self.workflow.state.state.copy(),
                    "instance_name": self.workflow.state.instance_name,
                    "executions": len(self.workflow.state.executions)
                },

                # Controller state
                "controller_state": {
                    "execution_counter": self.execution_counter,
                    "execution_position": self.execution_position,
                    "total_execution_time": self.total_execution_time,
                    "node_execution_counts": self.node_execution_counts.copy(),
                    "auto_checkpoint_counter": self._auto_checkpoint_counter,
                    "current_execution_path": self.current_execution_path.copy(),
                    "execution_depth": self.execution_depth
                },

                # Execution history summary (last 10 entries for space efficiency)
                "recent_execution_history": [
                    {
                        "node_name": entry.node_name,
                        "effective_name": entry.effective_name,
                        "execution_id": entry.execution_id,
                        "duration": entry.duration,
                        "status": entry.status,
                        "timestamp": entry.start_time.isoformat() if entry.start_time else None
                    }
                    for entry in self.execution_history.get_recent(10)
                ]
            }

            # Save checkpoint file
            checkpoint_file = self.checkpoint_dir / f"{checkpoint_id}.json"
            with open(checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)

            # Checkpoint created successfully

            return checkpoint_id

        except Exception as e:
            return None

    def save(self, checkpoint_name: Optional[str] = None) -> Optional[str]:
        """Create manual checkpoint with optional custom name"""
        if checkpoint_name is None:
            checkpoint_name = f"manual_{int(time.time())}"

        # Sanitize checkpoint name for filename
        safe_name = "".join(c for c in checkpoint_name if c.isalnum() or c in ("_", "-", "."))
        checkpoint_id = f"manual_{safe_name}_{self.execution_counter}_{int(time.time())}"

        return self._create_checkpoint(checkpoint_id, checkpoint_type="manual")

    def load(self, checkpoint_id: str) -> 'Sequence':
        """Load workflow from checkpoint and return restored workflow"""
        # Import here to avoid circular import
        from egregore.core.workflow.sequence.base import Sequence

        try:
            # Find checkpoint file
            checkpoint_file = self.checkpoint_dir / f"{checkpoint_id}.json"
            if not checkpoint_file.exists():
                raise FileNotFoundError(f"Checkpoint {checkpoint_id} not found")

            # Load checkpoint data
            with open(checkpoint_file, 'r') as f:
                checkpoint_data = json.load(f)

            # Restore workflow using Plan 15 JSON serialization
            restored_workflow = Sequence.from_json(checkpoint_data["workflow_json"])

            # Restore workflow state
            if "workflow_state" in checkpoint_data:
                workflow_state = checkpoint_data["workflow_state"]
                restored_workflow.state.state.update(workflow_state["state_dict"])
                restored_workflow.state.instance_name = workflow_state["instance_name"]

            # Restore controller state
            controller_state = checkpoint_data["controller_state"]
            restored_workflow.controller.execution_counter = controller_state["execution_counter"]
            restored_workflow.controller.execution_position = controller_state["execution_position"]
            restored_workflow.controller.total_execution_time = controller_state["total_execution_time"]
            restored_workflow.controller.node_execution_counts = controller_state["node_execution_counts"]
            restored_workflow.controller._auto_checkpoint_counter = controller_state["auto_checkpoint_counter"]
            restored_workflow.controller.current_execution_path = controller_state["current_execution_path"]
            restored_workflow.controller.execution_depth = controller_state["execution_depth"]


            return restored_workflow

        except Exception as e:
            raise

    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """List available checkpoints with metadata"""
        if not self.checkpoint_dir.exists():
            return []

        checkpoints = []
        for checkpoint_file in self.checkpoint_dir.glob("*.json"):
            try:
                with open(checkpoint_file, 'r') as f:
                    data = json.load(f)

                checkpoints.append({
                    "checkpoint_id": data["checkpoint_id"],
                    "checkpoint_type": data["checkpoint_type"],
                    "timestamp": data["timestamp"],
                    "workflow_name": data["workflow_name"],
                    "file_path": str(checkpoint_file),
                    "file_size": checkpoint_file.stat().st_size
                })
            except (json.JSONDecodeError, KeyError, OSError) as e:
                pass  # Skip corrupted files

        # Sort by timestamp (newest first)
        checkpoints.sort(key=lambda x: x["timestamp"], reverse=True)
        return checkpoints

    def cleanup_old_checkpoints(self, days: Optional[int] = None) -> int:
        """Remove checkpoints older than specified days (default: retention_days)"""
        if days is None:
            days = self.checkpoint_retention_days

        if not self.checkpoint_dir.exists():
            return 0

        cutoff_time = datetime.now() - timedelta(days=days)
        removed_count = 0

        for checkpoint_file in self.checkpoint_dir.glob("*.json"):
            try:
                # Check file modification time
                file_mtime = datetime.fromtimestamp(checkpoint_file.stat().st_mtime)
                if file_mtime < cutoff_time:
                    checkpoint_file.unlink()
                    removed_count += 1
            except OSError as e:
                pass
        return removed_count

    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """Delete a specific checkpoint"""
        try:
            checkpoint_file = self.checkpoint_dir / f"{checkpoint_id}.json"
            if checkpoint_file.exists():
                checkpoint_file.unlink()
                return True
            else:
                return False
        except OSError as e:
            return False

    def subscribe(self, callback) -> str:
        """Subscribe to workflow events with clean callback API

        Args:
            callback: Function that accepts (event_type: str, event_data: dict)

        Returns:
            Subscription ID for unsubscribing
        """
        self._subscription_counter += 1
        subscription_id = f"sub_{self._subscription_counter}"

        self._callback_subscribers.append({
            'id': subscription_id,
            'callback': callback
        })

        return subscription_id

    def _register_hook(self, hook_type: str, hook_func, target: Optional[Any] = None) -> None:
        """Register a hook function for the specified hook type and optional target

        Args:
            hook_type: Type of hook (pre_execution, post_execution, etc.)
            hook_func: Hook function to register
            target: Optional target name (node/sequence name). None = all targets
        """
        if hook_type not in self._hook_registry:
            raise ValueError(f"Invalid hook type: {hook_type}. Valid types: {list(self._hook_registry.keys())}")

        # Store as tuple: (hook_func, target_name) - keeping it simple for now
        # FUTURE: Use weak references to prevent memory leaks in long-running workflows
        self._hook_registry[hook_type].append((hook_func, target))

    def _cleanup_hook_reference(self, dead_ref):
        """Clean up dead weak references from hook registry"""
        for hook_type, hooks in self._hook_registry.items():
            self._hook_registry[hook_type] = [
                (hook_ref, target) for hook_ref, target in hooks
                if hook_ref is not dead_ref
            ]

    def _unregister_hook(self, hook_type: str, hook_func) -> bool:
        """Unregister a hook function from the specified hook type

        Args:
            hook_type: Type of hook (pre_execution, post_execution, etc.)
            hook_func: Hook function to unregister

        Returns:
            True if hook was found and removed, False otherwise
        """
        if hook_type not in self._hook_registry:
            raise ValueError(f"Invalid hook type: {hook_type}. Valid types: {list(self._hook_registry.keys())}")

        # Find and remove all instances of this hook function (regardless of target)
        original_count = len(self._hook_registry[hook_type])
        self._hook_registry[hook_type] = [
            (func, target) for func, target in self._hook_registry[hook_type]
            if func != hook_func
        ]
        new_count = len(self._hook_registry[hook_type])

        return new_count < original_count  # True if any were removed

    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from workflow events using subscription ID

        Args:
            subscription_id: ID returned from subscribe() method

        Returns:
            True if subscription was found and removed, False otherwise
        """
        original_count = len(self._callback_subscribers)

        # Remove subscription with matching ID
        self._callback_subscribers = [
            sub for sub in self._callback_subscribers
            if sub['id'] != subscription_id
        ]

        new_count = len(self._callback_subscribers)
        return new_count < original_count  # True if any were removed

    def _create_hook_decorator(self, hook_type: str):
        """Create a hook decorator for the specified hook type

        Args:
            hook_type: Type of hook (pre_execution, post_execution, etc.)

        Returns:
            Decorator function that can be called with or without arguments
        """
        def decorator(*args, **kwargs):
            # Case 1: @seq.hooks.pre_execution (no arguments) - function passed directly
            if len(args) == 1 and callable(args[0]) and not self._is_target_parameter(args[0]):
                hook_func = args[0]
                # Register hook with no target (global)
                self._register_hook(hook_type, hook_func, target=None)
                return hook_func

            # Case 2: @seq.hooks.pre_execution("node_name") or @seq.hooks.on_error(ValueError)
            elif len(args) >= 1:
                target = args[0]

                # Handle combined targeting: @seq.hooks.on_error(ValueError, "node_name")
                if len(args) == 2:
                    target = (args[0], args[1])

                def inner_decorator(hook_func):
                    # Register hook with specific target (string, exception class, or tuple)
                    self._register_hook(hook_type, hook_func, target=target)
                    return hook_func
                return inner_decorator

            else:
                # Invalid usage
                raise ValueError(f"Invalid hook decorator usage for {hook_type}")

        return decorator

    def _is_target_parameter(self, arg) -> bool:
        """Check if an argument is a target parameter (not a hook function)"""
        # String targets
        if isinstance(arg, str):
            return True
        # Exception class targets
        if isinstance(arg, type) and issubclass(arg, Exception):
            return True
        # Tuple targets
        if isinstance(arg, tuple):
            return True
        # Otherwise, assume it's a function
        return False

    async def _execute_single_hook(self, hook_func, *args):
        """Execute a single hook function with async support

        Args:
            hook_func: Hook function to execute
            *args: Arguments to pass to the hook function
        """
        import asyncio

        if asyncio.iscoroutinefunction(hook_func):
            # Async hook
            await hook_func(*args)
        else:
            # Sync hook
            hook_func(*args)

    async def _execute_hooks(self, hook_type: str, context: Optional[dict] = None) -> None:
        """Execute all registered hooks of the specified type

        Args:
            hook_type: Type of hook to execute (pre_execution, post_execution, etc.)
            context: Context data containing node, sequence, result, error, etc.
        """
        if hook_type not in self._hook_registry:
            return

        context = context or {}
        hooks = self._hook_registry[hook_type]

        # Filter hooks based on targeting and exception type
        target_name = context.get('target_name')
        error = context.get('error')
        filtered_hooks = self._get_matching_hooks(hooks, target_name, error)

        for hook_func, target in filtered_hooks:
            try:
                # Pass entire context dict to hook function
                await self._execute_single_hook(hook_func, context)

            except Exception as e:
                # Hook failures should not break workflow execution
                func_name = getattr(hook_func, '__name__', 'unknown') if 'hook_func' in locals() and hook_func else 'dead_reference'
                print(f"Hook execution failed: {func_name} ({hook_type}): {e}")

        # CALLBACK BRIDGE FIX: Fire callback events after hook execution
        await self._notify_callback_subscribers(hook_type, context)

    def _execute_hooks_sync(self, hook_type: str, context: Optional[dict] = None) -> None:
        """Execute hooks synchronously for sync workflows

        Args:
            hook_type: Type of hook to execute (pre_execution, post_execution, etc.)
            context: Context data containing node, sequence, result, error, etc.
        """
        if hook_type not in self._hook_registry:
            return

        context = context or {}
        hooks = self._hook_registry[hook_type]

        # Filter hooks based on targeting and exception type
        target_name = context.get('target_name')
        error = context.get('error')
        filtered_hooks = self._get_matching_hooks(hooks, target_name, error)

        for hook_func, target in filtered_hooks:
            try:
                # Pass entire context dict to hook function
                if hook_func:
                    hook_func(context)
            except Exception as e:
                # Hook failures should not break workflow execution
                func_name = getattr(hook_func, '__name__', 'unknown') if hook_func else 'dead_reference'
                print(f"Sync hook execution failed: {func_name} ({hook_type}): {e}")

    async def _notify_callback_subscribers(self, hook_type: str, context: dict):
        """Convert hook execution to callback events and notify subscribers

        Args:
            hook_type: The type of hook that was executed
            context: Hook execution context
        """
        # Convert hook event to callback event format
        event_data = self._convert_hook_to_callback_event(hook_type, context)

        # Notify all callback subscribers
        for subscriber in self._callback_subscribers:
            try:
                callback_func = subscriber['callback']
                if asyncio.iscoroutinefunction(callback_func):
                    await callback_func(hook_type, event_data)
                else:
                    callback_func(hook_type, event_data)
            except Exception as e:
                print(f"Callback subscriber failed: {e}")

    def _convert_hook_to_callback_event(self, hook_type: str, context: dict) -> dict:
        """Convert hook execution context to callback event data

        Args:
            hook_type: Type of hook executed
            context: Hook execution context

        Returns:
            Event data dictionary for callback subscribers
        """
        event_data: Dict[str, Any] = {  # type: ignore[misc]
            'timestamp': time.time(),
        }

        if hook_type in ['pre_sequence', 'post_sequence', 'on_sequence_error']:
            # Sequence-level events
            sequence = context.get('sequence')
            if sequence:
                event_data['sequence_name'] = sequence.name
                event_data['sequence_id'] = getattr(sequence, 'workflow_id', 'unknown')

            if hook_type == 'post_sequence':
                event_data['result'] = context.get('result')
                # Calculate duration if start time available
                if sequence and hasattr(sequence, '_monitoring_start_time'):
                    event_data['duration'] = time.time() - sequence._monitoring_start_time  # type: ignore[attr-defined]

            elif hook_type == 'on_sequence_error':
                error = context.get('error')
                if error:
                    event_data['error'] = str(error)
                    event_data['error_type'] = type(error).__name__

        elif hook_type in ['pre_execution', 'post_execution', 'on_error']:
            # Node-level events
            node = context.get('node')
            if node:
                event_data['node_name'] = getattr(node, 'name', 'unknown')
                event_data['node_guid'] = getattr(node, 'guid', 'unknown')

            if hook_type == 'post_execution':
                event_data['result'] = context.get('result')
                event_data['output_value'] = context.get('result')

            elif hook_type == 'on_error':
                error = context.get('error')
                if error:
                    event_data['error'] = str(error)
                    event_data['error_type'] = type(error).__name__

        return event_data

    def _get_matching_hooks(self, hooks: list, target_name: Optional[str] = None, error: Optional[Exception] = None) -> list:
        """Filter hooks based on targeting logic and exception type filtering

        Args:
            hooks: List of (hook_ref, target) tuples (with weak references)
            target_name: Current target name (node/sequence name)
            error: Exception instance for error hook filtering

        Returns:
            Filtered list of hooks that should execute for this target
        """
        matching_hooks = []

        # Standard filtering - no complex exception handling for now
        for hook_func, hook_target in hooks:
            if self._hook_matches_criteria(hook_target, target_name, error):
                matching_hooks.append((hook_func, hook_target))

        return matching_hooks

    def _calculate_exception_specificity(self, hook_exception_class: type, actual_error: Exception) -> int:
        """Calculate exception specificity for most-specific-first matching

        Returns:
            -1 if no match, 0+ for match depth (0 = exact match, higher = more general)
        """
        if not isinstance(actual_error, hook_exception_class):
            return -1

        # Calculate inheritance distance (0 = exact match, higher = more general)
        error_class = type(actual_error)
        if error_class == hook_exception_class:
            return 0

        # Find distance in inheritance hierarchy
        distance = 0
        for base_class in error_class.__mro__[1:]:  # Skip self
            distance += 1
            if base_class == hook_exception_class:
                return distance

        return -1  # Not in hierarchy

    def _hook_matches_criteria(self, hook_target, target_name: Optional[str] = None, error: Optional[Exception] = None) -> bool:
        """Check if a hook matches the current execution criteria

        Args:
            hook_target: Hook target (can be None, string, exception class, or tuple)
            target_name: Current target name
            error: Current exception (for error hooks)

        Returns:
            True if hook should execute, False otherwise
        """
        # Handle different hook target types
        if hook_target is None:
            # Global hook - always matches
            return True

        elif isinstance(hook_target, str):
            # String target - match by name
            return hook_target == target_name

        elif isinstance(hook_target, type) and issubclass(hook_target, Exception):
            # Exception class target - match by exception type
            return error is not None and isinstance(error, hook_target)

        elif isinstance(hook_target, tuple) and len(hook_target) == 2:
            # Combined target: (exception_class, target_name)
            exception_class, target_str = hook_target
            exception_matches = error is not None and isinstance(error, exception_class)
            target_matches = target_str == target_name
            return exception_matches and target_matches

        else:
            # Unknown target type - don't match
            return False
