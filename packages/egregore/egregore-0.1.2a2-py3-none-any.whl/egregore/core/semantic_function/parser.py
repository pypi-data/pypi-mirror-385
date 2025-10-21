"""Type-based response parsing."""

import json
from typing import Any, Type, Union, get_origin, get_args
from pydantic import BaseModel, ValidationError

def parse_response(response: str, return_type: Type) -> Any:
    """Parse response based on return type.
    
    Args:
        response: Raw LLM response string
        return_type: Target type for parsing
        
    Returns:
        Parsed response in the target type
        
    Raises:
        ValueError: If parsing fails
        TypeError: If return_type is not supported
    """
    if not response or not response.strip():
        if return_type == str:
            return ""
        else:
            raise ValueError("Empty response cannot be parsed to non-string type")
    
    response = response.strip()
    
    # Handle string type (no parsing needed)
    if return_type == str:
        # Handle JSON-quoted strings
        if response.startswith('"') and response.endswith('"'):
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                pass
        return response
    
    # Handle basic types
    if return_type == int:
        return _parse_int(response)
    elif return_type == float:
        return _parse_float(response)
    elif return_type == bool:
        return _parse_bool(response)
    elif return_type == list:
        return _parse_list(response)
    elif return_type == dict:
        return _parse_dict(response)
    
    # Handle Pydantic BaseModel types
    if _is_basemodel_type(return_type):
        return _parse_basemodel(response, return_type)
    
    # Handle Union types (including Optional)
    origin = get_origin(return_type)
    if origin is Union:
        return _parse_union(response, return_type)
    
    # Handle generic list types like List[str]
    if origin is list:
        return _parse_generic_list(response, return_type)
    
    # Handle generic dict types like Dict[str, Any]
    if origin is dict:
        return _parse_generic_dict(response, return_type)
    
    # Fallback: try JSON parsing for complex types
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        # If JSON fails, return string for unknown types
        return response

def _parse_int(response: str) -> int:
    """Parse integer from response."""
    # Try direct conversion first
    try:
        return int(response)
    except ValueError:
        pass
    
    # Try to extract number from text
    import re
    numbers = re.findall(r'-?\d+', response)
    if numbers:
        return int(numbers[0])
    
    raise ValueError(f"Cannot parse integer from: {response}")

def _parse_float(response: str) -> float:
    """Parse float from response."""
    try:
        return float(response)
    except ValueError:
        pass
    
    # Try to extract number from text
    import re
    numbers = re.findall(r'-?\d+\.?\d*', response)
    if numbers:
        return float(numbers[0])
    
    raise ValueError(f"Cannot parse float from: {response}")

def _parse_bool(response: str) -> bool:
    """Parse boolean from response."""
    response_lower = response.lower().strip()
    
    # Direct matches
    if response_lower in ['true', 'yes', '1', 'on', 'enabled']:
        return True
    elif response_lower in ['false', 'no', '0', 'off', 'disabled']:
        return False
    
    # Try JSON parsing
    try:
        parsed = json.loads(response)
        if isinstance(parsed, bool):
            return parsed
    except json.JSONDecodeError:
        pass
    
    # Look for boolean keywords in text
    if any(word in response_lower for word in ['true', 'yes', 'correct', 'right', 'positive']):
        return True
    elif any(word in response_lower for word in ['false', 'no', 'incorrect', 'wrong', 'negative']):
        return False
    
    raise ValueError(f"Cannot parse boolean from: {response}")

def _parse_list(response: str) -> list:
    """Parse list from response."""
    import ast

    # Strategy 1: Try JSON parsing first (strict JSON with double quotes)
    try:
        parsed = json.loads(response)
        if isinstance(parsed, list):
            return parsed
    except json.JSONDecodeError:
        pass

    # Strategy 2: Try Python literal evaluation (handles single quotes)
    try:
        parsed = ast.literal_eval(response.strip())
        if isinstance(parsed, list):
            return parsed
    except (ValueError, SyntaxError):
        pass

    # Strategy 3: Try to extract JSON from mixed text
    extracted_json = _extract_json_from_text(response)
    if extracted_json:
        try:
            parsed = json.loads(extracted_json)
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            pass

    # Strategy 4: Try to parse as simple comma-separated values
    if ',' in response and not response.startswith('['):
        items = [item.strip() for item in response.split(',')]
        return items

    raise ValueError(f"Cannot parse list from: {response}")

def _parse_dict(response: str) -> dict:
    """Parse dict from response."""
    import logging
    import ast
    logger = logging.getLogger("semantic_function.parser")
    logger.debug(f"_parse_dict received: {repr(response)}")

    # Strategy 1: Try JSON parsing first (strict JSON with double quotes)
    try:
        parsed = json.loads(response)
        if isinstance(parsed, dict):
            logger.debug(f"Successfully parsed dict: {parsed}")
            return parsed
    except json.JSONDecodeError as e:
        logger.debug(f"JSON parsing failed: {e}")
        pass

    # Strategy 2: Try Python literal evaluation (handles single quotes)
    try:
        parsed = ast.literal_eval(response.strip())
        if isinstance(parsed, dict):
            logger.debug(f"Successfully parsed dict via literal_eval: {parsed}")
            return parsed
    except (ValueError, SyntaxError) as e:
        logger.debug(f"literal_eval parsing failed: {e}")
        pass

    # Strategy 3: Try to extract JSON from mixed text (common in LLM responses)
    extracted_json = _extract_json_from_text(response)
    logger.debug(f"Extracted JSON: {repr(extracted_json)}")
    if extracted_json:
        try:
            parsed = json.loads(extracted_json)
            if isinstance(parsed, dict):
                logger.debug(f"Successfully parsed dict from extracted JSON: {parsed}")
                return parsed
        except json.JSONDecodeError as e:
            logger.debug(f"Extracted JSON parsing failed: {e}")
            pass

    logger.error(f"Cannot parse dict from: {repr(response)}")
    raise ValueError(f"Cannot parse dict from: {response}")

