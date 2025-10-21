"""
Native Discovery Integration

Provides workflow-level agent discovery that's always enabled by default.
This makes agent discovery a core workflow feature rather than an optional add-on.
"""

from typing import Dict, Any, Optional, List, Callable
from .agent_discovery import get_agent_registry, AgentDiscoveryRegistry
from .agent_interceptor import create_agent_manager, WorkflowAgentManager
import threading
import uuid


class GlobalWorkflowManager:
    """
    Global manager for workflow-level agent discovery.
    
    Tracks all workflows and provides cross-workflow agent management capabilities.
    Always enabled - no need for explicit discovery activation.
    """
    
    def __init__(self):
        self.workflows: Dict[str, WorkflowAgentManager] = {}
        self.current_workflow: Optional[str] = None
        self._lock = threading.RLock()
        self._thread_local = threading.local()
        
    def get_or_create_workflow_manager(self, workflow_name: Optional[str] = None) -> WorkflowAgentManager:
        """
        Get or create a workflow manager for the current context.
        
        Args:
            workflow_name: Optional workflow name, auto-generated if None
            
        Returns:
            WorkflowAgentManager for the workflow
        """
        with self._lock:
            # Use thread-local storage to track current workflow
            current_workflow_name = getattr(self._thread_local, 'workflow_name', None)
            
            if not current_workflow_name:
                # Auto-generate workflow name if none provided
                if not workflow_name:
                    workflow_name = f"workflow_{uuid.uuid4().hex[:8]}"
                
                current_workflow_name = workflow_name
                self._thread_local.workflow_name = current_workflow_name
            
            # Get or create workflow manager
            if current_workflow_name not in self.workflows:
                self.workflows[current_workflow_name] = create_agent_manager(current_workflow_name)
            
            return self.workflows[current_workflow_name]
    
    def set_current_workflow(self, workflow_name: str):
        """Set the current workflow context"""
        with self._lock:
            self._thread_local.workflow_name = workflow_name
    
    def get_current_workflow_manager(self) -> Optional[WorkflowAgentManager]:
        """Get the current workflow manager"""
        current_workflow_name = getattr(self._thread_local, 'workflow_name', None)
        if current_workflow_name:
            return self.workflows.get(current_workflow_name)
        return None
    
    def get_all_discovered_agents(self) -> Dict[str, Any]:
        """Get all agents discovered across all workflows"""
        return get_agent_registry().get_discovered_agents()
    
    def get_workflow_agents(self, workflow_name: str) -> Dict[str, Any]:
        """Get agents discovered in a specific workflow"""
        if workflow_name in self.workflows:
            return self.workflows[workflow_name].get_all_agents()
        return {}
    
    def interrupt_all_workflows(self):
        """Interrupt all agents across all workflows"""
        for manager in self.workflows.values():
            manager.interrupt_all_agents()
    
    def get_global_summary(self) -> Dict[str, Any]:
        """Get summary of all workflows and discovered agents"""
        base_summary = get_agent_registry().get_pipeline_summary()
        
        workflow_summaries = {}
        for name, manager in self.workflows.items():
            workflow_summaries[name] = manager.get_pipeline_summary()
        
        return {
            "global_agent_discovery": base_summary,
            "workflows": workflow_summaries,
            "total_workflows": len(self.workflows)
        }


# Global instance
_global_workflow_manager = GlobalWorkflowManager()


def get_workflow_manager() -> GlobalWorkflowManager:
    """Get the global workflow manager"""
    return _global_workflow_manager


def get_current_agents() -> Dict[str, Any]:
    """
    Get agents discovered in the current workflow context.
    
    This is the main API for accessing discovered agents - always available,
    no need to explicitly enable discovery.
    """
    manager = _global_workflow_manager.get_current_workflow_manager()
    if manager:
        return manager.get_all_agents()
    return {}


def get_current_agent_states() -> Dict[str, str]:
    """
    Get states of agents in the current workflow context.
    
    Returns:
        Dictionary of agent_id -> state
    """
    manager = _global_workflow_manager.get_current_workflow_manager()
    if manager:
        return manager.get_agent_states()
    return {}


def interrupt_current_agents():
    """
    Interrupt all agents in the current workflow.
    
    This provides immediate access to dual control - no setup required.
    """
    manager = _global_workflow_manager.get_current_workflow_manager()
    if manager:
        manager.interrupt_all_agents()


def apply_policy_to_current_agents(policy_func: Callable[[str, Any], None]) -> None:
    """
    Apply cross-cutting policy to all agents in current workflow.
    
    Args:
        policy_func: Function that takes (agent_id, agent) and applies policy
    """
    manager = _global_workflow_manager.get_current_workflow_manager()
    if manager:
        manager.apply_policy_to_agents(policy_func)


def get_agents_in_node(node_name: str) -> Dict[str, Any]:
    """
    Get agents created within a specific node in the current workflow.
    
    Args:
        node_name: Name of the workflow node
        
    Returns:
        Dictionary of agent_id -> agent instance
    """
    manager = _global_workflow_manager.get_current_workflow_manager()
    if manager:
        return manager.get_agents_in_node(node_name)
    return {}


def monitor_current_workflow(callback: Callable[[str, str, Dict[str, Any]], None]) -> None:
    """
    Add monitoring callback for the current workflow's agent lifecycle events.
    
    Args:
        callback: Function called with (event, agent_id, data)
    """
    manager = _global_workflow_manager.get_current_workflow_manager()
    if manager:
        manager.registry.add_observer(callback)


# Workflow context manager for explicit workflow naming
class workflow_context:
    """
    Context manager for explicitly naming workflows.
    
    Usage:
        with workflow_context("data_processing"):
            workflow = Sequence(load_data >> process >> save)
            result = workflow.execute(data)
            
            # Agent discovery is automatic
            agents = get_current_agents()
    """
    
    def __init__(self, workflow_name: str):
        self.workflow_name = workflow_name
        self.previous_workflow = None
        
    def __enter__(self):
        # Store previous workflow context
        current_manager = _global_workflow_manager.get_current_workflow_manager()
        if current_manager:
            self.previous_workflow = current_manager.workflow_name
        
        # Set new workflow context
        _global_workflow_manager.set_current_workflow(self.workflow_name)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore previous workflow context
        if self.previous_workflow:
            _global_workflow_manager.set_current_workflow(self.previous_workflow)


# Auto-initialize global workflow context
def _auto_initialize_workflow():
    """Auto-initialize a workflow context if none exists"""
    if not _global_workflow_manager.get_current_workflow_manager():
        _global_workflow_manager.get_or_create_workflow_manager()


# Export main API functions
__all__ = [
    'get_current_agents',
    'get_current_agent_states', 
    'interrupt_current_agents',
    'apply_policy_to_current_agents',
    'get_agents_in_node',
    'monitor_current_workflow',
    'workflow_context',
    'get_workflow_manager'
]