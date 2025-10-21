"""
Hook → Event mapping utilities.

Converts hook contexts emitted by the hook system into typed events defined in
`event_types.py` (e.g., ToolExecStartEvent, StreamDeltaEvent, ContextUpdatedEvent).
"""

from __future__ import annotations

from typing import Any, Optional

from ..hooks.execution import HookType
from ..hooks.execution_contexts import (
    BaseExecContext,
    ToolExecContext,
    StreamExecContext,
    ContextExecContext,
    MessageExecContext,
)
from .event_types import (
    AgentEventBase,
    ToolExecStartEvent,
    ToolExecCompleteEvent,
    ToolExecErrorEvent,
    ToolCallPreEvent,
    ToolCallPostEvent,
    ToolTaskStartedEvent,
    ToolTaskCompletedEvent,
    ToolTaskFailedEvent,
    StreamDeltaEvent,
    StreamToolStartEvent,
    StreamToolDeltaEvent,
    StreamToolCompleteEvent,
    StreamToolResultEvent,
    ContextUpdatedEvent,
    ContextAddedEvent,
    ContextDispatchedEvent,
    MessageUserInputEvent,
    MessageProviderResponseEvent,
    MessageErrorEvent,
    ScaffoldOpCompletedEvent,
    ScaffoldStateChangedEvent,
)


def _base_meta(ctx: BaseExecContext) -> dict:
    return {
        "agent_id": getattr(ctx, "agent_id", None),
        "execution_id": getattr(ctx, "execution_id", None),
    }


