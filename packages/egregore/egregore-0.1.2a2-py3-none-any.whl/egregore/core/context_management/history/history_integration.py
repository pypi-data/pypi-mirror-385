"""
ContextHistory Integration Utilities

Helper functions and mixins for integrating ContextHistory with other V2 components.
Provides easy integration patterns for MessageScheduler, ToolExecutor, and Provider systems.
"""

from typing import Optional, Protocol, Any, List
from datetime import datetime

from .context_history import ContextHistory
from ..pact.context import Context
from ...tool_calling.tool_execution_group import ToolExecutionGroup, ToolExecution
from ...messaging import ProviderToolCall
from ...tool_calling.context_components import ToolResult


class HistoryAware(Protocol):
    """Protocol for components that are aware of ContextHistory"""
    
    context_history: Optional[ContextHistory]
    
    def set_context_history(self, history: ContextHistory) -> None:
        """Set the context history for this component"""
        ...


class ContextHistoryIntegration:
    """Mixin class for components that need ContextHistory integration"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.context_history: Optional[ContextHistory] = None
    
    def set_context_history(self, history: ContextHistory) -> None:
        """Set the context history for this component"""
        self.context_history = history
    
    def _create_snapshot_if_available(self, context: Context, trigger: str, **metadata) -> Optional[str]:
        """Create snapshot if context history is available
        
        Args:
            context: Context to snapshot
            trigger: What triggered this snapshot
            **metadata: Additional metadata
            
        Returns:
            Snapshot ID if created, None if no history available
        """
        if self.context_history:
            return self.context_history.create_snapshot(context, trigger, **metadata)
        return None
    
    def _add_execution_group_if_available(self, group: ToolExecutionGroup, snapshot_id: str) -> None:
        """Add execution group if context history is available
        
        Args:
            group: ToolExecutionGroup to add
            snapshot_id: ID of snapshot that triggered this execution
        """
        if self.context_history:
            self.context_history.add_execution_group(group, snapshot_id)


def create_tool_execution_group(
    tool_calls: List[ProviderToolCall],
    results: List[ToolResult],
    cycle_id: str,
    snapshot_id: str,
    provider_name: Optional[str] = None
) -> ToolExecutionGroup:
    """Create a ToolExecutionGroup from tool calls and results
    
    Args:
        tool_calls: List of tool calls made by provider
        results: List of tool execution results
        cycle_id: Message cycle/turn identifier
        snapshot_id: ID of snapshot that triggered execution
        provider_name: Name of provider that made the calls
        
    Returns:
        ToolExecutionGroup with all executions
    """
    group_id = f"group_{cycle_id}_{int(datetime.now().timestamp())}"
    
    group = ToolExecutionGroup(
        id=group_id,
        cycle_id=cycle_id,
        snapshot_id=snapshot_id,
        provider_name=provider_name,
        completed_at=None,
        total_duration_ms=None,
        context_size_before=None,  # Can be set by caller
        context_size_after=None,   # Can be set by caller
    )
    
    # Pair tool calls with results
    for i, tool_call in enumerate(tool_calls):
        result = results[i] if i < len(results) else None
        
        execution = ToolExecution(
            tool_call=tool_call,
            result=result,
            scaffold_result=None,
            tool_name=tool_call.tool_name,
            tool_call_id=tool_call.tool_call_id,
            execution_time=(result.execution_time if (result and result.execution_time) else datetime.now()),
            duration_ms=None,  # Can be calculated if timing data available
            error=None if result and result.success else "Execution failed"
        )
        
        group.add_execution(execution)
    
    group.mark_completed()
    return group


def track_provider_call(
    history: ContextHistory,
    context: Context,
    provider_name: str,
    turn_id: Optional[str] = None
) -> str:
    """Track a provider call by creating a snapshot
    
    Args:
        history: ContextHistory to add snapshot to
        context: Context being sent to provider
        provider_name: Name of provider being called
        turn_id: Optional turn identifier
        
    Returns:
        Snapshot ID
    """
    if turn_id is None:
        turn_id = f"turn_{getattr(context, 'cadence', 0)}"
    
    return history.create_snapshot(
        context=context,
        trigger="before_provider_call",
        turn_id=turn_id,
        provider_name=provider_name
    )


def track_tool_execution(
    history: ContextHistory,
    tool_calls: List[ProviderToolCall],
    results: List[ToolResult],
    snapshot_id: str,
    cycle_id: str,
    provider_name: Optional[str] = None
) -> None:
    """Track tool execution by creating and adding ToolExecutionGroup
    
    Args:
        history: ContextHistory to add execution group to
        tool_calls: List of tool calls made
        results: List of execution results
        snapshot_id: ID of snapshot that triggered execution
        cycle_id: Message cycle identifier
        provider_name: Name of provider that made the calls
    """
    group = create_tool_execution_group(
        tool_calls=tool_calls,
        results=results,
        cycle_id=cycle_id,
        snapshot_id=snapshot_id,
        provider_name=provider_name
    )
    
    history.add_execution_group(group, snapshot_id)


class MessageSchedulerIntegration(ContextHistoryIntegration):
    """Integration for MessageScheduler with ContextHistory"""
    
    def rebuild_context_with_snapshot(self, context: Context, *inputs, turn_id: Optional[str] = None) -> Optional[str]:
        """Rebuild context and create snapshot before provider call
        
        Args:
            context: Context to rebuild
            *inputs: Input messages/data
            turn_id: Optional turn identifier
            
        Returns:
            Snapshot ID if history available, None otherwise
        """
        # First rebuild the context (call the original method)
        if hasattr(super(), 'rebuild_context'):
            super().rebuild_context(context, *inputs)  # type: ignore
        
        # Then create snapshot for provider call
        if turn_id is None:
            turn_id = f"turn_{getattr(context, 'cadence', 0)}"
        
        return self._create_snapshot_if_available(
            context=context,
            trigger="after_context_rebuild",
            turn_id=turn_id
        )


class ToolExecutorIntegration(ContextHistoryIntegration):
    """Integration for ToolExecutor with ContextHistory"""
    
    def execute_tools_with_tracking(
        self,
        tool_calls: List[ProviderToolCall],
        cycle_id: str,
        snapshot_id: Optional[str] = None,
        provider_name: Optional[str] = None
    ) -> List[ToolResult]:
        """Execute tools and track execution in history
        
        Args:
            tool_calls: List of tool calls to execute
            cycle_id: Message cycle identifier
            snapshot_id: Optional snapshot ID that triggered execution
            provider_name: Optional provider name
            
        Returns:
            List of tool execution results
        """
        results = []
        
        # Execute each tool call
        for tool_call in tool_calls:
            # Execute the tool (call the original method)
            if hasattr(self, 'execute_tool'):
                result = self.execute_tool(tool_call)  # type: ignore
                if isinstance(result, ToolResult):
                    results.append(result)
        
        # Track execution if history is available and we have a snapshot
        if self.context_history and snapshot_id and results:
            track_tool_execution(
                history=self.context_history,
                tool_calls=tool_calls,
                results=results,
                snapshot_id=snapshot_id,
                cycle_id=cycle_id,
                provider_name=provider_name
            )
        
        return results


def integrate_with_history(component: Any, history: ContextHistory) -> None:
    """Integrate a component with ContextHistory
    
    Args:
        component: Component to integrate (must implement HistoryAware protocol)
        history: ContextHistory to integrate with
    """
    if hasattr(component, 'set_context_history'):
        component.set_context_history(history)
    else:
        # Fallback: set attribute directly
        component.context_history = history


def create_history_aware_component(component_class: type, history: ContextHistory, *args, **kwargs) -> Any:
    """Create a component instance that is integrated with ContextHistory
    
    Args:
        component_class: Class to instantiate
        history: ContextHistory to integrate with
        *args: Arguments for component constructor
        **kwargs: Keyword arguments for component constructor
        
    Returns:
        Component instance integrated with history
    """
    component = component_class(*args, **kwargs)
    integrate_with_history(component, history)
    return component