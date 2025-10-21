"""
Context Viewer utility functions for serialization and testing support.
"""

import json
from datetime import datetime
from typing import Any, Dict
from pathlib import Path


class ContextJSONEncoder(json.JSONEncoder):
    """JSON encoder that handles datetime and other PACT-specific objects"""
    
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        # Handle Pydantic models by using their dict representation
        if hasattr(obj, 'model_dump'):
            return obj.model_dump()
        # Handle other objects with dict representation
        if hasattr(obj, '__dict__'):
            return {
                '__type__': obj.__class__.__name__,
                '__data__': obj.__dict__
            }
        # For other non-serializable objects, convert to string representation
        try:
            return str(obj)
        except:
            return f"<{obj.__class__.__name__} object>"


def save_context_to_file(context, file_path: str) -> None:
    """Save context to JSON file with proper datetime handling
    
    Args:
        context: Context instance to save
        file_path: Path to save the JSON file
    """
    pact_data = context.model_dump()
    
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w') as f:
        json.dump(pact_data, f, indent=2, cls=ContextJSONEncoder)


def load_context_from_file(file_path: str) -> Dict[str, Any]:
    """Load context data from JSON file
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dictionary containing PACT data
    """
    with open(file_path, 'r') as f:
        return json.load(f)


def create_test_context():
    """Create a context with sample content for testing
    
    Returns:
        Context instance with test content
    """
    from egregore.core.context_management import Context, TextPACTCore
    
    context = Context()
    
    # Add system content
    context.insert("(d-1,0)", TextPACTCore(
        content="You are a helpful AI assistant. Please provide clear and concise responses.",
        id="system-prompt"
    ))
    
    # Add conversation history
    context.insert("(d1,0)", TextPACTCore(
        content="User: What is the capital of France?",
        id="user-message-1"
    ))
    
    context.insert("(d1,1)", TextPACTCore(
        content="Assistant: The capital of France is Paris.",
        id="assistant-response-1"
    ))
    
    # Add active message
    context.insert("(d0,0)", TextPACTCore(
        content="User: Can you tell me more about Paris?",
        id="active-user-message"
    ))
    
    return context


def validate_context_structure(context) -> Dict[str, Any]:
    """Validate context structure and return diagnostics
    
    Args:
        context: Context instance to validate
        
    Returns:
        Dictionary with validation results
    """
    diagnostics = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "info": {}
    }
    
    try:
        # Test basic operations
        rendered = context.render()
        diagnostics["info"]["render_length"] = len(rendered)
        
        # Test PACT serialization
        pact_data = context.model_dump()
        diagnostics["info"]["pact_keys"] = list(pact_data.keys()) if isinstance(pact_data, dict) else "Not a dict"
        
        # Test with ContextViewer
        from .viewer import ContextViewer
        viewer = ContextViewer(context)
        
        tree_view = viewer.view_tree()
        diagnostics["info"]["tree_view_length"] = len(tree_view)
        
        text_view = viewer.view_text()
        diagnostics["info"]["text_view_length"] = len(text_view)
        
        xml_view = viewer.view_xml()
        diagnostics["info"]["xml_view_length"] = len(xml_view)
        
        diagnostics["info"]["status"] = "All operations successful"
        
    except Exception as e:
        diagnostics["valid"] = False
        diagnostics["errors"].append(f"Validation failed: {str(e)}")
    
    return diagnostics