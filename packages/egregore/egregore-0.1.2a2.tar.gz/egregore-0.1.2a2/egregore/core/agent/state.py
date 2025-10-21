"""
Agent State System for Scaffold IPC

Provides formal state system for scaffold Inter-Process Communication (IPC) 
that enables elegant scaffold intercommunication with automatic source tracking.
"""

from typing import Any, Dict, Optional, Iterator, Tuple, List
from datetime import datetime
from pydantic import BaseModel, Field, PrivateAttr


class ScaffoldStateAccessor:
    """Provides access to scaffold states via scaffold type keys."""
    
    def __init__(self, agent_state: 'AgentState'):
        self._agent_state = agent_state
        self._scaffolds_by_type: Dict[str, Any] = {}
        self._scaffolds_by_index: List[Any] = []
        self._refresh_needed = True
        
    def __getitem__(self, key) -> Any:
        """Access scaffold by type string or index."""
        self._ensure_fresh()
        if isinstance(key, str):
            return self._scaffolds_by_type.get(key)
        elif isinstance(key, int):
            return self._scaffolds_by_index[key] if 0 <= key < len(self._scaffolds_by_index) else None
        else:
            raise TypeError(f"Scaffold accessor key must be str or int, got {type(key)}")
            
    def __len__(self) -> int:
        self._ensure_fresh()
        return len(self._scaffolds_by_index)
        
    def _ensure_fresh(self) -> None:
        """Rebuild scaffold mappings if needed."""
        if self._refresh_needed:
            self._rebuild_mappings()
            
    def _rebuild_mappings(self) -> None:
        """Rebuild type->scaffold and index mappings."""
        self._scaffolds_by_type.clear()
        self._scaffolds_by_index.clear()
        
        # Get actual scaffold instances from registered scaffolds
        for scaffold_id, scaffold_name in self._agent_state._registered_scaffolds.items():
            scaffold_instance = self._agent_state._scaffold_instances.get(scaffold_id)
            if scaffold_instance is not None:
                self._scaffolds_by_type[scaffold_name] = scaffold_instance
                self._scaffolds_by_index.append(scaffold_instance)
            
        self._refresh_needed = False
        
    def refresh(self) -> None:
        """Mark for refresh on next access."""
        self._refresh_needed = True


