from egregore.core.workflow.nodes.async_node import AsyncNode, AsyncBatchNode
from egregore.core.workflow.nodes.node import NodeType
from typing import Optional, List, Any
from egregore.core.workflow.exceptions import ParallelExecutionError, ParallelTimeoutError

import asyncio


class AsyncParallelBatchNode(AsyncBatchNode):
    """
    Processes a batch of items asynchronously and in parallel.
    Subclasses should implement async_execute_item.
    """
    def __init__(self, label: Optional[str] = None, *args, **kwargs):
        super().__init__(label=label or "AsyncParallelBatch", *args, **kwargs)

    async def async_execute(self, *args, **kwargs) -> List[Any]:
        """
        Executes async_execute_item concurrently for all items in the batch.
        """
        items = self.state.get_previous_output() # Default to previous output
        # Allow overriding via direct args
        if args and isinstance(args[0], (list, tuple)):
             items = args[0]
             args = args[1:] # Adjust args for item execution


        if not isinstance(items, (list, tuple)):
            import warnings
            warnings.warn(f"{self.name} received non-iterable input for async parallel batch processing: {type(items)}. Returning empty list.")
            return []

        tasks = []
        for item in items:
             # Create a task for each item execution
             # Pass remaining args/kwargs
             task = asyncio.create_task(self.async_execute_item(item, *args, **kwargs))
             tasks.append(task)

        # Run all tasks concurrently and gather results
        # return_exceptions=True allows the gather to complete even if some tasks fail
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results, potentially logging errors for exceptions
        processed_results = []
        for i, res in enumerate(results):
            if isinstance(res, Exception):
                processed_results.append(None) # Or handle error differently
            else:
                processed_results.append(res)

        return processed_results




