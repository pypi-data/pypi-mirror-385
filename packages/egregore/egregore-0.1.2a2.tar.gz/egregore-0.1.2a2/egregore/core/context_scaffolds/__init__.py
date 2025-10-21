"""
Context Scaffolds - V2 Scaffold Infrastructure

Core scaffold infrastructure and data types for V2 Context Scaffolds system.
This module provides the foundation for all scaffold implementations including:

- ScaffoldState: Change-tracking state management for scaffolds with automatic change detection
- @operation: Decorator for marking scaffold operations (formerly @scaffold_operation)
- SystemInterface: Core scaffold registry and management
- ScaffoldAccessor: Dynamic attribute access for agent.scaffolds.<name>
- ScaffoldProxy: Operation exposure and state access
- ScaffoldResult: Context component for scaffold operation results
- Exception hierarchy: Comprehensive error handling for scaffolds
- Change tracking system: Automatic mutation detection for all data types

Usage:
    ```python
    from egregore.core.context_scaffolds import (
        ScaffoldState, 
        operation,
        SystemInterface,
        ScaffoldAccessor,
        InternalNotesScaffold,
        ChangeTrackingList
    )
    
    # Create scaffold with state and automatic change detection
    class MyScaffold(BaseContextScaffold):
        def __init__(self):
            self.state = ScaffoldState(count=0, items=[])
        
        @operation(description="Increment counter")
        def increment(self) -> int:
            self.state.count += 1
            return self.state.count
        
        @operation(description="Add item")
        def add_item(self, item: str) -> str:
            # Automatic change detection - no manual mark_changed needed!
            self.state.items.append(item)  # Triggers scaffold re-rendering automatically
            return f"Added {item}"
    
    # Use with agent
    system = SystemInterface()
    accessor = ScaffoldAccessor(system)
    
    system.add_scaffold("counter", MyScaffold())
    result = accessor.counter.increment()  # Returns 1
    ```

## Scaffold Operation Retention System

Scaffolds support intelligent retention management for conversation memory control:

### Basic Retention Configuration
    ```python
    # Simple scaffold-level defaults
    scaffold = InternalNotesScaffold(
        operation_ttl=5,        # Operations live for 5 conversation turns  
        operation_retention=3   # Keep maximum of 3 operations in memory
    )
    ```

### Agent-Level Default Configuration
    ```python
    from egregore.core.agent.base import Agent
    
    # Agent provides retention defaults for all its scaffolds
    agent = Agent(
        provider="openai",
        operation_ttl=5,         # Default TTL for all scaffold operations
        operation_retention=10,  # Default retention limit for all operations
        scaffolds=[scaffold]
    )
    ```

### Granular Per-Operation Control
    ```python
    # Fine-grained control over specific operations
    scaffold = InternalNotesScaffold(
        operation_ttl=5,
        operation_retention=10,
        operation_config={
            "update": {"ttl": 2, "retention": 1},    # Short-lived updates
            "append": {"retention": 5},              # TTL from scaffold default (5)
            "clear": {"ttl": 20}                     # Long-lived clears, retention from scaffold default (10)
        }
    )
    ```

### Retention Configuration Priority (Cascading System)
    The system resolves retention settings with the following priority:
    1. **Per-operation config** (highest priority) - Specific operation overrides
    2. **Scaffold-level defaults** - Scaffold instance configuration
    3. **Agent-level defaults** - Agent-wide configuration
    4. **System defaults** - Built-in fallbacks (TTL=3, retention=10)

### Memory Management Features
    - **Episodic retention**: Based on conversation turns, not wall-clock time
    - **LLM pairing integrity**: Tool calls and results expire together  
    - **Automatic cleanup**: MessageScheduler enforces retention limits globally
    - **Capacity-based pruning**: Oldest operations removed when limits exceeded
    - **TTL countdown**: Operations age out naturally over conversation turns

### Usage Examples
    ```python
    # Memory-efficient notes for long conversations  
    notes = InternalNotesScaffold(
        operation_ttl=3,        # Notes expire after 3 turns
        operation_retention=5   # Keep only 5 most recent notes
    )
    
    # High-retention configuration for important data
    important_scaffold = MyDataScaffold(
        operation_ttl=20,       # Long-lived operations
        operation_retention=50  # Large memory capacity
    )
    
    # Mixed configuration for different operation types
    mixed_scaffold = TaskManagerScaffold(
        operation_ttl=10,
        operation_retention=15,
        operation_config={
            "create_task": {"ttl": 15, "retention": 20},  # Important tasks live longer
            "mark_done": {"ttl": 2, "retention": 3},      # Completion actions are short-lived
            "list_tasks": {"ttl": 1, "retention": 1}      # Queries are very short-lived
        }
    )
    ```

### Integration with PACT Selector System
    Scaffold operations are discoverable via PACT selectors in conversation context:
    ```python
    # Find all scaffold results in conversation
    scaffold_ops = context.select(".cb:scaffold_result")
    
    # Find specific scaffold operations
    notes_ops = context.select(".cb:scaffold_result[scaffold_id='internal_notes_123']")
    ```
"""

# Core data types and state management
from .data_types import ScaffoldState, StateOperatorResult

# Change tracking system
from .change_tracking import (
    ChangeNotifier,
    ChangeTrackingList,
    ChangeTrackingDict, 
    ChangeTrackingSet,
    ChangeTrackingProxy
)

# Base scaffold class
from .base import BaseContextScaffold

# Scaffold operation decorators
from .decorators import (
    operation,
    ScaffoldOperationMetadata,
    get_scaffold_operations,
    is_scaffold_operation,
    get_operation_metadata
)

# Registry and access management  
from .registry import (
    SystemInterface,
    ScaffoldAccessor,
    ScaffoldProxy
)

# Context components
from .components import ScaffoldResult

# Exception hierarchy
from .exceptions import (
    ScaffoldError,
    ScaffoldStateError,
    ScaffoldOperationError,
    ScaffoldRegistrationError,
    ScaffoldConfigurationError,
    ScaffoldAccessError,
    ScaffoldValidationError,
    # Convenience functions
    scaffold_not_found_error,
    operation_not_found_error,
    invalid_state_error
)

# Built-in scaffolds
from .builtins import InternalNotesScaffold, NotesState

__all__ = [
    # Core data types and base class
    'ScaffoldState',
    'StateOperatorResult',
    'BaseContextScaffold',
    
    # Change tracking system
    'ChangeNotifier',
    'ChangeTrackingList',
    'ChangeTrackingDict',
    'ChangeTrackingSet',
    'ChangeTrackingProxy',
    
    # Decorators and metadata
    'operation',
    'ScaffoldOperationMetadata', 
    'get_scaffold_operations',
    'is_scaffold_operation',
    'get_operation_metadata',
    
    # Registry and access
    'SystemInterface',
    'ScaffoldAccessor',
    'ScaffoldProxy',
    
    # Context components
    'ScaffoldResult',
    
    # Exceptions
    'ScaffoldError',
    'ScaffoldStateError', 
    'ScaffoldOperationError',
    'ScaffoldRegistrationError',
    'ScaffoldConfigurationError',
    'ScaffoldAccessError',
    'ScaffoldValidationError',
    
    # Exception convenience functions
    'scaffold_not_found_error',
    'operation_not_found_error',
    'invalid_state_error',
    
    # Built-in scaffolds
    'InternalNotesScaffold',
    'NotesState'
]