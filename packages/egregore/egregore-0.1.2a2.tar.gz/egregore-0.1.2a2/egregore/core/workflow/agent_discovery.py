"""
Native Agent Discovery System for V2 Workflows

Provides pipeline-level agent introspection and dual control capabilities.
Enables workflows to discover, monitor, and control agents created inside nodes.
"""

import weakref
from typing import Dict, List, Set, Optional, Any, Callable
from dataclasses import dataclass, field
from threading import RLock
import logging

logger = logging.getLogger(__name__)


@dataclass
class AgentMetadata:
    """Metadata about a discovered agent"""
    agent_id: str
    node_name: Optional[str] = None
    creation_context: Dict[str, Any] = field(default_factory=dict)
    lifecycle_state: str = "created"  # created, active, completed, error, interrupted
    performance_metrics: Dict[str, Any] = field(default_factory=dict)


class AgentDiscoveryRegistry:
    """
    Global registry for tracking agents across workflow execution.
    
    Provides pipeline-level introspection and control over agents created
    inside workflow nodes, enabling the V2 breakthrough dual control feature.
    """
    
    def __init__(self):
        self._agents: Dict[str, Any] = {}  # agent_id -> agent (weak references)
        self._metadata: Dict[str, AgentMetadata] = {}  # agent_id -> metadata
        self._node_agents: Dict[str, Set[str]] = {}  # node_name -> set of agent_ids
        self._observers: List[Callable] = []  # Agent lifecycle observers
        self._lock = RLock()
        
    def register_agent(self, agent: Any, node_name: Optional[str] = None, 
                      context: Optional[Dict[str, Any]] = None) -> str:
        """
        Register an agent for discovery and tracking.
        
        Args:
            agent: The agent instance to register
            node_name: Optional name of the node creating the agent
            context: Additional context about agent creation
            
        Returns:
            Agent ID for tracking
        """
        with self._lock:
            agent_id = getattr(agent, 'agent_id', None) or f"agent_{id(agent)}"
            
            # Store weak reference to avoid circular dependencies
            self._agents[agent_id] = weakref.ref(agent, self._cleanup_agent(agent_id))
            
            # Store metadata
            self._metadata[agent_id] = AgentMetadata(
                agent_id=agent_id,
                node_name=node_name,
                creation_context=context or {},
                lifecycle_state="created"
            )
            
            # Track node-agent relationships
            if node_name:
                if node_name not in self._node_agents:
                    self._node_agents[node_name] = set()
                self._node_agents[node_name].add(agent_id)
            
            # Notify observers
            self._notify_observers("agent_registered", agent_id, {
                "node_name": node_name,
                "context": context
            })
            
            logger.debug(f"Registered agent {agent_id} in node {node_name}")
            return agent_id
    
    def get_discovered_agents(self, node_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get all discovered agents, optionally filtered by node.
        
        Args:
            node_name: Optional node name filter
            
        Returns:
            Dictionary of agent_id -> agent instance
        """
        with self._lock:
            result = {}
            
            if node_name:
                # Return agents for specific node
                agent_ids = self._node_agents.get(node_name, set())
            else:
                # Return all agents
                agent_ids = self._agents.keys()
            
            for agent_id in agent_ids:
                agent_ref = self._agents.get(agent_id)
                if agent_ref:
                    agent = agent_ref()  # Dereference weak reference
                    if agent is not None:
                        result[agent_id] = agent
            
            return result
    
    def get_agent_metadata(self, agent_id: str) -> Optional[AgentMetadata]:
        """Get metadata for a specific agent"""
        with self._lock:
            return self._metadata.get(agent_id)
    
    def update_agent_state(self, agent_id: str, state: str, metrics: Optional[Dict] = None):
        """Update agent lifecycle state and metrics"""
        with self._lock:
            if agent_id in self._metadata:
                self._metadata[agent_id].lifecycle_state = state
                if metrics:
                    self._metadata[agent_id].performance_metrics.update(metrics)
                
                self._notify_observers("agent_state_changed", agent_id, {
                    "state": state,
                    "metrics": metrics
                })
    
    def add_observer(self, observer: Callable):
        """Add observer for agent lifecycle events"""
        self._observers.append(observer)
    
    def remove_observer(self, observer: Callable):
        """Remove observer"""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def _notify_observers(self, event: str, agent_id: str, data: Dict[str, Any]):
        """Notify all observers of agent lifecycle events"""
        for observer in self._observers:
            try:
                observer(event, agent_id, data)
            except Exception as e:
                logger.error(f"Observer notification failed: {e}")
    
    def _cleanup_agent(self, agent_id: str):
        """Create cleanup callback for weak reference"""
        def cleanup(ref):
            with self._lock:
                # Clean up metadata when agent is garbage collected
                if agent_id in self._metadata:
                    del self._metadata[agent_id]
                
                # Remove from node mappings
                for node_name, agent_ids in self._node_agents.items():
                    agent_ids.discard(agent_id)
                
                logger.debug(f"Cleaned up agent {agent_id}")
        
        return cleanup
    
    def get_pipeline_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary of all discovered agents"""
        with self._lock:
            summary = {
                "total_agents": len(self._agents),
                "active_agents": 0,
                "nodes_with_agents": len(self._node_agents),
                "agents_by_node": {},
                "state_distribution": {}
            }
            
            # Count active agents and collect states
            for agent_id, metadata in self._metadata.items():
                # Check if agent is still alive
                agent_ref = self._agents.get(agent_id)
                if agent_ref and agent_ref() is not None:
                    summary["active_agents"] += 1
                    
                    # Track state distribution
                    state = metadata.lifecycle_state
                    summary["state_distribution"][state] = summary["state_distribution"].get(state, 0) + 1
            
            # Agents by node
            for node_name, agent_ids in self._node_agents.items():
                active_count = sum(1 for aid in agent_ids 
                                 if aid in self._agents and self._agents[aid]() is not None)
                summary["agents_by_node"][node_name] = {
                    "total": len(agent_ids),
                    "active": active_count
                }
            
            return summary


# Global registry instance
_global_discovery_registry = AgentDiscoveryRegistry()


def get_agent_registry() -> AgentDiscoveryRegistry:
    """Get the global agent discovery registry"""
    return _global_discovery_registry


def register_agent(agent: Any, node_name: Optional[str] = None, 
                  context: Optional[Dict[str, Any]] = None) -> str:
    """Convenience function to register an agent for discovery"""
    return get_agent_registry().register_agent(agent, node_name, context)


def get_discovered_agents(node_name: Optional[str] = None) -> Dict[str, Any]:
    """Convenience function to get discovered agents"""
    return get_agent_registry().get_discovered_agents(node_name)