"""
Workflow Reporting System

Comprehensive workflow monitoring and observability leveraging existing 
WorkflowController.ExecutionHistory and inspired by SuiteForge reporting patterns.

Access via: sequence.controller.reporting
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Callable, cast
from datetime import datetime, timedelta
import json
import statistics
import traceback
import uuid
from pathlib import Path
import logging

from .execution import ExecutionEntry, ExecutionHistory


@dataclass
class WorkflowMetrics:
    """Comprehensive workflow execution metrics"""
    total_nodes_executed: int
    successful_executions: int
    failed_executions: int
    success_rate: float
    total_execution_time: float
    average_node_duration: float
    min_node_duration: float
    max_node_duration: float
    unique_nodes_count: int
    execution_start_time: Optional[datetime]
    execution_end_time: Optional[datetime]
    node_execution_counts: Dict[str, int]


@dataclass
class PerformanceSummary:
    """Performance analysis summary"""
    average_node_duration: float
    median_node_duration: float
    slowest_nodes: List[tuple]  # [(node_name, avg_duration), ...]
    fastest_nodes: List[tuple]  # [(node_name, avg_duration), ...]
    bottlenecks: List[str]  # Node names with performance issues
    performance_outliers: List[ExecutionEntry]
    total_workflow_time: float
    nodes_analyzed: int


@dataclass
class ExecutionStatus:
    """Real-time execution status"""
    controller_state: str  # ready, running, paused, stopped, completed, error
    current_execution_path: List[str]
    execution_depth: int
    total_executions: int
    running_time: float
    last_executed_node: Optional[str]
    current_node: Optional[str]
    is_active: bool


@dataclass
class ErrorReport:
    """Error analysis and categorization"""
    total_errors: int
    error_categories: Dict[str, int]  # {error_type: count}
    failed_nodes: List[str]
    error_details: List[Dict[str, Any]]
    error_rate: float
    most_common_errors: List[tuple]  # [(error_type, count), ...]


@dataclass
class BottleneckAnalysis:
    """Phase 4: Comprehensive bottleneck analysis and performance insights"""
    bottleneck_nodes: List[Dict[str, Any]]  # Nodes causing performance issues
    performance_outliers: List[Dict[str, Any]]  # Individual execution outliers
    resource_constraints: List[str]  # Identified resource constraints
    optimization_suggestions: List[str]  # Actionable optimization recommendations
    critical_path: List[str]  # Nodes on the performance-critical execution path
    performance_distribution: Dict[str, Any]  # Statistical performance distribution
    threshold_violations: List[Dict[str, Any]]  # Executions exceeding thresholds
    total_bottleneck_impact: float  # Total time impact of bottlenecks (seconds)


@dataclass
class PerformanceThreshold:
    """Phase 4: Performance threshold definition for monitoring"""
    node_name: Optional[str]  # None for global threshold
    max_duration: float  # Maximum allowed duration in seconds
    warning_duration: float  # Warning threshold in seconds
    alert_callback: Optional[Callable[[Dict[str, Any]], None]]  # Callback for threshold violations
    description: str  # Human-readable description of the threshold


@dataclass
class PerformanceAlert:
    """Phase 4: Performance alert triggered by threshold violation"""
    alert_id: str
    node_name: str
    execution_id: str
    threshold_name: str
    severity: str  # 'warning' or 'critical'
    actual_duration: float
    threshold_duration: float
    violation_factor: float  # actual / threshold
    timestamp: datetime
    message: str


@dataclass
class PerformanceTrend:
    """Phase 4: Performance trend analysis over time"""
    node_name: str
    trend_direction: str  # 'improving', 'degrading', 'stable'
    trend_strength: float  # -1.0 to 1.0, negative = degrading, positive = improving
    current_avg_duration: float
    historical_avg_duration: float
    change_percentage: float  # percentage change from historical average
    data_points: int  # number of executions analyzed
    confidence_level: float  # 0.0 to 1.0, confidence in trend analysis
    time_span_hours: float  # time span of data analyzed
    recent_outliers: int  # number of recent outliers detected


@dataclass
class PerformanceComparison:
    """Phase 4: Performance comparison between two time periods or node sets"""
    comparison_type: str  # 'temporal', 'node_to_node', 'baseline'
    baseline_name: str  # Name/description of baseline
    current_name: str   # Name/description of current period
    baseline_avg_duration: float
    current_avg_duration: float
    performance_change: float  # percentage change (positive = slower, negative = faster)
    significance_level: float  # statistical significance of the change (0.0 to 1.0)
    baseline_data_points: int
    current_data_points: int
    recommendation: str  # actionable recommendation based on comparison


class WorkflowMetricsCollector:
    """Collects and aggregates workflow metrics using SuiteForge patterns"""
    
    def __init__(self, execution_history: ExecutionHistory):
        self.execution_history = execution_history
    
    def collect_timing_metrics(self) -> Dict[str, Any]:
        """Collect timing-related metrics"""
        entries = [e for e in self.execution_history.entries if e.duration is not None]
        
        if not entries:
            return {
                "total_duration": 0.0,
                "average_duration": 0.0,
                "median_duration": 0.0,
                "duration_distribution": {}
            }
        
        durations: List[float] = [cast(float, e.duration) for e in entries if e.duration is not None]
        
        # Duration distribution (SuiteForge pattern)
        distribution = {
            "fast": len([d for d in durations if d < 0.01]),      # < 10ms
            "medium": len([d for d in durations if 0.01 <= d < 0.1]),  # 10-100ms
            "slow": len([d for d in durations if d >= 0.1])       # >= 100ms
        }
        
        return {
            "total_duration": sum(durations),
            "average_duration": statistics.mean(durations),
            "median_duration": statistics.median(durations),
            "duration_distribution": distribution
        }
    
    def collect_error_metrics(self) -> Dict[str, Any]:
        """Collect error-related metrics using SuiteForge error categorization"""
        error_entries = [e for e in self.execution_history.entries if e.is_error]
        
        error_categories = {}
        error_details = []
        
        for entry in error_entries:
            if entry.error:
                error_type = type(entry.error).__name__
                error_categories[error_type] = error_categories.get(error_type, 0) + 1
                
                # Get stack trace if available
                stack_trace = None
                if hasattr(entry.error, '__traceback__') and entry.error.__traceback__:
                    stack_trace = ''.join(traceback.format_exception(
                        type(entry.error), entry.error, entry.error.__traceback__
                    ))
                
                error_details.append({
                    "node_name": entry.node_name,
                    "error_type": error_type,
                    "error_message": str(entry.error),
                    "stack_trace": stack_trace,
                    "timestamp": entry.start_time.isoformat(),
                    "execution_id": entry.execution_id
                })
        
        return {
            "total_errors": len(error_entries),
            "error_categories": error_categories,
            "error_details": error_details,
            "error_rate": len(error_entries) / len(self.execution_history.entries) if self.execution_history.entries else 0.0
        }
    
    def collect_node_metrics(self) -> Dict[str, Any]:
        """Collect node-specific metrics"""
        node_stats = {}
        
        for entry in self.execution_history.entries:
            if entry.node_name not in node_stats:
                node_stats[entry.node_name] = {
                    "total_executions": 0,
                    "successful_executions": 0,
                    "failed_executions": 0,
                    "durations": []
                }
            
            stats = node_stats[entry.node_name]
            stats["total_executions"] += 1
            
            if entry.is_completed:
                stats["successful_executions"] += 1
            elif entry.is_error:
                stats["failed_executions"] += 1
            
            if entry.duration is not None:
                stats["durations"].append(entry.duration)
        
        # Calculate aggregated metrics for each node
        for node_name, stats in node_stats.items():
            if stats["durations"]:
                stats["average_duration"] = statistics.mean(stats["durations"])
                stats["success_rate"] = stats["successful_executions"] / stats["total_executions"]
            else:
                stats["average_duration"] = 0.0
                stats["success_rate"] = 0.0
        
        return node_stats


class WorkflowReportingSystem:
    """
    Comprehensive workflow reporting system using SuiteForge patterns
    
    Access via: sequence.controller.reporting
    """
    
    def __init__(self, controller):
        """Initialize reporting system with WorkflowController"""
        from .sequence.base import WorkflowController  # Avoid circular import
        
        self.controller: 'WorkflowController' = controller
        self._event_subscribers: List[Dict[str, Any]] = []
        self.metrics_collector = WorkflowMetricsCollector(controller.execution_history)
        
        # Phase 4: Performance threshold monitoring
        self.performance_thresholds: Dict[str, PerformanceThreshold] = {}
        self.performance_alerts: List[PerformanceAlert] = []
        self._global_threshold: Optional[PerformanceThreshold] = None
        
    def get_execution_metrics(self) -> WorkflowMetrics:
        """Get comprehensive execution metrics using ExecutionHistory data"""
        history = self.controller.execution_history
        
        if not history.entries:
            return WorkflowMetrics(
                total_nodes_executed=0,
                successful_executions=0,
                failed_executions=0,
                success_rate=0.0,
                total_execution_time=0.0,
                average_node_duration=0.0,
                min_node_duration=0.0,
                max_node_duration=0.0,
                unique_nodes_count=0,
                execution_start_time=None,
                execution_end_time=None,
                node_execution_counts={}
            )
        # Calculate metrics from ExecutionHistory
        total_nodes = len(history.entries)
        successful = len([e for e in history.entries if e.is_completed])
        failed = len([e for e in history.entries if e.is_error])
        success_rate = successful / total_nodes if total_nodes > 0 else 0.0
        
        # Duration calculations
        completed_entries = [e for e in history.entries if e.duration is not None]
        if completed_entries:
            durations: List[float] = [cast(float, e.duration) for e in completed_entries]
            avg_duration = statistics.mean(durations)
            min_duration = min(durations)
            max_duration = max(durations)
        else:
            avg_duration = min_duration = max_duration = 0.0
        
        # Execution time window
        start_time = min(e.start_time for e in history.entries) if history.entries else None
        end_time = max(e.end_time for e in history.entries if e.end_time) if history.entries else None
        total_time = (end_time - start_time).total_seconds() if start_time and end_time else 0.0
        
        # Unique nodes
        unique_nodes = len(set(e.node_name for e in history.entries))
        
        return WorkflowMetrics(
            total_nodes_executed=total_nodes,
            successful_executions=successful,
            failed_executions=failed,
            success_rate=success_rate,
            total_execution_time=total_time,
            average_node_duration=avg_duration,
            min_node_duration=min_duration,
            max_node_duration=max_duration,
            unique_nodes_count=unique_nodes,
            execution_start_time=start_time,
            execution_end_time=end_time,
            node_execution_counts=history._node_counts.copy()
        )
    
    def get_performance_summary(self) -> PerformanceSummary:
        """Get performance analysis summary with timing analysis"""
        history = self.controller.execution_history
        
        if not history.entries:
            return PerformanceSummary(
                average_node_duration=0.0,
                median_node_duration=0.0,
                slowest_nodes=[],
                fastest_nodes=[],
                bottlenecks=[],
                performance_outliers=[],
                total_workflow_time=0.0,
                nodes_analyzed=0
            )
        # Analyze completed entries only
        completed_entries = [e for e in history.entries if e.duration is not None]
        
        if not completed_entries:
            return PerformanceSummary(
                average_node_duration=0.0,
                median_node_duration=0.0,
                slowest_nodes=[],
                fastest_nodes=[],
                bottlenecks=[],
                performance_outliers=[],
                total_workflow_time=self.controller.total_execution_time,
                nodes_analyzed=0
            )
        # Duration statistics
        durations = [e.duration for e in completed_entries if e.duration is not None]
        avg_duration = statistics.mean(durations)
        median_duration = statistics.median(durations)
        
        # Node performance analysis
        node_durations = {}
        for entry in completed_entries:
            if entry.node_name not in node_durations:
                node_durations[entry.node_name] = []
            node_durations[entry.node_name].append(entry.duration)
        
        # Calculate average duration per node
        node_avg_durations = {}
        for node_name, durations in node_durations.items():
            node_avg_durations[node_name] = statistics.mean(durations)
        
        # Sort nodes by performance
        sorted_nodes = sorted(node_avg_durations.items(), key=lambda x: x[1])
        slowest_nodes = sorted_nodes[-5:][::-1]  # Top 5 slowest
        fastest_nodes = sorted_nodes[:5]  # Top 5 fastest
        
        # Identify bottlenecks (nodes significantly slower than average)
        bottlenecks = []
        threshold = avg_duration * 2.0  # 2x slower than average
        for node_name, avg_dur in node_avg_durations.items():
            if avg_dur > threshold:
                bottlenecks.append(node_name)
        
        # Find performance outliers
        outliers = []
        for entry in completed_entries:
            if entry.duration is not None and entry.duration > avg_duration * 3.0:  # 3x slower than average
                outliers.append(entry)
        
        return PerformanceSummary(
            average_node_duration=avg_duration,
            median_node_duration=median_duration,
            slowest_nodes=slowest_nodes,
            fastest_nodes=fastest_nodes,
            bottlenecks=bottlenecks,
            performance_outliers=outliers,
            total_workflow_time=self.controller.total_execution_time,
            nodes_analyzed=len(completed_entries)
        )
    
    def get_error_analysis(self) -> ErrorReport:
        """Get comprehensive error analysis using SuiteForge error categorization"""
        error_metrics = self.metrics_collector.collect_error_metrics()
        
        # Sort error categories by frequency
        sorted_errors = sorted(error_metrics["error_categories"].items(), 
                              key=lambda x: x[1], reverse=True)
        
        # Get failed node names
        failed_nodes = list(set([
            detail["node_name"] for detail in error_metrics["error_details"]
        ]))
        
        return ErrorReport(
            total_errors=error_metrics["total_errors"],
            error_categories=error_metrics["error_categories"],
            failed_nodes=failed_nodes,
            error_details=error_metrics["error_details"],
            error_rate=error_metrics["error_rate"],
            most_common_errors=sorted_errors[:5]  # Top 5 most common errors
        )
    
    def get_bottleneck_analysis(self, outlier_threshold: float = 2.0, 
                               bottleneck_multiplier: float = 2.5) -> BottleneckAnalysis:
        """Phase 4: Get comprehensive bottleneck analysis with performance insights"""
        history = self.controller.execution_history
        
        if not history.entries:
            return BottleneckAnalysis(
                bottleneck_nodes=[],
                performance_outliers=[],
                resource_constraints=[],
                optimization_suggestions=[],
                critical_path=[],
                performance_distribution={},
                threshold_violations=[],
                total_bottleneck_impact=0.0
            )
        
        # Analyze completed entries only
        completed_entries = [e for e in history.entries if e.duration is not None and e.is_completed]
        
        if not completed_entries:
            return BottleneckAnalysis(
                bottleneck_nodes=[],
                performance_outliers=[],
                resource_constraints=["Insufficient execution data"],
                optimization_suggestions=["Execute workflow to gather performance data"],
                critical_path=[],
                performance_distribution={},
                threshold_violations=[],
                total_bottleneck_impact=0.0
            )
        
        # Calculate baseline performance metrics
        durations: List[float] = [cast(float, e.duration) for e in completed_entries if e.duration is not None]
        mean_duration = statistics.mean(durations)
        median_duration = statistics.median(durations)
        stdev_duration = statistics.stdev(durations) if len(durations) > 1 else 0.0
        
        # Performance distribution analysis
        distribution = {
            "mean": mean_duration,
            "median": median_duration,
            "std_dev": stdev_duration,
            "min": min(durations),
            "max": max(durations),
            "p95": sorted(durations)[int(len(durations) * 0.95)] if len(durations) > 20 else max(durations),
            "total_entries": len(completed_entries)
        }
        
        # 1. Identify performance outliers
        outliers = []
        for entry in completed_entries:
            if entry.is_performance_outlier(threshold=outlier_threshold, history=history):
                outlier_info = {
                    "node_name": entry.node_name,
                    "effective_name": entry.effective_name,
                    "execution_id": entry.execution_id,
                    "duration": entry.duration,
                    "z_score": ((entry.duration - mean_duration) / stdev_duration) if (entry.duration is not None and stdev_duration > 0) else 0.0,
                    "execution_position": entry.execution_position,
                    "timestamp": entry.start_time.isoformat() if entry.start_time else None,
                    "impact_factor": (entry.duration / mean_duration) if (entry.duration is not None and mean_duration > 0) else 1.0
                }
                outliers.append(outlier_info)
        
        # 2. Identify bottleneck nodes (consistently slow)
        node_performance = {}
        for entry in completed_entries:
            canonical = entry.canonical_name or entry.node_name
            if canonical not in node_performance:
                node_performance[canonical] = []
            node_performance[canonical].append(entry.duration)
        
        bottleneck_nodes = []
        total_bottleneck_impact = 0.0
        
        for node_name, durations in node_performance.items():
            if len(durations) < 2:  # Need multiple executions for analysis
                continue
                
            node_mean = statistics.mean(durations)
            node_median = statistics.median(durations)
            
            # Node is a bottleneck if it's consistently slower than overall average
            if node_mean > mean_duration * bottleneck_multiplier:
                impact = (node_mean - mean_duration) * len(durations)
                total_bottleneck_impact += impact
                
                bottleneck_info = {
                    "node_name": node_name,
                    "avg_duration": node_mean,
                    "median_duration": node_median,
                    "execution_count": len(durations),
                    "performance_ratio": node_mean / mean_duration if mean_duration > 0 else 1.0,
                    "total_time_impact": impact,
                    "worst_execution": max(durations),
                    "best_execution": min(durations)
                }
                bottleneck_nodes.append(bottleneck_info)
        
        # Sort bottlenecks by impact
        bottleneck_nodes.sort(key=lambda x: x["total_time_impact"], reverse=True)
        
        # 3. Identify critical path (most time-consuming execution sequence)
        # For now, identify nodes that appear most frequently in slow executions
        critical_nodes = set()
        slow_threshold = mean_duration * 1.5
        
        for entry in completed_entries:
            if entry.duration is not None and entry.duration > slow_threshold:
                critical_nodes.add(entry.effective_name)
        
        critical_path = list(critical_nodes)
        
        # 4. Identify resource constraints
        constraints = []
        
        # High standard deviation suggests inconsistent performance
        if stdev_duration > mean_duration * 0.5:
            constraints.append("High performance variability detected - possible resource contention")
        
        # Large gap between mean and median suggests outlier skew
        if abs(mean_duration - median_duration) > mean_duration * 0.3:
            constraints.append("Performance distribution skewed by outliers")
        
        # Many bottlenecks suggest systemic issues
        if len(bottleneck_nodes) > len(node_performance) * 0.3:
            constraints.append("Multiple bottleneck nodes detected - consider workflow redesign")
        
        # 5. Generate optimization suggestions
        suggestions = []
        
        if bottleneck_nodes:
            top_bottleneck = bottleneck_nodes[0]
            suggestions.append(f"Optimize '{top_bottleneck['node_name']}' - highest performance impact ({top_bottleneck['total_time_impact']:.3f}s)")
        
        if outliers:
            suggestions.append(f"Investigate {len(outliers)} performance outliers for intermittent issues")
        
        if stdev_duration > mean_duration:
            suggestions.append("High performance variance - consider adding performance monitoring and alerting")
        
        if not suggestions:
            suggestions.append("Performance appears stable - continue monitoring")
        
        # 6. Identify threshold violations
        violations = []
        high_threshold = mean_duration * 3.0  # 3x average is concerning
        
        for entry in completed_entries:
            if entry.duration is not None and entry.duration > high_threshold:
                violations.append({
                    "node_name": entry.node_name,
                    "effective_name": entry.effective_name,
                    "execution_id": entry.execution_id,
                    "duration": entry.duration,
                    "threshold": high_threshold,
                    "violation_factor": entry.duration / high_threshold,
                    "timestamp": entry.start_time.isoformat() if entry.start_time else None
                })
        
        return BottleneckAnalysis(
            bottleneck_nodes=bottleneck_nodes,
            performance_outliers=outliers,
            resource_constraints=constraints,
            optimization_suggestions=suggestions,
            critical_path=critical_path,
            performance_distribution=distribution,
            threshold_violations=violations,
            total_bottleneck_impact=total_bottleneck_impact
        )
    
    def add_performance_threshold(self, name: str, threshold: PerformanceThreshold) -> None:
        """Phase 4: Add a performance threshold for monitoring"""
        self.performance_thresholds[name] = threshold
        if threshold.node_name is None:
            self._global_threshold = threshold
    
    def set_global_threshold(self, max_duration: float, warning_duration: float, 
                           description: str = "Global performance threshold",
                           alert_callback: Optional[Callable[[Dict[str, Any]], None]] = None) -> None:
        """Phase 4: Set global performance threshold for all nodes"""
        threshold = PerformanceThreshold(
            node_name=None,
            max_duration=max_duration,
            warning_duration=warning_duration,
            alert_callback=alert_callback,
            description=description
        )
        self.add_performance_threshold("global", threshold)
    
    def set_node_threshold(self, node_name: str, max_duration: float, warning_duration: float,
                          description: Optional[str] = None,
                          alert_callback: Optional[Callable[[Dict[str, Any]], None]] = None) -> None:
        """Phase 4: Set performance threshold for a specific node"""
        if description is None:
            description = f"Performance threshold for {node_name}"
            
        threshold = PerformanceThreshold(
            node_name=node_name,
            max_duration=max_duration,
            warning_duration=warning_duration,
            alert_callback=alert_callback,
            description=description
        )
        self.add_performance_threshold(f"node_{node_name}", threshold)
    
    def check_performance_thresholds(self, execution_entry: ExecutionEntry) -> List[PerformanceAlert]:
        """Phase 4: Check an execution entry against all applicable thresholds"""
        alerts = []
        
        if not execution_entry.duration or not execution_entry.is_completed:
            return alerts
        
        # Check node-specific thresholds first
        node_threshold_key = f"node_{execution_entry.node_name}"
        if node_threshold_key in self.performance_thresholds:
            threshold = self.performance_thresholds[node_threshold_key]
            alert = self._check_single_threshold(execution_entry, threshold, node_threshold_key)
            if alert:
                alerts.append(alert)
        
        # Check global threshold if no node-specific threshold matched
        elif self._global_threshold:
            alert = self._check_single_threshold(execution_entry, self._global_threshold, "global")
            if alert:
                alerts.append(alert)
        
        # Store alerts for later retrieval
        self.performance_alerts.extend(alerts)
        
        return alerts
    
    def _check_single_threshold(self, entry: ExecutionEntry, threshold: PerformanceThreshold, 
                               threshold_name: str) -> Optional[PerformanceAlert]:
        """Check execution entry against a single threshold"""
        if not entry.duration:
            return None
        
        # Determine severity and threshold value
        if entry.duration > threshold.max_duration:
            severity = "critical"
            threshold_value = threshold.max_duration
            message = f"Critical: {entry.node_name} execution exceeded maximum threshold"
        elif entry.duration > threshold.warning_duration:
            severity = "warning"
            threshold_value = threshold.warning_duration
            message = f"Warning: {entry.node_name} execution exceeded warning threshold"
        else:
            return None  # No violation
        
        # Create alert
        alert = PerformanceAlert(
            alert_id=f"{entry.execution_id}_{threshold_name}_{severity}",
            node_name=entry.node_name,
            execution_id=entry.execution_id,
            threshold_name=threshold_name,
            severity=severity,
            actual_duration=entry.duration,
            threshold_duration=threshold_value,
            violation_factor=entry.duration / threshold_value,
            timestamp=entry.end_time or datetime.now(),
            message=message
        )
        # Trigger callback if provided
        if threshold.alert_callback:
            try:
                alert_data = {
                    "alert": alert,
                    "entry": entry,
                    "threshold": threshold
                }
                threshold.alert_callback(alert_data)
            except Exception as e:
                # Don't let callback errors break the monitoring
                pass
        
        return alert
    
    def get_recent_alerts(self, limit: int = 50, severity: Optional[str] = None) -> List[PerformanceAlert]:
        """Phase 4: Get recent performance alerts, optionally filtered by severity"""
        alerts = self.performance_alerts
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        # Sort by timestamp (most recent first)
        alerts.sort(key=lambda a: a.timestamp, reverse=True)
        
        return alerts[:limit]
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Phase 4: Get summary of performance alerts"""
        if not self.performance_alerts:
            return {
                "total_alerts": 0,
                "critical_alerts": 0,
                "warning_alerts": 0,
                "most_frequent_violators": [],
                "alert_rate": 0.0
            }
        
        critical_count = len([a for a in self.performance_alerts if a.severity == "critical"])
        warning_count = len([a for a in self.performance_alerts if a.severity == "warning"])
        
        # Find most frequent violators
        node_violations = {}
        for alert in self.performance_alerts:
            node_violations[alert.node_name] = node_violations.get(alert.node_name, 0) + 1
        
        frequent_violators = sorted(node_violations.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Calculate alert rate (alerts per execution)
        total_executions = len(self.controller.execution_history.entries)
        alert_rate = len(self.performance_alerts) / total_executions if total_executions > 0 else 0.0
        
        return {
            "total_alerts": len(self.performance_alerts),
            "critical_alerts": critical_count,
            "warning_alerts": warning_count,
            "most_frequent_violators": frequent_violators,
            "alert_rate": alert_rate
        }
    
    def clear_alerts(self) -> None:
        """Phase 4: Clear all stored performance alerts"""
        self.performance_alerts.clear()
    
    def get_performance_trends(self, lookback_hours: float = 24.0, 
                              min_executions: int = 5) -> Dict[str, PerformanceTrend]:
        """Phase 4: Analyze performance trends over time for each node
        
        Args:
            lookback_hours: How far back to look for trend analysis (default: 24 hours)
            min_executions: Minimum executions needed for trend analysis (default: 5)
            
        Returns:
            Dictionary mapping node names to their performance trends
        """
        history = self.controller.execution_history
        
        if not history.entries:
            return {}
        
        # Filter entries to specified time window
        cutoff_time = datetime.now() - timedelta(hours=lookback_hours)
        recent_entries = [
            entry for entry in history.entries
            if (entry.start_time and entry.start_time >= cutoff_time and 
                entry.duration is not None and entry.is_completed)
        ]
        
        if not recent_entries:
            return {}
        
        # Group entries by canonical node name
        node_groups = {}
        for entry in recent_entries:
            canonical = entry.canonical_name or entry.node_name
            if canonical not in node_groups:
                node_groups[canonical] = []
            node_groups[canonical].append(entry)
        
        # Analyze trends for each node
        trends = {}
        for node_name, entries in node_groups.items():
            if len(entries) < min_executions:
                continue  # Skip nodes with insufficient data
            
            trend = self._analyze_node_trend(node_name, entries, lookback_hours)
            if trend:
                trends[node_name] = trend
        
        return trends
    
    def _analyze_node_trend(self, node_name: str, entries: List[ExecutionEntry], 
                           time_span_hours: float) -> Optional[PerformanceTrend]:
        """Analyze performance trend for a single node"""
        if len(entries) < 3:
            return None
        
        # Sort entries by time
        entries.sort(key=lambda e: e.start_time or datetime.min)
        
        # Split into historical and recent data
        split_point = len(entries) // 2
        historical_entries = entries[:split_point]
        recent_entries = entries[split_point:]
        
        # Calculate averages
        historical_durations = [e.duration for e in historical_entries if e.duration]
        recent_durations = [e.duration for e in recent_entries if e.duration]
        
        if not historical_durations or not recent_durations:
            return None
        
        historical_avg = statistics.mean(historical_durations)
        current_avg = statistics.mean(recent_durations)
        
        # Calculate trend metrics
        change_percentage = ((current_avg - historical_avg) / historical_avg) * 100 if historical_avg > 0 else 0.0
        
        # Determine trend direction and strength
        if abs(change_percentage) < 5.0:  # Less than 5% change is considered stable
            trend_direction = "stable"
            trend_strength = 0.0
        elif change_percentage > 0:
            trend_direction = "degrading"  # Higher duration = worse performance
            trend_strength = min(-change_percentage / 100.0, -1.0)  # Negative for degrading
        else:
            trend_direction = "improving"  # Lower duration = better performance
            trend_strength = min(-change_percentage / 100.0, 1.0)  # Positive for improving
        
        # Calculate confidence based on data consistency and sample size
        # More data points and lower variance = higher confidence
        all_durations = historical_durations + recent_durations
        variance = statistics.variance(all_durations) if len(all_durations) > 1 else 0.0
        coefficient_of_variation = (variance ** 0.5) / statistics.mean(all_durations) if statistics.mean(all_durations) > 0 else 1.0
        
        # Confidence factors
        data_factor = min(len(entries) / 20.0, 1.0)  # More data = higher confidence
        consistency_factor = max(0.0, 1.0 - coefficient_of_variation)  # Lower variation = higher confidence
        significance_factor = min(abs(change_percentage) / 50.0, 1.0)  # Larger changes = higher confidence
        
        confidence_level = (data_factor + consistency_factor + significance_factor) / 3.0
        
        # Count recent outliers
        recent_outliers = 0
        for entry in recent_entries:
            if entry.is_performance_outlier(threshold=2.0, history=self.controller.execution_history):
                recent_outliers += 1
        
        return PerformanceTrend(
            node_name=node_name,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            current_avg_duration=current_avg,
            historical_avg_duration=historical_avg,
            change_percentage=change_percentage,
            data_points=len(entries),
            confidence_level=confidence_level,
            time_span_hours=time_span_hours,
            recent_outliers=recent_outliers
        )
    
    def get_trending_summary(self, lookback_hours: float = 24.0) -> Dict[str, Any]:
        """Phase 4: Get summary of performance trends across all nodes"""
        trends = self.get_performance_trends(lookback_hours)
        
        if not trends:
            return {
                "total_nodes_analyzed": 0,
                "improving_nodes": [],
                "degrading_nodes": [],
                "stable_nodes": [],
                "high_confidence_trends": [],
                "nodes_with_outliers": [],
                "overall_system_trend": "insufficient_data"
            }
        
        # Categorize trends
        improving = [name for name, trend in trends.items() if trend.trend_direction == "improving"]
        degrading = [name for name, trend in trends.items() if trend.trend_direction == "degrading"]
        stable = [name for name, trend in trends.items() if trend.trend_direction == "stable"]
        
        # High confidence trends (confidence > 0.7)
        high_confidence = [
            name for name, trend in trends.items() 
            if trend.confidence_level > 0.7
        ]
        
        # Nodes with recent outliers
        nodes_with_outliers = [
            name for name, trend in trends.items()
            if trend.recent_outliers > 0
        ]
        
        # Overall system trend (average of all trend strengths)
        if trends:
            avg_trend_strength = statistics.mean([trend.trend_strength for trend in trends.values()])
            if avg_trend_strength < -0.1:
                overall_trend = "degrading"
            elif avg_trend_strength > 0.1:
                overall_trend = "improving"
            else:
                overall_trend = "stable"
        else:
            overall_trend = "insufficient_data"
        
        return {
            "total_nodes_analyzed": len(trends),
            "improving_nodes": improving,
            "degrading_nodes": degrading,
            "stable_nodes": stable,
            "high_confidence_trends": high_confidence,
            "nodes_with_outliers": nodes_with_outliers,
            "overall_system_trend": overall_trend
        }
    
    def compare_time_periods(self, node_name: str, recent_hours: float = 2.0, 
                           baseline_hours: float = 24.0) -> Optional[PerformanceComparison]:
        """Phase 4: Compare performance between recent and historical time periods
        
        Args:
            node_name: Name of node to compare
            recent_hours: Hours to look back for recent performance
            baseline_hours: Hours to look back for baseline (should be > recent_hours)
            
        Returns:
            Performance comparison or None if insufficient data
        """
        history = self.controller.execution_history
        now = datetime.now()
        
        # Get recent entries
        recent_cutoff = now - timedelta(hours=recent_hours)
        recent_entries = [
            entry for entry in history.entries
            if (entry.start_time and entry.start_time >= recent_cutoff and
                entry.duration is not None and entry.is_completed and
                (entry.canonical_name or entry.node_name) == node_name)
        ]
        
        # Get baseline entries (excluding recent period)
        baseline_cutoff = now - timedelta(hours=baseline_hours)
        baseline_entries = [
            entry for entry in history.entries
            if (entry.start_time and baseline_cutoff <= entry.start_time < recent_cutoff and
                entry.duration is not None and entry.is_completed and
                (entry.canonical_name or entry.node_name) == node_name)
        ]
        
        if len(recent_entries) < 2 or len(baseline_entries) < 2:
            return None  # Insufficient data for comparison
        
        # Calculate averages
        recent_avg = statistics.mean([cast(float, e.duration) for e in recent_entries])
        baseline_avg = statistics.mean([cast(float, e.duration) for e in baseline_entries])
        
        # Calculate performance change
        performance_change = ((recent_avg - baseline_avg) / baseline_avg) * 100 if baseline_avg > 0 else 0.0
        
        # Calculate statistical significance using simple variance comparison
        recent_durations: List[float] = [cast(float, e.duration) for e in recent_entries]
        baseline_durations: List[float] = [cast(float, e.duration) for e in baseline_entries]
        
        # Simple significance test based on overlapping confidence intervals
        recent_std = statistics.stdev(recent_durations) if len(recent_durations) > 1 else 0.0
        baseline_std = statistics.stdev(baseline_durations) if len(baseline_durations) > 1 else 0.0
        
        # Rough significance estimate (higher when difference is large relative to variance)
        pooled_std = ((recent_std + baseline_std) / 2) if (recent_std + baseline_std) > 0 else 1.0
        significance = min(abs(performance_change) / (pooled_std * 100), 1.0)
        
        # Generate recommendation
        if abs(performance_change) < 5.0:
            recommendation = "Performance is stable - no action needed"
        elif performance_change > 15.0:
            recommendation = f"Performance degraded significantly by {performance_change:.1f}% - investigate recent changes"
        elif performance_change < -15.0:
            recommendation = f"Performance improved significantly by {abs(performance_change):.1f}% - document optimizations"
        elif performance_change > 0:
            recommendation = f"Minor performance degradation ({performance_change:.1f}%) - monitor closely"
        else:
            recommendation = f"Minor performance improvement ({abs(performance_change):.1f}%) - trending positive"
        
        return PerformanceComparison(
            comparison_type="temporal",
            baseline_name=f"Baseline ({baseline_hours-recent_hours:.1f}h ago)",
            current_name=f"Recent ({recent_hours:.1f}h)",
            baseline_avg_duration=baseline_avg,
            current_avg_duration=recent_avg,
            performance_change=performance_change,
            significance_level=significance,
            baseline_data_points=len(baseline_entries),
            current_data_points=len(recent_entries),
            recommendation=recommendation
        )
    
    def compare_nodes(self, node1_name: str, node2_name: str, 
                     lookback_hours: float = 24.0) -> Optional[PerformanceComparison]:
        """Phase 4: Compare performance between two different nodes
        
        Args:
            node1_name: Name of first node (baseline)
            node2_name: Name of second node (comparison)
            lookback_hours: Hours to look back for data
            
        Returns:
            Performance comparison or None if insufficient data
        """
        history = self.controller.execution_history
        cutoff_time = datetime.now() - timedelta(hours=lookback_hours)
        
        # Get entries for both nodes
        node1_entries = [
            entry for entry in history.entries
            if (entry.start_time and entry.start_time >= cutoff_time and
                entry.duration is not None and entry.is_completed and
                (entry.canonical_name or entry.node_name) == node1_name)
        ]
        
        node2_entries = [
            entry for entry in history.entries
            if (entry.start_time and entry.start_time >= cutoff_time and
                entry.duration is not None and entry.is_completed and
                (entry.canonical_name or entry.node_name) == node2_name)
        ]
        
        if len(node1_entries) < 2 or len(node2_entries) < 2:
            return None  # Insufficient data for comparison
        
        # Calculate averages
        node1_avg = statistics.mean([cast(float, e.duration) for e in node1_entries])
        node2_avg = statistics.mean([cast(float, e.duration) for e in node2_entries])
        
        # Calculate relative performance (node2 vs node1)
        performance_change = ((node2_avg - node1_avg) / node1_avg) * 100 if node1_avg > 0 else 0.0
        
        # Calculate significance
        node1_std = statistics.stdev([cast(float, e.duration) for e in node1_entries]) if len(node1_entries) > 1 else 0.0
        node2_std = statistics.stdev([cast(float, e.duration) for e in node2_entries]) if len(node2_entries) > 1 else 0.0
        pooled_std = ((node1_std + node2_std) / 2) if (node1_std + node2_std) > 0 else 1.0
        significance = min(abs(performance_change) / (pooled_std * 100), 1.0)
        
        # Generate recommendation
        if abs(performance_change) < 10.0:
            recommendation = f"{node1_name} and {node2_name} have similar performance"
        elif performance_change > 25.0:
            recommendation = f"{node2_name} is significantly slower than {node1_name} - consider optimizing"
        elif performance_change < -25.0:
            recommendation = f"{node2_name} is significantly faster than {node1_name} - consider applying optimizations to {node1_name}"
        elif performance_change > 0:
            recommendation = f"{node2_name} is moderately slower than {node1_name}"
        else:
            recommendation = f"{node2_name} is moderately faster than {node1_name}"
        
        return PerformanceComparison(
            comparison_type="node_to_node",
            baseline_name=node1_name,
            current_name=node2_name,
            baseline_avg_duration=node1_avg,
            current_avg_duration=node2_avg,
            performance_change=performance_change,
            significance_level=significance,
            baseline_data_points=len(node1_entries),
            current_data_points=len(node2_entries),
            recommendation=recommendation
        )
    
    def compare_to_baseline(self, node_name: str, baseline_duration: float,
                           lookback_hours: float = 24.0) -> Optional[PerformanceComparison]:
        """Phase 4: Compare current performance to a known baseline duration
        
        Args:
            node_name: Name of node to compare
            baseline_duration: Target/expected duration in seconds
            lookback_hours: Hours to look back for current performance data
            
        Returns:
            Performance comparison or None if insufficient data
        """
        history = self.controller.execution_history
        cutoff_time = datetime.now() - timedelta(hours=lookback_hours)
        
        # Get recent entries for the node
        entries = [
            entry for entry in history.entries
            if (entry.start_time and entry.start_time >= cutoff_time and
                entry.duration is not None and entry.is_completed and
                (entry.canonical_name or entry.node_name) == node_name)
        ]
        
        if len(entries) < 2:
            return None  # Insufficient data for comparison
        
        # Calculate current average
        current_avg = statistics.mean([cast(float, e.duration) for e in entries])
        
        # Calculate performance change
        performance_change = ((current_avg - baseline_duration) / baseline_duration) * 100 if baseline_duration > 0 else 0.0
        
        # Calculate significance based on consistency of measurements
        current_std = statistics.stdev([cast(float, e.duration) for e in entries]) if len(entries) > 1 else 0.0
        significance = min(abs(performance_change) / 50.0, 1.0) if current_std < current_avg * 0.5 else 0.5
        
        # Generate recommendation
        if abs(performance_change) < 10.0:
            recommendation = f"{node_name} performance is within acceptable range of baseline"
        elif performance_change > 30.0:
            recommendation = f"{node_name} is significantly slower than baseline - urgent optimization needed"
        elif performance_change > 15.0:
            recommendation = f"{node_name} is slower than baseline - optimization recommended"
        elif performance_change < -15.0:
            recommendation = f"{node_name} is performing better than baseline - excellent"
        else:
            recommendation = f"{node_name} performance is close to baseline"
        
        return PerformanceComparison(
            comparison_type="baseline",
            baseline_name="Target Baseline",
            current_name=f"Current ({lookback_hours:.1f}h avg)",
            baseline_avg_duration=baseline_duration,
            current_avg_duration=current_avg,
            performance_change=performance_change,
            significance_level=significance,
            baseline_data_points=1,  # Baseline is a single target value
            current_data_points=len(entries),
            recommendation=recommendation
        )

    
    def get_live_status(self) -> ExecutionStatus:
        """Phase 3: Get real-time execution status using existing controller state"""
        controller = self.controller
        
        # Calculate running time
        running_time = 0.0
        if hasattr(controller, 'total_execution_time'):
            running_time = controller.total_execution_time
        
        # Get current and last executed nodes
        current_node = None
        last_executed_node = None
        
        if controller.current_execution_path:
            current_node = controller.current_execution_path[-1]  # Last node in path
        
        if controller.execution_history.entries:
            last_entry = controller.execution_history.entries[-1]
            last_executed_node = last_entry.effective_name
        
        # Determine if workflow is actively executing
        is_active = controller.state in ['running', 'paused']
        
        return ExecutionStatus(
            controller_state=controller.state,
            current_execution_path=controller.current_execution_path.copy(),
            execution_depth=controller.execution_depth,
            total_executions=len(controller.execution_history.entries),
            running_time=running_time,
            last_executed_node=last_executed_node,
            current_node=current_node,
            is_active=is_active
        )
    
    def get_execution_flow_diagram(self, highlight_current: bool = True, 
                                  show_performance: bool = False) -> str:
        """Phase 3: Get Mermaid flow diagram with current execution position highlighting
        
        Args:
            highlight_current: Whether to highlight the current execution position
            show_performance: Whether to include performance metrics in the diagram
            
        Returns:
            Mermaid diagram string with execution state indicators
        """
        # Get the base Mermaid diagram
        base_diagram = self.controller.workflow.get_schema(format="mermaid", mode="full")
        
        if not highlight_current and not show_performance:
            return base_diagram
        
        # Parse the Mermaid diagram to enhance it
        lines = base_diagram.split('\n')
        enhanced_lines = []
        
        # Get current execution status
        status = self.get_live_status()
        current_node = status.current_node
        execution_path = status.current_execution_path
        
        # Get performance data if requested
        performance_data = {}
        if show_performance:
            for entry in self.controller.execution_history.entries:
                if entry.duration and entry.is_completed:
                    node_name = entry.effective_name
                    if node_name not in performance_data:
                        performance_data[node_name] = []
                    performance_data[node_name].append(entry.duration)
        
        for line in lines:
            enhanced_line = line
            
            # Skip mermaid wrapper lines
            if line.strip() in ['```mermaid', '```', 'graph TD']:
                enhanced_lines.append(line)
                continue
            
            # Process node definitions and connections
            if '-->' in line or '[]' in line:
                enhanced_line = self._enhance_mermaid_line(
                    line, current_node, execution_path, performance_data, 
                    status.controller_state
                )
                if enhanced_line is None:
                    continue
            
            enhanced_lines.append(enhanced_line)
        
        # Add styling for execution state indicators
        if highlight_current or show_performance:
            enhanced_lines.insert(-1, "")  # Before closing ```
            enhanced_lines.insert(-1, "    %% Execution State Styling")
            
            if highlight_current and current_node:
                # Highlight current node in green
                node_id = self._sanitize_node_name(current_node) if current_node else ""
                enhanced_lines.insert(-1, f"    classDef current fill:#90EE90,stroke:#006400,stroke-width:3px")
                enhanced_lines.insert(-1, f"    class {node_id} current")
            
            # Highlight completed nodes in light blue
            for entry in self.controller.execution_history.entries:
                if entry.is_completed:
                    node_id = self._sanitize_node_name(entry.effective_name)
                    enhanced_lines.insert(-1, f"    classDef completed fill:#E6F3FF,stroke:#0066CC")
                    enhanced_lines.insert(-1, f"    class {node_id} completed")
            
            # Highlight error nodes in red
            for entry in self.controller.execution_history.entries:
                if entry.is_error:
                    node_id = self._sanitize_node_name(entry.effective_name)
                    enhanced_lines.insert(-1, f"    classDef error fill:#FFE6E6,stroke:#CC0000,stroke-width:2px")
                    enhanced_lines.insert(-1, f"    class {node_id} error")
        
        return '\n'.join(enhanced_lines)
    
    def _enhance_mermaid_line(self, line: str, current_node: Optional[str], 
                             execution_path: List[str], performance_data: Dict[str, List[float]],
                             controller_state: str) -> str:
        """Enhance a single Mermaid diagram line with execution state information"""
        enhanced_line = line
        
        # Extract node names from the line
        if '[' in line and ']' in line:
            # This is a node definition line
            for node_name in execution_path + ([current_node] if current_node else []):
                if node_name and node_name in line:
                    # Add execution state indicator to node label
                    if node_name == current_node and controller_state == 'running':
                        enhanced_line = enhanced_line.replace(
                            f'["{node_name}"]', 
                            f'["🔄 {node_name} (RUNNING)"]'
                        )
                    elif node_name in [entry.effective_name for entry in self.controller.execution_history.entries if entry.is_completed]:
                        # Add performance info if available
                        if node_name in performance_data:
                            avg_duration = sum(performance_data[node_name]) / len(performance_data[node_name])
                            enhanced_line = enhanced_line.replace(
                                f'["{node_name}"]',
                                f'["✅ {node_name} ({avg_duration*1000:.1f}ms)"]'
                            )
                        else:
                            enhanced_line = enhanced_line.replace(
                                f'["{node_name}"]',
                                f'["✅ {node_name}"]'
                            )
        
        return enhanced_line
    
    def _sanitize_node_name(self, node_name: str) -> str:
        """Sanitize node name for use as CSS class name"""
        # Replace non-alphanumeric characters with underscores
        import re
        return re.sub(r'[^a-zA-Z0-9_]', '_', node_name)
    
    def subscribe_to_events(self, callback: Callable[[str, Dict[str, Any]], None]) -> str:
        """Phase 3: Subscribe to real-time workflow execution events
        
        Args:
            callback: Function to call when events occur. Signature: (event_type, event_data)
            
        Returns:
            Subscription ID that can be used to unsubscribe
        """
        subscription_id = str(uuid.uuid4())[:8]
        
        # Add callback to the existing event subscribers list
        self._event_subscribers.append({
            'id': subscription_id,
            'callback': callback
        })
        
        return subscription_id
    
    def unsubscribe_from_events(self, subscription_id: str) -> bool:
        """Phase 3: Unsubscribe from workflow execution events
        
        Args:
            subscription_id: The subscription ID returned by subscribe_to_events()
            
        Returns:
            True if successfully unsubscribed, False if subscription not found
        """
        for i, subscriber in enumerate(self._event_subscribers):
            if subscriber['id'] == subscription_id:
                del self._event_subscribers[i]
                return True
        return False
    
    def _notify_subscribers(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Phase 3: Notify all subscribers of an event"""
        for subscriber in self._event_subscribers:
            try:
                subscriber['callback'](event_type, event_data)
            except Exception as e:
                # Don't let subscriber errors break the workflow
                logging.warning(f"Event subscriber callback failed: {e}")
    
    def get_event_stream(self, include_history: bool = False) -> List[Dict[str, Any]]:
        """Phase 3: Get stream of execution events for real-time monitoring
        
        Args:
            include_history: Whether to include historical events from execution history
            
        Returns:
            List of event dictionaries with timestamps and event data
        """
        events = []
        
        if include_history:
            # Add historical events from execution history
            for entry in self.controller.execution_history.entries:
                # Node start event
                events.append({
                    'timestamp': entry.start_time.isoformat() if entry.start_time else None,
                    'event_type': 'node_execution_started',
                    'node_name': entry.effective_name,
                    'node_guid': entry.node_guid,
                    'execution_id': entry.execution_id,
                    'input_value': str(entry.input_value)[:100] if entry.input_value else None
                })
                
                # Node completion/error event
                if entry.is_completed:
                    events.append({
                        'timestamp': entry.end_time.isoformat() if entry.end_time else None,
                        'event_type': 'node_execution_completed',
                        'node_name': entry.effective_name,
                        'node_guid': entry.node_guid,
                        'execution_id': entry.execution_id,
                        'duration': entry.duration,
                        'output_value': str(entry.output_value)[:100] if entry.output_value else None
                    })
                elif entry.is_error:
                    events.append({
                        'timestamp': entry.end_time.isoformat() if entry.end_time else None,
                        'event_type': 'node_execution_failed',
                        'node_name': entry.effective_name,
                        'node_guid': entry.node_guid,
                        'execution_id': entry.execution_id,
                        'error': str(entry.error) if entry.error else None
                    })
        
        # Add current status as an event
        current_status = self.get_live_status()
        events.append({
            'timestamp': datetime.now().isoformat(),
            'event_type': 'workflow_status',
            'controller_state': current_status.controller_state,
            'current_node': current_status.current_node,
            'execution_path': current_status.current_execution_path,
            'total_executions': current_status.total_executions,
            'running_time': current_status.running_time,
            'is_active': current_status.is_active
        })
        
        return events
    
    def get_alias_analysis(self) -> Dict[str, Any]:
        """Phase 5: Get comprehensive analysis of aliased nodes and their performance"""
        history = self.controller.execution_history
        
        if not history.entries:
            return {}
        
        # Group entries by canonical component name
        canonical_groups = {}
        
        for entry in history.entries:
            canonical = entry.canonical_name or entry.node_name
            if canonical not in canonical_groups:
                canonical_groups[canonical] = {
                    "canonical_name": canonical,
                    "total_aliases": 0,
                    "total_executions": 0,
                    "alias_instances": {},  # effective_name -> data
                    "execution_positions": [],
                    "performance_variance": 0.0,
                    "recommendations": []
                }
            
            group = canonical_groups[canonical]
            effective_name = entry.effective_name
            
            # Track alias instances
            if effective_name not in group["alias_instances"]:
                group["alias_instances"][effective_name] = {
                    "effective_name": effective_name,
                    "alias_name": entry.node_alias,
                    "node_guid": entry.node_guid,
                    "executions": 0,
                    "durations": [],
                    "positions": [],
                    "success_count": 0,
                    "error_count": 0
                }
                if entry.node_alias:  # Only count actual aliases, not originals
                    group["total_aliases"] += 1
            
            alias_data = group["alias_instances"][effective_name]
            alias_data["executions"] += 1
            alias_data["positions"].append(entry.execution_position)
            group["execution_positions"].append(entry.execution_position)
            group["total_executions"] += 1
            
            if entry.duration is not None:
                alias_data["durations"].append(entry.duration)
            
            if entry.is_completed:
                alias_data["success_count"] += 1
            elif entry.is_error:
                alias_data["error_count"] += 1
        
        # Calculate performance metrics for each alias
        for canonical, group in canonical_groups.items():
            alias_performance = {}
            all_durations = []
            
            for effective_name, alias_data in group["alias_instances"].items():
                if alias_data["durations"]:
                    avg_duration = statistics.mean(alias_data["durations"])
                    alias_data["avg_duration"] = avg_duration
                    alias_data["min_duration"] = min(alias_data["durations"])
                    alias_data["max_duration"] = max(alias_data["durations"])
                    all_durations.extend(alias_data["durations"])
                else:
                    alias_data["avg_duration"] = 0.0
                    alias_data["min_duration"] = 0.0
                    alias_data["max_duration"] = 0.0
                
                alias_data["success_rate"] = (
                    alias_data["success_count"] / alias_data["executions"] 
                    if alias_data["executions"] > 0 else 0.0
                )
                
                alias_performance[effective_name] = {
                    "execution_count": alias_data["executions"],
                    "avg_duration": alias_data["avg_duration"],
                    "success_rate": alias_data["success_rate"],
                    "positions": alias_data["positions"]
                }
            
            group["alias_performance"] = alias_performance
            
            # Calculate performance variance across aliases
            if len(all_durations) > 1:
                group["performance_variance"] = statistics.stdev(all_durations)
            
            # Generate recommendations
            if group["total_aliases"] > 0:
                durations_by_alias = {
                    name: data["avg_duration"] 
                    for name, data in group["alias_instances"].items() 
                    if data["avg_duration"] > 0
                }
                
                if len(durations_by_alias) > 1:
                    sorted_by_duration = sorted(durations_by_alias.items(), key=lambda x: x[1])
                    fastest = sorted_by_duration[0]
                    slowest = sorted_by_duration[-1]
                    
                    if slowest[1] > fastest[1] * 1.5:  # 50% slower
                        percent_slower = ((slowest[1] - fastest[1]) / fastest[1]) * 100
                        group["recommendations"].append(
                            f"{slowest[0]} shows {percent_slower:.0f}% slower performance than {fastest[0]}"
                        )
        
        return canonical_groups
    
    def get_canonical_component_analysis(self, canonical_name: str) -> Dict[str, Any]:
        """Phase 5: Get detailed analysis for a specific canonical component across all its aliases"""
        alias_analysis = self.get_alias_analysis()
        
        if canonical_name not in alias_analysis:
            return {
                "canonical_name": canonical_name,
                "found": False,
                "error": f"Component '{canonical_name}' not found in execution history"
            }
        
        component_data = alias_analysis[canonical_name]
        
        # Enhanced component analysis
        analysis = {
            "canonical_name": canonical_name,
            "found": True,
            "summary": {
                "total_aliases": component_data["total_aliases"],
                "total_executions": component_data["total_executions"],
                "unique_instances": len(component_data["alias_instances"]),
                "execution_positions": sorted(set(component_data["execution_positions"])),
                "performance_variance": component_data["performance_variance"]
            },
            "alias_breakdown": {},
            "position_analysis": {},
            "performance_comparison": {},
            "recommendations": component_data["recommendations"].copy()
        }
        
        # Detailed alias breakdown
        for effective_name, alias_data in component_data["alias_instances"].items():
            analysis["alias_breakdown"][effective_name] = {
                "alias_name": alias_data["alias_name"],
                "node_guid": alias_data["node_guid"],
                "executions": alias_data["executions"],
                "avg_duration": alias_data["avg_duration"],
                "min_duration": alias_data["min_duration"],
                "max_duration": alias_data["max_duration"],
                "success_rate": alias_data["success_rate"],
                "positions": alias_data["positions"],
                "is_original": alias_data["alias_name"] is None
            }
        
        # Position-based analysis
        position_groups = {}
        for effective_name, alias_data in component_data["alias_instances"].items():
            for pos in alias_data["positions"]:
                if pos not in position_groups:
                    position_groups[pos] = []
                position_groups[pos].append({
                    "effective_name": effective_name,
                    "avg_duration": alias_data["avg_duration"],
                    "executions": alias_data["executions"]
                })
        
        analysis["position_analysis"] = position_groups
        
        # Performance comparison metrics
        if len(component_data["alias_instances"]) > 1:
            durations = [
                (name, data["avg_duration"]) 
                for name, data in component_data["alias_instances"].items() 
                if data["avg_duration"] > 0
            ]
            
            if len(durations) > 1:
                sorted_durations = sorted(durations, key=lambda x: x[1])
                fastest = sorted_durations[0]
                slowest = sorted_durations[-1]
                
                analysis["performance_comparison"] = {
                    "fastest_instance": {
                        "name": fastest[0],
                        "avg_duration": fastest[1]
                    },
                    "slowest_instance": {
                        "name": slowest[0],
                        "avg_duration": slowest[1]
                    },
                    "performance_spread": slowest[1] - fastest[1],
                    "relative_difference": (
                        ((slowest[1] - fastest[1]) / fastest[1]) * 100 
                        if fastest[1] > 0 else 0
                    )
                }
        
        return analysis
    
    def get_position_performance_analysis(self, canonical_name: str) -> Dict[str, Any]:
        """Phase 5: Analyze performance of a component across different workflow positions"""
        component_analysis = self.get_canonical_component_analysis(canonical_name)
        
        if not component_analysis["found"]:
            return component_analysis
        
        position_analysis = component_analysis["position_analysis"]
        
        # Group performance by position
        position_performance = {}
        
        for position, instances in position_analysis.items():
            total_executions = sum(inst["executions"] for inst in instances)
            avg_durations = [inst["avg_duration"] for inst in instances if inst["avg_duration"] > 0]
            
            if avg_durations:
                position_avg = statistics.mean(avg_durations)
                position_median = statistics.median(avg_durations)
            else:
                position_avg = position_median = 0.0
            
            position_performance[position] = {
                "position": position,
                "instances": len(instances),
                "total_executions": total_executions,
                "avg_duration": position_avg,
                "median_duration": position_median,
                "instance_details": instances
            }
        
        # Analyze performance trends by position
        sorted_positions = sorted(position_performance.items(), key=lambda x: x[0])
        performance_trend = []
        
        for pos, data in sorted_positions:
            performance_trend.append({
                "position": pos,
                "avg_duration": data["avg_duration"],
                "executions": data["total_executions"]
            })
        
        # Identify performance patterns
        recommendations = []
        if len(performance_trend) > 1:
            durations = [p["avg_duration"] for p in performance_trend if p["avg_duration"] > 0]
            if durations:
                max_duration = max(durations)
                min_duration = min(durations)
                
                if max_duration > min_duration * 1.5:  # Significant variance
                    worst_pos = max(performance_trend, key=lambda x: x["avg_duration"])
                    best_pos = min(performance_trend, key=lambda x: x["avg_duration"])
                    
                    recommendations.append(
                        f"Performance varies significantly by position: "
                        f"position {worst_pos['position']} is {((worst_pos['avg_duration'] - best_pos['avg_duration']) / best_pos['avg_duration'] * 100):.0f}% slower than position {best_pos['position']}"
                    )
        
        return {
            "canonical_name": canonical_name,
            "found": True,
            "position_performance": position_performance,
            "performance_trend": performance_trend,
            "recommendations": recommendations,
            "summary": {
                "positions_analyzed": len(position_performance),
                "total_instances": sum(p["instances"] for p in position_performance.values()),
                "total_executions": sum(p["total_executions"] for p in position_performance.values())
            }
        }
    
    def export_report(self, format: str = "markdown") -> str:
        """Export execution report in specified format (markdown, json, csv, html)"""
        # Generate the data once and format appropriately
        report_data = self._generate_report_data()
        
        format_lower = format.lower()
        if format_lower == "markdown":
            return self._format_as_markdown(report_data)
        elif format_lower == "json":
            return self._format_as_json(report_data)
        elif format_lower == "csv":
            return self._format_as_csv(report_data)
        elif format_lower == "html":
            return self._format_as_html(report_data)
        else:
            raise ValueError(f"Unsupported format: {format}. Supported: markdown, json, csv, html")
    
    def _generate_report_data(self) -> Dict[str, Any]:
        """Generate comprehensive report data structure used by all formats"""
        metrics = self.get_execution_metrics()
        performance = self.get_performance_summary()
        error_analysis = self.get_error_analysis()
        
        # Phase 5: Include alias analysis in all export formats
        alias_analysis = self.get_alias_analysis()
        
        report_data = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "workflow_name": getattr(self.controller.workflow, 'name', 'Unnamed'),
                "workflow_id": getattr(self.controller.workflow, 'workflow_id', 'Unknown')
            },
            "execution_metrics": {
                "total_nodes_executed": metrics.total_nodes_executed,
                "successful_executions": metrics.successful_executions,
                "failed_executions": metrics.failed_executions,
                "success_rate": metrics.success_rate,
                "unique_nodes_count": metrics.unique_nodes_count,
                "total_execution_time": metrics.total_execution_time,
                "node_execution_counts": metrics.node_execution_counts
            },
            "performance_metrics": {
                "average_node_duration": metrics.average_node_duration,
                "median_node_duration": performance.median_node_duration,
                "min_node_duration": metrics.min_node_duration,
                "max_node_duration": metrics.max_node_duration,
                "slowest_nodes": performance.slowest_nodes,
                "fastest_nodes": performance.fastest_nodes,
                "bottlenecks": performance.bottlenecks,
                "nodes_analyzed": performance.nodes_analyzed
            },
            "error_analysis": {
                "total_errors": error_analysis.total_errors,
                "error_rate": error_analysis.error_rate,
                "error_categories": error_analysis.error_categories,
                "failed_nodes": error_analysis.failed_nodes,
                "most_common_errors": error_analysis.most_common_errors,
                "error_details": error_analysis.error_details
            },
            # Phase 5: Enhanced execution data with GUID and alias information
            "recent_executions": [
                {
                    "node_name": entry.node_name,
                    "effective_name": entry.effective_name,
                    "node_guid": entry.node_guid,
                    "node_alias": entry.node_alias,
                    "canonical_name": entry.canonical_name,
                    "execution_position": entry.execution_position,
                    "status": entry.status,
                    "duration": entry.duration,
                    "start_time": entry.start_time.isoformat(),
                    "end_time": entry.end_time.isoformat() if entry.end_time else None,
                    "execution_id": entry.execution_id,
                    "error_info": {
                        "error_type": type(entry.error).__name__,
                        "error_message": str(entry.error),
                        "stack_trace": ''.join(traceback.format_exception(
                            type(entry.error), entry.error, entry.error.__traceback__
                        )) if hasattr(entry.error, '__traceback__') and entry.error.__traceback__ else None
                    } if entry.error else None
                }
                for entry in self.controller.execution_history.get_recent(10)
            ],
            # Phase 5: Alias analysis data
            "alias_analysis": alias_analysis
        }
        
        return report_data
    
    def _format_as_json(self, report_data: Dict[str, Any]) -> str:
        """Format report data as JSON"""
        return json.dumps(report_data, indent=2)
    
    def _format_as_markdown(self, report_data: Dict[str, Any]) -> str:
        """Format report data as Markdown"""
        metadata = report_data["report_metadata"]
        exec_metrics = report_data["execution_metrics"]
        perf_metrics = report_data["performance_metrics"]
        recent_execs = report_data["recent_executions"]
        
        # Parse generated_at for formatting
        generated_time = datetime.fromisoformat(metadata["generated_at"].replace('Z', '+00:00'))
        
        report_lines = [
            "# Workflow Execution Report",
            "",
            "",
            "## Execution Summary",
            "",
            "",
            "## Performance Metrics",
            "",
            ""
        ]
        
        # Node execution counts
        if exec_metrics['node_execution_counts']:
            report_lines.extend([
                "## Node Execution Counts",
                "",
                "| Node Name | Executions |",
                "|-----------|------------|"
            ])
            for node_name, count in sorted(exec_metrics['node_execution_counts'].items()):
                report_lines.append(f"| {node_name} | {count} |")
            report_lines.append("")
        
        # Performance analysis
        if perf_metrics['slowest_nodes']:
            report_lines.extend([
                "## Performance Analysis",
                "",
                "### Slowest Nodes",
                "",
                "| Node Name | Average Duration |",
                "|-----------|------------------|"
            ])
            for node_name, duration in perf_metrics['slowest_nodes']:
                report_lines.append(f"| {node_name} | {duration:.3f}s |")
            report_lines.append("")
        
        # Bottlenecks
        if perf_metrics['bottlenecks']:
            report_lines.extend([
                "### Bottlenecks Detected",
                "",
                "The following nodes are significantly slower than average:",
                ""
            ])
            for bottleneck in perf_metrics['bottlenecks']:
                report_lines.append(f"- **{bottleneck}**")
            report_lines.append("")
        
        # Error Analysis
        error_analysis = report_data.get("error_analysis", {})
        if error_analysis.get("total_errors", 0) > 0:
            report_lines.extend([
                "## Error Analysis",
                "",
                ""
            ])
            
            if error_analysis.get("error_categories"):
                report_lines.extend([
                    "### Error Categories",
                    "",
                    "| Error Type | Count |",
                    "|------------|-------|"
                ])
                for error_type, count in error_analysis['error_categories'].items():
                    report_lines.append(f"| {error_type} | {count} |")
                report_lines.append("")
        
        # Error analysis section
        error_analysis = report_data["error_analysis"]
        if error_analysis["total_errors"] > 0:
            report_lines.extend([
                "## Error Analysis",
                "",
                ""
            ])
            
            if error_analysis["error_categories"]:
                report_lines.extend([
                    "### Error Categories",
                    "",
                    "| Error Type | Count |",
                    "|------------|-------|"
                ])
                for error_type, count in error_analysis["most_common_errors"]:
                    report_lines.append(f"| {error_type} | {count} |")
                report_lines.append("")

        # Phase 5: Alias Analysis section
        alias_analysis = report_data.get("alias_analysis", {})
        if alias_analysis:
            report_lines.extend([
                "## Alias Analysis",
                "",
                "Component reuse analysis across workflow positions:",
                ""
            ])
            
            for canonical_name, component_data in alias_analysis.items():
                report_lines.extend([
                    "",
                    ""
                ])
                
                # Alias instances table
                if component_data['alias_instances']:
                    report_lines.extend([
                        "| Instance | Type | Executions | Avg Duration | Positions |",
                        "|----------|------|------------|--------------|-----------|"
                    ])
                    
                    for effective_name, alias_data in component_data['alias_instances'].items():
                        instance_type = "Original" if alias_data['alias_name'] is None else "Alias"
                        positions_str = ", ".join(map(str, alias_data['positions']))
                        report_lines.append(
                            f"| {effective_name} | {instance_type} | {alias_data['executions']} | "
                            f"{alias_data['avg_duration']:.3f}s | {positions_str} |"
                        )
                    report_lines.append("")
                
                # Recommendations
                if component_data['recommendations']:
                    report_lines.extend([
                        "**Recommendations:**",
                        ""
                    ])
                    for rec in component_data['recommendations']:
                        report_lines.append(f"- {rec}")
                    report_lines.append("")
        
        # Recent executions with enhanced data
        if recent_execs:
            report_lines.extend([
                "## Recent Executions",
                "",
                "| Effective Name | Type | Status | Duration | Position | GUID | Start Time |",
                "|----------------|------|--------|----------|----------|------|------------|"
            ])
            for entry in recent_execs:
                duration_str = f"{entry['duration']:.3f}s" if entry['duration'] else "N/A"
                start_time = datetime.fromisoformat(entry['start_time'].replace('Z', '+00:00'))
                start_time_str = start_time.strftime('%H:%M:%S')
                status_emoji = "❌" if entry['status'] == 'error' else "✅" if entry['status'] == 'completed' else "⏳"
                
                # Phase 5: Enhanced execution data
                effective_name = entry.get('effective_name', entry['node_name'])
                node_type = "Alias" if entry.get('node_alias') else "Original"
                position = entry.get('execution_position', 'N/A')
                guid_short = entry.get('node_guid', 'Unknown')[:8] + "..." if entry.get('node_guid') else "N/A"
                
                report_lines.append(
                    f"| {effective_name} | {node_type} | {status_emoji} {entry['status']} | "
                    f"{duration_str} | {position} | {guid_short} | {start_time_str} |"
                )
        
        return "\n".join(report_lines)
    
    def _format_as_csv(self, report_data: Dict[str, Any]) -> str:
        """Format report data as CSV"""
        import csv
        import io
        
        output = io.StringIO()
        
        # Write metadata section
        output.write("# Workflow Execution Report\n")
        output.write(f"Generated,{report_data['report_metadata']['generated_at']}\n")
        output.write(f"Workflow,{report_data['report_metadata']['workflow_name']}\n")
        output.write(f"Workflow ID,{report_data['report_metadata']['workflow_id']}\n")
        output.write("\n")
        
        # Write execution metrics
        output.write("# Execution Metrics\n")
        exec_metrics = report_data['execution_metrics']
        output.write("Metric,Value\n")
        output.write(f"Total Nodes Executed,{exec_metrics['total_nodes_executed']}\n")
        output.write(f"Successful Executions,{exec_metrics['successful_executions']}\n")
        output.write(f"Failed Executions,{exec_metrics['failed_executions']}\n")
        output.write(f"Success Rate,{exec_metrics['success_rate']:.3f}\n")
        output.write(f"Unique Nodes Count,{exec_metrics['unique_nodes_count']}\n")
        output.write(f"Total Execution Time,{exec_metrics['total_execution_time']:.3f}\n")
        output.write("\n")
        
        # Write performance metrics
        output.write("# Performance Metrics\n")
        perf_metrics = report_data['performance_metrics']
        output.write("Metric,Value\n")
        output.write(f"Average Node Duration,{perf_metrics['average_node_duration']:.3f}\n")
        output.write(f"Median Node Duration,{perf_metrics['median_node_duration']:.3f}\n")
        output.write(f"Min Node Duration,{perf_metrics['min_node_duration']:.3f}\n")
        output.write(f"Max Node Duration,{perf_metrics['max_node_duration']:.3f}\n")
        output.write(f"Nodes Analyzed,{perf_metrics['nodes_analyzed']}\n")
        output.write("\n")
        
        # Write node execution counts
        if exec_metrics['node_execution_counts']:
            output.write("# Node Execution Counts\n")
            output.write("Node Name,Executions\n")
            for node_name, count in sorted(exec_metrics['node_execution_counts'].items()):
                output.write(f"{node_name},{count}\n")
            output.write("\n")
        
        # Phase 5: Write alias analysis data
        alias_analysis = report_data.get("alias_analysis", {})
        if alias_analysis:
            output.write("# Alias Analysis\n")
            output.write("Canonical Name,Total Aliases,Total Executions,Performance Variance\n")
            for canonical_name, component_data in alias_analysis.items():
                output.write(f"{canonical_name},{component_data['total_aliases']},{component_data['total_executions']},{component_data['performance_variance']:.4f}\n")
            output.write("\n")
            
            # Detailed alias instances
            output.write("# Alias Instances\n")
            output.write("Canonical Name,Effective Name,Instance Type,Node GUID,Executions,Avg Duration,Min Duration,Max Duration,Success Rate,Positions\n")
            for canonical_name, component_data in alias_analysis.items():
                for effective_name, alias_data in component_data['alias_instances'].items():
                    instance_type = "Original" if alias_data['alias_name'] is None else "Alias"
                    positions_str = ";".join(map(str, alias_data['positions']))
                    output.write(
                        f"{canonical_name},{effective_name},{instance_type},{alias_data['node_guid']},"
                        f"{alias_data['executions']},{alias_data['avg_duration']:.3f},"
                        f"{alias_data['min_duration']:.3f},{alias_data['max_duration']:.3f},"
                        f"{alias_data['success_rate']:.3f},{positions_str}\n"
                    )
            output.write("\n")
        
        # Write recent executions with enhanced data
        if report_data['recent_executions']:
            output.write("# Recent Executions\n")
            output.write("Node Name,Effective Name,Node Type,Status,Duration,Position,GUID,Start Time,End Time,Execution ID\n")
            for entry in report_data['recent_executions']:
                duration = f"{entry['duration']:.3f}" if entry['duration'] else ""
                end_time = entry['end_time'] if entry['end_time'] else ""
                effective_name = entry.get('effective_name', entry['node_name'])
                node_type = "Alias" if entry.get('node_alias') else "Original"
                position = entry.get('execution_position', '')
                guid = entry.get('node_guid', '')
                output.write(
                    f"{entry['node_name']},{effective_name},{node_type},{entry['status']},"
                    f"{duration},{position},{guid},{entry['start_time']},{end_time},{entry['execution_id']}\n"
                )
        
        return output.getvalue()
    
    def _format_as_html(self, report_data: Dict[str, Any]) -> str:
        """Format report data as HTML using Jinja2 template"""
        try:
            from jinja2 import Template
        except ImportError:
            # Fallback to simple HTML if Jinja2 not available
            return self._format_as_simple_html(report_data)
        
        template_str = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Workflow Execution Report</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px;
            background-color: #f5f7fa;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { margin: 0 0 15px 0; font-size: 2.5em; }
        .header p { margin: 5px 0; opacity: 0.9; }
        .content { padding: 30px; }
        .section { margin-bottom: 40px; }
        .section h2 { 
            color: #4a5568; 
            border-bottom: 2px solid #e2e8f0; 
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .metric-card {
            background: #f8fafc;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            text-align: center;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }
        .metric-label {
            color: #718096;
            font-size: 0.9em;
        }
        table { 
            width: 100%; 
            border-collapse: collapse; 
            margin: 20px 0;
            background: white;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
        }
        th, td { 
            padding: 12px 15px; 
            text-align: left; 
            border-bottom: 1px solid #e2e8f0;
        }
        th { 
            background: #f7fafc; 
            font-weight: 600;
            color: #4a5568;
        }
        .success { color: #38a169; font-weight: 600; }
        .error { color: #e53e3e; font-weight: 600; }
        .running { color: #d69e2e; font-weight: 600; }
        .bottleneck { background-color: #fed7d7; }
        tr:hover { background-color: #f7fafc; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔧 Workflow Execution Report</h1>
            <p><strong>Generated:</strong> {{ generated_time }}</p>
            <p><strong>Workflow:</strong> {{ metadata.workflow_name }}</p>
            <p><strong>ID:</strong> {{ metadata.workflow_id }}</p>
        </div>
        
        <div class="content">
            <div class="section">
                <h2>📊 Execution Summary</h2>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">{{ exec_metrics.total_nodes_executed }}</div>
                        <div class="metric-label">Total Nodes Executed</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{{ "%.1f"|format(exec_metrics.success_rate * 100) }}%</div>
                        <div class="metric-label">Success Rate</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{{ "%.3f"|format(exec_metrics.total_execution_time) }}s</div>
                        <div class="metric-label">Total Time</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{{ exec_metrics.unique_nodes_count }}</div>
                        <div class="metric-label">Unique Nodes</div>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>⚡ Performance Metrics</h2>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">{{ "%.3f"|format(perf_metrics.average_node_duration) }}s</div>
                        <div class="metric-label">Average Duration</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{{ "%.3f"|format(perf_metrics.median_node_duration) }}s</div>
                        <div class="metric-label">Median Duration</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{{ perf_metrics.bottlenecks|length }}</div>
                        <div class="metric-label">Bottlenecks</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{{ perf_metrics.nodes_analyzed }}</div>
                        <div class="metric-label">Nodes Analyzed</div>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>📋 Node Execution Counts</h2>
                <table>
                    <thead>
                        <tr><th>Node Name</th><th>Executions</th></tr>
                    </thead>
                    <tbody>
                        <tr><td>{{ node_name }}</td><td>{{ count }}</td></tr>
                    </tbody>
                </table>
            </div>

            <div class="section">
                <h2>🐌 Performance Analysis</h2>
                <table>
                    <thead>
                        <tr><th>Node Name</th><th>Average Duration</th><th>Status</th></tr>
                    </thead>
                    <tbody>
                        <tr {% if node_name in perf_metrics.bottlenecks %}class="bottleneck"{% endif %}>
                            <td>{{ node_name }}</td>
                            <td>{{ "%.3f"|format(duration) }}s</td>
                            <td>{% if node_name in perf_metrics.bottlenecks %}<span class="error">Bottleneck</span>{% else %}Normal{% endif %}</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="section">
                <h2>🔄 Alias Analysis</h2>
                <p>Component reuse analysis across workflow positions:</p>
                
                <div style="margin-bottom: 30px;">
                    <h3>{{ canonical_name }}</h3>
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-value">{{ component_data.total_aliases }}</div>
                            <div class="metric-label">Total Aliases</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{{ component_data.total_executions }}</div>
                            <div class="metric-label">Total Executions</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{{ "%.4f"|format(component_data.performance_variance) }}s</div>
                            <div class="metric-label">Performance Variance</div>
                        </div>
                    </div>
                    
                    <table>
                        <thead>
                            <tr><th>Instance</th><th>Type</th><th>GUID</th><th>Executions</th><th>Avg Duration</th><th>Positions</th></tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>{{ effective_name }}</td>
                                <td>{% if alias_data.alias_name %}Alias{% else %}Original{% endif %}</td>
                                <td><code>{{ alias_data.node_guid[:8] }}...</code></td>
                                <td>{{ alias_data.executions }}</td>
                                <td>{{ "%.3f"|format(alias_data.avg_duration) }}s</td>
                                <td>{{ alias_data.positions|join(', ') }}</td>
                            </tr>
                        </tbody>
                    </table>
                    
                    <div style="margin-top: 15px;">
                        <strong>Recommendations:</strong>
                        <ul>
                            <li>{{ rec }}</li>
                        </ul>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>🕒 Recent Executions</h2>
                <table>
                    <thead>
                        <tr><th>Effective Name</th><th>Type</th><th>Status</th><th>Duration</th><th>Position</th><th>GUID</th><th>Start Time</th></tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>{{ entry.effective_name or entry.node_name }}</td>
                            <td>{% if entry.node_alias %}Alias{% else %}Original{% endif %}</td>
                            <td>
                                <span class="{% if entry.status == 'completed' %}success{% elif entry.status == 'error' %}error{% else %}running{% endif %}">
                                </span>
                            </td>
                            <td>{% if entry.duration %}{{ "%.3f"|format(entry.duration) }}s{% else %}N/A{% endif %}</td>
                            <td>{{ entry.execution_position if entry.execution_position is not none else 'N/A' }}</td>
                            <td><code>{{ entry.node_guid[:8] if entry.node_guid else 'N/A' }}...</code></td>
                            <td>{{ entry.formatted_start_time }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>"""

        # Prepare template data
        metadata = report_data["report_metadata"]
        exec_metrics = report_data["execution_metrics"]
        perf_metrics = report_data["performance_metrics"]
        recent_execs = report_data["recent_executions"]
        
        # Format recent executions with readable start times
        for entry in recent_execs:
            if entry['start_time']:
                start_time = datetime.fromisoformat(entry['start_time'].replace('Z', '+00:00'))
                entry['formatted_start_time'] = start_time.strftime('%H:%M:%S')
        
        # Parse generated_at for formatting
        generated_time = datetime.fromisoformat(metadata["generated_at"].replace('Z', '+00:00'))
        
        template = Template(template_str)
        return template.render(
            metadata=metadata,
            exec_metrics=exec_metrics,
            perf_metrics=perf_metrics,
            recent_execs=recent_execs,
            alias_analysis=report_data.get("alias_analysis", {}),  # Phase 5: Add alias analysis
            generated_time=generated_time.strftime('%Y-%m-%d %H:%M:%S')
        )
    
    def _format_as_simple_html(self, report_data: Dict[str, Any]) -> str:
        """Fallback simple HTML formatter when Jinja2 is not available"""
        metadata = report_data["report_metadata"]
        exec_metrics = report_data["execution_metrics"]
        
        return f"""<!DOCTYPE html>
<html>
<head><title>Workflow Report</title></head>
<body>
    <h1>Workflow Execution Report</h1>
    <p><strong>Workflow:</strong> {metadata['workflow_name']}</p>
    <p><strong>Total Nodes:</strong> {exec_metrics['total_nodes_executed']}</p>
    <p><strong>Success Rate:</strong> {exec_metrics['success_rate']:.1%}</p>
    <p><em>Install Jinja2 for enhanced HTML reports: pip install jinja2</em></p>
</body>
</html>"""