class ParallelNode(AsyncNode):
    """Node that executes multiple child nodes in parallel with enhanced features"""

    def __init__(self, *nodes, max_concurrent: Optional[int] = None, timeout: Optional[float] = None, optimization_enabled: bool = True):
        super().__init__(label="Parallel")

        # ParallelNode produces a dictionary of results keyed by terminal node names
        self._produces_data = True

        self.name = f"parallel_{id(self)}"
        self.max_concurrent = max_concurrent
        self.timeout = timeout

        # Plan 10: Resource optimization support
        self.optimization_enabled = optimization_enabled

        # DEFERRED EXECUTION: Store ChainBuilders, not instances
        self.parallel_branches = []  # List[ChainBuilder]

        from egregore.core.workflow.chain_builder import ChainBuilder
        from egregore.core.workflow.nodes.node_types import NodeType

        for node in nodes:
            if isinstance(node, ChainBuilder):
                # Already a ChainBuilder - store directly
                self.parallel_branches.append(node)
            elif isinstance(node, NodeType):
                # NodeType - convert to ChainBuilder
                self.parallel_branches.append(ChainBuilder.from_single(node))
            else:
                # Unknown type - raise error
                raise TypeError(
                    f"Parallel nodes must be NodeType or ChainBuilder. "
                    f"Got: {type(node).__name__}. "
                    f"Use @node decorator or chain nodes with >>"
                )

        # Resource tracking setup
        from egregore.core.workflow.memory_management import get_resource_tracker, get_memory_monitor, ResourceTracker, MemoryMonitor

        self.resource_tracker: ResourceTracker = get_resource_tracker()
        self.memory_monitor: MemoryMonitor = get_memory_monitor()

        # NOTE: Cannot validate unique names until execution time
        # Store branch count for validation later
        self._branch_count = len(self.parallel_branches)
    
    def _validate_unique_names(self, branch_data_list: List[tuple]):
        """Validate that all parallel branches have unique identifiers.

        NOTE: This validation now allows duplicate NODE NAMES because NodeType
        creates fresh instances. Each reference to the same NodeType gets a
        unique GUID. We only validate that we have a terminal node for each branch.

        Args:
            branch_data_list: List of (ChainSpec, Graph) tuples for each branch

        Raises:
            ValueError: If any branch has no terminal node
        """
        for idx, (chain_spec, graph) in enumerate(branch_data_list):
            # Find terminal nodes in the graph (nodes with no outgoing edges)
            terminal_nodes = []
            for node_id, graph_node in graph.nodes.items():
                outgoing = graph.get_outgoing_edges(graph_node)
                if not outgoing:
                    terminal_nodes.append(graph_node)

            # Verify branch has a terminal node
            if not terminal_nodes:
                raise ValueError(
                    f"Parallel branch {idx} has no terminal node. "
                    f"Each branch must have at least one node."
                )
    
    async def _instantiate_branches(self) -> List[tuple]:
        """Instantiate all parallel branches from ChainBuilders.

        This is called at execution time (not build time) to create
        fresh instances and graphs for all branches.

        Returns:
            List of tuples: (ChainSpec, Graph) for each branch
        """
        from egregore.core.workflow.graph import GraphBuilder

        branch_data = []

        for branch_builder in self.parallel_branches:
            # Convert ChainBuilder to ChainSpec
            chain_spec = branch_builder.to_spec()

            # Build a proper graph from the ChainSpec
            # This creates all nodes and edges for the entire chain
            builder = GraphBuilder()
            graph = builder._build_from_chain_spec(chain_spec)

            branch_data.append((chain_spec, graph))

        return branch_data

    def _get_terminal_node_name(self, branch_data):
        """Get the name of the terminal node in a branch.

        Args:
            branch_data: Tuple of (ChainSpec, Graph) for this branch

        Returns:
            str: Name of the terminal node
        """
        chain_spec, graph = branch_data

        # Find terminal nodes in the graph (nodes with no outgoing edges)
        for node_id, graph_node in graph.nodes.items():
            outgoing = graph.get_outgoing_edges(graph_node)
            if not outgoing:
                # Found terminal node
                node_spec = graph_node.node_instance
                return getattr(node_spec, 'node_name', 'unknown')

        # Fallback if no terminal found
        return 'unknown'
    # Plan 10: Resource optimization methods
    def _allocate_resources(self) -> dict:
        """Calculate optimal resource allocation for parallel execution"""
        import os
        
        if not self.optimization_enabled or not self.memory_monitor:
            # Fallback configuration
            return {
                "max_workers": self.max_concurrent or self._branch_count,
                "memory_limit_mb": float('inf'),
                "cpu_limit": os.cpu_count(),
                "batch_size": None
            }
        
        # Get current system state
        try:
            available_memory = self.memory_monitor._get_available_memory()
            if available_memory is None:
                available_memory = 1000.0 * 1024 * 1024  # 1GB in bytes
        except Exception:
            available_memory = 1000.0 * 1024 * 1024  # 1GB fallback in bytes
        
        available_cpu = os.cpu_count()
        
        # Estimate memory per node (can be enhanced with profiling)
        estimated_memory_per_node = 50.0  # MB - conservative estimate
        
        # Calculate optimal workers based on resource constraints
        memory_limited_workers = int(available_memory * 0.7 / estimated_memory_per_node)
        cpu_limited_workers = available_cpu
        resource_limited_workers = min(memory_limited_workers, cpu_limited_workers or memory_limited_workers)
        
        optimal_workers = min(
            self.max_concurrent or self._branch_count,
            self._branch_count,
            max(1, resource_limited_workers)  # At least 1 worker
        )

        # Calculate batch size for load balancing
        batch_size = max(1, self._branch_count // optimal_workers) if optimal_workers > 1 else None
        
        resource_config = {
            "max_workers": optimal_workers,
            "memory_limit_mb": available_memory * 0.8,  # Reserve 20%
            "cpu_limit": available_cpu,
            "batch_size": batch_size
        }
        
        return resource_config
    
    def _create_execution_batches(self, resource_config: dict, branch_data_list: List[tuple]) -> list:
        """Create balanced batches for execution based on resource configuration.

        Args:
            resource_config: Resource allocation configuration
            branch_data_list: List of (ChainSpec, Graph) tuples

        Returns:
            List of batches, where each batch is a list of (ChainSpec, Graph) tuples
        """
        batch_size = resource_config.get("batch_size")

        if not batch_size or batch_size >= len(branch_data_list):
            # Single batch - execute all at once (with semaphore limiting)
            return [branch_data_list]

        # Create multiple batches
        batches = []
        for i in range(0, len(branch_data_list), batch_size):
            batch = branch_data_list[i:i + batch_size]
            batches.append(batch)

        return batches
    
    async def _execute_optimized(self, branch_data_list: List[tuple], *args, **kwargs):
        """Resource-optimized parallel execution.

        Args:
            branch_data_list: List of (ChainSpec, Graph) tuples for each branch

        Returns:
            List of results from each branch (in same order as input)
        """
        # Step 1: Analyze system resources and create configuration
        resource_config = self._allocate_resources()

        # Step 2: Create execution batches based on resource limits
        batches = self._create_execution_batches(resource_config, branch_data_list)

        # Step 3: Execute batches with resource monitoring
        try:
            all_results = []
            for batch_idx, batch in enumerate(batches):
                batch_results = await self._execute_batch(batch, resource_config, *args, **kwargs)
                all_results.extend(batch_results)

            return all_results

        finally:
            # Release any allocated resources
            if self.resource_tracker:
                try:
                    self.resource_tracker.release_resources(self.name or "parallel_node")
                except Exception:
                    pass
    
    async def _execute_batch(self, batch: list, resource_config: dict, *args, **kwargs) -> list:
        """Execute a batch of branches with resource limits.

        Args:
            batch: List of (ChainSpec, Graph) tuples for this batch
            resource_config: Resource allocation configuration

        Returns:
            List of results from each branch in the batch
        """
        import asyncio

        # Create semaphore to limit concurrent execution
        max_workers = min(resource_config["max_workers"], len(batch))
        semaphore = asyncio.Semaphore(max_workers)

        async def execute_with_limit(branch_data):
            async with semaphore:
                # Get terminal node name for tracking (static)
                terminal_name = self._get_terminal_node_name(branch_data)

                if self.resource_tracker:
                    try:
                        with self.resource_tracker.track_execution(terminal_name):
                            result, actual_name = await self._execute_single_branch(branch_data, *args, **kwargs)
                            return (result, actual_name)
                    except Exception:
                        # Fallback if resource tracking fails
                        result, actual_name = await self._execute_single_branch(branch_data, *args, **kwargs)
                        return (result, actual_name)
                else:
                    result, actual_name = await self._execute_single_branch(branch_data, *args, **kwargs)
                    return (result, actual_name)

        # Execute all branches in batch concurrently (but limited by semaphore)
        tasks = [execute_with_limit(branch_data) for branch_data in batch]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results and handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                branch_name = self._get_terminal_node_name(batch[i])
                # Re-raise the exception to maintain existing error handling behavior
                raise ParallelExecutionError(f"Branch '{branch_name}' failed in parallel execution: {result}") from result
            else:
                # Result is now a tuple (value, actual_terminal_name)
                processed_results.append(result)

        return processed_results
    
    async def _execute_single_branch(self, branch_data, *args, **kwargs):
        """Execute a single branch (chain) via graph controller.

        Args:
            branch_data: Tuple of (ChainSpec, Graph) for this branch

        Returns:
            Tuple of (result, actual_terminal_name) where actual_terminal_name
            is the name of the node that actually executed last (important for
            Decision branches where the static terminal is Decision but the
            runtime terminal is the executed branch handler)

        Uses the graph execution infrastructure to properly handle:
        - Multi-node chains (follows next_node connections)
        - State management and data passing
        - Decision nodes and routing
        - All workflow features

        This is the robust long-term solution - leverages existing graph infrastructure.
        """
        from egregore.core.workflow.graph_controller import GraphExecutionController

        chain_spec, graph = branch_data

        # Verify graph has a root node
        if not graph.root_node:
            # Empty branch - return None, None
            return None, 'unknown'

        # Create controller with shared state and workflow controller for hooks
        # Get workflow controller from state if available
        workflow_controller = None
        if self.state and hasattr(self.state, 'workflow') and hasattr(self.state.workflow, 'controller'):
            workflow_controller = self.state.workflow.controller

        controller = GraphExecutionController(
            graph=graph,
            state=self.state,
            workflow_controller=workflow_controller
        )

        # Execute the branch through the graph controller
        # This handles chains, decisions, state, everything properly
        # The controller will automatically instantiate NodeSpec objects from the graph
        input_data = args[0] if args else None
        result = await controller.execute_graph(graph.root_node, input_data)

        # Get the actual terminal node that executed from execution history
        # This is critical for Decision branches where the static graph shows Decision
        # as terminal, but runtime execution goes through a specific branch handler
        actual_terminal_name = self._get_terminal_node_name(branch_data)  # Default fallback

        if controller.execution_history.entries:
            # Get the last executed node from history
            last_entry = controller.execution_history.entries[-1]
            if hasattr(last_entry, 'node') and hasattr(last_entry.node, 'name'):
                actual_terminal_name = last_entry.node.name

        return result, actual_terminal_name
    
    async def async_execute(self, *args, **kwargs):
        """Execute all nodes in parallel with optional optimization"""

        # DEFERRED INSTANTIATION: Build graphs for all branches
        branch_data = await self._instantiate_branches()

        # Validate unique names after graph building
        self._validate_unique_names(branch_data)

        # Plan 10: Route to optimized execution if enabled
        if self.optimization_enabled:
            return await self._execute_optimized_with_state_handling(branch_data, *args, **kwargs)
        else:
            return await self._execute_basic(branch_data, *args, **kwargs)
    
    async def _execute_optimized_with_state_handling(self, branch_data_list: List[tuple], *args, **kwargs):
        """Wrapper for optimized execution with state change notifications.

        Args:
            branch_data_list: List of (ChainSpec, Graph) tuples for each branch

        Returns:
            Dictionary mapping terminal node names to their results
        """
        # Extract terminal names for notifications
        terminal_names = [self._get_terminal_node_name(bd) for bd in branch_data_list]

        # Notify start of parallel execution
        if hasattr(self.state, '_notify_state_change'):
            self.state._notify_state_change('parallel_start', self.name, {
                'node_count': len(branch_data_list),
                'node_names': terminal_names,
                'max_concurrent': self.max_concurrent,
                'timeout': self.timeout,
                'optimization_enabled': True
            })

        try:
            # Use optimized execution
            results = await self._execute_optimized(branch_data_list, *args, **kwargs)

            # Process and store results in state (maintaining compatibility) - return as dictionary
            # Handle duplicate terminal node names by storing results as lists
            # Results are now tuples of (value, actual_terminal_name)
            final_results = {}
            for i, result_tuple in enumerate(results):
                # Unpack tuple: (result_value, actual_terminal_name)
                result_value, actual_terminal_name = result_tuple

                # If duplicate key, convert to list or append to existing list
                if actual_terminal_name in final_results:
                    # Key already exists
                    if isinstance(final_results[actual_terminal_name], list):
                        # Already a list, append
                        final_results[actual_terminal_name].append(result_value)
                    else:
                        # First duplicate - convert to list
                        final_results[actual_terminal_name] = [final_results[actual_terminal_name], result_value]
                else:
                    # First occurrence - store directly
                    final_results[actual_terminal_name] = result_value

                # Store result by terminal node name (Phase 2: enhanced storage)
                # For state storage, use the same logic
                if actual_terminal_name in self.state:
                    # Duplicate - convert to list
                    if isinstance(self.state[actual_terminal_name], list):
                        self.state[actual_terminal_name].append(result_value)
                    else:
                        self.state[actual_terminal_name] = [self.state[actual_terminal_name], result_value]
                else:
                    self.state[actual_terminal_name] = result_value

                # NEW: Plan 20 - Store child node execution in state.executions for workflow_state() access
                from egregore.core.workflow.state import NodeOutput
                child_execution = NodeOutput(name=actual_terminal_name)
                child_execution.execute = result_value
                self.state.executions.append(child_execution)

                # Notify observers of completion
                if hasattr(self.state, '_notify_state_change'):
                    self.state._notify_state_change('parallel_node_complete', actual_terminal_name, result_value)

            # Notify completion of parallel block
            if hasattr(self.state, '_notify_state_change'):
                self.state._notify_state_change('parallel_complete', self.name, {
                    'results': final_results,
                    'node_names': terminal_names,
                    'optimization_enabled': True
                })

            return final_results

        except Exception as e:
            # Handle timeout and other errors
            if hasattr(self.state, '_notify_state_change'):
                self.state._notify_state_change('parallel_error', self.name, {
                    'error': str(e),
                    'optimization_enabled': True
                })
            raise
    
    async def _execute_basic(self, branch_data_list: List[tuple], *args, **kwargs):
        """Basic parallel execution without optimization.

        Args:
            branch_data_list: List of (ChainSpec, Graph) tuples for each branch

        Returns:
            Dictionary mapping terminal node names to their results
        """
        # Extract terminal names for notifications
        terminal_names = [self._get_terminal_node_name(bd) for bd in branch_data_list]

        # Notify start of parallel execution
        if hasattr(self.state, '_notify_state_change'):
            self.state._notify_state_change('parallel_start', self.name, {
                'node_count': len(branch_data_list),
                'node_names': terminal_names,
                'max_concurrent': self.max_concurrent,
                'timeout': self.timeout,
                'optimization_enabled': False
            })

        try:
            # Create semaphore for concurrency control
            semaphore = asyncio.Semaphore(self.max_concurrent or len(branch_data_list))

            async def execute_with_semaphore(branch_data):
                async with semaphore:
                    result, actual_name = await self._execute_single_branch(branch_data, *args, **kwargs)
                    return (result, actual_name)

            # Create tasks for all branches
            tasks = [execute_with_semaphore(bd) for bd in branch_data_list]

            # Execute with timeout if specified
            if self.timeout:
                results = await asyncio.wait_for(
                    asyncio.gather(*tasks, return_exceptions=True),
                    timeout=self.timeout
                )
            else:
                results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results and handle errors - return as dictionary
            # Handle duplicate terminal node names by storing results as lists
            # Results are now tuples of (value, actual_terminal_name)
            final_results = {}
            for i, result_tuple in enumerate(results):
                if isinstance(result_tuple, Exception):
                    # Get static terminal name for error reporting
                    branch_data = branch_data_list[i]
                    terminal_node_name = self._get_terminal_node_name(branch_data)

                    error_info = {
                        'node': terminal_node_name,
                        'error': str(result_tuple),
                        'error_type': type(result_tuple).__name__
                    }

                    # Notify observers of error
                    if hasattr(self.state, '_notify_state_change'):
                        self.state._notify_state_change('parallel_node_error', terminal_node_name, error_info)

                    # Re-raise with context
                    raise ParallelExecutionError(
                        f"Branch '{terminal_node_name}' failed in parallel execution: {result_tuple}"
                    ) from result_tuple
                else:
                    # Unpack tuple: (result_value, actual_terminal_name)
                    result_value, actual_terminal_name = result_tuple

                    # If duplicate key, convert to list or append to existing list
                    if actual_terminal_name in final_results:
                        # Key already exists
                        if isinstance(final_results[actual_terminal_name], list):
                            # Already a list, append
                            final_results[actual_terminal_name].append(result_value)
                        else:
                            # First duplicate - convert to list
                            final_results[actual_terminal_name] = [final_results[actual_terminal_name], result_value]
                    else:
                        # First occurrence - store directly
                        final_results[actual_terminal_name] = result_value

                    # Store result by terminal node name (Phase 2: enhanced storage)
                    # For state storage, use the same logic
                    if actual_terminal_name in self.state:
                        # Duplicate - convert to list
                        if isinstance(self.state[actual_terminal_name], list):
                            self.state[actual_terminal_name].append(result_value)
                        else:
                            self.state[actual_terminal_name] = [self.state[actual_terminal_name], result_value]
                    else:
                        self.state[actual_terminal_name] = result_value

                    # NEW: Plan 20 - Store child node execution in state.executions for workflow_state() access
                    from egregore.core.workflow.state import NodeOutput
                    child_execution = NodeOutput(name=actual_terminal_name)
                    child_execution.execute = result_value
                    self.state.executions.append(child_execution)

                    # Notify observers of completion
                    if hasattr(self.state, '_notify_state_change'):
                        self.state._notify_state_change('parallel_node_complete', actual_terminal_name, result_value)

            # Notify completion of parallel block
            if hasattr(self.state, '_notify_state_change'):
                self.state._notify_state_change('parallel_complete', self.name, {
                    'results': final_results,
                    'node_names': terminal_names
                })

            return final_results

        except asyncio.TimeoutError:
            timeout_error = ParallelTimeoutError(
                f"Parallel execution timed out after {self.timeout} seconds"
            )

            # Notify observers of timeout
            if hasattr(self.state, '_notify_state_change'):
                self.state._notify_state_change('parallel_timeout', self.name, {
                    'timeout': self.timeout,
                    'node_names': terminal_names
                })

            raise timeout_error

    def execute(self, *args, **kwargs):
        """Sync wrapper for async execution"""
        return asyncio.run(self.async_execute(*args, **kwargs))

    def __rshift__(self, other):
        """Chain parallel node with another node using ChainBuilder pattern.

        This overrides BaseNode.__rshift__ to support deferred execution architecture.
        Instead of setting next_node in place, it creates a ChainBuilder for graph building.

        Args:
            other: Next node (NodeType, ChainBuilder, or BaseNode)

        Returns:
            ChainBuilder with self and other combined
        """
        from egregore.core.workflow.chain_builder import ChainBuilder
        from egregore.core.workflow.nodes.node_types import NodeType

        # Convert self to ChainBuilder (wrap as BaseNode instance)
        left_builder = ChainBuilder(
            node_types=[self],
            edges=[],
            alias_map={}
        )

        # Convert other to ChainBuilder based on type
        if isinstance(other, NodeType):
            right_builder = ChainBuilder.from_single(other)
        elif isinstance(other, ChainBuilder):
            right_builder = other
        else:
            # Another BaseNode instance - wrap it
            right_builder = ChainBuilder(
                node_types=[other],
                edges=[],
                alias_map={}
            )

        # Combine via ChainBuilder.from_chain
        return ChainBuilder.from_chain(left_builder, right_builder)




def parallel(*nodes, max_concurrent: Optional[int] = None, timeout: Optional[float] = None) -> ParallelNode:
    """
    Create a parallel execution node
    
    Args:
        *nodes: Variable number of nodes to execute in parallel
        max_concurrent: Maximum number of concurrent executions (optional)
        timeout: Timeout in seconds for parallel block (optional)
        
    Returns:
        ParallelNode: Node that executes all children in parallel
    
    Example:
        # Basic parallel execution
        workflow = Sequence(
            load_data >>
            parallel(
                clean_data,
                validate_schema,
                extract_features
            ) >>
            process_results
        
        # With concurrency limit and timeout
        parallel_node = parallel(
            node1, node2, node3,
            max_concurrent=2,
            timeout=30.0
    """
    return ParallelNode(*nodes, max_concurrent=max_concurrent, timeout=timeout)

