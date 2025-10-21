"""
Sequence package for workflow orchestration.

This package provides composable workflow sequences with advanced features:
- Node inheritance for composability with >> operator
- WorkflowController for external workflow control (pause/resume/stop)
- JSON serialization for Cerebrum visual builder integration
- Mermaid diagram generation for schema visualization
- State management with node result indexing
- Execution tracking and observer pattern integration
- Async node support and nested sequence composition

Main classes:
- Sequence: Core workflow sequence class
- WorkflowController: External workflow control
- WorkflowStoppedException: Exception for stopped workflows

Utilities:
- render_mermaid_schema: Generate Mermaid diagrams
- sequence_to_mermaid: Legacy Mermaid function
"""

from .base import (
    Sequence,
    WorkflowController, 
    WorkflowStoppedException
)

from .mermaid_renderer import (
    render_mermaid_schema,
    sequence_to_mermaid,
    MermaidRenderer
)

__all__ = [
    # Core classes
    'Sequence',
    'WorkflowController',
    'WorkflowStoppedException',
    
    # Rendering utilities
    'render_mermaid_schema',
    'sequence_to_mermaid',
    'MermaidRenderer'
]