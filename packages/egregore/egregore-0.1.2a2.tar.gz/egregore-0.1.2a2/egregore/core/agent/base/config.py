"""
Agent Configuration

Configuration dataclass for Agent initialization with config accessor.
"""

from typing import Optional, List, Union, Any, Set
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)
from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    """Configuration for Agent initialization."""
    provider: str  # Provider name (e.g., 'openai', 'anthropic', 'google')
    scaffolds: List = Field(default_factory=list)  # List of scaffold instances to register
    tools: List = Field(default_factory=list)  # List of tools available to the agent
    api_key: Optional[str] = None  # API key for the provider
    provider_config: Optional[dict] = None  # Provider-specific configuration
    instructions: str = ""  # Instructions for the agent (was system_message)
    reasoning: bool = False  # Whether to require a reasoning-capable model
    max_tool_executions: Optional[int] = None  # Maximum tool executions (None for unlimited, was max_tool_recursions)
    api_call_delay: Optional[float] = None  # API call delay


class ConfigAccessor:
    """
    Accessor for AgentConfig that controls which properties are mutable at runtime.
    
    Immutable properties require agent reinitialization to change.
    Mutable properties can be changed on the fly with automatic component updates.
    """
    
    # Properties that cannot be changed after agent initialization
    IMMUTABLE_PROPERTIES: Set[str] = {
        'provider',
        'api_key',
        'provider_config'
    }
    
    # Properties that can be changed at runtime
    MUTABLE_PROPERTIES: Set[str] = {
        'scaffolds',
        'tools', 
        'instructions',
        'reasoning',
        'max_tool_executions', 
        'api_call_delay'
    }
    
    def __init__(self, agent_config: AgentConfig, agent_ref=None):
        """
        Initialize config accessor.
        
        Args:
            agent_config: The underlying AgentConfig instance
            agent_ref: Reference to the agent for component updates
        """
        self._config = agent_config
        self._agent_ref = agent_ref
        
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value with mutability validation.
        
        Args:
            key: Configuration key to set
            value: New value to set
            
        Raises:
            ValueError: If attempting to modify an immutable property
            AttributeError: If property doesn't exist
        """
        if not hasattr(self._config, key):
            raise AttributeError(f"Configuration property '{key}' does not exist")
            
        if key in self.IMMUTABLE_PROPERTIES:
            raise ValueError(
                f"Property '{key}' is immutable after agent initialization. "
                f"Create a new agent instance to change this property."
            )
            
        if key not in self.MUTABLE_PROPERTIES:
            logger.warning(f"Property '{key}' mutability is not explicitly defined")
            
        # Set the value
        old_value = getattr(self._config, key)
        setattr(self._config, key, value)
        
        logger.debug(f"Config updated: {key} = {value} (was: {old_value})")
        
        # Trigger component updates if needed
        self._handle_config_change(key, value, old_value)
        
    def _handle_config_change(self, key: str, new_value: Any, old_value: Any) -> None:
        """
        Handle configuration changes that require component updates.
        
        Args:
            key: Configuration key that changed
            new_value: New value
            old_value: Previous value
        """
        if self._agent_ref is None:
            return
            
        try:
            # Handle specific configuration changes
            if key == 'scaffolds':
                # Re-initialize scaffold system with new scaffolds
                if hasattr(self._agent_ref, '_initialize_scaffold_system'):
                    self._agent_ref._initialize_scaffold_system()
                    logger.info(f"Scaffold system reinitialized with {len(new_value or [])} scaffolds")
                    
            elif key == 'tools':
                # Update tool registry with new tools
                if hasattr(self._agent_ref, 'tool_registry'):
                    # Clear existing tools and re-register
                    self._agent_ref.tool_registry.clear()
                    for tool in (new_value or []):
                        self._agent_ref.tool_registry.register_tool(tool)
                    logger.info(f"Tool registry updated with {len(new_value or [])} tools")
                    
            elif key == 'max_tool_executions':
                # Update tool executor limits if needed
                if hasattr(self._agent_ref, 'tool_executor'):
                    # Tool executor doesn't currently have configurable limits,
                    # but this is where you'd update them
                    pass
                    
            elif key == 'instructions':
                # Instructions changes would affect context system messages
                # This would trigger context system updates in a full implementation
                pass
                
            elif key == 'reasoning':
                # Reasoning requirement changes might affect model selection
                # This would trigger provider model updates in a full implementation
                pass
                
            elif key == 'api_call_delay':
                # Update provider delay settings
                if hasattr(self._agent_ref, '_provider'):
                    # Provider doesn't currently expose delay configuration,
                    # but this is where you'd update it
                    pass
                    
        except Exception as e:
            logger.warning(f"Failed to update components after config change '{key}': {e}")
            
    def get(self, key: str) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key to get
            
        Returns:
            Configuration value
            
        Raises:
            AttributeError: If property doesn't exist
        """
        if not hasattr(self._config, key):
            raise AttributeError(f"Configuration property '{key}' does not exist")
        return getattr(self._config, key)
        
    def __getattr__(self, name: str) -> Any:
        """Allow direct attribute access to config properties."""
        return getattr(self._config, name)
        
    def __setattr__(self, name: str, value: Any) -> None:
        """Prevent direct attribute setting - force use of set() method."""
        if name.startswith('_') or name in {'IMMUTABLE_PROPERTIES', 'MUTABLE_PROPERTIES'}:
            super().__setattr__(name, value)
        else:
            raise AttributeError(
                f"Cannot set '{name}' directly. Use config.set('{name}', value) instead."
            )
            
    def to_dict(self) -> dict:
        """Return configuration as dictionary."""
        result = {
            'provider': self._config.provider,
            'scaffolds': self._config.scaffolds,
            'tools': self._config.tools,
            'api_key': self._config.api_key,
            'provider_config': self._config.provider_config,
            'instructions': self._config.instructions,
            'reasoning': self._config.reasoning,
            'max_tool_executions': self._config.max_tool_executions,
            'api_call_delay': self._config.api_call_delay
        }
        
        # Add agent-specific properties if available
        if self._agent_ref:
            result['operation_ttl'] = getattr(self._agent_ref, 'operation_ttl', None)
            result['operation_retention'] = getattr(self._agent_ref, 'operation_retention', None)
            
        return result
        
    def __repr__(self) -> str:
        """String representation."""
        return f"ConfigAccessor({self._config})"
