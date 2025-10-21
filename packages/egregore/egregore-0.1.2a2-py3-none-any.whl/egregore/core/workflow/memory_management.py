"""
Memory management utilities for workflow execution.

This module provides copy-on-write state management, state pooling, and resource 
cleanup to prevent memory leaks in long-running workflows.
"""

import gc
import asyncio
import weakref
import traceback
from collections import deque
from typing import Any, Dict, List, Optional, Set, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

from egregore.core.workflow.state import SharedState


@dataclass
class MemoryStats:
    """Memory usage statistics for workflow execution"""
    total_states_created: int = 0
    total_states_reused: int = 0
    active_states: int = 0
    pool_size: int = 0
    total_resources_tracked: int = 0
    resources_cleaned: int = 0
    memory_warnings: int = 0
    last_gc_collection: Optional[datetime] = None
    
    @property
    def reuse_ratio(self) -> float:
        """Calculate state reuse efficiency"""
        total = self.total_states_created + self.total_states_reused
        return self.total_states_reused / max(1, total)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/monitoring"""
        return {
            "total_states_created": self.total_states_created,
            "total_states_reused": self.total_states_reused,
            "active_states": self.active_states,
            "pool_size": self.pool_size,
            "reuse_ratio": self.reuse_ratio,
            "total_resources_tracked": self.total_resources_tracked,
            "resources_cleaned": self.resources_cleaned,
            "memory_warnings": self.memory_warnings,
            "last_gc_collection": self.last_gc_collection.isoformat() if self.last_gc_collection else None
        }


class CopyOnWriteState:
    """
    State implementation that shares data until modification.
    
    This allows efficient state sharing between parallel tasks while maintaining
    isolation when modifications occur.
    """
    
    def __init__(self, parent: Optional['CopyOnWriteState'] = None, instance_name: str = "CopyOnWriteState"):
        self.parent = parent
        self.local_data: Dict[str, Any] = {}
        self.instance_name = instance_name
        self.is_dirty = False
        self._creation_time = datetime.now()
        self._access_count = 0
        self._modification_count = 0
        
        # Track resources for cleanup
        self._tracked_resources: Dict[str, Any] = {}
        self._cleanup_callbacks: List[Callable[[], None]] = []
    
    def get_attribute(self, name: str, default: Any = None) -> Any:
        """Get attribute with fallback to parent"""
        self._access_count += 1
        
        if name in self.local_data:
            return self.local_data[name]
        
        if self.parent:
            return self.parent.get_attribute(name, default)
        
        return default
    
    def set_attribute(self, name: str, value: Any) -> None:
        """Set attribute, triggering copy-on-write if needed"""
        if not self.is_dirty and self.parent:
            self._copy_essential_from_parent()
        
        # Always mark as dirty when setting attributes
        self.is_dirty = True
        self.local_data[name] = value
        self._modification_count += 1
    
    def has_attribute(self, name: str) -> bool:
        """Check if attribute exists in this state or parent"""
        if name in self.local_data:
            return True
        if self.parent:
            return self.parent.has_attribute(name)
        return False
    
    def _copy_essential_from_parent(self) -> None:
        """Copy only essential data from parent on first write"""
        if not self.parent:
            return
        
        # Copy only the essential fields that are commonly accessed
        essential_fields = ['execution_sequence', 'executions', 'current', 'previous_output']
        
        for field in essential_fields:
            if self.parent.has_attribute(field):
                parent_value = self.parent.get_attribute(field)
                # Deep copy for mutable objects to ensure isolation
                if isinstance(parent_value, (list, dict)):
                    import copy
                    self.local_data[field] = copy.deepcopy(parent_value)
                else:
                    self.local_data[field] = parent_value
    
    def register_resource(self, name: str, resource: Any, cleanup_callback: Optional[Callable[[], None]] = None) -> None:
        """Register a resource for cleanup tracking"""
        self._tracked_resources[name] = resource
        if cleanup_callback:
            self._cleanup_callbacks.append(cleanup_callback)
    
    def cleanup_resources(self) -> None:
        """Clean up all registered resources"""
        for callback in self._cleanup_callbacks:
            try:
                callback()
            except Exception as e:
                pass
        
        self._tracked_resources.clear()
        self._cleanup_callbacks.clear()
    
    def reset_for_reuse(self, template: Optional['CopyOnWriteState'] = None) -> None:
        """Reset state for reuse in pool"""
        self.cleanup_resources()
        self.local_data.clear()
        self.parent = template
        self.is_dirty = False
        self._access_count = 0
        self._modification_count = 0
        self._creation_time = datetime.now()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics for this state"""
        return {
            "instance_name": self.instance_name,
            "is_dirty": self.is_dirty,
            "access_count": self._access_count,
            "modification_count": self._modification_count,
            "local_data_size": len(self.local_data),
            "tracked_resources": len(self._tracked_resources),
            "age_seconds": (datetime.now() - self._creation_time).total_seconds(),
            "has_parent": self.parent is not None
        }
    
    def __del__(self):
        """Ensure cleanup on destruction"""
        try:
            self.cleanup_resources()
        except Exception:
            pass  # Don't raise exceptions in __del__


