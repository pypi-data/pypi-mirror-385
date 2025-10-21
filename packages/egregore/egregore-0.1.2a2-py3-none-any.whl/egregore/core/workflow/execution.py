"""
Execution Tracking for Workflow Controller

This module provides comprehensive execution tracking for workflow nodes,
enabling proper state management, loop detection, and historical execution visibility.
"""

from dataclasses import dataclass, field
from typing import Any, Optional, TYPE_CHECKING, Dict, List
from datetime import datetime
import uuid
import statistics

if TYPE_CHECKING:
    from egregore.core.workflow.nodes.base import BaseNode


@dataclass
class NodePerformanceMetrics:
    """Performance metrics for a single node execution"""
    
    node_guid: str
    node_name: str
    effective_name: str
    execution_id: str
    duration: float
    status: str
    execution_position: int
    input_size_bytes: Optional[int] = None
    output_size_bytes: Optional[int] = None
    memory_usage_mb: Optional[float] = None
    
    @property
    def is_successful(self) -> bool:
        """Check if execution was successful"""
        return self.status == "completed"
    
    @property
    def execution_rate(self) -> Optional[float]:
        """Executions per second (1/duration)"""
        return 1.0 / self.duration if self.duration > 0 else None


@dataclass
class ExecutionEntry:
    """Record of a single node execution with enhanced identity tracking"""

    node: 'BaseNode'
    node_guid: str                    # Phase 3: Stable GUID identifier
    node_name: str                    # Component name: "processor"
    node_alias: Optional[str]         # Phase 3: Alias: "processor_2"
    canonical_name: Optional[str]     # Phase 3: Original component: "processor"
    effective_name: str               # Phase 3: State reference name
    execution_position: int           # Phase 3: Position in workflow sequence
    input_value: Any
    output_value: Optional[Any] = None
    is_router: bool = False           # Router node flag (feeds decision criteria to Decision)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    error: Optional[Exception] = None
    
    @property
    def duration(self) -> Optional[float]:
        """Execution duration in seconds"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    @property
    def status(self) -> str:
        """Execution status: running, completed, error"""
        if self.error:
            return "error"
        elif self.end_time:
            return "completed" 
        else:
            return "running"
    
    @property
    def is_completed(self) -> bool:
        """Check if execution completed successfully"""
        return self.status == "completed"
    
    @property
    def is_running(self) -> bool:
        """Check if execution is currently running"""
        return self.status == "running"
    
    @property
    def is_error(self) -> bool:
        """Check if execution ended with error"""
        return self.status == "error"
    
    def complete(self, output_value: Any) -> None:
        """Mark execution as completed with output"""
        self.output_value = output_value
        self.end_time = datetime.now()
    
    def fail(self, error: Exception) -> None:
        """Mark execution as failed with error"""
        self.error = error
        self.end_time = datetime.now()
    
    def is_performance_outlier(self, threshold: float = 2.0, history: Optional['ExecutionHistory'] = None) -> bool:
        """Phase 4: Check if this execution is a performance outlier
        
        Args:
            threshold: Standard deviations from mean to consider outlier (default: 2.0)
            history: ExecutionHistory to compare against (if None, cannot determine outlier status)
            
        Returns:
            True if execution duration is significantly higher than historical average
        """
        if not self.duration or not history:
            return False
        
        # Get historical executions for same canonical component
        historical_entries = history.get_by_canonical(self.canonical_name or self.node_name)
        
        # Need at least 3 data points for meaningful statistical analysis
        if len(historical_entries) < 3:
            return False
        
        # Calculate durations for completed executions only
        durations = [entry.duration for entry in historical_entries 
                    if entry.duration and entry.is_completed and entry.execution_id != self.execution_id]
        
        if len(durations) < 2:
            return False
        
        try:
            mean_duration = statistics.mean(durations)
            stdev_duration = statistics.stdev(durations) if len(durations) > 1 else 0.0
            
            # If no variation in historical data, use simple multiplier
            if stdev_duration == 0.0:
                return self.duration > mean_duration * (1 + threshold)
            
            # Check if current duration is more than threshold standard deviations above mean
            z_score = (self.duration - mean_duration) / stdev_duration
            return z_score > threshold
            
        except statistics.StatisticsError:
            # Fallback to simple comparison if statistical analysis fails
            return self.duration > max(durations) * 1.5 if durations else False
    
    def get_performance_metrics(self) -> NodePerformanceMetrics:
        """Phase 4: Get comprehensive performance metrics for this execution"""
        return NodePerformanceMetrics(
            node_guid=self.node_guid,
            node_name=self.node_name,
            effective_name=self.effective_name,
            execution_id=self.execution_id,
            duration=self.duration or 0.0,
            status=self.status,
            execution_position=self.execution_position,
            # FUTURE: Implement precise memory size calculation for workflow optimization
            input_size_bytes=self._estimate_size(self.input_value),
            output_size_bytes=self._estimate_size(self.output_value)
        )
    
    def _estimate_size(self, obj: Any) -> Optional[int]:
        """Estimate memory size of an object in bytes"""
        if obj is None:
            return 0
        
        try:
            import sys
            if isinstance(obj, (str, int, float, bool)):
                return sys.getsizeof(obj)
            elif isinstance(obj, (list, tuple, dict, set)):
                return sys.getsizeof(obj) + sum(sys.getsizeof(item) for item in (obj if not isinstance(obj, dict) else list(obj.keys()) + list(obj.values())))
            else:
                return sys.getsizeof(obj)
        except (ImportError, TypeError, RecursionError):
            # Fallback for objects that can't be sized
            return None
    
    @classmethod
    def from_node(cls, node: 'BaseNode', input_value: Any, position: int) -> 'ExecutionEntry':
        """Phase 3: Create execution entry from node with full identity info"""
        return cls(
            node=node,
            node_guid=node.guid,
            node_name=node.name,
            node_alias=node.alias_name,
            canonical_name=node.canonical_name or node.name,
            effective_name=node.effective_name,
            execution_position=position,
            input_value=input_value,
            is_router=getattr(node, '_is_router', False)
        )
    
    def __repr__(self) -> str:
        duration_str = f", {self.duration:.3f}s" if self.duration else ""
        alias_str = f" (alias: {self.node_alias})" if self.node_alias else ""
        return f"ExecutionEntry({self.effective_name}[{self.execution_id}], {self.status}{duration_str}{alias_str})"
    
    def __str__(self) -> str:
        return self.__repr__()


class ExecutionHistory:
    """Container for managing execution history with query capabilities"""
    
    def __init__(self, max_entries: int = 1000):
        self.entries: list[ExecutionEntry] = []
        self.max_entries = max_entries
        self._node_counts: dict[str, int] = {}  # Legacy - kept for backward compatibility
        # Phase 3: GUID-based tracking
        self._guid_counts: dict[str, int] = {}
        self._effective_name_counts: dict[str, int] = {}  # Count by effective name (better for aliases)
        self._alias_counts: dict[str, int] = {}
        self._canonical_counts: dict[str, int] = {}
        
    def add_entry(self, entry: ExecutionEntry) -> None:
        """Add a new execution entry with enhanced tracking"""
        self.entries.append(entry)
        
        # Update node execution count (legacy)
        self._node_counts[entry.node_name] = self._node_counts.get(entry.node_name, 0) + 1
        
        # Phase 3: Update GUID-based counts
        self._guid_counts[entry.node_guid] = self._guid_counts.get(entry.node_guid, 0) + 1
        
        # Phase 3: Count by effective name (handles aliases properly)
        self._effective_name_counts[entry.effective_name] = self._effective_name_counts.get(entry.effective_name, 0) + 1
        
        if entry.node_alias:
            self._alias_counts[entry.node_alias] = self._alias_counts.get(entry.node_alias, 0) + 1
        
        if entry.canonical_name:
            self._canonical_counts[entry.canonical_name] = self._canonical_counts.get(entry.canonical_name, 0) + 1
        
        # Trim history if needed
        if len(self.entries) > self.max_entries:
            removed = self.entries.pop(0)
            
            # Update count for removed entry (legacy)
            self._node_counts[removed.node_name] -= 1
            if self._node_counts[removed.node_name] <= 0:
                del self._node_counts[removed.node_name]
            
            # Phase 3: Update GUID-based counts for removed entry
            self._guid_counts[removed.node_guid] -= 1
            if self._guid_counts[removed.node_guid] <= 0:
                del self._guid_counts[removed.node_guid]
            
            # Phase 3: Update effective name counts
            self._effective_name_counts[removed.effective_name] -= 1
            if self._effective_name_counts[removed.effective_name] <= 0:
                del self._effective_name_counts[removed.effective_name]
            
            if removed.node_alias:
                self._alias_counts[removed.node_alias] -= 1
                if self._alias_counts[removed.node_alias] <= 0:
                    del self._alias_counts[removed.node_alias]
            
            if removed.canonical_name:
                self._canonical_counts[removed.canonical_name] -= 1
                if self._canonical_counts[removed.canonical_name] <= 0:
                    del self._canonical_counts[removed.canonical_name]
    
    def get_last_completed(self) -> Optional[ExecutionEntry]:
        """Get the last completed execution entry"""
        for entry in reversed(self.entries):
            if entry.is_completed:
                return entry
        return None
    
    def get_by_node_name(self, node_name: str, limit: Optional[int] = None) -> list[ExecutionEntry]:
        """Get executions for a specific node name"""
        matches = [entry for entry in self.entries if entry.node_name == node_name]
        if limit:
            matches = matches[-limit:]
        return matches
    
    def get_by_guid(self, node_guid: str, limit: Optional[int] = None) -> list[ExecutionEntry]:
        """Phase 3: Get executions for a specific node GUID"""
        matches = [entry for entry in self.entries if entry.node_guid == node_guid]
        if limit:
            matches = matches[-limit:]
        return matches
    
    def get_by_alias(self, alias_name: str, limit: Optional[int] = None) -> list[ExecutionEntry]:
        """Phase 3: Get executions for a specific alias"""
        matches = [entry for entry in self.entries if entry.node_alias == alias_name]
        if limit:
            matches = matches[-limit:]
        return matches
    
    def get_by_canonical(self, canonical_name: str, limit: Optional[int] = None) -> list[ExecutionEntry]:
        """Phase 3: Get all executions for a canonical component (including aliases)"""
        matches = [entry for entry in self.entries if entry.canonical_name == canonical_name]
        if limit:
            matches = matches[-limit:]
        return matches
    
    def get_by_effective_name(self, effective_name: str, limit: Optional[int] = None) -> list[ExecutionEntry]:
        """Phase 3: Get executions by effective name (what appears in state)"""
        matches = [entry for entry in self.entries if entry.effective_name == effective_name]
        if limit:
            matches = matches[-limit:]
        return matches
    
    def get_by_position(self, position: int) -> list[ExecutionEntry]:
        """Phase 3: Get all executions at a specific workflow position"""
        return [entry for entry in self.entries if entry.execution_position == position]
    
    def get_recent(self, limit: int = 10) -> list[ExecutionEntry]:
        """Get recent execution entries"""
        return self.entries[-limit:] if limit <= len(self.entries) else self.entries
    
    def get_node_execution_count(self, node_name: str) -> int:
        """Get total execution count for a node by effective name (more accurate with aliases)"""
        # Phase 3: Use efficient dictionary lookup by effective name
        return self._effective_name_counts.get(node_name, 0)
    
    def get_guid_execution_count(self, node_guid: str) -> int:
        """Phase 3: Get execution count for a specific GUID"""
        return self._guid_counts.get(node_guid, 0)
    
    def get_alias_execution_count(self, alias_name: str) -> int:
        """Phase 3: Get execution count for a specific alias"""
        return self._alias_counts.get(alias_name, 0)
    
    def get_canonical_execution_count(self, canonical_name: str) -> int:
        """Phase 3: Get total execution count for a canonical component (all aliases)"""
        return self._canonical_counts.get(canonical_name, 0)
    
    def detect_repetitive_pattern(self, target_node_name: str, pattern_length: int = 3) -> bool:
        """Detect if selecting target would create a repetitive execution pattern"""
        recent = self.get_recent(pattern_length * 2)
        
        if len(recent) < pattern_length:
            return False
        
        # Count occurrences of target_node_name in recent executions
        recent_names = [entry.node_name for entry in recent[-pattern_length:]]
        return recent_names.count(target_node_name) >= 2
    
    def get_execution_sequence(self, limit: Optional[int] = None) -> list[str]:
        """Get sequence of node names in execution order"""
        entries = self.get_recent(limit) if limit else self.entries
        return [entry.node_name for entry in entries]
    
    def clear(self) -> None:
        """Clear all execution history"""
        self.entries.clear()
        self._node_counts.clear()
        # Phase 3: Clear GUID-based tracking
        self._guid_counts.clear()
        self._effective_name_counts.clear()
        self._alias_counts.clear()
        self._canonical_counts.clear()
    
    def __len__(self) -> int:
        return len(self.entries)
    
    def __repr__(self) -> str:
        return f"ExecutionHistory({len(self.entries)} entries, {len(self._node_counts)} unique nodes)"