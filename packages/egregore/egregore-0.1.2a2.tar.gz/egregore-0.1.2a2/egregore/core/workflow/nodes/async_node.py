from egregore.core.workflow.nodes.node import Node
from typing import Optional, Any, List
import asyncio
import warnings
from egregore.core.workflow.nodes.node import BatchNode

class AsyncNode(Node):
    """
    A node that performs its operations asynchronously.
    Subclasses should implement async_execute and optionally others.
    Requires an async-aware sequence runner.
    """
    def __init__(self, label: Optional[str] = None, max_retries: int = 0, retry_wait: float = 0.5, *args, **kwargs):
        super().__init__(label=label or "Async", *args, **kwargs)
        self.max_retries = max_retries
        self.retry_wait = retry_wait
        # Indicate that standard run won't work
        self._is_async = True


    async def async_execute(self, *args, **kwargs) -> Any:
        """Asynchronous execution with native agent discovery."""
        # Import here to avoid circular imports
        from egregore.core.workflow.agent_interceptor import workflow_node_context
        from egregore.core.workflow.agent_discovery import get_agent_registry
        
        # Always execute within discovery context
        with workflow_node_context(self.name):
            try:
                # Notify that node execution is starting
                registry = get_agent_registry()
                registry._notify_observers("node_execution_started", self.name, {
                    "node": self,
                    "args": str(args)[:100] if args else "",
                    "kwargs": {k: str(v)[:50] for k, v in kwargs.items()}
                })
                
                # Call the actual async implementation
                result = await self._async_execute_impl(*args, **kwargs)
                
                # Notify completion
                registry._notify_observers("node_execution_completed", self.name, {
                    "node": self,
                    "result": str(result)[:100] if result else None
                })
                
                return result
                
            except Exception as e:
                # Notify error
                get_agent_registry()._notify_observers("node_execution_failed", self.name, {
                    "node": self,
                    "error": str(e)
                })
                raise
    
    async def _async_execute_impl(self, *args, **kwargs) -> Any:
        """Asynchronous core execution logic - implement in subclasses."""
        raise NotImplementedError(f"_async_execute_impl is not implemented for {self.name}")
        
    # Lifecycle methods removed in Plan 16: Lifecycle Simplification
    # Use separate nodes for setup/cleanup instead

    async def async_execute_fallback(self, error: Exception, *args, **kwargs) -> Any:
        """Asynchronous logic to run if all retries fail."""
        raise error # Default is to re-raise the last error


    async def async_run(self, *args, **kwargs) -> Any:
        """Orchestrates the async execution lifecycle."""
        exec_result = None
        last_error = None
        
        # Simple retry logic for backward compatibility
        for attempt in range(self.max_retries + 1):
            try:
                exec_result = await self.async_execute(*args, **kwargs)
                self.state.current.execute = exec_result
                last_error = None  # Success
                break
            except Exception as e:
                last_error = e
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_wait)
                else:
                    break

        # If we still have an error after all attempts, try fallback
        if last_error:
            try:
                exec_result = await self.async_execute_fallback(last_error, *args, **kwargs)
                self.state.current.execute = exec_result
                last_error = None  # Fallback succeeded
            except Exception:
                # Fallback also failed - re-raise original error
                raise last_error

        return exec_result


    # Override synchronous methods to prevent accidental use
    def execute(self, *args, **kwargs):
         raise RuntimeError(f"{self.name} is an AsyncNode. Use an async runner and async_execute.")
         
    # Lifecycle methods removed in Plan 16: Lifecycle Simplification
    # Use separate nodes for setup/cleanup instead

    def run(self):
         raise RuntimeError(f"{self.name} is an AsyncNode and requires an async-compatible sequence runner (e.g., calling async_run).")



class AsyncBatchNode(AsyncNode, BatchNode):
    """
    Processes a batch of items asynchronously, one after another.
    Subclasses should implement async_execute_item.
    """
    def __init__(self, label: Optional[str] = None, *args, **kwargs):
        # Combine initializers, prioritize AsyncNode for retry logic etc.
        AsyncNode.__init__(self, label=label or "AsyncBatch", *args, **kwargs)
        # BatchNode init logic is mainly naming, covered by AsyncNode's super call chain.

    async def async_execute_item(self, item: Any, *args, **kwargs) -> Any:
        """Process a single item from the batch asynchronously."""
        raise NotImplementedError(f"async_execute_item is not implemented for {self.name}")

    async def async_execute(self, *args, **kwargs) -> List[Any]:
        """
        Executes async_execute_item sequentially for each item in the batch.
        """
        items = self.state.get_previous_output() # Default to previous output
        # Allow overriding via direct args
        if args and isinstance(args[0], (list, tuple)):
             items = args[0]
             args = args[1:] # Adjust args for item execution


        if not isinstance(items, (list, tuple)):
            warnings.warn(f"{self.name} received non-iterable input for async batch processing: {type(items)}. Returning empty list.")
            return []

        results = []
        for item in items:
            try:
                 # Pass remaining args/kwargs
                result = await self.async_execute_item(item, *args, **kwargs)
                results.append(result)
            except Exception as e:
                results.append(None) # Or handle error differently
        return results

    # Need to override the sync _execute_item from BatchNode
    def _execute_item(self, item: Any, *args, **kwargs) -> Any:
        raise RuntimeError(f"{self.name} uses async_execute_item.")