class StatePool:
    """
    Pool for reusing state instances to reduce memory allocation overhead.
    
    Maintains a pool of CopyOnWriteState instances that can be reused across
    workflow executions to minimize garbage collection pressure.
    """
    
    def __init__(self, max_pool_size: int = 100, cleanup_interval: int = 300):
        self.max_pool_size = max_pool_size
        self.cleanup_interval = cleanup_interval  # seconds
        
        self._pool: deque = deque(maxlen=max_pool_size)
        self._active_states: weakref.WeakSet = weakref.WeakSet()
        self._stats = MemoryStats()
        self._last_cleanup = datetime.now()
        
        # Thread pool for async cleanup operations
        self._cleanup_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="StatePool")
    
    def acquire_state(self, template: Optional[Union[SharedState, CopyOnWriteState]] = None, 
                     instance_name: str = "PooledState") -> CopyOnWriteState:
        """
        Acquire a state from the pool or create new one.
        
        Args:
            template: Template state to initialize from
            instance_name: Name for the new state instance
            
        Returns:
            CopyOnWriteState instance ready for use
        """
        if self._pool:
            # Reuse from pool
            state = self._pool.popleft()
            self._stats.pool_size -= 1
            self._stats.total_states_reused += 1
            
            # Reset for new use
            if isinstance(template, CopyOnWriteState):
                state.reset_for_reuse(template)
            else:
                state.reset_for_reuse()
                if template:
                    # Initialize from SharedState template
                    self._initialize_from_shared_state(state, template)
            
            state.instance_name = instance_name
        else:
            # Create new state
            if isinstance(template, CopyOnWriteState):
                state = CopyOnWriteState(parent=template, instance_name=instance_name)
            else:
                state = CopyOnWriteState(instance_name=instance_name)
                if template:
                    self._initialize_from_shared_state(state, template)
            
            self._stats.total_states_created += 1
        
        self._active_states.add(state)
        self._stats.active_states = len(self._active_states)
        
        # Periodic cleanup
        if self._should_run_cleanup():
            asyncio.create_task(self._async_cleanup())
        
        return state
    
    def release_state(self, state: CopyOnWriteState) -> None:
        """
        Return a state to the pool for reuse.
        
        Args:
            state: State instance to return to pool
        """
        if state in self._active_states:
            self._active_states.discard(state)
            self._stats.active_states = len(self._active_states)
            
            # Clean up resources before pooling
            state.cleanup_resources()
            
            # Add to pool if there's space
            if len(self._pool) < self.max_pool_size:
                self._pool.append(state)
                self._stats.pool_size += 1
            # Otherwise let it be garbage collected
    
    def _initialize_from_shared_state(self, cow_state: CopyOnWriteState, shared_state: SharedState) -> None:
        """Initialize CopyOnWriteState from SharedState template"""
        # Only copy essential, safe attributes from SharedState
        safe_attributes = [
            'instance_name', 'previous_output', 'executions', 'execution_sequence'
        ]
        
        for attr_name in safe_attributes:
            if hasattr(shared_state, attr_name):
                attr_value = getattr(shared_state, attr_name)
                if attr_value is not None:
                    # Deep copy mutable objects to ensure isolation
                    if isinstance(attr_value, (list, dict)):
                        import copy
                        attr_value = copy.deepcopy(attr_value)
                    cow_state.set_attribute(attr_name, attr_value)
        
        # Always initialize current as None for new states
        cow_state.set_attribute('current', None)
    
    def _should_run_cleanup(self) -> bool:
        """Check if cleanup should be performed"""
        return (datetime.now() - self._last_cleanup).total_seconds() > self.cleanup_interval
    
    async def _async_cleanup(self) -> None:
        """Perform background cleanup operations"""
        self._last_cleanup = datetime.now()
        
        # Force garbage collection periodically
        await asyncio.get_event_loop().run_in_executor(
            self._cleanup_executor, self._force_gc_collection
        )
    
    def _force_gc_collection(self) -> None:
        """Force garbage collection and update stats"""
        collected = gc.collect()
        self._stats.last_gc_collection = datetime.now()
    
    def get_statistics(self) -> MemoryStats:
        """Get current pool statistics"""
        # Update active states count
        self._stats.active_states = len(self._active_states)
        self._stats.pool_size = len(self._pool)
        return self._stats
    
    def force_cleanup(self) -> Dict[str, int]:
        """Force immediate cleanup and return statistics"""
        initial_pool_size = len(self._pool)
        initial_active = len(self._active_states)
        
        # Clean up pool
        while self._pool:
            state = self._pool.popleft()
            state.cleanup_resources()
        
        # Force GC
        collected = gc.collect()
        
        self._stats.pool_size = 0
        self._stats.last_gc_collection = datetime.now()
        
        return {
            "pool_states_cleaned": initial_pool_size,
            "active_states": initial_active,
            "gc_objects_collected": collected
        }
    
    def __del__(self):
        """Cleanup on destruction"""
        try:
            self.force_cleanup()
            self._cleanup_executor.shutdown(wait=False)
        except Exception:
            pass


