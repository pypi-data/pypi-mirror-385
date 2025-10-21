# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportCallIssue=false, reportOperatorIssue=false, reportIndexIssue=false, reportReturnType=false, reportOptionalMemberAccess=false, reportAssignmentType=false
"""
Declarative Context Template System

Provides ContextStructure for defining reusable context templates with
listener-based population logic.
"""

import uuid
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass

from .pact.components.core import PACTCore


@dataclass
class ListenerMetadata:
    """Metadata for template listener functions"""
    component_type: str
    handler: Callable
    properties: Dict[str, Any]


class ContextTree:
    """Template container with listener decorator support for declarative context management"""
    
    def __init__(self, *components: PACTCore):
        """
        Initialize template with root components.

        Args:
            *components: Root PACTCore instances that define the template structure
        """
        self.root_components = list(components)
        self.listeners: Dict[str, List[ListenerMetadata]] = {}
        self.template_id = str(uuid.uuid4())
    
    def listener(self, component_type: str, **properties):
        """
        Decorator for template-scoped listeners that respond to agent state changes.
        
        Usage:
            @template.listener("tool_explanations")
            def handle_tool_events(agent: Agent):
                if agent.tools_help_enabled:
                    template["tool_explanations"] = format_tool_docs(agent.tools)
        
        Args:
            component_type: The type of component to populate (matches TemplateComponent type)
            **properties: Additional properties for listener configuration
            
        Returns:
            Decorator function that registers the listener
        """
        def decorator(func: Callable) -> Callable:
            # Register listener for this component type
            if component_type not in self.listeners:
                self.listeners[component_type] = []
            
            metadata = ListenerMetadata(
                component_type=component_type,
                handler=func,
                properties=properties
            )
            
            self.listeners[component_type].append(metadata)
            return func
        
        return decorator
    
    def trigger_listeners(self, agent) -> None:
        """
        Trigger all registered listeners with current agent state.
        
        Args:
            agent: Agent instance to pass to listener functions
        """
        try:
            for component_type, listener_list in self.listeners.items():
                for listener_metadata in listener_list:
                    try:
                        # Call listener function with agent
                        listener_metadata.handler(agent)
                    except Exception as e:
                        print(f"Warning: Template listener error for '{component_type}': {e}")
                        continue
        except Exception as e:
            print(f"Warning: Could not trigger template listeners: {e}")
    
    def find_component_by_type(self, component_type: str) -> Optional[PACTCore]:
        """
        Find component by type in template tree.
        
        This method delegates to MessageScheduler's smart caching system for O(1) lookups.
        
        Args:
            component_type: The type identifier to search for
            
        Returns:
            PACTCore if found, None otherwise
        """
        # This will be connected to MessageScheduler's caching in integration phase
        # For now, implement basic recursive search
        return self._search_components_by_type(self.root_components, component_type)
    
    def _search_components_by_type(self, components: List[PACTCore], target_type: str) -> Optional[PACTCore]:
        """Recursively search for component by type"""
        for component in components:
            # Check if this component has the target type
            if hasattr(component, 'type') and component.type == target_type:
                return component
            
            # Search children if this component has list content
            if hasattr(component, 'content') and isinstance(component.content, list):
                found = self._search_components_by_type(component.content, target_type)
                if found:
                    return found
        
        return None
    
    def __getitem__(self, component_type: str) -> Optional[PACTCore]:
        """Allow template["type"] access for component lookup"""
        return self.find_component_by_type(component_type)
    
    def __setitem__(self, component_type: str, content) -> None:
        """
        Allow template["type"] = content assignment for direct content manipulation.
        
        This delegates to MessageScheduler's assign_template_content method for consistency.
        
        Args:
            component_type: The type of component to assign content to
            content: Content to assign (string, PACTCore, or list)
        """
        # This will be connected to MessageScheduler in integration phase
        # For now, implement basic assignment
        component = self.find_component_by_type(component_type)
        if component and hasattr(component, 'content'):
            component.content = content
        else:
            print(f"Warning: Could not assign content to template component type '{component_type}'")
    
    def __repr__(self) -> str:
        component_count = len(self.root_components)
        listener_count = sum(len(listeners) for listeners in self.listeners.values())
        return f"ContextStructure(id='{self.template_id[:8]}...', components={component_count}, listeners={listener_count})"