class AgentState(BaseModel):
    """
    Formalized agent state with automatic scaffold source tracking.
    
    This class provides a formal state system for scaffold intercommunication
    where scaffolds can share state while tracking which scaffold made each change.
    
    Features:
    - Pydantic-based clean state management
    - Simple store for generic key-value data
    - Scaffold registration system for automatic source tracking
    - Source tracking for store changes
    
    Example:
        >>> state = AgentState()
        >>> state.register_scaffold(shell_scaffold)
        >>> state.set_from_registered(shell_scaffold, 'cwd', '/new/path')
        >>> value, source = state.get_with_source('cwd')
        >>> print(f"cwd={value} (set by {source})")
        cwd=/new/path (set by ShellScaffold)
    """
    
    # Canonical agent state properties
    current_turn: int = 0
    execution_state: str = "idle"
    cwd: Optional[str] = None
    conversation_started_at: Optional[datetime] = None
    provider_calls_count: int = 0
    tool_calls_count: int = 0
    errors_count: int = 0
    message_count: int = 0
    total_messages: int = 0
    execution_id: Optional[str] = None
    execution_start_time: Optional[datetime] = None
    last_provider_call: Optional[datetime] = None
    active_scaffolds: List[str] = Field(default_factory=list)
    last_error: Optional[datetime] = None
    
    # Generic store and internal systems
    store: Dict[str, Any] = Field(default_factory=dict)
    _sources: Dict[str, str] = PrivateAttr(default_factory=dict)  # Track which scaffold set each store key
    _registered_scaffolds: Dict[int, str] = PrivateAttr(default_factory=dict)  # scaffold_id -> scaffold_name mapping
    _scaffold_instances: Dict[int, Any] = PrivateAttr(default_factory=dict)  # scaffold_id -> scaffold_instance mapping
    _scaffolds_accessor: Optional['ScaffoldStateAccessor'] = PrivateAttr(default=None)
    
    model_config = {"arbitrary_types_allowed": True}
    
    def register_scaffold(self, scaffold_instance: Any) -> None:
        """
        Register a scaffold instance for automatic source tracking.
        
        Args:
            scaffold_instance: The scaffold instance to register
        """
        # Priority: type attribute > name attribute > class name
        scaffold_name = (
            getattr(scaffold_instance, 'type', None) or 
            getattr(scaffold_instance, 'name', None) or 
            scaffold_instance.__class__.__name__
        )
        scaffold_id = id(scaffold_instance)
        self._registered_scaffolds[scaffold_id] = scaffold_name
        self._scaffold_instances[scaffold_id] = scaffold_instance
        
        # Update active_scaffolds list
        if scaffold_name not in self.active_scaffolds:
            self.active_scaffolds.append(scaffold_name)
        
        # Refresh scaffold accessor if it exists
        if self._scaffolds_accessor:
            self._scaffolds_accessor.refresh()
    
    def unregister_scaffold(self, scaffold_instance: Any) -> None:
        """
        Unregister a scaffold instance.
        
        Args:
            scaffold_instance: The scaffold instance to unregister
        """
        scaffold_id = id(scaffold_instance)
        scaffold_name = self._registered_scaffolds.get(scaffold_id)
        
        if scaffold_name:
            # Remove from registrations
            del self._registered_scaffolds[scaffold_id]
            del self._scaffold_instances[scaffold_id]
            
            # Remove from active_scaffolds list
            if scaffold_name in self.active_scaffolds:
                self.active_scaffolds.remove(scaffold_name)
            
            # Refresh scaffold accessor if it exists
            if self._scaffolds_accessor:
                self._scaffolds_accessor.refresh()
    
    def set_from_registered(self, scaffold_instance: Any, key: str, value: Any) -> None:
        """
        Set store value from a registered scaffold with automatic source tracking.
        
        Args:
            scaffold_instance: The scaffold instance making the change
            key: Store key to set
            value: Value to set
        """
        scaffold_id = id(scaffold_instance)
        scaffold_name = self._registered_scaffolds.get(scaffold_id, 'unknown')
        self.store[key] = value
        self._sources[key] = scaffold_name
    
    def get_source(self, key: str) -> Optional[str]:
        """
        Get which scaffold set this store key.
        
        Args:
            key: Store key to check
            
        Returns:
            Name of scaffold that set this key, or None if not found
        """
        return self._sources.get(key)
    
    def get_with_source(self, key: str) -> Tuple[Any, Optional[str]]:
        """
        Get both store value and source scaffold.
        
        Args:
            key: Store key to get
            
        Returns:
            Tuple of (value, source_scaffold_name)
        """
        return self.store.get(key), self._sources.get(key)
        
    @property
    def scaffolds(self) -> 'ScaffoldStateAccessor':
        """Access scaffold states via scaffold type keys."""
        if self._scaffolds_accessor is None:
            self._scaffolds_accessor = ScaffoldStateAccessor(self)
        return self._scaffolds_accessor
        
    # Increment methods for counts with automatic timestamp updates
    def increment_provider_calls(self) -> None:
        """Increment provider calls count and update timestamp."""
        self.provider_calls_count += 1
        self.last_provider_call = datetime.now()
        
    def increment_tool_calls(self) -> None:
        """Increment tool calls count."""
        self.tool_calls_count += 1
        
    def increment_errors(self) -> None:
        """Increment errors count and update timestamp."""
        self.errors_count += 1
        self.last_error = datetime.now()
        

    def __repr__(self) -> str:
        """String representation showing registered scaffolds and store."""
        scaffold_count = len(self._registered_scaffolds)
        store_count = len(self.store)
        return f"AgentState(scaffolds={scaffold_count}, store_items={store_count})"