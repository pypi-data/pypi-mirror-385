"""Error handling data classes."""

from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel

class HandlerAction(Enum):
    """Actions for error handlers."""
    RETRY = "retry"
    ABORT = "abort"  
    RETURN = "return"
    RAISE = "raise"
    PASS = "pass"

class ErrorContext(BaseModel):
    """Context information for error handlers."""
    exception: Exception
    attempt_index: int
    max_retries: int
    provider: str
    model: str
    return_type: Any  # Changed from 'type' to 'Any' to handle typing special forms
    last_assistant: Optional[Any] = None  # Response object from provider
    user_prompt: str
    system_prompt: str

    model_config = {"arbitrary_types_allowed": True}

class HandlerResult(BaseModel):
    """Result from error handler."""
    action: HandlerAction
    user_feedback: Optional[str] = None    # becomes a new UserMessage
    system_delta: Optional[str] = None     # appended to the single SystemMessage
    model_overrides: Optional[dict] = None # e.g., {"temperature": 0.2, "top_p": 0.7}
    backoff_seconds: Optional[float] = None
    fallback_value: Optional[Any] = None   # used when action == HandlerAction.RETURN

    model_config = {"arbitrary_types_allowed": True}