class ResourceTracker:
    """
    Track and automatically clean up workflow resources.
    
    Provides centralized resource management to prevent resource leaks
    in long-running workflows.
    """
    
    def __init__(self):
        self._resources: Dict[str, Dict[str, Any]] = {}
        self._cleanup_callbacks: Dict[str, List[Callable[[], None]]] = {}
        self._task_resources: Dict[int, Set[str]] = {}
        self._stats = {"total_tracked": 0, "total_cleaned": 0}
    
    def register_resource(self, resource_id: str, resource: Any, 
                         cleanup_callback: Optional[Callable[[], None]] = None,
                         category: str = "general") -> None:
        """
        Register a resource for tracking and cleanup.
        
        Args:
            resource_id: Unique identifier for the resource
            resource: The resource object to track
            cleanup_callback: Optional cleanup function
            category: Resource category for organization
        """
        self._resources[resource_id] = {
            "resource": resource,
            "category": category,
            "created_at": datetime.now(),
            "access_count": 0
        }
        
        if cleanup_callback:
            if resource_id not in self._cleanup_callbacks:
                self._cleanup_callbacks[resource_id] = []
            self._cleanup_callbacks[resource_id].append(cleanup_callback)
        
        self._stats["total_tracked"] += 1
    
    def register_task_resources(self, task_id: int, resource_ids: Union[str, List[str]]) -> None:
        """Associate resources with a specific task for batch cleanup"""
        if isinstance(resource_ids, str):
            resource_ids = [resource_ids]
        
        if task_id not in self._task_resources:
            self._task_resources[task_id] = set()
        
        self._task_resources[task_id].update(resource_ids)
    
    def cleanup_resource(self, resource_id: str) -> bool:
        """Clean up a specific resource"""
        if resource_id not in self._resources:
            return False
        
        # Run cleanup callbacks
        if resource_id in self._cleanup_callbacks:
            for callback in self._cleanup_callbacks[resource_id]:
                try:
                    callback()
                except Exception as e:
                    pass
        
        # Remove from tracking - handle potential race conditions
        try:
            del self._resources[resource_id]
            self._cleanup_callbacks.pop(resource_id, None)
            self._stats["total_cleaned"] += 1
        except KeyError:
            # Resource was already cleaned up by another thread
            return False
        
        return True
    
    def cleanup_task_resources(self, task_id: int) -> int:
        """Clean up all resources associated with a task"""
        if task_id not in self._task_resources:
            return 0
        
        resource_ids = self._task_resources[task_id].copy()
        cleaned_count = 0
        
        for resource_id in resource_ids:
            if self.cleanup_resource(resource_id):
                cleaned_count += 1
        
        del self._task_resources[task_id]
        return cleaned_count
    
    def cleanup_all_resources(self) -> int:
        """Clean up all tracked resources"""
        resource_ids = list(self._resources.keys())
        cleaned_count = 0
        
        for resource_id in resource_ids:
            if self.cleanup_resource(resource_id):
                cleaned_count += 1
        
        self._task_resources.clear()
        return cleaned_count
    
    def cleanup_by_category(self, category: str) -> int:
        """Clean up all resources in a specific category"""
        resource_ids = [
            rid for rid, data in self._resources.items() 
            if data["category"] == category
        ]
        
        cleaned_count = 0
        for resource_id in resource_ids:
            if self.cleanup_resource(resource_id):
                cleaned_count += 1
        
        return cleaned_count
    
    def cleanup_old_resources(self, max_age: timedelta) -> int:
        """Clean up resources older than specified age"""
        cutoff_time = datetime.now() - max_age
        old_resource_ids = [
            rid for rid, data in self._resources.items()
            if data["created_at"] < cutoff_time
        ]
        
        cleaned_count = 0
        for resource_id in old_resource_ids:
            if self.cleanup_resource(resource_id):
                cleaned_count += 1
        
        return cleaned_count
    
    def get_resource_stats(self) -> Dict[str, Any]:
        """Get resource tracking statistics"""
        categories = {}
        for data in self._resources.values():
            category = data["category"]
            categories[category] = categories.get(category, 0) + 1

        return {
            "total_tracked": len(self._resources),
            "by_category": categories,
            "active_tasks": len(self._task_resources),
            "total_ever_tracked": self._stats["total_tracked"],
            "total_cleaned": self._stats["total_cleaned"]
        }

    def release_resources(self, resource_name: str) -> int:
        """Release all resources associated with a given name/category.

        Args:
            resource_name: Name or category to release resources for

        Returns:
            Number of resources cleaned up
        """
        # Try by category first
        cleaned = self.cleanup_by_category(resource_name)

        # Also try direct resource ID
        if self.cleanup_resource(resource_name):
            cleaned += 1

        return cleaned

    def track_execution(self, execution_name: str):
        """Context manager for tracking resource usage during execution.

        Args:
            execution_name: Name of the execution to track

        Usage:
            with tracker.track_execution("my_node"):
                # resources allocated here will be tracked
                pass
        """
        from contextlib import contextmanager

        @contextmanager
        def _tracker():
            # Generate unique resource ID for this execution
            resource_id = f"execution_{execution_name}_{id(self)}"

            # Register the execution
            self.register_resource(
                resource_id=resource_id,
                resource={"name": execution_name, "type": "execution"},
                category=execution_name
            )

            try:
                yield resource_id
            finally:
                # Clean up execution resources
                self.cleanup_resource(resource_id)

        return _tracker()


