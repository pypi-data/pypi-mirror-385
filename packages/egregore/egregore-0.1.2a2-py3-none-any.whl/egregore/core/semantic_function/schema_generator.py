"""Schema and example generation."""

from typing import Any, Type, Dict, get_origin, get_args, Union
from pydantic import BaseModel

# Built-in type examples
TYPE_EXAMPLES = {
    str: "example_string",
    int: 42,
    float: 3.14,
    bool: True,
    list: ["item1", "item2"],
    dict: {"key": "value"}
}

def generate_json_schema(type_hint: Type) -> Dict[str, Any]:
    """Generate JSON schema for type.
    
    Args:
        type_hint: Type to generate schema for
        
    Returns:
        JSON schema dictionary
    """
    # Handle None type
    if type_hint is type(None):
        return {"type": "null"}
    
    # Handle BaseModel classes
    if _is_basemodel_type(type_hint):
        return type_hint.model_json_schema()
    
    # Handle generic types
    origin = get_origin(type_hint)
    if origin is not None:
        args = get_args(type_hint)
        
        if origin is list and args:
            return {
                "type": "array", 
                "items": generate_json_schema(args[0])
            }
        elif origin is dict:
            if len(args) >= 2:
                return {
                    "type": "object",
                    "additionalProperties": generate_json_schema(args[1])
                }
            return {"type": "object"}
        elif origin is Union:
            # Handle Optional (Union[X, None]) and other unions
            non_none_args = [arg for arg in args if arg is not type(None)]
            if len(non_none_args) == 1:
                # Optional type
                schema = generate_json_schema(non_none_args[0])
                schema["nullable"] = True
                return schema
            else:
                # Multiple union types
                return {"oneOf": [generate_json_schema(arg) for arg in args]}
    
    # Handle built-in types
    if type_hint == str:
        return {"type": "string"}
    elif type_hint == int:
        return {"type": "integer"}
    elif type_hint == float:
        return {"type": "number"}
    elif type_hint == bool:
        return {"type": "boolean"}
    elif type_hint == list:
        return {"type": "array"}
    elif type_hint == dict:
        return {"type": "object"}
    
    # Fallback for unknown types
    return {"type": "object"}

def generate_example_json(type_hint: Type, _visited=None) -> Any:
    """Generate example JSON for type.
    
    Args:
        type_hint: Type to generate example for
        _visited: Set of visited types (for circular reference detection)
        
    Returns:
        Example value of the specified type
    """
    # Prevent infinite recursion
    if _visited is None:
        _visited = set()
    
    if type_hint in _visited:
        return "..."  # Circular reference placeholder
    
    # Handle None type
    if type_hint is type(None):
        return None
    
    # Handle BaseModel classes
    if _is_basemodel_type(type_hint):
        _visited.add(type_hint)
        example = {}
        
        # Get model fields
        if hasattr(type_hint, 'model_fields'):
            for field_name, field_info in type_hint.model_fields.items():
                field_type = field_info.annotation if hasattr(field_info, 'annotation') else str
                example[field_name] = generate_example_json(field_type, _visited.copy())
        
        _visited.discard(type_hint)
        return example
    
    # Handle generic types
    origin = get_origin(type_hint)
    if origin is not None:
        args = get_args(type_hint)
        
        if origin is list and args:
            element_example = generate_example_json(args[0], _visited)
            return [element_example]
        elif origin is dict:
            if len(args) >= 2:
                key_example = generate_example_json(args[0], _visited)
                value_example = generate_example_json(args[1], _visited)
                return {key_example: value_example}
            return {"key": "value"}
        elif origin is Union:
            # Handle Optional (Union[X, None]) and other unions
            non_none_args = [arg for arg in args if arg is not type(None)]
            if non_none_args:
                return generate_example_json(non_none_args[0], _visited)
            return None
    
    # Handle built-in types with TYPE_EXAMPLES lookup
    if type_hint in TYPE_EXAMPLES:
        return TYPE_EXAMPLES[type_hint]
    
    # Fallback for unknown types
    return f"example_{type_hint.__name__}" if hasattr(type_hint, '__name__') else "example_value"

def _is_basemodel_type(type_hint: Type) -> bool:
    """Check if type is a Pydantic BaseModel."""
    try:
        return isinstance(type_hint, type) and issubclass(type_hint, BaseModel)
    except TypeError:
        return False