def map_hook_context_to_event(hook_type: HookType, ctx: BaseExecContext) -> Optional[AgentEventBase]:
    """Map a hook invocation to a typed event instance.

    Returns None when no direct event mapping is applicable.
    """
    meta = _base_meta(ctx)

    # Tool lifecycle (non-streaming)
    if hook_type == HookType.BEFORE_TOOL_EXECUTION and isinstance(ctx, ToolExecContext):
        return ToolExecStartEvent(tool_name=getattr(ctx, "tool_name", ""), metadata=meta)

    if hook_type == HookType.AFTER_TOOL_EXECUTION and isinstance(ctx, ToolExecContext):
        return ToolExecCompleteEvent(
            tool_name=getattr(ctx, "tool_name", ""),
            result=getattr(ctx, "result", None),
            metadata=meta,
        )

    if hook_type == HookType.ON_TOOL_ERROR and isinstance(ctx, ToolExecContext):
        err = getattr(ctx, "error", None)
        return ToolExecErrorEvent(
            tool_name=getattr(ctx, "tool_name", ""),
            error=str(err) if err is not None else "",
            metadata=meta,
        )

    # Streaming signals
    if hook_type in {HookType.ON_CONTENT_CHUNK, HookType.ON_STREAMING_CHUNK} and isinstance(ctx, StreamExecContext):
        # Map content chunks to StreamDeltaEvent
        chunk = getattr(ctx, "chunk_data", None)
        text = ""
        if isinstance(chunk, dict):
            text = chunk.get("delta") or chunk.get("content") or ""
        elif isinstance(chunk, str):
            text = chunk
        return StreamDeltaEvent(text=text, raw=chunk, metadata=meta)

    if hook_type == HookType.ON_TOOL_CALL_DETECTED and isinstance(ctx, StreamExecContext):
        # Treat as a tool start intent for streaming
        return StreamToolStartEvent(
            tool_name=str(getattr(ctx, "tool_name", "")),
            call_id=str(getattr(ctx, "tool_call_id", "")),
            metadata=meta,
        )

    if hook_type == HookType.ON_TOOL_START_CHUNK and isinstance(ctx, StreamExecContext):
        return StreamToolStartEvent(
            tool_name=str(getattr(ctx, "tool_name", "")),
            call_id=str(getattr(ctx, "tool_call_id", "")),
            metadata=meta,
        )

    if hook_type == HookType.ON_TOOL_DELTA_CHUNK and isinstance(ctx, StreamExecContext):
        return StreamToolDeltaEvent(
            tool_name=str(getattr(ctx, "tool_name", "")),
            call_id=str(getattr(ctx, "tool_call_id", "")),
            delta=dict(getattr(ctx, "chunk_data", {}) or {}),
            metadata=meta,
        )

    if hook_type == HookType.ON_TOOL_COMPLETE_CHUNK and isinstance(ctx, StreamExecContext):
        return StreamToolCompleteEvent(
            tool_name=str(getattr(ctx, "tool_name", "")),
            call_id=str(getattr(ctx, "tool_call_id", "")),
            metadata=meta,
        )

    if hook_type == HookType.ON_TOOL_RESULT_CHUNK and isinstance(ctx, StreamExecContext):
        return StreamToolResultEvent(
            tool_name=str(getattr(ctx, "tool_name", "")),
            call_id=str(getattr(ctx, "tool_call_id", "")),
            result=getattr(ctx, "result", None),
            metadata=meta,
        )

    # Context
    if isinstance(ctx, ContextExecContext):
        op = getattr(ctx, "operation_type", None)
        details = getattr(ctx, "metadata", {}) or {}
        if hook_type == HookType.CONTEXT_ADD:
            return ContextAddedEvent(selector=op, details=details, metadata=meta)
        if hook_type == HookType.CONTEXT_DISPATCH:
            return ContextDispatchedEvent(selector=op, details=details, metadata=meta)
        if hook_type == HookType.CONTEXT_UPDATE:
            return ContextUpdatedEvent(selector=op, change=details, metadata=meta)

    # Message editing
    if hook_type == HookType.MESSAGE_USER_INPUT and isinstance(ctx, MessageExecContext):
        length = None
        content = getattr(ctx, "message_content", None)
        if isinstance(content, str):
            length = len(content)
        return MessageUserInputEvent(content_length=length, metadata=meta)

    if hook_type == HookType.MESSAGE_PROVIDER_RESPONSE and isinstance(ctx, MessageExecContext):
        length = None
        content = getattr(ctx, "message_content", None)
        if isinstance(content, str):
            length = len(content)
        final = bool(getattr(ctx, "is_final_response", True))
        return MessageProviderResponseEvent(content_length=length, is_final_response=final, metadata=meta)

    if hook_type == HookType.MESSAGE_ERROR and isinstance(ctx, MessageExecContext):
        # Bubble up a message-level error event
        err = getattr(ctx, "error", None)
        return MessageErrorEvent(message=str(err) if err else "", metadata=meta)

    # Tool per-call hooks
    if hook_type == HookType.BEFORE_TOOL_CALL and isinstance(ctx, ToolExecContext):
        return ToolCallPreEvent(tool_name=getattr(ctx, "tool_name", ""), params=getattr(ctx, "tool_params", {}) or {}, metadata=meta)
    if hook_type == HookType.AFTER_TOOL_CALL and isinstance(ctx, ToolExecContext):
        return ToolCallPostEvent(tool_name=getattr(ctx, "tool_name", ""), result=getattr(ctx, "tool_result", None), metadata=meta)

    # ToolTaskLoop lifecycle hooks
    if hook_type == HookType.ON_TOOL_TASK_STARTED and isinstance(ctx, ToolExecContext):
        task_id = None
        md = getattr(ctx, "metadata", {}) or {}
        if isinstance(md, dict):
            task_id = md.get("task_id")
        return ToolTaskStartedEvent(tool_name=getattr(ctx, "tool_name", ""), task_id=str(task_id or ""), metadata=meta)
    if hook_type == HookType.ON_TOOL_TASK_COMPLETED and isinstance(ctx, ToolExecContext):
        task_id = None
        md = getattr(ctx, "metadata", {}) or {}
        if isinstance(md, dict):
            task_id = md.get("task_id")
        return ToolTaskCompletedEvent(tool_name=getattr(ctx, "tool_name", ""), task_id=str(task_id or ""), result=getattr(ctx, "tool_result", None), metadata=meta)
    if hook_type == HookType.ON_TOOL_TASK_FAILED and isinstance(ctx, ToolExecContext):
        task_id = None
        md = getattr(ctx, "metadata", {}) or {}
        if isinstance(md, dict):
            task_id = md.get("task_id")
        err = getattr(ctx, "error", None)
        return ToolTaskFailedEvent(tool_name=getattr(ctx, "tool_name", ""), task_id=str(task_id or ""), error=str(err) if err else "", metadata=meta)

    # Call intercept
    if hook_type == HookType.CALL_INTERCEPT:
        # Not enough structure here; future expansion point.
        # We could define a CallInterceptEvent if needed.
        return None

    # No direct mapping
    # Scaffold operation completed (major use case)
    if hook_type == HookType.ON_SCAFFOLD_OPERATION_COMPLETED:
        # This hook uses ScaffoldExecContext
        try:
            from ..hooks.execution_contexts import ScaffoldExecContext  # local import to avoid cycles
        except Exception:
            ScaffoldExecContext = None  # type: ignore
        if ScaffoldExecContext and isinstance(ctx, ScaffoldExecContext):
            op_result = getattr(ctx, "operation_result", None)
            success = None
            # Try to extract success flag if present on result object
            if hasattr(op_result, "success"):
                try:
                    success = bool(getattr(op_result, "success"))
                except Exception:
                    success = None
            return ScaffoldOpCompletedEvent(
                scaffold_type=getattr(ctx, "scaffold_type", ""),
                scaffold_id=getattr(ctx, "scaffold_id", ""),
                operation_name=getattr(ctx, "operation_name", ""),
                result=op_result,
                success=success,
                metadata=meta,
            )
        # If not typed, attempt best-effort mapping from known attributes
        return ScaffoldOpCompletedEvent(
            scaffold_type=str(getattr(ctx, "scaffold_type", "")),
            scaffold_id=str(getattr(ctx, "scaffold_id", "")),
            operation_name=str(getattr(ctx, "operation_name", "")),
            result=getattr(ctx, "operation_result", None),
            metadata=meta,
        )

    # Scaffold state change (new mapping for Task 6)
    if hook_type == HookType.ON_SCAFFOLD_STATE_CHANGE:
        # This hook uses ScaffoldExecContext
        try:
            from ..hooks.execution_contexts import ScaffoldExecContext  # local import to avoid cycles
        except Exception:
            ScaffoldExecContext = None  # type: ignore
        
        if ScaffoldExecContext and isinstance(ctx, ScaffoldExecContext):
            return ScaffoldStateChangedEvent(
                scaffold_type=getattr(ctx, "scaffold_type", ""),
                scaffold_id=getattr(ctx, "scaffold_id", ""),
                changed_fields=getattr(ctx, "changed_fields", None),
                snapshot=getattr(ctx, "snapshot", None),
                metadata=meta,
            )
        
        # If not typed, attempt best-effort mapping from known attributes
        return ScaffoldStateChangedEvent(
            scaffold_type=str(getattr(ctx, "scaffold_type", "")),
            scaffold_id=str(getattr(ctx, "scaffold_id", "")),
            changed_fields=getattr(ctx, "changed_fields", None),
            snapshot=getattr(ctx, "snapshot", None),
            metadata=meta,
        )

    # No direct mapping
    return None


__all__ = ["map_hook_context_to_event"]