class MemoryMonitor:
    """
    Monitor workflow memory usage and detect potential leaks.
    
    Provides memory pressure detection and automatic cleanup triggers.
    """
    
    def __init__(self, warning_threshold_mb: int = 500, critical_threshold_mb: int = 1000):
        self.warning_threshold = warning_threshold_mb * 1024 * 1024  # Convert to bytes
        self.critical_threshold = critical_threshold_mb * 1024 * 1024
        
        self._measurements: List[Dict[str, Any]] = []
        self._leak_patterns: List[Dict[str, Any]] = []
        
        # Try to import psutil for advanced memory monitoring
        try:
            import psutil
            self._process = psutil.Process()
            self._psutil_available = True
        except ImportError:
            self._psutil_available = False
    
    def take_memory_snapshot(self, label: str = "snapshot") -> Dict[str, Any]:
        """Take a snapshot of current memory usage"""
        snapshot = {
            "timestamp": datetime.now(),
            "label": label,
            "gc_stats": self._get_gc_stats()
        }
        
        if self._psutil_available:
            memory_info = self._process.memory_info()
            snapshot.update({
                "rss_bytes": memory_info.rss,
                "vms_bytes": memory_info.vms,
                "percent": self._process.memory_percent(),
                "available_bytes": self._get_available_memory()
            })
        
        self._measurements.append(snapshot)
        
        # Keep only recent measurements (last 100)
        if len(self._measurements) > 100:
            self._measurements = self._measurements[-100:]
        
        return snapshot
    
    def _get_gc_stats(self) -> Dict[str, int]:
        """Get garbage collector statistics"""
        return {
            f"generation_{i}": len(gc.get_objects(i))
            for i in range(gc.get_count().__len__())
        }
    
    def _get_available_memory(self) -> Optional[int]:
        """Get available system memory"""
        if self._psutil_available:
            try:
                import psutil
                return psutil.virtual_memory().available
            except Exception:
                pass
        return None
    
    def check_memory_pressure(self) -> Dict[str, Any]:
        """Check current memory pressure and return status"""
        if not self._measurements:
            self.take_memory_snapshot("pressure_check")
        
        latest = self._measurements[-1]
        pressure_status = {
            "timestamp": latest["timestamp"],
            "status": "normal",
            "memory_mb": 0,
            "recommendations": []
        }
        
        if self._psutil_available and "rss_bytes" in latest:
            memory_bytes = latest["rss_bytes"]
            memory_mb = memory_bytes / (1024 * 1024)
            pressure_status["memory_mb"] = memory_mb
            
            if memory_bytes >= self.critical_threshold:
                pressure_status["status"] = "critical"
                pressure_status["recommendations"].extend([
                    "Force garbage collection",
                    "Clear state pools",
                    "Reduce parallel task count"
                ])
            elif memory_bytes >= self.warning_threshold:
                pressure_status["status"] = "warning"
                pressure_status["recommendations"].extend([
                    "Consider garbage collection",
                    "Monitor state pool usage"
                ])
        
        return pressure_status
    
    def detect_memory_leaks(self, min_measurements: int = 10) -> List[Dict[str, Any]]:
        """Detect potential memory leak patterns"""
        if len(self._measurements) < min_measurements:
            return []
        
        leaks = []
        recent_measurements = self._measurements[-min_measurements:]
        
        if self._psutil_available:
            # Check for consistent memory growth
            memory_values = [m.get("rss_bytes", 0) for m in recent_measurements]
            if len(memory_values) >= min_measurements:
                # Simple trend detection
                growth_rate = (memory_values[-1] - memory_values[0]) / len(memory_values)
                
                if growth_rate > 1024 * 1024:  # > 1MB per measurement
                    leaks.append({
                        "type": "memory_growth",
                        "severity": "high" if growth_rate > 10 * 1024 * 1024 else "medium",
                        "growth_rate_mb_per_measurement": growth_rate / (1024 * 1024),
                        "total_growth_mb": (memory_values[-1] - memory_values[0]) / (1024 * 1024),
                        "measurements_analyzed": len(memory_values)
                    })
        
        # Check GC object growth
        gc_measurements = [m.get("gc_stats", {}) for m in recent_measurements]
        for generation in ["generation_0", "generation_1", "generation_2"]:
            values = [gc.get(generation, 0) for gc in gc_measurements if gc]
            if len(values) >= min_measurements:
                growth = values[-1] - values[0]
                if growth > 1000:  # Significant object growth
                    leaks.append({
                        "type": "gc_object_growth",
                        "generation": generation,
                        "severity": "medium",
                        "object_growth": growth,
                        "measurements_analyzed": len(values)
                    })
        
        self._leak_patterns.extend(leaks)
        return leaks
    
    def get_memory_report(self) -> Dict[str, Any]:
        """Generate comprehensive memory usage report"""
        if not self._measurements:
            self.take_memory_snapshot("report")
        
        latest = self._measurements[-1]
        report = {
            "timestamp": latest["timestamp"],
            "current_snapshot": latest,
            "pressure_status": self.check_memory_pressure(),
            "detected_leaks": self.detect_memory_leaks(),
            "measurement_count": len(self._measurements),
            "leak_patterns_found": len(self._leak_patterns)
        }
        
        if len(self._measurements) >= 2:
            first = self._measurements[0]
            report["session_growth"] = {
                "duration_minutes": (latest["timestamp"] - first["timestamp"]).total_seconds() / 60,
            }
            
            if self._psutil_available and "rss_bytes" in latest and "rss_bytes" in first:
                growth_bytes = latest["rss_bytes"] - first["rss_bytes"]
                report["session_growth"]["memory_growth_mb"] = growth_bytes / (1024 * 1024)
        
        return report
    
    def force_memory_cleanup(self) -> Dict[str, Any]:
        """Force memory cleanup and return results"""
        initial_snapshot = self.take_memory_snapshot("before_cleanup")
        
        # Force garbage collection
        collected_objects = gc.collect()
        
        final_snapshot = self.take_memory_snapshot("after_cleanup")
        
        cleanup_result = {
            "gc_objects_collected": collected_objects,
            "before_cleanup": initial_snapshot,
            "after_cleanup": final_snapshot
        }
        
        if self._psutil_available:
            initial_memory = initial_snapshot.get("rss_bytes", 0)
            final_memory = final_snapshot.get("rss_bytes", 0)
            memory_freed = initial_memory - final_memory
            
            cleanup_result["memory_freed_mb"] = memory_freed / (1024 * 1024)
            cleanup_result["memory_freed_bytes"] = memory_freed
        
        return cleanup_result


