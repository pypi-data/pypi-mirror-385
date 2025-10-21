"""Structured output protocol implementation for automatic structured generation."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Type, Union
import time
import logging

logger = logging.getLogger(__name__)


@dataclass
class StructuredResponse:
    """Standardized structured output response.
    
    This response wrapper provides complete information about structured output
    processing, including the parsed result, fallback information, and performance
    metrics.
    
    Attributes:
        parsed_result: The successfully parsed structured result
        raw_response: The original provider response before parsing
        result_type: The requested result type for validation
        fallback_used: Strategy used ("native", "json_parse", None if no fallback)
        confidence: Confidence score for the parsing (0.0-1.0)
        retries_used: Number of retry attempts before success
        parse_time: Time taken for parsing in seconds
        metadata: Additional parsing information and debug data
    """
    parsed_result: Any
    raw_response: Any
    result_type: Type[Any]
    fallback_used: Optional[str] = None
    confidence: float = 1.0
    retries_used: int = 0
    parse_time: float = 0.0
    metadata: Optional[Dict[str, Any]] = None


def _classify_result_type(result_type: Type[Any]) -> str:
    """Classify the requested result type for appropriate handling.
    
    Determines the category of the result type to route to the appropriate
    parsing strategy. Supports dataclass, Pydantic BaseModel, dict, and
    native Python types including complex annotations.
    
    Args:
        result_type: The type to classify
        
    Returns:
        Classification string: "dataclass", "pydantic", "dict", or "native"
        
    Examples:
        >>> _classify_result_type(dict)
        'dict'
        >>> from dataclasses import dataclass
        >>> @dataclass
        ... class MyData: pass
        >>> _classify_result_type(MyData)
        'dataclass'
        >>> from typing import List
        >>> _classify_result_type(List[str])
        'native'
    """
    # Check for dataclass
    if hasattr(result_type, '__dataclass_fields__'):
        return "dataclass"
    
    # Check for Pydantic BaseModel
    if hasattr(result_type, 'model_fields'):
        return "pydantic"
    
    # Check for basic dict type
    if result_type == dict:
        return "dict"
    
    # Everything else is native Python type (int, str, List[str], Dict[str, int], etc.)
    return "native"


def _try_native_structured_parsing(raw_response: Any, result_type: Type[Any]) -> Union[Any, None]:
    """Attempt to parse response using native provider structured output.
    
    This function attempts to extract structured data from a provider response
    that was generated using the provider's native structured output capabilities.
    The exact parsing logic depends on the provider's response format.
    
    Args:
        raw_response: The raw response from the provider
        result_type: The expected type to parse into
        
    Returns:
        Parsed result if successful, None if parsing fails
        
    Note:
        This is a placeholder implementation. Concrete providers should
        implement their own native parsing logic.
    """
    try:
        # This is a placeholder implementation
        # Real providers will override this with provider-specific logic
        if hasattr(raw_response, 'structured_content'):
            return raw_response.structured_content
        elif hasattr(raw_response, 'parsed_response'):
            return raw_response.parsed_response
        elif hasattr(raw_response, 'content') and isinstance(raw_response.content, result_type):
            return raw_response.content
        
        # Fallback: try to extract from text content if available
        if hasattr(raw_response, 'text') or hasattr(raw_response, 'content'):
            text_content = getattr(raw_response, 'text', None) or getattr(raw_response, 'content', None)
            if text_content and result_type == str:
                return text_content
        
        return None
        
    except Exception as e:
        logger.debug(f"Native structured parsing failed: {e}")
        return None


def _apply_json_parsing_fallback(raw_response: Any, result_type: Type[Any]) -> Union[Any, None]:
    """Apply JSON parsing fallback for structured output generation.

    Extracts structured data from raw text response using JSON parsing.
    This serves as the universal fallback when native structured output is not
    available or fails.

    Args:
        raw_response: The raw response from the provider
        result_type: The expected type to generate

    Returns:
        Structured result if successful, None if parsing fails
    """
    import json
    import re
    
    try:
        # Extract text content from response
        text_content = _extract_text_content(raw_response)
        if text_content is None:
            return None
            
        logger.debug(f"Applying JSON parsing fallback for type: {result_type}")
        
        # Handle different result types with basic parsing strategies
        type_category = _classify_result_type(result_type)
        
        if type_category == "dict":
            # Try to extract JSON from text
            return _extract_json_from_text(text_content)
            
        elif type_category == "native":
            # Handle basic native types
            if result_type == str:
                return text_content.strip()
            elif result_type == int:
                return _extract_integer_from_text(text_content)
            elif result_type == float:
                return _extract_float_from_text(text_content)
            elif result_type == bool:
                return _extract_boolean_from_text(text_content)
            else:
                # For complex types like List[str], Dict[str, int], try JSON parsing
                return _extract_json_from_text(text_content)
        
        elif type_category in ["dataclass", "pydantic"]:
            # For structured types, try to extract JSON and convert
            json_data = _extract_json_from_text(text_content)
            if json_data is not None:
                try:
                    if type_category == "dataclass":
                        return result_type(**json_data)
                    elif type_category == "pydantic":
                        return result_type.model_validate(json_data)
                except Exception as e:
                    logger.debug(f"Failed to construct {type_category} from JSON: {e}")
                    return None
        
        logger.warning(f"JSON parsing fallback could not handle type: {result_type}")
        return None

    except Exception as e:
        logger.error(f"JSON parsing fallback failed: {e}")
        return None


def _extract_json_from_text(text: str) -> Union[Dict, List, None]:
    """Extract JSON data from text content.
    
    Attempts to find and parse JSON content from text, handling
    various formats and markdown code blocks.
    
    Args:
        text: Text content to extract JSON from
        
    Returns:
        Parsed JSON data or None if extraction fails
    """
    import json
    import re
    
    # Try to find JSON in markdown code blocks
    json_pattern = r'```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```'
    matches = re.findall(json_pattern, text, re.DOTALL)
    
    for match in matches:
        try:
            return json.loads(match.strip())
        except json.JSONDecodeError:
            continue
    
    # Try to find JSON anywhere in the text
    brace_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    bracket_pattern = r'\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\]'
    
    for pattern in [brace_pattern, bracket_pattern]:
        matches = re.findall(pattern, text)
        for match in matches:
            try:
                return json.loads(match.strip())
            except json.JSONDecodeError:
                continue
    
    return None


def _extract_integer_from_text(text: str) -> Union[int, None]:
    """Extract integer value from text."""
    import re
    numbers = re.findall(r'-?\d+', text)
    if numbers:
        try:
            return int(numbers[0])
        except ValueError:
            pass
    return None


def _extract_float_from_text(text: str) -> Union[float, None]:
    """Extract float value from text."""
    import re
    numbers = re.findall(r'-?\d*\.?\d+', text)
    if numbers:
        try:
            return float(numbers[0])
        except ValueError:
            pass
    return None


def _extract_boolean_from_text(text: str) -> Union[bool, None]:
    """Extract boolean value from text."""
    import re
    text_lower = text.lower().strip()
    
    # Use word boundaries to avoid partial matches like "no" in "unknown"
    true_patterns = [r'\btrue\b', r'\byes\b', r'\bcorrect\b', r'\bright\b']
    false_patterns = [r'\bfalse\b', r'\bno\b', r'\bincorrect\b', r'\bwrong\b']
    
    if any(re.search(pattern, text_lower) for pattern in true_patterns):
        return True
    elif any(re.search(pattern, text_lower) for pattern in false_patterns):
        return False
    return None


def _extract_text_content(raw_response: Any) -> str:
    """Extract text content from various response formats.
    
    Utility function to extract text content from different provider response
    formats for use in fallback parsing. Updated for V2 architecture.
    
    Args:
        raw_response: The response to extract text from
        
    Returns:
        Extracted text content
    """
    if isinstance(raw_response, str):
        return raw_response
    
    # Handle V2 ProviderResponse with ContentBlock list
    try:
        if hasattr(raw_response, 'content') and isinstance(raw_response.content, list):
            text_parts = []
            for content_block in raw_response.content:
                # Check for TextContent blocks
                if hasattr(content_block, 'content_type') and hasattr(content_block, 'content'):
                    if content_block.content_type == 'text':
                        text_parts.append(content_block.content)
                elif hasattr(content_block, 'content') and isinstance(content_block.content, str):
                    # Fallback for content blocks that just have content attribute
                    text_parts.append(content_block.content)
            
            if text_parts:
                return '\n'.join(text_parts)
    except Exception:
        # Skip if content property raises an exception
        pass
    
    # Try common text content attributes (original logic)
    found_any_attr = False
    for attr in ['text', 'content', 'message', 'response']:
        if hasattr(raw_response, attr):
            found_any_attr = True
            try:
                value = getattr(raw_response, attr)
                if isinstance(value, str):
                    return value
            except Exception:
                # Skip attributes that raise exceptions when accessed
                continue
    
    # If no text attributes found at all, check string representation
    if not found_any_attr:
        str_result = str(raw_response)
        # Return None if the string representation is just an object reference
        if str_result.startswith('<') and 'object at 0x' in str_result:
            return None
        return str_result
    
    # If attributes exist but failed to access, fall back to string conversion
    return str(raw_response)


def _validate_json_parsing_availability() -> bool:
    """Check if JSON parsing is available (always True as json is stdlib).

    Returns:
        True (json module is always available in Python)
    """
    return True


# Backwards compatibility alias
_apply_outlines_fallback = _apply_json_parsing_fallback