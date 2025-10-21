"""
Graph Execution Controller

Executes workflows by following graph edges. This is the new execution engine
that replaces internal orchestration in Decision/Sequence nodes.

Architecture:
- Graph is the single source of truth for execution flow
- Controller follows edges (SEQUENTIAL, BRANCH, PARALLEL)
- Nodes are stateless - just execute and return results
- Loop detection via node revisitation tracking (implicit through node reuse)
"""

from typing import Any, Optional, Dict
from egregore.core.workflow.graph import Graph, GraphNode, GraphEdge, EdgeTypeEnum, NodeTypeEnum
from egregore.core.workflow.exceptions import MaxIterationsExceededError
from egregore.core.workflow.execution import ExecutionHistory, ExecutionEntry


class GraphExecutionController:
    """Executes workflow by following graph edges."""

    def __init__(
        self,
        graph: Graph,
        state: Any = None,
        execution_history: Optional[ExecutionHistory] = None,
        max_loop_iterations: int = 1000,
        workflow_controller: Any = None,
        error_handler: Optional[Any] = None,
        error_config: Optional[Dict] = None
    ):
        """Initialize controller with graph.

        Args:
            graph: The execution graph
            state: Workflow state to inject into nodes
            execution_history: Shared execution history for tracking (from WorkflowController)
            max_loop_iterations: Maximum iterations for any loop (global fallback)
            workflow_controller: WorkflowController instance for hook execution
            error_handler: AsyncErrorHandler instance for retry logic
            error_config: Error configuration dict for node attribute lookups
        """
        self.graph = graph
        self.state = state
        self.max_loop_iterations = max_loop_iterations
        self.loop_counters: Dict[str, int] = {}  # edge_id -> iteration count (global safety)
        self.decision_iteration_tracking: Dict[str, int] = {}  # decision_id -> iteration count (per-branch)
        self.decision_last_branch: Dict[str, str] = {}  # decision_id -> last_branch_id (for reset detection)
        self.node_instances: Dict[str, Any] = {}  # node_id -> instantiated node
        self.next_instance_override: Optional[Any] = None  # Override for next node instance (used by decisions)

        # Use shared ExecutionHistory from WorkflowController, or create new one
        self.execution_history = execution_history if execution_history is not None else ExecutionHistory()

        # Track execution position for ExecutionEntry
        self.execution_position = 0

        # Store workflow controller for hook execution
        self.workflow_controller = workflow_controller

        # Store error handler and config
        self.error_handler = error_handler
        self.error_config = error_config or {}

    async def execute_graph(self, start_node: GraphNode, initial_input: Any = None) -> Any:
        """Execute workflow starting from a node.

        Args:
            start_node: Starting GraphNode
            initial_input: Initial input data

        Returns:
            Final result from workflow execution
        """
        current = start_node
        result = initial_input

        max_steps = 10000  # Safety limit for total execution
        step_count = 0

        while current and step_count < max_steps:
            # Get or instantiate node
            node_instance = self._get_node_instance(current)

            # Create ExecutionEntry BEFORE executing node
            entry = ExecutionEntry.from_node(
                node=node_instance,
                input_value=result,
                position=self.execution_position
            )
            self.execution_position += 1

            # ROUTER PRE-DECISION DATA STORAGE:
            # Store router's input BEFORE execution for later restoration.
            # We'll decide whether to restore based on router type (initial vs branch).
            if current.is_router and self.state is not None:
                router_id = current.id
                # Store router's input for this specific router
                self.state.store[f'_router_input_{router_id}'] = result

            # Execute node
            result = await self._execute_node(node_instance, result)

            # ROUTER POST-DECISION DATA STORAGE:
            # For branch routers (transformers), also store OUTPUT for restoration.
            # Branch routers transform data; branches should receive transformed data.
            # Initial routers classify data; branches should receive original data.
            if current.is_router and self.state is not None:
                router_id = current.id
                # Store router's output as well
                self.state.store[f'_router_output_{router_id}'] = result

            # Complete ExecutionEntry AFTER executing node
            entry.complete(result)

            # Add to ExecutionHistory
            self.execution_history.add_entry(entry)

            # DECISION DATA RESTORATION:
            # Decision returns router's output (routing criteria). Restore the data
            # that was being routed (router's input) for branches to consume.
            # State is our source of truth for tracking this.
            if current.node_type == NodeTypeEnum.DECISION:
                # Save decision output (routing criteria) before restoration
                # This is what we return if max_iter terminates gracefully
                decision_output = result

                router_node = self.graph.get_router_for_decision(current)
                if router_node and self.state is not None:
                    router_id = router_node.id
                    router_input_key = f'_router_input_{router_id}'
                    router_output_key = f'_router_output_{router_id}'

                    if router_input_key in self.state.store:
                        stored_input = self.state.store[router_input_key]
                        stored_output = self.state.store.get(router_output_key)

                        # Determine which value to restore based on router type:
                        # - Transformers: Router IS a branch handler (reused node), restore OUTPUT
                        # - Classifiers: Router is separate from branch handlers, restore INPUT
                        if self._is_transformer_router(router_node):
                            # Transformer router - restore its output (transformed data)
                            result = stored_output if stored_output is not None else stored_input
                        else:
                            # Classifier router - restore its input (original data)
                            result = stored_input

                        # Clean up - no longer needed
                        del self.state.store[router_input_key]
                        if router_output_key in self.state.store:
                            del self.state.store[router_output_key]

                # BRANCH SWITCHING DETECTION AND COUNTER INCREMENT:
                # After decision execution, we know which branch was selected
                # Track the branch and increment/reset the iteration counter accordingly
                if hasattr(node_instance, 'next_node') and node_instance.next_node:
                    # Identify branch by its ROOT node, not loop target
                    # Find which subgraph contains the selected next_node
                    branch_id = self._get_branch_id_for_node(current, node_instance.next_node)
                    decision_id = current.id
                    last_branch = self.decision_last_branch.get(decision_id)

                    # Get current iteration count
                    iteration_count = self.decision_iteration_tracking.get(decision_id, 0)

                    # Check if branch switched
                    branch_switched = (last_branch is not None and last_branch != branch_id)

                    if branch_switched:
                        # Branch switched - reset iteration counter to 0
                        # Next increment will make it 1 (first execution of new branch)
                        self.decision_iteration_tracking[decision_id] = 0
                        iteration_count = 0  # Update local variable too

                    # MAX_ITER CHECK (BEFORE incrementing counter):
                    # Check if we've hit max_iter for this branch
                    # This happens AFTER we know if branch switched, but BEFORE incrementing
                    max_iter = self._get_decision_max_iter(current)
                    if max_iter is not None:
                        # Calculate what the counter will be after increment
                        # counter=0 → next=1 (1st execution)
                        # counter=1 → next=2 (2nd execution)
                        # max_iter=N means allow N-1 executions per branch
                        # So when next_count >= max_iter, we've reached the limit
                        next_count = iteration_count + 1 if not branch_switched else 1

                        if next_count >= max_iter:
                            # Max iter reached - either raise or terminate
                            raise_on_max_iter = self._get_decision_raise_on_max_iter(current)

                            if raise_on_max_iter:
                                raise MaxIterationsExceededError(
                                    max_iter,
                                    next_count,  # Report the iteration we tried to execute
                                    f"Decision {self._get_node_name(current)}"
                                )
                            else:
                                # Terminate execution - return restored data (not routing criteria)
                                # result contains the restored router input/output
                                return result

                    # Increment counter (after max_iter check)
                    if not branch_switched:
                        self.decision_iteration_tracking[decision_id] = iteration_count + 1
                    else:
                        # After reset, set to 1 (first execution of new branch)
                        self.decision_iteration_tracking[decision_id] = 1

                    # Update last branch for next comparison
                    self.decision_last_branch[decision_id] = branch_id

            # Get next node from graph structure
            next_node = self._get_next_node(current, result, node_instance)

            # Check for loop (global safety check only)
            if next_node and self._is_loop(current, next_node):
                loop_key = f"{current.id}->{next_node.id}"
                self.loop_counters[loop_key] = self.loop_counters.get(loop_key, 0) + 1

                # Global max_loop_iterations as safety fallback
                if self.loop_counters[loop_key] >= self.max_loop_iterations:
                    raise MaxIterationsExceededError(
                        self.max_loop_iterations,
                        self.loop_counters[loop_key],
                        f"Loop from {self._get_node_name(current)} to {self._get_node_name(next_node)}"
                    )

            current = next_node
            step_count += 1

        return result

    def _get_node_instance(self, graph_node: GraphNode) -> Any:
        """Get or instantiate a node.

        Args:
            graph_node: GraphNode to instantiate

        Returns:
            Node instance ready for execution
        """
        node_id = graph_node.id

        # PRIORITY 1: Check if decision provided an override instance for this node
        # This ensures decisions can provide fresh instances for each branch
        if self.next_instance_override is not None:
            instance = self.next_instance_override
            self.next_instance_override = None  # Clear after using

            # Inject state and graph references
            if self.state:
                instance.state = self.state
            instance._graph = self.graph
            instance._graph_node = graph_node
            if not hasattr(instance, '_is_router'):
                instance._is_router = graph_node.is_router

            # DO NOT cache override instances!
            # When a node is reused in different branches, each branch gets a fresh instance.
            # Caching would cause all branches to share the same instance, defeating the purpose.
            # The decision will provide a fresh override for each branch execution.
            return instance

        # PRIORITY 2: Check cache
        if node_id in self.node_instances:
            return self.node_instances[node_id]

        # PRIORITY 3: Instantiate from NodeSpec
        node_spec = graph_node.node_instance

        # If it's a NodeSpec (lazy construction), instantiate it
        if hasattr(node_spec, 'instantiate'):
            instance = node_spec.instantiate()
            # Inject state immediately after instantiation (ALWAYS - don't check truthiness)
            instance.state = self.state
            # Copy graph references (graph is stored in controller, not in graph_node)
            instance._graph = self.graph
            instance._graph_node = graph_node
            # Copy router flag
            instance._is_router = graph_node.is_router

            self.node_instances[node_id] = instance
            return instance

        # Already an instance
        node_instance = node_spec
        # Inject state (ALWAYS - don't check truthiness)
        node_instance.state = self.state
        self.node_instances[node_id] = node_instance
        return node_instance

    async def _execute_node(self, node_instance: Any, input_data: Any) -> Any:
        """Execute a node with retry logic and error handling.

        Args:
            node_instance: The node to execute
            input_data: Input data for the node

        Returns:
            Node execution result
        """
        from egregore.core.workflow.sequence import Sequence
        from egregore.core.workflow.exceptions import create_error_context

        # Inject state
        if self.state:
            node_instance.state = self.state
        if hasattr(node_instance, 'state') and hasattr(node_instance.state, 'set_previous_output'):
            node_instance.state.set_previous_output(input_data)

        # Get node metadata
        node_name = getattr(node_instance, 'name', str(node_instance))
        node_type = type(node_instance).__name__

        # Get retry configuration (from node attributes or config)
        max_retries = self._get_node_max_retries(node_instance)

        # RETRY LOOP
        for attempt in range(max_retries):
            # Create error context for this attempt
            error_context = create_error_context(
                node_name=node_name,
                node_type=node_type,
                execution_phase="execution",
                attempt_number=attempt + 1,
                workflow_state=self.state.store if self.state and hasattr(self.state, 'store') else {}
            )

            try:
                # Execute pre-execution hooks (fire on every attempt)
                if self.workflow_controller:
                    await self.workflow_controller._execute_hooks('pre_execution', {
                        'node': node_instance,
                        'target_name': node_name,
                        'execution_path': [],
                        'depth': 0,
                        'attempt_number': attempt + 1
                    })

                # Execute node based on type
                if isinstance(node_instance, Sequence):
                    result = await node_instance.async_execute(input_data)
                elif hasattr(node_instance, 'async_execute'):
                    result = await node_instance.async_execute(input_data)
                else:
                    # Sync node execution
                    import asyncio
                    from egregore.core.workflow.state import _wrap_for_executor
                    loop = asyncio.get_event_loop()
                    node_instance.state.set_current(node_instance)
                    result = await loop.run_in_executor(None, _wrap_for_executor(node_instance.execute))
                    node_instance.state.current.execute = result

                # SUCCESS - Execute post-execution hooks and return
                if self.workflow_controller:
                    await self.workflow_controller._execute_hooks('post_execution', {
                        'node': node_instance,
                        'result': result,
                        'target_name': node_name,
                        'execution_path': [],
                        'depth': 0,
                        'attempt_number': attempt + 1,
                        'total_attempts': attempt + 1
                    })

                # Update state with result
                if hasattr(node_instance, 'state') and hasattr(node_instance.state, 'set_previous_output'):
                    node_instance.state.set_previous_output(result)

                return result  # Success - exit retry loop

            except Exception as e:
                # Execute error hooks (fire on every attempt)
                if self.workflow_controller:
                    await self.workflow_controller._execute_hooks('on_error', {
                        'node': node_instance,
                        'error': e,
                        'target_name': node_name,
                        'execution_path': [],
                        'depth': 0,
                        'attempt_number': attempt + 1,
                        'is_final_attempt': attempt == max_retries - 1
                    })

                # Let error handler decide: retry? fallback? fatal?
                if self.error_handler:
                    try:
                        # Error handler processes the error
                        # Returns fallback value OR raises to signal retry/failure
                        handler_result = await self.error_handler.handle_node_error(
                            e, node_instance, error_context
                        )

                        # Error handler returned a fallback value
                        # Check if node has its own fallback_value to use instead
                        if hasattr(node_instance, 'fallback_value'):
                            result = node_instance.fallback_value
                        else:
                            # No node-level fallback, but error handler says continue
                            # This shouldn't happen for errors without fallback_value
                            # Raise the original error instead
                            raise e

                        if hasattr(node_instance, 'state') and hasattr(node_instance.state, 'set_previous_output'):
                            node_instance.state.set_previous_output(result)
                        return result

                    except Exception as raised_error:
                        # Error handler raised - check if this is a fatal error or retryable
                        # Fatal programming errors and permission errors should NOT retry
                        fatal_programming_errors = (TypeError, ValueError, AttributeError, NameError, SyntaxError, PermissionError)
                        if isinstance(raised_error, fatal_programming_errors):
                            # Fatal error - raise immediately, don't retry
                            raise

                        # Not a fatal programming error - check if we should retry
                        if attempt < max_retries - 1:
                            # More attempts available - continue retry loop
                            continue
                        else:
                            # Final attempt failed
                            # Check if node has fallback_value attribute
                            if hasattr(node_instance, 'fallback_value'):
                                fallback = node_instance.fallback_value
                                if hasattr(node_instance, 'state') and hasattr(node_instance.state, 'set_previous_output'):
                                    node_instance.state.set_previous_output(fallback)
                                return fallback
                            # No fallback - raise the error
                            raise
                else:
                    # No error handler - check if we should retry or use fallback
                    if attempt < max_retries - 1:
                        # More retries available - continue loop
                        continue
                    else:
                        # Final attempt - check for fallback_value
                        if hasattr(node_instance, 'fallback_value'):
                            fallback = node_instance.fallback_value
                            if hasattr(node_instance, 'state') and hasattr(node_instance.state, 'set_previous_output'):
                                node_instance.state.set_previous_output(fallback)
                            return fallback
                        # No fallback - raise the error
                        raise

        # Should never reach here
        raise RuntimeError(f"Unexpected state in _execute_node retry loop for {node_name}")

    def _get_node_max_retries(self, node_instance: Any) -> int:
        """Get max_retries for a node using priority chain.

        Priority:
        1. Node attribute (node.max_retries) - HIGHEST (per-node customization)
        2. Global config (error_config["max_retries"]) - workflow-wide default
        3. Error handler default
        4. System fallback (1 - no retry by default)
        """
        # Priority 1: Node attribute (HIGHEST - per-node customization)
        if hasattr(node_instance, 'max_retries'):
            max_retries = node_instance.max_retries
            return max(1, max_retries) if max_retries >= 0 else 1

        # Priority 2: Global config (workflow-wide default)
        if self.error_config and 'max_retries' in self.error_config:
            max_retries = self.error_config['max_retries']
            # Handle edge case: max_retries=0 means execute once (no retry)
            # Convert to 1 so range(1) executes once
            return max(1, max_retries) if max_retries >= 0 else 1

        # Priority 3: Error handler default
        if self.error_handler and hasattr(self.error_handler, 'recovery_strategy'):
            if hasattr(self.error_handler.recovery_strategy, 'max_retries'):
                return self.error_handler.recovery_strategy.max_retries

        # Priority 4: System fallback (1 = no retry, just original attempt)
        return 1

    def _get_next_node(self, current: GraphNode, result: Any, node_instance: Any) -> Optional[GraphNode]:
        """Get next node from graph based on current node and result.

        Args:
            current: Current GraphNode
            result: Result from current node execution
            node_instance: Current node instance

        Returns:
            Next GraphNode to execute, or None if terminal
        """
        # Check if node set next_node (Decision pattern matching)
        if hasattr(node_instance, 'next_node') and node_instance.next_node:
            # Store the decision's chosen instance so it gets used instead of cached instance
            chosen_instance = node_instance.next_node
            self.next_instance_override = chosen_instance

            # Find the corresponding GraphNode
            next_graph_node = self._find_graph_node_by_instance(chosen_instance)

            # CRITICAL: Clear next_node after using it to prevent pollution
            # When a node is reused in multiple branches, we don't want the next_node
            # from one branch to leak into another branch's execution
            node_instance.next_node = None

            return next_graph_node

        # Get outgoing edges
        edges = self.graph.get_outgoing_edges(current)

        if not edges:
            # No outgoing edges - this is a terminal node
            # Loops are created with explicit edges (e.g., 'back' >> node)
            # Terminal nodes should truly terminate, not route back
            return None

        # Follow SEQUENTIAL edge (loops are implicit through node reuse)
        for edge in edges:
            if edge.edge_type == EdgeTypeEnum.SEQUENTIAL:
                return edge.to_node

        return None

    def _find_graph_node_by_instance(self, node_instance: Any) -> Optional[GraphNode]:
        """Find GraphNode by node instance.

        Args:
            node_instance: Node instance to find

        Returns:
            GraphNode or None
        """
        # PRIORITY 1: Check if instance has _graph_node reference
        # This is set when Decision instantiates a branch node
        if hasattr(node_instance, '_graph_node') and node_instance._graph_node:
            return node_instance._graph_node

        # PRIORITY 2: Check if we already instantiated this (instance equality)
        for node_id, instance in self.node_instances.items():
            if instance == node_instance:
                return self.graph.nodes.get(node_id)

        # PRIORITY 3: Try to find by guid/id
        node_id = self.graph._get_node_id(node_instance)
        return self.graph.nodes.get(node_id)

    def _is_loop(self, current: GraphNode, next_node: GraphNode) -> bool:
        """Check if transition from current to next is a loop.

        A true loop is when we transition to a node that appears CONSECUTIVELY
        in recent execution history, indicating we're cycling through the same
        sequence of nodes repeatedly.

        For nested decisions, nodes can legitimately be visited multiple times
        (as branch handlers and routers), so we only detect loops when there's
        a pattern of consecutive revisitation.

        Args:
            current: Current GraphNode
            next_node: Next GraphNode

        Returns:
            True if this is a loop (cycling through same sequence)
        """
        # Look for the last N executions to detect cycling patterns
        # If we see current -> next_node repeatedly, that's a loop
        recent_transitions = []
        prev_node_id = None

        for entry in self.execution_history.entries[-10:]:  # Check last 10 executions
            if hasattr(entry.node, '_graph_node') and entry.node._graph_node:
                node_id = entry.node._graph_node.id
                if prev_node_id:
                    recent_transitions.append((prev_node_id, node_id))
                prev_node_id = node_id

        # Check if current->next_node transition appears multiple times recently
        transition = (current.id, next_node.id)
        transition_count = recent_transitions.count(transition)

        # If this transition has occurred 3+ times recently, it's a loop
        return transition_count >= 3

    def _get_router_entry_for_node(self, router_node: GraphNode) -> Optional[ExecutionEntry]:
        """Get the execution entry for a specific router node.

        Args:
            router_node: The GraphNode that is the router

        Returns:
            ExecutionEntry for this router, or None if not found
        """
        # Search backwards through execution history for the most recent execution of this router
        for entry in reversed(self.execution_history.entries):
            # Match by GraphNode ID
            if (hasattr(entry.node, '_graph_node') and
                entry.node._graph_node and
                entry.node._graph_node.id == router_node.id):
                return entry
        return None

    def _get_node_name(self, graph_node: GraphNode) -> str:
        """Get displayable name for a node.

        Args:
            graph_node: GraphNode

        Returns:
            Node name string
        """
        node_spec = graph_node.node_instance
        return getattr(node_spec, 'node_name', getattr(node_spec, 'name', 'unknown'))

    def _get_decision_max_iter(self, decision_node: GraphNode) -> Optional[int]:
        """Get max_iter configuration from Decision's graph metadata.

        OPTION 3: Configuration stored in graph metadata at build time.

        Args:
            decision_node: Decision GraphNode

        Returns:
            max_iter value or None if not configured
        """
        subgraphs = self.graph.get_subgraphs(decision_node)
        if not subgraphs:
            return None

        return subgraphs[0].metadata.get('max_iter')

    def _get_decision_raise_on_max_iter(self, decision_node: GraphNode) -> bool:
        """Get raise_on_max_iter configuration from Decision's graph metadata.

        OPTION 3: Configuration stored in graph metadata at build time.

        Args:
            decision_node: Decision GraphNode

        Returns:
            raise_on_max_iter flag (default False)
        """
        subgraphs = self.graph.get_subgraphs(decision_node)
        if not subgraphs:
            return False

        return subgraphs[0].metadata.get('raise_on_max_iter', False)

    def _get_branch_id_for_node(self, decision_node: GraphNode, target_node: Any) -> str:
        """Get branch ID by finding which subgraph contains the target node.

        Branch ID should uniquely identify a branch (subgraph), not the loop target.
        When both branches loop back to the same node, using the loop target as branch_id
        would make all branches appear identical.

        Args:
            decision_node: The Decision GraphNode
            target_node: The node instance selected by the decision

        Returns:
            Branch ID (subgraph root node ID)
        """
        # Get all subgraphs for this decision
        subgraphs = self.graph.get_subgraphs(decision_node)

        if not subgraphs:
            # Fallback to instance ID if no subgraphs found
            return str(id(target_node))

        # Find the GraphNode corresponding to target_node
        target_graph_node = self._find_graph_node_by_instance(target_node)

        if not target_graph_node:
            # Fallback to instance ID if can't find graph node
            return str(id(target_node))

        # Find which subgraph contains this target node
        for subgraph in subgraphs:
            if target_graph_node in subgraph.nodes:
                # Use the subgraph's root node as the branch identifier
                if subgraph.root_node:
                    return subgraph.root_node.id
                # Fallback if no root node
                return str(id(subgraph))

        # Fallback if not found in any subgraph (shouldn't happen)
        return str(id(target_node))

    def _is_transformer_router(self, router_node: GraphNode) -> bool:
        """Check if a router is a transformer (branch handler) vs classifier.

        PROPER LONG-TERM SOLUTION: Check return type annotation from graph metadata.

        Transformers/Generators: Router produces data that branches should receive
        - Transformers: Same input/output type (int → int, str → str)
        - Generators: No input params, produces output (e.g., () → int)
        Branches should receive the router's OUTPUT.

        Classifiers: Router produces routing decisions (e.g., 'even'/'odd', 'pass'/'fail')
        - Literal return type
        - Different input/output types (int → str routing value)
        Branches should receive the original INPUT data, not the classification.

        Detection (priority order):
        1. Routers with Literal[...] return type are ALWAYS classifiers → restore INPUT
        2. Routers with same input/output types (e.g., int → int) are transformers → restore OUTPUT
        3. Routers with NO input params are generators (e.g., () → int) → restore OUTPUT
        4. Default: Different types (e.g., int → str) are classifiers → restore INPUT

        Args:
            router_node: The router GraphNode to check

        Returns:
            True if router is a transformer/generator (restore OUTPUT), False if classifier (restore INPUT)
        """
        # PRIORITY 1: Check for Literal return type metadata
        is_literal = router_node.metadata.get('is_literal_return', None)

        if is_literal is True:
            # Literal return type → definitely a classifier
            return False  # Restore INPUT

        # PRIORITY 2: Check for same input/output type (transformer pattern)
        same_io_type = router_node.metadata.get('same_input_output_type', None)

        if same_io_type is True:
            # Same input/output type → transformer (e.g., int → int, str → str)
            return True  # Restore OUTPUT

        # PRIORITY 3: Check if router has no input params (generator pattern)
        # If same_input_output_type is not set at all (not False, but None), it means no input params
        # Generators produce data from nothing, branches should receive the generated OUTPUT
        if same_io_type is None and is_literal is not None:
            # We have type metadata, but no same_input_output_type → no input params
            # This is a generator pattern (e.g., () -> int)
            return True  # Restore OUTPUT (generator)

        # PRIORITY 4: Default to classifier
        # Different types (e.g., int → str) are routing values, not transformations
        return False  # Restore INPUT (classifier)

