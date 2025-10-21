"""
Scaffold Notification System

Provides @notification decorator for scaffold-specific state monitoring and warning generation.
This system allows scaffolds to monitor their internal state and generate warnings for the LLM
when certain conditions are met (e.g., too many files opened, memory limits exceeded).
"""

from typing import List, Callable, TYPE_CHECKING, TypeVar, Any

if TYPE_CHECKING:
    from .base import BaseContextScaffold


F = TypeVar("F", bound=Callable[..., str])


def notification(func: F) -> F:
    """
    Decorator for scaffold-specific notification methods (safety valves).
    
    This decorator marks methods that should be called during each message cycle
    to check scaffold state and return warning messages for the LLM if needed.
    
    The decorated method should:
    - Take only self as parameter (scaffold instance)
    - Return string warning message or empty string
    - Check internal scaffold state (e.g., self.state.open_files)
    - Generate user-friendly warnings for the LLM
    
    Notifications are automatically added to context with default temporal properties:
    - ttl=0 (immediate expiry after one cycle)
    - cycle=1 (appears every cycle while condition is true)
    - offset=1 (appears after main message content)
    
    Usage:
        class FileScaffold(BaseContextScaffold):
            @notification
            def too_many_files_warning(self):
                if len(self.state.open_files) > 10:
                    return "⚠️ Too many files opened! Close some first."
                return ""
            
            @notification
            def memory_warning(self):
                if self.state.total_file_size > 1_000_000:  # 1MB limit
                    return "🚨 File context too large - LLM will forget things!"
                return ""
    
    Args:
        func: Function to decorate (should return string warning or empty string)
        
    Returns:
        Decorated function with _is_notification marker attribute
    """
    # Mark the method as a notification handler
    func._is_notification = True  # type: ignore[attr-defined]
    return func


def get_scaffold_notifications(scaffold: 'BaseContextScaffold') -> List[str]:
    """
    Get all notification messages from a scaffold's @notification decorated methods.
    
    This function discovers all methods decorated with @notification on the scaffold
    instance, calls them, and collects any non-empty warning messages they return.
    
    Args:
        scaffold: BaseContextScaffold instance to check for notifications
        
    Returns:
        List of notification warning strings (empty list if no warnings)
    """
    notifications = []
    
    try:
        # Find all methods marked with @notification
        for attr_name in dir(scaffold):
            try:
                attr = getattr(scaffold, attr_name)
                
                # Check if it's a callable with notification marker
                if callable(attr) and hasattr(attr, '_is_notification'):
                    # Call method (should only take self parameter)
                    result = attr()
                    
                    # Add non-empty results to notifications
                    if result and isinstance(result, str) and result.strip():
                        notifications.append(result.strip())
                        
            except Exception as e:
                print(f"Warning: Scaffold notification error in method '{attr_name}': {e}")
                continue
                
    except Exception as e:
        print(f"Warning: Could not get scaffold notifications: {e}")
    
    return notifications


def trigger_scaffold_notifications(agent) -> List[str]:
    """
    Trigger notifications for all scaffolds registered with an agent.
    
    This function discovers all scaffolds associated with an agent and collects
    notification messages from their @notification decorated methods.
    
    Args:
        agent: Agent instance to check for scaffold notifications
        
    Returns:
        List of all notification messages from all scaffolds
    """
    all_notifications = []
    
    try:
        # Get scaffolds from agent (implementation depends on agent architecture)
        scaffolds = getattr(agent, 'scaffolds', [])
        
        for scaffold in scaffolds:
            try:
                scaffold_notifications = get_scaffold_notifications(scaffold)
                all_notifications.extend(scaffold_notifications)
            except Exception as e:
                print(f"Warning: Could not get notifications from scaffold: {e}")
                continue
                
    except Exception as e:
        print(f"Warning: Could not trigger scaffold notifications: {e}")
    
    return all_notifications