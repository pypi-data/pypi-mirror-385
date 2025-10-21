from abc import ABC, abstractmethod

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from threading import Lock
from .data_models import CacheEntry
from ..context_snapshot import ContextSnapshot
from ..loader_settings import BaseLoaderSettings
import logging

logger = logging.getLogger(__name__)

class SnapshotLoaderEngine(ABC):
    """Smart snapshot storage engine with intelligent memory management.

    Handles ALL snapshot operations (current session + external) with automatic
    memory management, persistence, and optimization.
    """

    def __init__(self, settings: BaseLoaderSettings, memory_limit: int = 50, age_limit_minutes: int = 60):
        """Initialize smart snapshot engine.

        Args:
            settings: Loader-specific settings
            memory_limit: Maximum snapshots to keep in memory
            age_limit_minutes: Age limit for automatic cache eviction
        """
        # Store settings
        self.settings = settings

        # Smart memory cache
        self._memory_cache: Dict[str, CacheEntry] = {}
        self._cache_lock = Lock()

        # Configuration
        self.memory_limit = memory_limit
        self.age_limit = timedelta(minutes=age_limit_minutes)

        # Agent-specific snapshot indexes for fast lookup
        self._agent_snapshots: Dict[str, List[str]] = {}  # agent_id -> [snapshot_ids]
        self._agent_cycles: Dict[str, Dict[int, str]] = {}  # agent_id -> {cycle -> snapshot_id}

        logger.info(f"Initialized SnapshotLoaderEngine: memory_limit={memory_limit}, age_limit={age_limit_minutes}min")
    
    # === Public Interface ===
    
    def add_snapshot(self, snapshot: ContextSnapshot) -> bool:
        """Add new snapshot to the engine (for current session snapshots).
        
        Args:
            snapshot: ContextSnapshot to add
            
        Returns:
            True if successfully added
        """
        with self._cache_lock:
            # Add to memory cache
            self._memory_cache[snapshot.id] = CacheEntry(
                snapshot=snapshot,
                last_access=datetime.now(),
                access_count=1
            )
            
            # Update agent indexes
            agent_id = snapshot.agent_id or "default"
            if agent_id not in self._agent_snapshots:
                self._agent_snapshots[agent_id] = []
                self._agent_cycles[agent_id] = {}
            
            self._agent_snapshots[agent_id].append(snapshot.id)
            self._agent_cycles[agent_id][snapshot.message_cycle] = snapshot.id
            
            # Sort by message cycle (newest first)
            self._agent_snapshots[agent_id].sort(
                key=lambda sid: self._get_snapshot_cycle(sid),
                reverse=True
            )
            
            # Async persist to storage
            self._async_persist(snapshot)
            
            # Smart cache cleanup
            self._smart_cache_cleanup()
            
            return True
    
    def get_snapshot_by_offset(self, agent_id: str, offset: int) -> Optional[ContextSnapshot]:
        """Get snapshot by relative offset (@t-N) for specific agent.
        
        Args:
            agent_id: Agent identifier 
            offset: Relative offset (1 = @t-1, 2 = @t-2, etc.)
            
        Returns:
            ContextSnapshot if found, None otherwise
        """
        agent_id = agent_id or "default"
        
        with self._cache_lock:
            snapshot_ids = self._agent_snapshots.get(agent_id, [])
            
            if offset <= 0 or offset > len(snapshot_ids):
                return None
            
            target_id = snapshot_ids[offset - 1]  # offset-1 because 0-indexed
            return self._get_snapshot(target_id)
    
    def get_snapshot_by_cycle(self, agent_id: str, cycle: int) -> Optional[ContextSnapshot]:
        """Get snapshot by absolute message cycle (@cN) for specific agent.
        
        Args:
            agent_id: Agent identifier
            cycle: Absolute message cycle number
            
        Returns:
            ContextSnapshot if found, None otherwise
        """
        agent_id = agent_id or "default"
        
        with self._cache_lock:
            cycles = self._agent_cycles.get(agent_id, {})
            snapshot_id = cycles.get(cycle)
            
            if snapshot_id:
                return self._get_snapshot(snapshot_id)
            
            return None
    
    def list_snapshots(self, agent_id: str, limit: Optional[int] = None) -> List[ContextSnapshot]:
        """List snapshots for specific agent, newest first.
        
        Args:
            agent_id: Agent identifier
            limit: Optional limit on number of snapshots returned
            
        Returns:
            List of ContextSnapshot objects, newest first
        """
        agent_id = agent_id or "default"
        
        with self._cache_lock:
            snapshot_ids = self._agent_snapshots.get(agent_id, [])
            
            if limit:
                snapshot_ids = snapshot_ids[:limit]
            
            snapshots = []
            for snapshot_id in snapshot_ids:
                snapshot = self._get_snapshot(snapshot_id)
                if snapshot:
                    snapshots.append(snapshot)
            
            return snapshots
    
    def get_snapshots_by_trigger(self, agent_id: str, trigger: str) -> List[ContextSnapshot]:
        """Get snapshots with specific trigger for agent.
        
        Args:
            agent_id: Agent identifier
            trigger: Trigger string to match
            
        Returns:
            List of ContextSnapshot objects with matching trigger
        """
        agent_id = agent_id or "default"
        
        snapshots = []
        snapshot_ids = self._agent_snapshots.get(agent_id, [])
        
        for snapshot_id in snapshot_ids:
            snapshot = self._get_snapshot(snapshot_id)
            if snapshot and snapshot.trigger == trigger:
                snapshots.append(snapshot)
        
        return snapshots
    
    def load_external(self, identifier: str) -> Optional[ContextSnapshot]:
        """Load external snapshot (from file, URL, etc).
        
        Args:
            identifier: Engine-specific identifier
            
        Returns:
            ContextSnapshot if found and valid, None otherwise
        """
        snapshot = self._load_from_storage(identifier)
        
        if snapshot:
            # Add to cache for future access
            with self._cache_lock:
                self._memory_cache[snapshot.id] = CacheEntry(
                    snapshot=snapshot,
                    last_access=datetime.now(),
                    access_count=1
                )
        
        return snapshot
    
    # === Internal Cache Management ===
    
    def _get_snapshot(self, snapshot_id: str) -> Optional[ContextSnapshot]:
        """Get snapshot from cache or storage with access tracking."""
        # Try memory cache first
        if snapshot_id in self._memory_cache:
            entry = self._memory_cache[snapshot_id]
            entry.last_access = datetime.now()
            entry.access_count += 1
            return entry.snapshot
        
        # Load from storage and cache
        snapshot = self._load_from_storage(snapshot_id)
        if snapshot:
            with self._cache_lock:
                self._memory_cache[snapshot_id] = CacheEntry(
                    snapshot=snapshot,
                    last_access=datetime.now(),
                    access_count=1
                )
        
        return snapshot
    
    def _get_snapshot_cycle(self, snapshot_id: str) -> int:
        """Get message cycle for a snapshot (for sorting)."""
        if snapshot_id in self._memory_cache:
            return self._memory_cache[snapshot_id].snapshot.message_cycle
        
        # If not in cache, we'd need to load it, but for now return 0
        # In production, we might want to maintain a lightweight index
        return 0
    
    def _smart_cache_cleanup(self):
        """Intelligent cache cleanup based on usage patterns."""
        if len(self._memory_cache) <= self.memory_limit:
            return
        
        now = datetime.now()
        eviction_candidates = []
        
        # Find candidates for eviction
        for snapshot_id, entry in self._memory_cache.items():
            age = now - entry.last_access
            
            # Score for eviction (higher = more likely to evict)
            score = 0
            
            # Age factor (older = higher score)
            if age > self.age_limit:
                score += 100
            else:
                score += (age.total_seconds() / self.age_limit.total_seconds()) * 50
            
            # Access frequency factor (less used = higher score)
            score += max(0, 50 - entry.access_count)
            
            eviction_candidates.append((score, snapshot_id))
        
        # Sort by eviction score and remove least important
        eviction_candidates.sort(reverse=True)
        
        evictions_needed = len(self._memory_cache) - self.memory_limit
        for i in range(evictions_needed):
            if i < len(eviction_candidates):
                _, snapshot_id = eviction_candidates[i]
                
                # Persist before evicting (if not already persisted)
                if snapshot_id in self._memory_cache:
                    snapshot = self._memory_cache[snapshot_id].snapshot
                    self._persist_to_storage(snapshot)
                    del self._memory_cache[snapshot_id]
        
        logger.debug(f"Cache cleanup: evicted {evictions_needed} snapshots, {len(self._memory_cache)} remaining")
    
    def _async_persist(self, snapshot: ContextSnapshot):
        """Asynchronously persist snapshot to storage."""
        # For now, do synchronous persistence
        # In production, we'd use a background thread or asyncio
        try:
            self._persist_to_storage(snapshot)
        except Exception as e:
            logger.error(f"Failed to persist snapshot {snapshot.id}: {e}")
    
    # === Abstract Storage Methods (implemented by subclasses) ===
    
    @abstractmethod
    def _persist_to_storage(self, snapshot: ContextSnapshot) -> bool:
        """Persist snapshot to underlying storage."""
        pass
    
    @abstractmethod
    def _load_from_storage(self, identifier: str) -> Optional[ContextSnapshot]:
        """Load snapshot from underlying storage."""
        pass
    
    # === Abstract History Operations (NEW) ===
    
    @abstractmethod
    def save_history(self, snapshots: List[ContextSnapshot], groups_data: Dict) -> str:
        """Save complete history state with all snapshots and metadata.
        
        Args:
            snapshots: List of all context snapshots to save
            groups_data: Metadata including execution_groups, groups_by_snapshot, etc.
            
        Returns:
            str: Unique identifier for saved history (filename, key, ID, etc.)
            
        Raises:
            ContextHistoryError: On save failures, permission issues, etc.
        """
        pass

    @abstractmethod 
    def load_history(self, identifier: str, merge: bool = False) -> Dict:
        """Load complete history state from storage.
        
        Args:
            identifier: Storage identifier (from save_history return value)
            merge: Whether to merge with existing snapshots or replace
            
        Returns:
            Dict containing:
            - 'snapshots': List[Dict] - Serialized snapshot data
            - 'execution_groups': Dict - Execution groups data
            - 'groups_by_snapshot': Dict - Snapshot to groups mapping
            - 'groups_by_turn': Dict - Turn to groups mapping
            - 'metadata': Dict - Additional metadata
            - 'format': str - Data format ('json', 'pickle')
            - 'timestamp': str - Save timestamp
            
        Raises:
            ContextHistoryError: On load failures, missing files, corruption
        """
        pass

    @abstractmethod
    def list_saved_histories(self, agent_id: str) -> List[Dict]:
        """List all saved histories for an agent.
        
        Args:
            agent_id: Agent ID to list histories for
            
        Returns:
            List of dicts with keys: 'identifier', 'timestamp', 'snapshot_count'
        """
        pass

    @abstractmethod
    def delete_history(self, identifier: str) -> bool:
        """Delete saved history by identifier.
        
        Args:
            identifier: History identifier to delete
            
        Returns:
            bool: True if successfully deleted, False otherwise
        """
        pass