def _extract_json_from_text(text: str) -> str:
    """Extract JSON object or array from mixed text."""
    import re
    
    # Look for JSON objects {...}
    obj_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    obj_matches = re.findall(obj_pattern, text)
    
    for match in obj_matches:
        try:
            json.loads(match)  # Validate it's real JSON
            return match
        except json.JSONDecodeError:
            continue
    
    # Look for JSON arrays [...]
    arr_pattern = r'\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\]'
    arr_matches = re.findall(arr_pattern, text)
    
    for match in arr_matches:
        try:
            json.loads(match)  # Validate it's real JSON
            return match
        except json.JSONDecodeError:
            continue
    
    return ""

def _is_basemodel_type(return_type: Type) -> bool:
    """Check if type is a Pydantic BaseModel."""
    try:
        return isinstance(return_type, type) and issubclass(return_type, BaseModel)
    except TypeError:
        return False

def _parse_basemodel(response: str, return_type: Type[BaseModel]) -> BaseModel:
    """Parse Pydantic BaseModel from response with multiple parsing strategies."""
    import re
    import ast
    
    # Strategy 1: Try JSON parsing first
    try:
        data = json.loads(response)
        return return_type(**data)
    except json.JSONDecodeError:
        pass
    except ValidationError as e:
        raise ValueError(f"BaseModel validation failed: {e}")
    
    # Strategy 2: Try Python dict parsing (common LLM format)
    try:
        # Convert single quotes to double quotes for JSON compatibility
        json_response = response.replace("'", '"')
        data = json.loads(json_response)
        return return_type(**data)
    except json.JSONDecodeError:
        pass
    except ValidationError as e:
        raise ValueError(f"BaseModel validation failed: {e}")
    
    # Strategy 3: Extract JSON from mixed text using regex
    try:
        # Look for JSON-like objects in the response
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, response)
        for match in matches:
            try:
                # Try parsing each potential JSON object
                data = json.loads(match)
                if isinstance(data, dict):
                    return return_type(**data)
            except json.JSONDecodeError:
                try:
                    # Try with quote conversion
                    json_match = match.replace("'", '"')
                    data = json.loads(json_match)
                    if isinstance(data, dict):
                        return return_type(**data)
                except json.JSONDecodeError:
                    continue
            except ValidationError as e:
                raise ValueError(f"BaseModel validation failed: {e}")
    except Exception:
        pass
    
    # Strategy 4: Try Python literal evaluation as last resort
    try:
        data = ast.literal_eval(response.strip())
        if isinstance(data, dict):
            return return_type(**data)
    except (ValueError, SyntaxError):
        pass
    except ValidationError as e:
        raise ValueError(f"BaseModel validation failed: {e}")
    
    # If all strategies fail, raise error
    raise ValueError(f"Cannot parse BaseModel from response: {response}")

def _parse_union(response: str, return_type: Type) -> Any:
    """Parse Union type (try each type in order)."""
    args = get_args(return_type)
    
    for arg_type in args:
        if arg_type is type(None):
            continue  # Skip None type for now
            
        try:
            return parse_response(response, arg_type)
        except (ValueError, TypeError):
            continue  # Try next type
    
    # If all types fail, check if None is allowed
    if type(None) in args:
        return None
    
    raise ValueError(f"Cannot parse response as any type in Union: {return_type}")

def _parse_generic_list(response: str, return_type: Type) -> list:
    """Parse generic list type like List[str]."""
    # First parse as basic list
    base_list = _parse_list(response)
    
    # Get the element type
    args = get_args(return_type)
    if not args:
        return base_list
    
    element_type = args[0]
    
    # Convert each element to the target type
    try:
        return [parse_response(str(item), element_type) for item in base_list]
    except (ValueError, TypeError):
        # If conversion fails, return as-is
        return base_list

def _parse_generic_dict(response: str, return_type: Type) -> dict:
    """Parse generic dict type like Dict[str, Any]."""
    # First parse as basic dict
    base_dict = _parse_dict(response)
    
    # Get the key and value types
    args = get_args(return_type)
    if len(args) < 2:
        return base_dict
    
    key_type, value_type = args[0], args[1]
    
    # Convert keys and values to target types
    try:
        converted_dict = {}
        for k, v in base_dict.items():
            new_key = parse_response(str(k), key_type)
            new_value = parse_response(str(v), value_type) if value_type != Any else v
            converted_dict[new_key] = new_value
        return converted_dict
    except (ValueError, TypeError):
        # If conversion fails, return as-is
        return base_dict