"""
AgentController for managing agent lifecycle and execution state.

Provides thread-safe execution state tracking, interruption handling,
and lifecycle hooks for V2 agents.
"""

import threading
import uuid
from enum import Enum
from typing import Optional, Dict, Any, Callable, List
from datetime import datetime
import asyncio
import logging

from ..utils import validate_execution_state

logger = logging.getLogger(__name__)


class ExecutionState(Enum):
    """Agent execution states."""
    IDLE = "idle"
    PROCESSING = "processing"
    TOOL_EXECUTION = "tool_execution"
    INTERRUPTED = "interrupted"


class AgentController:
    """
    Thread-safe agent lifecycle and execution state manager.
    
    Tracks execution state, handles interruptions, and manages
    lifecycle hooks for agent operations.
    """
    
    def __init__(self, agent_id: Optional[str] = None):
        """
        Initialize agent controller.
        
        Args:
            agent_id: Optional agent identifier. Generated if not provided.
        """
        self.agent_id = agent_id or str(uuid.uuid4())
        self._state = ExecutionState.IDLE
        self._state_lock = threading.RLock()
        self._interruption_event = threading.Event()
        self._execution_id: Optional[str] = None
        self._execution_start_time: Optional[datetime] = None
        
        # NEW: Reference to agent for state updates
        self._agent_ref: Optional[Any] = None
        
        # Lifecycle hooks
        self._before_execution_hooks: List[Callable] = []
        self._after_execution_hooks: List[Callable] = []
        self._on_interruption_hooks: List[Callable] = []
        self._on_error_hooks: List[Callable] = []
        
        # State change callbacks
        self._state_change_callbacks: List[Callable[[ExecutionState, ExecutionState], None]] = []
        
        logger.debug(f"AgentController initialized: {self.agent_id}")
    
    # State Management
    
    @property
    def state(self) -> ExecutionState:
        """Get current execution state."""
        with self._state_lock:
            return self._state
    
    @property
    def execution_id(self) -> Optional[str]:
        """Get current execution ID if any."""
        with self._state_lock:
            return self._execution_id
    
    @property
    def is_idle(self) -> bool:
        """Check if agent is idle."""
        return self.state == ExecutionState.IDLE
    
    @property
    def is_processing(self) -> bool:
        """Check if agent is processing."""
        return self.state == ExecutionState.PROCESSING
    
    @property
    def is_tool_executing(self) -> bool:
        """Check if agent is executing tools."""
        return self.state == ExecutionState.TOOL_EXECUTION
    
    @property
    def is_interrupted(self) -> bool:
        """Check if agent is interrupted."""
        return self.state == ExecutionState.INTERRUPTED
    
    def set_agent_reference(self, agent: Any) -> None:
        """
        Set reference to agent for state updates.
        
        Args:
            agent: The agent instance to reference
        """
        self._agent_ref = agent
    
    def _transition_state(self, new_state: ExecutionState) -> None:
        """
        Thread-safe state transition with callbacks.
        
        Args:
            new_state: Target execution state
        """
        with self._state_lock:
            old_state = self._state
            if old_state != new_state:
                self._state = new_state
                logger.debug(f"Agent {self.agent_id} state: {old_state.value} -> {new_state.value}")
                
                # Call state change callbacks
                for callback in self._state_change_callbacks:
                    try:
                        callback(old_state, new_state)
                    except Exception as e:
                        logger.error(f"State change callback error: {e}")
                
                # NEW: Update agent state if available
                if self._agent_ref and hasattr(self._agent_ref, 'state'):
                    self._agent_ref.state.execution_state = new_state.value
    
    # Execution Management
    
    def start_execution(self) -> str:
        """
        Start new execution cycle.
        
        Returns:
            Execution ID for tracking
            
        Raises:
            RuntimeError: If agent is not idle
        """
        with self._state_lock:
            validate_execution_state(
                self._state, 
                [ExecutionState.IDLE], 
                "starting execution"
            )
            
            execution_id = str(uuid.uuid4())
            self._execution_id = execution_id
            self._execution_start_time = datetime.now()
            self._interruption_event.clear()
            
            # Execute before hooks
            self._execute_hooks(self._before_execution_hooks, execution_id=execution_id)
            
            self._transition_state(ExecutionState.PROCESSING)
            
            logger.info(f"Started execution {execution_id} for agent {self.agent_id}")
            return execution_id
    
    def end_execution(self, execution_id: str) -> None:
        """
        End execution cycle.
        
        Args:
            execution_id: Execution ID to end
            
        Raises:
            RuntimeError: If execution ID doesn't match current execution
        """
        with self._state_lock:
            if self._execution_id != execution_id:
                raise RuntimeError(f"Execution ID mismatch: expected {self._execution_id}, got {execution_id}")
            
            # Calculate execution time
            duration = None
            if self._execution_start_time:
                duration = datetime.now() - self._execution_start_time
            
            # Execute after hooks
            self._execute_hooks(self._after_execution_hooks, 
                              execution_id=execution_id, 
                              duration=duration)
            
            self._execution_id = None
            self._execution_start_time = None
            self._transition_state(ExecutionState.IDLE)
            
            logger.info(f"Ended execution {execution_id} for agent {self.agent_id}")
    
    def start_tool_execution(self) -> None:
        """Transition to tool execution state."""
        with self._state_lock:
            validate_execution_state(
                self._state, 
                [ExecutionState.PROCESSING, ExecutionState.TOOL_EXECUTION], 
                "starting tool execution"
            )
            
            self._transition_state(ExecutionState.TOOL_EXECUTION)
    
    def end_tool_execution(self) -> None:
        """End tool execution state."""
        with self._state_lock:
            validate_execution_state(
                self._state, 
                [ExecutionState.TOOL_EXECUTION], 
                "ending tool execution"
            )
            
            self._transition_state(ExecutionState.PROCESSING)
    
    # Interruption Management
    
    def interrupt(self) -> None:
        """
        Interrupt current execution.
        
        Sets interruption flag and calls interruption hooks.
        """
        with self._state_lock:
            if self._state == ExecutionState.IDLE:
                logger.warning(f"Agent {self.agent_id} is idle, cannot interrupt")
                return
            
            self._interruption_event.set()
            self._transition_state(ExecutionState.INTERRUPTED)
            
            # Execute interruption hooks
            self._execute_hooks(self._on_interruption_hooks, 
                              execution_id=self._execution_id)
            
            # Cancel ToolTaskLoop operations if available
            if (self._agent_ref and 
                hasattr(self._agent_ref, '_task_loop')):
                try:
                    # Schedule cancellation in the task loop's event loop
                    try:
                        loop = asyncio.get_running_loop()
                        loop.create_task(self._agent_ref._task_loop.cancel_all_operations())
                    except RuntimeError:
                        # No running event loop, will be handled when loop starts
                        logger.debug("No event loop available for immediate task cancellation")
                except Exception as e:
                    logger.error(f"Failed to cancel ToolTaskLoop operations: {e}")
            
            logger.info(f"Interrupted agent {self.agent_id}")
    
    def check_interruption(self) -> bool:
        """
        Check if interruption has been requested.
        
        Returns:
            True if interruption requested
        """
        return self._interruption_event.is_set()
    
    def clear_interruption(self) -> None:
        """Clear interruption flag and return to processing."""
        with self._state_lock:
            if self._state == ExecutionState.INTERRUPTED:
                self._interruption_event.clear()
                self._transition_state(ExecutionState.PROCESSING)
                logger.info(f"Cleared interruption for agent {self.agent_id}")
    
    # Hook Management
    
    def add_before_execution_hook(self, hook: Callable) -> None:
        """Add hook to execute before execution starts."""
        self._before_execution_hooks.append(hook)
    
    def add_after_execution_hook(self, hook: Callable) -> None:
        """Add hook to execute after execution ends."""
        self._after_execution_hooks.append(hook)
    
    def add_interruption_hook(self, hook: Callable) -> None:
        """Add hook to execute when interrupted."""
        self._on_interruption_hooks.append(hook)
    
    def add_error_hook(self, hook: Callable) -> None:
        """Add hook to execute when errors occur."""
        self._on_error_hooks.append(hook)
    
    def add_state_change_callback(self, callback: Callable[[ExecutionState, ExecutionState], None]) -> None:
        """Add callback for state changes."""
        self._state_change_callbacks.append(callback)
    
    def _execute_hooks(self, hooks: List[Callable], **kwargs) -> None:
        """
        Execute hooks with error handling.
        
        Args:
            hooks: List of hook functions to execute
            **kwargs: Arguments to pass to hooks
        """
        # Early bailout if no hooks registered for performance
        if not hooks:
            return
        
        for hook in hooks:
            try:
                hook(agent_id=self.agent_id, **kwargs)
            except Exception as e:
                logger.error(f"Hook execution error for agent {self.agent_id}: {e}")
                # Execute error hooks if this isn't already an error hook execution
                if hooks != self._on_error_hooks:
                    self._execute_hooks(self._on_error_hooks, error=e, **kwargs)
    
    # Context Manager Support
    
    def __enter__(self):
        """Context manager entry."""
        execution_id = self.start_execution()
        return execution_id
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self._execution_id:
            if exc_type:
                # Execute error hooks
                self._execute_hooks(self._on_error_hooks, 
                                  execution_id=self._execution_id,
                                  error=exc_val)
            self.end_execution(self._execution_id)
    
    # Status Information
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive status information.
        
        Returns:
            Status dictionary with agent state information
        """
        with self._state_lock:
            status = {
                "agent_id": self.agent_id,
                "state": self._state.value,
                "execution_id": self._execution_id,
                "is_interrupted": self._interruption_event.is_set(),
                "execution_start_time": self._execution_start_time.isoformat() if self._execution_start_time else None
            }
            
            if self._execution_start_time:
                status["execution_duration_seconds"] = (datetime.now() - self._execution_start_time).total_seconds()
            
            return status
    
    def __repr__(self) -> str:
        """String representation."""
        return f"AgentController(agent_id={self.agent_id}, state={self.state.value})"