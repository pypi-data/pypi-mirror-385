"""
Typed event classes for the Agent Event Stream and hook emissions.

These classes provide a stable, developer-friendly surface with clear names
that match our planned API (e.g., AgentIdleEvent, StreamDeltaEvent, AgentDoneEvent).

They are transport-agnostic: use them for CLI, WebSocket, or workflow bridges.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class AgentEventBase:
    """Common metadata for all events."""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    agent_id: Optional[str] = None
    execution_id: Optional[str] = None
    sequence: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


# Lifecycle / Chat
@dataclass
class AgentIdleEvent(AgentEventBase):
    """Agent is idle and ready for the next input."""
    pass


@dataclass
class StreamDeltaEvent(AgentEventBase):
    """A streamed token/text delta from the provider."""
    text: str = ""
    raw: Optional[Any] = None  # provider/native chunk (optional)


@dataclass
class AgentDoneEvent(AgentEventBase):
    """Turn completed (either naturally or interrupted)."""
    interrupted: bool = False
    citations: Optional[List[Dict[str, Any]]] = None
    usage: Optional[Dict[str, Any]] = None
    finish_reason: Optional[str] = None
    error: Optional[str] = None


@dataclass
class AgentErrorEvent(AgentEventBase):
    """Top-level agent error that prevented normal turn completion."""
    message: str = ""
    detail: Optional[str] = None


# Tool lifecycle (non-streaming)
@dataclass
class ToolExecStartEvent(AgentEventBase):
    tool_name: str = ""
    call_id: Optional[str] = None


@dataclass
class ToolExecCompleteEvent(AgentEventBase):
    tool_name: str = ""
    result: Optional[Any] = None
    call_id: Optional[str] = None


@dataclass
class ToolExecErrorEvent(AgentEventBase):
    tool_name: str = ""
    error: str = ""
    call_id: Optional[str] = None


# Tool signaling from streaming (intent + deltas)
@dataclass
class StreamToolStartEvent(AgentEventBase):
    tool_name: str = ""
    call_id: str = ""


@dataclass
class StreamToolDeltaEvent(AgentEventBase):
    tool_name: str = ""
    call_id: str = ""
    delta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StreamToolCompleteEvent(AgentEventBase):
    tool_name: str = ""
    call_id: str = ""


@dataclass
class StreamToolResultEvent(AgentEventBase):
    tool_name: str = ""
    call_id: str = ""
    result: Any = None


# Context / Message updates
@dataclass
class ContextUpdatedEvent(AgentEventBase):
    selector: Optional[str] = None
    change: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MessageUserInputEvent(AgentEventBase):
    content_length: Optional[int] = None


@dataclass
class MessageProviderResponseEvent(AgentEventBase):
    content_length: Optional[int] = None
    is_final_response: bool = True


__all__ = [
    # Base
    "AgentEventBase",
    # Lifecycle / chat
    "AgentIdleEvent",
    "StreamDeltaEvent",
    "AgentDoneEvent",
    "AgentErrorEvent",
    # Tools
    "ToolExecStartEvent",
    "ToolExecCompleteEvent",
    "ToolExecErrorEvent",
    # Streaming tool signals
    "StreamToolStartEvent",
    "StreamToolDeltaEvent",
    "StreamToolCompleteEvent",
    "StreamToolResultEvent",
    # Context / messages
    "ContextUpdatedEvent",
    "MessageUserInputEvent",
    "MessageProviderResponseEvent",
    "MessageErrorEvent",
    "ContextAddedEvent",
    "ContextDispatchedEvent",
    "ToolCallPreEvent",
    "ToolCallPostEvent",
    "ToolTaskStartedEvent",
    "ToolTaskCompletedEvent",
    "ToolTaskFailedEvent",
]

# --- Scaffold events (major use case) ---

@dataclass
class ScaffoldOpStartedEvent(AgentEventBase):
    """A scaffold operation started (if available)."""
    scaffold_type: str = ""
    scaffold_id: str = ""
    operation_name: str = ""


@dataclass
class ScaffoldOpCompletedEvent(AgentEventBase):
    """A scaffold operation completed successfully."""
    scaffold_type: str = ""
    scaffold_id: str = ""
    operation_name: str = ""
    result: Any = None
    success: Optional[bool] = None


@dataclass
class ScaffoldOpFailedEvent(AgentEventBase):
    """A scaffold operation failed."""
    scaffold_type: str = ""
    scaffold_id: str = ""
    operation_name: str = ""
    error: str = ""


@dataclass
class ScaffoldStateChangedEvent(AgentEventBase):
    """A scaffold's state changed and was re-rendered."""
    scaffold_type: str = ""
    scaffold_id: str = ""
    changed_fields: Optional[list[str]] = None
    snapshot: Optional[dict] = None
# Tool call (per-call granularity)
@dataclass
class ToolCallPreEvent(AgentEventBase):
    tool_name: str = ""
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolCallPostEvent(AgentEventBase):
    tool_name: str = ""
    result: Any = None


# Tool task loop (async engine lifecycle)
@dataclass
class ToolTaskStartedEvent(AgentEventBase):
    tool_name: str = ""
    task_id: str = ""


@dataclass
class ToolTaskCompletedEvent(AgentEventBase):
    tool_name: str = ""
    task_id: str = ""
    result: Any = None


@dataclass
class ToolTaskFailedEvent(AgentEventBase):
    tool_name: str = ""
    task_id: str = ""
    error: str = ""

@dataclass
class MessageErrorEvent(AgentEventBase):
    message: str = ""
    detail: Optional[str] = None

@dataclass
class ContextAddedEvent(AgentEventBase):
    selector: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContextDispatchedEvent(AgentEventBase):
    selector: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)



__all__ += [
    "ScaffoldOpStartedEvent",
    "ScaffoldOpCompletedEvent",
    "ScaffoldOpFailedEvent",
    "ScaffoldStateChangedEvent",
]
