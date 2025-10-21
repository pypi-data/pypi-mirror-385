"""
Provider information accessor for V2 Agent implementation.

Provides clean nested access to provider information via agent.provider.*
"""

from typing import Optional, Dict, Any, TYPE_CHECKING, MutableMapping, Iterator

if TYPE_CHECKING:
    from . import Agent
    from egregore.providers.core.interface import BaseProvider


class SettingsProxy(MutableMapping[str, Any]):
    """Mutable proxy over provider settings.

    Mutations update both the live provider instance (for immediate effect)
    and the agent's provider_config (for consistency/introspection).
    """

    def __init__(self, agent: 'Agent'):
        self._agent = agent

        # Ensure agent provider_config exists
        if getattr(self._agent.config, 'provider_config', None) is None:
            self._agent.config.provider_config = {}

    # Internal helpers
    @property
    def _provider_dict(self) -> Dict[str, Any]:
        provider = getattr(self._agent, '_provider', None)
        if provider is None:
            return {}
        # Provider.config is the live settings dict
        return getattr(provider, 'config', {})

    @property
    def _agent_dict(self) -> Dict[str, Any]:
        return self._agent.config.provider_config  # ensured to exist in __init__

    # MutableMapping implementation
    def __getitem__(self, key: str) -> Any:
        if key in self._provider_dict:
            return self._provider_dict[key]
        return self._agent_dict[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._provider_dict[key] = value
        self._agent_dict[key] = value

    def __delitem__(self, key: str) -> None:
        if key in self._provider_dict:
            del self._provider_dict[key]
        if key in self._agent_dict:
            del self._agent_dict[key]

    def __iter__(self) -> Iterator[str]:
        # Union of keys across both dicts
        keys = set(self._agent_dict.keys()) | set(self._provider_dict.keys())
        return iter(keys)

    def __len__(self) -> int:
        return len(set(self._agent_dict.keys()) | set(self._provider_dict.keys()))

    # Convenience utilities
    def update(self, other: Optional[Dict[str, Any]] = None, **kwargs) -> None:  # type: ignore[override]
        if other is None:
            merged = dict(**kwargs)
        else:
            merged = dict(other, **kwargs)
        for k, v in merged.items():
            self[k] = v


class ProviderInfo:
    """Provider information container with clean accessor interface."""
    
    def __init__(self, agent: 'Agent'):
        """
        Initialize provider info accessor.
        
        Args:
            agent: Agent instance to extract provider info from
        """
        self._agent = agent
        
        # Parse provider string once during initialization
        provider_string = agent._provider_string
        if ':' in provider_string:
            self._name, self._model = provider_string.split(':', 1)
            self._name = self._name.strip()
            self._model = self._model.strip()
        else:
            self._name = provider_string
            self._model = None
    
    @property
    def name(self) -> str:
        """
        Provider name (e.g., 'openai', 'anthropic').
        
        Returns:
            Provider name string
        """
        return self._name
    
    @property
    def model(self) -> Optional[str]:
        """
        Current model name (e.g., 'gpt-4', 'claude-3-sonnet').
        
        Returns:
            Model name or None if not specified
        """
        return self._model
    
    @property
    def config(self) -> Dict[str, Any]:
        """Deprecated dict-based config. Prefer ProviderAccessor.settings (mutable)"""
        return self._agent.config.provider_config or {}
    
    @property
    def client(self) -> Optional['BaseProvider']:
        """Live provider client (GeneralPurposeProvider instance)."""
        provider = getattr(self._agent, '_provider', None)
        if provider is not None:
            return provider
        # Fallback to legacy naming if present
        return getattr(self._agent, '_provider_manager', None)

    @property
    def settings(self) -> SettingsProxy:
        """
        Mutable provider settings proxy. Updates both the live provider client
        and the agent's provider_config.
        """
        if not hasattr(self, '_settings_proxy'):
            setattr(self, '_settings_proxy', SettingsProxy(self._agent))
        return getattr(self, '_settings_proxy')
    
    def __repr__(self) -> str:
        """String representation of provider info."""
        model_str = f":{self.model}" if self.model else ""
        return f"ProviderInfo(name={self.name}{model_str})"


class ProviderAccessor:
    """Clean accessor pattern for agent provider information."""
    
    def __init__(self, agent: 'Agent'):
        """
        Initialize provider accessor.
        
        Args:
            agent: Agent instance to provide access for
        """
        self._provider_info = ProviderInfo(agent)
    
    @property
    def name(self) -> str:
        """Provider name."""
        return self._provider_info.name
    
    @property
    def model(self) -> Optional[str]:
        """Model name or None."""
        return self._provider_info.model
    
    @property
    def client(self) -> Optional['BaseProvider']:
        """Provider client (GeneralPurposeProvider)."""
        return self._provider_info.client

    @property
    def settings(self) -> SettingsProxy:
        """Mutable provider settings proxy."""
        return self._provider_info.settings
    
    # No generic .config; use .client (object) and .settings (mutable mapping)
    
    def __repr__(self) -> str:
        """String representation."""
        return repr(self._provider_info)
