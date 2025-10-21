"""
Tool Execution Group - Context History Support

ToolExecutionGroup tracks tool executions for correlation with context snapshots.
Each group represents a set of tool calls executed during a single agent turn,
linked to the snapshot that triggered the tool execution.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..messaging import ProviderToolCall
from .context_components import ToolResult, ScaffoldResult


class ToolExecution(BaseModel):
    """Single tool execution within a group"""
    
    tool_call: ProviderToolCall = Field(..., description="Original tool call from provider")
    result: Optional[ToolResult] = Field(None, description="Tool execution result")
    scaffold_result: Optional[ScaffoldResult] = Field(None, description="Scaffold execution result if applicable")
    
    # Execution metadata
    execution_time: datetime = Field(default_factory=datetime.now, description="When tool was executed")
    duration_ms: Optional[int] = Field(None, description="Execution duration in milliseconds")
    error: Optional[str] = Field(None, description="Error message if execution failed")
    
    # Tool identification
    tool_name: str = Field(..., description="Name of executed tool")
    tool_call_id: str = Field(..., description="Unique tool call ID from provider")
    
    @property
    def success(self) -> bool:
        """Check if tool execution was successful"""
        return self.error is None
    
    @property
    def execution_result(self) -> Optional[ToolResult]:
        """Get the primary execution result (tool or scaffold)"""
        return self.result or self.scaffold_result


class ToolExecutionGroup(BaseModel):
    """Group of tool executions for a single agent turn"""
    
    # Group identification
    id: str = Field(..., description="Unique group identifier")
    cycle_id: str = Field(..., description="Message cycle/turn identifier")
    snapshot_id: str = Field(..., description="ID of snapshot that triggered this execution")
    
    # Execution data
    executions: List[ToolExecution] = Field(default_factory=list, description="List of tool executions in this group")
    
    # Group metadata
    created_at: datetime = Field(default_factory=datetime.now, description="When group was created")
    completed_at: Optional[datetime] = Field(None, description="When all executions completed")
    total_duration_ms: Optional[int] = Field(None, description="Total execution time for all tools")
    
    # Context linking
    provider_name: Optional[str] = Field(None, description="Provider that initiated the tool calls")
    context_size_before: Optional[int] = Field(None, description="Context size before tool execution")
    context_size_after: Optional[int] = Field(None, description="Context size after tool execution")
    
    def add_execution(self, execution: ToolExecution):
        """Add tool execution to this group"""
        self.executions.append(execution)
        
        # Update group metadata if this is the first execution
        if len(self.executions) == 1:
            self.created_at = execution.execution_time
    
    def mark_completed(self):
        """Mark group as completed and calculate total duration"""
        self.completed_at = datetime.now()
        
        if self.executions:
            # Calculate total duration from first to last execution
            first_execution = min(self.executions, key=lambda x: x.execution_time)
            last_execution = max(self.executions, key=lambda x: x.execution_time)
            
            duration = (last_execution.execution_time - first_execution.execution_time).total_seconds() * 1000
            self.total_duration_ms = int(duration)
    
    @property
    def execution_count(self) -> int:
        """Number of executions in this group"""
        return len(self.executions)
    
    @property
    def success_rate(self) -> float:
        """Success rate of executions in this group (0.0 to 1.0)"""
        if not self.executions:
            return 0.0
        
        successful = sum(1 for exec in self.executions if exec.success)
        return successful / len(self.executions)
    
    @property
    def tool_names(self) -> List[str]:
        """List of tool names executed in this group"""
        return [exec.tool_name for exec in self.executions]
    
    @property
    def failed_executions(self) -> List[ToolExecution]:
        """List of failed executions"""
        return [exec for exec in self.executions if not exec.success]
    
    def get_execution_by_tool_call_id(self, tool_call_id: str) -> Optional[ToolExecution]:
        """Find execution by tool call ID"""
        for execution in self.executions:
            if execution.tool_call_id == tool_call_id:
                return execution
        return None
    
    def get_executions_by_tool_name(self, tool_name: str) -> List[ToolExecution]:
        """Get all executions for a specific tool"""
        return [exec for exec in self.executions if exec.tool_name == tool_name]
    
    def to_summary(self) -> Dict[str, Any]:
        """Generate summary statistics for this group"""
        return {
            "id": self.id,
            "cycle_id": self.cycle_id,
            "snapshot_id": self.snapshot_id,
            "execution_count": self.execution_count,
            "success_rate": self.success_rate,
            "total_duration_ms": self.total_duration_ms,
            "tool_names": list(set(self.tool_names)),  # Unique tool names
            "failed_count": len(self.failed_executions),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }