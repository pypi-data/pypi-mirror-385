"""
Semantic Function Decorator - Transform Python functions into LLM-powered semantic functions.

This module provides the @semantic_function decorator that converts regular Python functions
with docstring templates into intelligent functions powered by Large Language Models.

Key Features:
- Template substitution in docstrings using {{parameter}} syntax
- Automatic type-aware response parsing based on return type annotations
- Support for multiple LLM providers (Anthropic, OpenAI, Google)
- Structured error handling with custom error handlers
- Workflow integration as nodes in Egregore workflows
- Automatic JSON schema generation for complex return types

Quick Start:
```python
from egregore.core.semantic_function import semantic_function

@semantic_function
def extract_sentiment(text: str) -> str:
    '''Analyze the sentiment of this text: {{text}}
    
    Return one of: positive, negative, neutral'''
    pass

result = extract_sentiment("I love this product!")
print(result)  # "positive"
```

For more examples and advanced usage, see the SemanticFunction class documentation.
"""

from typing import TypeVar, Callable, Any, Union, overload
from .semantic import semantic as _semantic_decorator, SemanticFunction

# Type variable for preserving function signatures
F = TypeVar('F', bound=Callable[..., Any])

# Create properly typed overloads for the decorator
@overload
def semantic(func: F) -> SemanticFunction: ...

@overload
def semantic(
    *,
    provider: str = "anthropic:claude-3-sonnet",
    provider_config: dict = None,
    system_message: str = None,
    max_retries: int = 3,
    temperature: float = None,
    use_schema_override: bool = None,
    schema_template: str = None,
    **kwargs: Any
) -> Callable[[F], SemanticFunction]: ...

# Create a function that preserves both typing and decorator methods
def semantic(func: F = None, **kwargs) -> Union[SemanticFunction, Callable[[F], SemanticFunction]]:
    """
    Transform a Python function into an LLM-powered semantic function.

    This decorator converts functions with docstring templates into intelligent functions
    that use Large Language Models to process inputs and return typed outputs.

    Args:
        func: The function to decorate (when used as @semantic)
        provider: LLM provider string (e.g., "anthropic:claude-3-sonnet", "openai:gpt-4")
        provider_config: Provider-specific configuration dict (e.g., {"model_config": {"verbosity": "low"}})
        system_message: Custom system prompt to prepend to the function's docstring
        max_retries: Maximum number of retry attempts on errors (default: 3)
        temperature: LLM temperature setting for response randomness
        use_schema_override: Whether to automatically generate JSON schema for complex return types
        schema_template: Custom template for schema prompts
        **kwargs: Additional configuration options passed to the provider

    Returns:
        SemanticFunction: A callable that executes the LLM-powered function
    """
    return _semantic_decorator(func, **kwargs)

# Wrap config method to return semantic (not _semantic_decorator) for proper chaining
def _config_wrapper(**kwargs):
    """Wrapper for config that returns semantic instead of _semantic_decorator."""
    _semantic_decorator.config(**kwargs)
    return semantic

semantic.config = _config_wrapper
semantic._config = _semantic_decorator._config

__all__ = ['semantic', 'SemanticFunction']