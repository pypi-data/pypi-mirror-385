"""
Enhanced Approval System for Context Scaffolds

Provides unified approval and input collection system for scaffold validation hooks.
Includes ApprovalResult, PolicyResult, and ScaffoldHooks for comprehensive tool validation.
"""

from dataclasses import dataclass
from typing import Optional, Any, Callable, Dict, List
from enum import Enum


@dataclass
class ApprovalResult:
    """
    Result of user approval request (handles both approval and input collection).
    
    Unified result type that can handle both approval decisions and input collection
    scenarios, providing consistent interface for scaffold validation hooks.
    
    Attributes:
        approved: Whether the operation was approved
        reason: Optional reason for denial or additional context
        remember_choice: Whether to remember this decision for future operations
        input_value: Collected input value (for input collection scenarios)
        expose_input: Whether to show the collected input value to LLM
        notification: Context message for LLM (appears as context component, offset=1, ttl=1)
        tool_message: Tool result content for LLM (appears in tool result)
    """
    approved: bool
    reason: Optional[str] = None
    remember_choice: bool = False
    
    # Input collection support
    input_value: Optional[Any] = None      # Collected input value
    expose_input: bool = True              # Whether to show input to LLM
    
    # Two message types for optimal DX
    notification: Optional[str] = None      # Context message for LLM (offset=1, ttl=1)
    tool_message: Optional[str] = None      # Tool result content for LLM
    
    @classmethod
    def APPROVED(cls, remember: bool = False, input_value: Any = None, expose_input: bool = True, 
                 notification: str = "", tool_message: str = "") -> 'ApprovalResult':
        """Create approved result with optional input value and messages."""
        return cls(
            approved=True, 
            remember_choice=remember,
            input_value=input_value,
            expose_input=expose_input,
            notification=notification,
            tool_message=tool_message
        )
    
    @classmethod
    def DENIED(cls, reason: str = "", notification: str = "", tool_message: str = "") -> 'ApprovalResult':
        """Create denied result with optional reason and messages."""
        return cls(
            approved=False, 
            reason=reason,
            notification=notification,
            tool_message=tool_message
        )


@dataclass
class PolicyResult:
    """
    Result of execution policy check.
    
    Represents the decision made by execution policies about whether to allow,
    block, or modify a tool execution request.
    
    Attributes:
        action: Policy decision action (ALLOW/BLOCK/MODIFY)
        message: Optional message to display to user/LLM
        reason: Optional reason for the decision
        approval_result: Optional ApprovalResult if approval was requested
    """
    action: str  # "ALLOW", "BLOCK", "MODIFY"
    message: Optional[str] = None
    reason: Optional[str] = None
    approval_result: Optional[ApprovalResult] = None
    
    @classmethod
    def ALLOW(cls, message: str = "") -> 'PolicyResult':
        """Create allow result with optional message."""
        return cls("ALLOW", message)
    
    @classmethod 
    def BLOCK(cls, reason: str, message: str = "") -> 'PolicyResult':
        """Create block result with required reason and optional message."""
        return cls("BLOCK", message or f"🚫 {reason}", reason)
    
    @classmethod
    def MODIFY(cls, message: str) -> 'PolicyResult':
        """Create modify result with required message."""
        return cls("MODIFY", f"🔄 {message}")
    
    @classmethod
    def APPROVAL_REQUIRED(cls, approval_result: ApprovalResult, message: str = "") -> 'PolicyResult':
        """Create result with approval decision attached."""
        action = "ALLOW" if approval_result.approved else "BLOCK"
        return cls(action, message, approval_result.reason, approval_result)


class ScaffoldHooks:
    """
    Scaffold-specific hooks accessor for unified approval and input collection.
    
    Provides a clean interface for scaffolds to register approval hooks that can
    handle both approval decisions and input collection scenarios through a single
    unified hook function.
    """
    
    def __init__(self, scaffold):
        """Initialize scaffold hooks for the given scaffold."""
        self.scaffold = scaffold
        self.approval_hook: Optional[Callable] = None
    
    def approval(self, func: Callable) -> Callable:
        """
        Decorator to set approval hook function (handles both approval and input collection).
        
        The decorated function should accept: title, message, command, context, **kwargs
        and return an ApprovalResult.
        
        Example:
            @scaffold.hooks.approval
            def my_approval_handler(title, message, command, context, **kwargs):
                if context.get('input_type') == 'password':
                    # Handle input collection
                    password = getpass.getpass(message)
                    return ApprovalResult.APPROVED(input_value=password, expose_input=False)
                else:
                    # Handle approval
                    response = input(f"{message} (y/n): ")
                    return ApprovalResult.APPROVED() if response == 'y' else ApprovalResult.DENIED()
        """
        self.approval_hook = func
        return func
    
    def request_approval(self, title: str, message: str, command: str, context: dict, **kwargs) -> ApprovalResult:
        """
        Request user approval (or input collection) using the configured approval hook.
        
        Args:
            title: Title/header for the approval request
            message: Main message/question to show to user
            command: Command or operation being requested
            context: Additional context dict (use 'input_type' key for input collection)
            **kwargs: Additional arguments passed to approval hook
            
        Returns:
            ApprovalResult with approval decision and any collected input
            
        Raises:
            NotImplementedError: If no approval hook is configured
        """
        if self.approval_hook is None:
            raise NotImplementedError(
                f"No approval hook configured. Set {self.scaffold.__class__.__name__}.hooks.approval_hook "
                f"or use @{self.scaffold.__class__.__name__.lower()}.hooks.approval decorator"
            )
        return self.approval_hook(title, message, command, context, **kwargs)