# Global instances for workflow memory management
_global_state_pool: Optional[StatePool] = None
_global_resource_tracker: Optional[ResourceTracker] = None
_global_memory_monitor: Optional[MemoryMonitor] = None


def get_state_pool() -> StatePool:
    """Get the global state pool instance"""
    global _global_state_pool
    if _global_state_pool is None:
        _global_state_pool = StatePool()
    return _global_state_pool


def get_resource_tracker() -> ResourceTracker:
    """Get the global resource tracker instance"""
    global _global_resource_tracker
    if _global_resource_tracker is None:
        _global_resource_tracker = ResourceTracker()
    return _global_resource_tracker


def get_memory_monitor() -> MemoryMonitor:
    """Get the global memory monitor instance"""
    global _global_memory_monitor
    if _global_memory_monitor is None:
        _global_memory_monitor = MemoryMonitor()
    return _global_memory_monitor


def cleanup_global_resources() -> Dict[str, Any]:
    """Clean up all global memory management resources"""
    results = {}
    
    if _global_state_pool:
        results["state_pool"] = _global_state_pool.force_cleanup()
    
    if _global_resource_tracker:
        results["resource_tracker"] = {
            "resources_cleaned": _global_resource_tracker.cleanup_all_resources()
        }
    
    if _global_memory_monitor:
        results["memory_monitor"] = _global_memory_monitor.force_memory_cleanup()
    
    return results