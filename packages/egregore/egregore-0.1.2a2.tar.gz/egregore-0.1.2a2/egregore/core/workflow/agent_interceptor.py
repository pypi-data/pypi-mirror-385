"""
Agent Creation Interception for Native Discovery

Automatically registers agents created within workflow nodes for pipeline-level
discovery and control. Provides transparent agent tracking without code changes.
"""

import inspect
from contextlib import contextmanager
from typing import Any, Optional, Dict, Callable
from functools import wraps
import threading

from .agent_discovery import get_agent_registry


# Thread-local storage for current workflow context
_workflow_context = threading.local()


@contextmanager
def workflow_node_context(node_name: str):
    """
    Context manager to track which workflow node is currently executing.
    
    Args:
        node_name: Name of the executing workflow node
    """
    # Store previous context
    prev_node = getattr(_workflow_context, 'current_node', None)
    
    # Set current node
    _workflow_context.current_node = node_name
    
    try:
        yield
    finally:
        # Restore previous context
        _workflow_context.current_node = prev_node


def get_current_node() -> Optional[str]:
    """Get the name of the currently executing workflow node"""
    return getattr(_workflow_context, 'current_node', None)


def intercept_agent_creation(original_agent_class):
    """
    Decorator to intercept Agent class instantiation for automatic registration.
    
    This enables transparent agent discovery - any Agent created within a workflow
    node context will automatically be registered for pipeline-level control.
    """
    
    original_init = original_agent_class.__init__
    
    @wraps(original_init)
    def intercepted_init(self, *args, **kwargs):
        # Call original initialization
        original_init(self, *args, **kwargs)
        
        # Auto-register if we're in a workflow context
        current_node = get_current_node()
        if current_node:
            # Get caller context for additional metadata
            frame = inspect.currentframe()
            caller_info = {}
            
            try:
                if frame and frame.f_back:
                    caller_frame = frame.f_back
                    caller_info = {
                        'filename': caller_frame.f_code.co_filename,
                        'line_number': caller_frame.f_lineno,
                        'function': caller_frame.f_code.co_name
                    }
            except Exception:
                # Don't let inspection errors break agent creation
                pass
            finally:
                del frame  # Prevent reference cycles
            
            # Register the agent with discovery system
            context = {
                'creation_args': args,
                'creation_kwargs': {k: str(v) for k, v in kwargs.items()},  # Stringify for safety
                'caller_info': caller_info
            }
            
            get_agent_registry().register_agent(self, current_node, context)
    
    # Replace the __init__ method
    original_agent_class.__init__ = intercepted_init
    
    return original_agent_class


class WorkflowAgentManager:
    """
    Workflow-level agent management providing dual control capabilities.
    
    Enables pipeline to discover, monitor, and control agents created inside nodes.
    """
    
    def __init__(self, workflow_name: str):
        self.workflow_name = workflow_name
        self.registry = get_agent_registry()
        
        # Add observer for agent lifecycle events
        self.registry.add_observer(self._handle_agent_event)
        
    def _handle_agent_event(self, event: str, agent_id: str, data: Dict[str, Any]):
        """Handle agent lifecycle events"""
        # This can be extended for custom workflow policies
        pass
    
    def get_all_agents(self) -> Dict[str, Any]:
        """Get all agents discovered in this workflow"""
        return self.registry.get_discovered_agents()
    
    def get_agents_in_node(self, node_name: str) -> Dict[str, Any]:
        """Get agents created within a specific node"""
        return self.registry.get_discovered_agents(node_name)
    
    def interrupt_all_agents(self):
        """Interrupt all discovered agents (dual control feature)"""
        agents = self.get_all_agents()
        
        for agent_id, agent in agents.items():
            if hasattr(agent, 'interrupt'):
                try:
                    agent.interrupt()
                    self.registry.update_agent_state(agent_id, "interrupted")
                except Exception as e:
                    # Log but don't fail the entire operation
                    import logging
                    logging.error(f"Failed to interrupt agent {agent_id}: {e}")
    
    def interrupt_node_agents(self, node_name: str):
        """Interrupt all agents within a specific node"""
        agents = self.get_agents_in_node(node_name)
        
        for agent_id, agent in agents.items():
            if hasattr(agent, 'interrupt'):
                try:
                    agent.interrupt()
                    self.registry.update_agent_state(agent_id, "interrupted")
                except Exception as e:
                    import logging
                    logging.error(f"Failed to interrupt agent {agent_id} in node {node_name}: {e}")
    
    def get_agent_states(self) -> Dict[str, str]:
        """Get current states of all discovered agents"""
        agents = self.get_all_agents()
        states = {}
        
        for agent_id in agents.keys():
            metadata = self.registry.get_agent_metadata(agent_id)
            if metadata:
                states[agent_id] = metadata.lifecycle_state
        
        return states
    
    def apply_policy_to_agents(self, policy_func: Callable[[str, Any], None]) -> None:
        """
        Apply cross-cutting policies to all discovered agents.
        
        Args:
            policy_func: Function that takes (agent_id, agent) and applies policy
        """
        agents = self.get_all_agents()
        
        for agent_id, agent in agents.items():
            try:
                policy_func(agent_id, agent)
            except Exception as e:
                import logging
                logging.error(f"Policy application failed for agent {agent_id}: {e}")
    
    def get_pipeline_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary of agent discovery in this workflow"""
        base_summary = self.registry.get_pipeline_summary()
        base_summary['workflow_name'] = self.workflow_name
        return base_summary


# Convenience function to create workflow agent manager
def create_agent_manager(workflow_name: str) -> WorkflowAgentManager:
    """Create a workflow agent manager for dual control"""
    return WorkflowAgentManager(workflow_name)