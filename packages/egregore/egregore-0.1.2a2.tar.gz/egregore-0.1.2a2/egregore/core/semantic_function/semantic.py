"""Main SemanticFunctionDecorator class."""

import inspect
import asyncio
from typing import Any, Dict, Optional, Type, List, Callable, Union
from egregore.core.workflow.nodes import Node
from .template import render_template, extract_template_variables
from .errors import HandlerAction, ErrorContext, HandlerResult

class SemanticFunction(Node):
    """
    Transform Python functions into LLM-powered semantic functions with automatic prompt templating,
    type-aware response parsing, error handling, and intelligent retry mechanisms.
    
    A semantic function converts a regular Python function with a docstring template into an LLM call
    that processes the inputs and returns typed outputs. It works both as a standalone function and
    as a workflow node in Egregore workflows.
    
    Key Features:
    - **Template Substitution**: Function docstring becomes prompt template with {{parameter}} substitution
    - **Type-Aware Parsing**: Automatically parses LLM responses based on return type annotations
    - **Error Handling**: Structured error handling with custom error handlers and automatic retries
    - **Dual Mode Operation**: Works standalone (@semantic_function) or in workflows
    - **Provider Agnostic**: Supports Anthropic, OpenAI, Google providers with model switching
    - **Schema Generation**: Automatic JSON schema generation for structured return types
    
    Usage Examples:
    
    Basic Usage:
    ```python
    from egregore.core.semantic_function import semantic_function
    
    @semantic_function
    def extract_sentiment(text: str) -> str:
        '''Analyze the sentiment of this text: {{text}}'''
        pass
    
    result = extract_sentiment("I love this product!")  # Returns: "positive"
    ```
    
    Structured Output:
    ```python
    from pydantic import BaseModel
    from typing import List
    
    class Person(BaseModel):
        name: str
        age: int
        occupation: str
    
    @semantic_function(provider="openai:gpt-4")
    def extract_people(text: str) -> List[Person]:
        '''Extract all people mentioned in this text with their details: {{text}}'''
        pass
    
    people = extract_people("John, 30, doctor, and Mary, 25, teacher")
    # Returns: [Person(name="John", age=30, occupation="doctor"), ...]
    ```
    
    Error Handling:
    ```python
    @semantic_function(max_retries=5)
    def risky_extraction(data: str) -> dict:
        '''Extract structured data: {{data}}'''
        pass
    
    @risky_extraction.on_error([ValueError, KeyError])
    def handle_parsing_errors(context, data):
        return HandlerResult(
            action=HandlerAction.RETRY,
            user_feedback=f"Invalid format. Please return valid JSON for: {data}"
        )
    ```
    
    Workflow Integration:
    ```python
    from egregore.core.workflow import Sequence, node
    
    @node
    @semantic_function
    def summarize(content: str, max_words: int = 50) -> str:
        '''Summarize this content in {{max_words}} words: {{content}}'''
        pass
    
    workflow = Sequence([summarize])
    result = workflow.execute(content="Long article text...", max_words=30)
    ```
    
    Configuration Options:
    - provider: LLM provider (e.g., "anthropic:claude-3-sonnet", "openai:gpt-4")  
    - system_message: Custom system prompt
    - max_retries: Maximum retry attempts (default: 3)
    - temperature: LLM temperature setting
    - use_schema_override: Enable/disable automatic schema generation
    - schema_template: Custom schema prompt template
    
    The function docstring serves as the prompt template where {{parameter}} patterns are
    replaced with actual parameter values. Return type annotations determine how the LLM
    response is parsed - simple types (str, int) are parsed directly, while complex types
    (Pydantic models, dicts, lists) get automatic JSON schema generation.
    """
    
    def __init__(self, func, config: Dict[str, Any]):
        """Initialize semantic function wrapper.
        
        Args:
            func: Original function being decorated
            config: Configuration merged from global + decorator args
        """
        super().__init__(func.__name__)
        # Override the Node's formatted name with just the function name
        self.name = func.__name__
        self.func = func
        self.config = config.copy()
        self.prompt_template = self._parse_docstring(func.__doc__)
        self.return_type = self._get_return_type(func)
        self.param_names = list(inspect.signature(func).parameters.keys())
        self.use_schema_override = self._should_use_schema_override()
        self.error_handlers = {}  # {exception_type: handler_function}
        
        # Apply intelligent parameter mapping wrapper to execute method
        self._apply_intelligent_wrapper()
    
    @property
    def label(self) -> str:
        """Get the node label (maps to name for Node compatibility)."""
        return self.name
    
    @label.setter 
    def label(self, value: str):
        """Set the node label (maps to name for Node compatibility)."""
        self.name = value
    
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Direct usage: extract_data("sometext")."""
        return self._semantic_function_logic(*args, **kwargs)
    
    def _apply_intelligent_wrapper(self):
        """Apply intelligent parameter mapping wrapper to the execute method."""
        from egregore.core.workflow.nodes import create_intelligent_wrapper
        
        # Create a wrapper function that properly handles the original function signature
        # Get the original function signature to create a proper wrapper
        orig_sig = inspect.signature(self.func)
        
        def semantic_execute_func(*args, **kwargs):
            """Semantic function execution with original function signature."""
            
            # The intelligent wrapper will call us with the correct kwargs based on our signature
            # Just pass everything through to _semantic_function_logic
            return self._semantic_function_logic(*args, **kwargs)
        
        # Copy the original function signature and annotations to the wrapper
        semantic_execute_func.__signature__ = inspect.signature(self.func)
        semantic_execute_func.__name__ = self.func.__name__
        semantic_execute_func.__doc__ = self.func.__doc__
        semantic_execute_func.__annotations__ = getattr(self.func, '__annotations__', {})
        
        
        # Apply intelligent wrapper and replace execute method
        wrapped_execute = create_intelligent_wrapper(semantic_execute_func)
        
        # Bind the wrapped method to this instance
        self.execute = wrapped_execute.__get__(self, type(self))

    def execute(self, *args: Any, **kwargs: Any) -> Any:
        """Workflow usage: called by workflow system via intelligent parameter mapping.
        This method will be replaced by the intelligent wrapper in __init__."""
        return self._semantic_function_logic(*args, **kwargs)
    
    def _semantic_function_logic(self, *args, **kwargs):
        """Core semantic function execution logic with retry mechanism."""
        from egregore.providers.core.provider import GeneralPurposeProvider
        from egregore.core.messaging import TextContent
        from egregore.core.context_management.pact.context import Context
        from egregore.core.agent.message_scheduler import MessageScheduler
        from .parser import parse_response
        from .schema_generator import generate_json_schema, generate_example_json
        from egregore.core.workflow.state import SharedState
        import logging
        import time

        logger = logging.getLogger(f"semantic_function.{self.func.__name__}")
        
        # 1. Handle arguments and render template
        logger.debug(f"Executing semantic function '{self.func.__name__}' with args: {args}, kwargs: {kwargs}")
        
        # Special handling for SharedState - preserve it for Jinja2 template
        sig = inspect.signature(self.func)
        state_param = None
        state_object = None
        
        # Find SharedState parameter
        for param_name, param in sig.parameters.items():
            if param.annotation is SharedState:
                state_param = param_name
                if param_name in kwargs:
                    state_object = kwargs[param_name]
                break
        
        if state_param and state_object and isinstance(state_object, SharedState):
            # We have a real SharedState - preserve it for template
            # For semantic functions, we can use _bind_arguments normally since we have all parameters
            # The SharedState object will just be passed through as-is
            bound_args = self._bind_arguments(args, kwargs)
        else:
            # No SharedState or it's not a real SharedState object
            bound_args = self._bind_arguments(args, kwargs)
            
        user_prompt = self._render_template(bound_args)
        logger.debug(f"User prompt: '{user_prompt[:100]}...'")
        
        # 2. Build initial system prompt (system_message + schema)
        base_system_prompt = self._build_system_prompt()
        if base_system_prompt:
            logger.debug(f"Base system prompt: '{base_system_prompt[:100]}...'")
        else:
            logger.debug("No base system prompt generated")
        
        # 3. Initialize V2 provider
        provider_name, model = self._parse_provider_and_model()
        provider_config = self._get_provider_init_config()
        logger.debug(f"Initializing provider: {provider_name}, model: {model}")
        logger.debug(f"Provider config: {provider_config}")
        provider = GeneralPurposeProvider(provider_name=provider_name, **provider_config)
        
        # 4. Retry loop with structured error handling
        max_retries = self.config.get('max_retries', 3)
        retry_feedback_messages = []  # Accumulate feedback for retries

        for attempt in range(max_retries + 1):
            try:
                logger.debug(f"Attempt {attempt + 1} of {max_retries + 1}")

                # Create fresh Context for this attempt
                context = Context()

                # Build context using PACT operations
                # 1. Add system prompt if present
                if base_system_prompt:
                    context.add_system(base_system_prompt)
                    logger.debug(f"Added system prompt to context")

                # 2. Add any accumulated retry feedback from previous attempts
                for feedback_msg in retry_feedback_messages:
                    context.add_user(feedback_msg)
                    logger.debug(f"Added retry feedback to context: '{feedback_msg[:100]}...'")

                # 3. Add current user prompt
                context.add_user(user_prompt)
                logger.debug(f"Added user prompt to context")

                # 4. Use MessageScheduler to render Context -> ProviderThread
                scheduler = MessageScheduler(context)
                provider_thread = scheduler.render()
                logger.debug(f"Rendered context to ProviderThread with MessageScheduler")

                # Make LLM call with V2 provider.call()
                call_kwargs = self._get_call_kwargs(model)

                logger.debug(f"Calling provider with model: {model}")
                response = provider.call(
                    provider_thread=provider_thread,
                    model=model,
                    result_type=self.return_type if self.use_schema_override else None,
                    **call_kwargs
                )
                logger.debug(f"Raw LLM response type: {type(response)}")

                # 5. Check if we got a StructuredResponse (already parsed)
                from egregore.providers.core.structured_output import StructuredResponse
                if isinstance(response, StructuredResponse):
                    # Provider already parsed the structured output
                    logger.debug(f"Received StructuredResponse with parsed result: {type(response.parsed_result)}")
                    return response.parsed_result

                # 6. Store response in context using MessageScheduler
                scheduler.add_response(response)

                # 7. Extract content from context tree
                response_content = self._extract_response_from_context(context)
                logger.debug(f"Extracted response content: {repr(response_content[:200] if response_content else response_content)}")

                # Parse response based on return type
                logger.debug(f"Parsing response to return type: {self.return_type}")
                result = parse_response(response_content, self.return_type)
                logger.debug(f"Parsing successful, result type: {type(result)}")

                # Success - return the result
                return result
                
            except Exception as e:
                logger.debug(f"Attempt {attempt + 1} failed: {e}")
                
                # Handle the error using structured error handling
                handler_result = self._handle_error(e, args, kwargs, attempt, response_content if 'response_content' in locals() else None)
                
                # Process the handler result
                if handler_result.action == HandlerAction.RETURN:
                    logger.debug(f"Handler requested RETURN with fallback value")
                    return handler_result.fallback_value
                    
                elif handler_result.action == HandlerAction.ABORT:
                    logger.debug(f"Handler requested ABORT")
                    return None  # Graceful abort
                    
                elif handler_result.action == HandlerAction.RAISE:
                    logger.debug(f"Handler requested RAISE")
                    raise e  # Re-raise the original exception
                    
                elif handler_result.action in [HandlerAction.RETRY, HandlerAction.PASS]:
                    # Continue with retry logic
                    if attempt >= max_retries:
                        logger.debug(f"Max retries ({max_retries}) reached, raising exception")
                        raise e

                    logger.debug(f"Handler requested RETRY, preparing for attempt {attempt + 2}")

                    # Add user feedback to retry messages if provided
                    if handler_result.user_feedback:
                        retry_feedback_messages.append(handler_result.user_feedback)
                        logger.debug(f"Added user feedback for retry: '{handler_result.user_feedback[:100]}...'")

                    # Update system prompt with delta if provided
                    if handler_result.system_delta:
                        if base_system_prompt:
                            base_system_prompt = f"{base_system_prompt}. {handler_result.system_delta}"
                        else:
                            base_system_prompt = handler_result.system_delta
                        logger.debug(f"Updated system prompt with delta: '{handler_result.system_delta[:100]}...'")

                    # Apply model overrides if provided
                    if handler_result.model_overrides:
                        provider_config.update(handler_result.model_overrides)
                        logger.debug(f"Applied model overrides: {handler_result.model_overrides}")

                    # Apply backoff delay if specified
                    if handler_result.backoff_seconds and handler_result.backoff_seconds > 0:
                        logger.debug(f"Applying backoff delay: {handler_result.backoff_seconds}s")
                        time.sleep(handler_result.backoff_seconds)
                    
                else:
                    logger.warning(f"Unknown handler action: {handler_result.action}, treating as RETRY")
        
        # This should not be reached due to the raise in the loop, but just in case
        raise RuntimeError(f"Semantic function '{self.func.__name__}' failed after {max_retries + 1} attempts")
    
    def _extract_response_from_context(self, context: 'Context') -> str:
        """Extract response content from context tree after add_response().

        After MessageScheduler.add_response() stores the provider response in context,
        we need to extract the text content from the context tree.

        The structure is: Context → DepthArray → MessageTurn (depth=0, role='assistant')
        → CoreOffsetArray → MessageContainer → CoreOffsetArray → TextContent

        Args:
            context: Context instance with provider response added

        Returns:
            Extracted text content as string
        """
        from egregore.core.messaging import TextContent
        import logging
        logger = logging.getLogger(f"semantic_function.{self.func.__name__}")

        try:
            # Find the assistant message turn at depth=0
            assistant_turn = None
            for depth_component in context.content:
                if (hasattr(depth_component, 'depth') and depth_component.depth == 0 and
                    hasattr(depth_component, 'role') and depth_component.role == 'assistant'):
                    assistant_turn = depth_component
                    break

            if not assistant_turn:
                logger.warning("No assistant message turn found in context")
                return ""

            # Navigate: MessageTurn.content (CoreOffsetArray) → core → MessageContainer
            if not hasattr(assistant_turn, 'content') or not hasattr(assistant_turn.content, 'core'):
                logger.warning("Assistant turn missing content.core structure")
                return ""

            message_container = assistant_turn.content.core

            # Navigate: MessageContainer.content (CoreOffsetArray) → iterate to find TextContent
            if not hasattr(message_container, 'content'):
                logger.warning("Message container missing content")
                return ""

            response_text = ""
            # Iterate through the CoreOffsetArray to find TextContent components
            for component in message_container.content:
                if isinstance(component, TextContent):
                    response_text += component.content
                elif hasattr(component, 'content') and isinstance(component.content, str):
                    response_text += component.content

            return response_text

        except Exception as e:
            logger.warning(f"Failed to extract from context tree: {e}, using fallback")
            return ""
    
    def _build_system_prompt(self) -> str:
        """Build system prompt by concatenating system_message + schema_prompt."""
        final_prompt = ""
        
        # 1. Start with custom system_message if provided
        if 'system_message' in self.config:
            final_prompt = self.config['system_message']
        
        # 2. Append schema prompt if enabled for structured types
        if self.use_schema_override:
            schema_prompt = self._get_schema_override()
            if final_prompt:
                final_prompt = f"{final_prompt}. {schema_prompt}"
            else:
                final_prompt = schema_prompt
        
        return final_prompt
    
    def _get_schema_override(self) -> str:
        """Generate system prompt with schema and example."""
        from .schema_generator import generate_json_schema, generate_example_json
        
        schema = generate_json_schema(self.return_type)
        example = generate_example_json(self.return_type)
        
        template = self.config.get('schema_template', 
            "Output your answer in the following schema: {schema} Example: {example}")
        
        return template.format(schema=schema, example=example)
    
    def _parse_provider_config(self) -> dict:
        """Parse provider configuration for ProviderManager initialization (V1 DEPRECATED)."""
        provider_string = self.config.get('provider', 'anthropic:claude-3-sonnet')

        if ':' in provider_string:
            provider_name, model = provider_string.split(':', 1)
        else:
            provider_name = provider_string
            model = None

        config = {
            'provider_name': provider_name,
            'model': model
        }

        # Add provider_config if specified (exclude model_config which goes to get_response)
        if 'provider_config' in self.config:
            provider_config_copy = self.config['provider_config'].copy()
            # Extract model_config for later use in get_response call - store in self.config
            model_config = provider_config_copy.pop('model_config', None)
            if model_config:
                self.config['_extracted_model_config'] = model_config  # Store for later use in get_response
            config.update(provider_config_copy)

        # Add other provider-specific configs (exclude semantic function and model specific configs)
        semantic_function_keys = [
            'provider', 'provider_config', 'system_message', 'schema_template', 'use_schema_override',
            'max_retries',  # This is for retry loop, not provider
            'temperature', 'top_p', 'max_tokens', 'frequency_penalty', 'presence_penalty',  # Model params, not ProviderManager params
            '_extracted_model_config'  # Internal storage, not for ProviderManager
        ]
        for key, value in self.config.items():
            if key not in semantic_function_keys:
                config[key] = value

        return config

    def _get_provider_init_config(self) -> dict:
        """Extract configuration for V2 GeneralPurposeProvider.__init__().

        Returns config dict with provider-level settings (timeout, retry_config, etc.)
        Excludes model params (temperature, max_tokens) and semantic function params.
        """
        config = {}

        # Extract provider_config if specified
        if 'provider_config' in self.config:
            provider_config_copy = self.config['provider_config'].copy()
            # model_config goes to call(), not __init__
            provider_config_copy.pop('model_config', None)
            config.update(provider_config_copy)

        # Exclude semantic function keys and model params from provider init
        excluded_keys = [
            'provider', 'provider_config', 'system_message', 'schema_template',
            'use_schema_override', 'max_retries',
            # Model params go to call(), not __init__
            'temperature', 'top_p', 'max_tokens', 'frequency_penalty', 'presence_penalty',
            'top_k', 'stop_sequences',
            '_extracted_model_config'
        ]

        # Add any remaining config that's not excluded
        for key, value in self.config.items():
            if key not in excluded_keys:
                config[key] = value

        return config

    def _get_call_kwargs(self, model: str) -> dict:
        """Extract kwargs for V2 provider.call().

        Includes model params (temperature, max_tokens) and model_config.
        """
        kwargs = {}

        # Model params that go to call()
        model_param_keys = [
            'temperature', 'top_p', 'max_tokens', 'frequency_penalty',
            'presence_penalty', 'top_k', 'stop_sequences'
        ]

        for key in model_param_keys:
            if key in self.config:
                kwargs[key] = self.config[key]

        # Add model_config if extracted from provider_config
        if '_extracted_model_config' in self.config:
            kwargs['model_config'] = self.config['_extracted_model_config']

        # Add model_config directly if specified
        if 'provider_config' in self.config and 'model_config' in self.config['provider_config']:
            kwargs['model_config'] = self.config['provider_config']['model_config']

        return kwargs
    
    def _parse_docstring(self, docstring: Optional[str]) -> str:
        """Extract prompt template from function docstring."""
        if not docstring:
            return ""
        return docstring.strip()
    
    def _get_return_type(self, func) -> Type:
        """Extract return type from function signature."""
        sig = inspect.signature(func)
        return sig.return_annotation if sig.return_annotation != inspect.Signature.empty else str
    
    def _bind_arguments(self, args, kwargs) -> Dict[str, Any]:
        """Bind function arguments to parameter names."""
        sig = inspect.signature(self.func)
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        return dict(bound.arguments)
    
    def _render_template(self, bound_args: Dict[str, Any]) -> str:
        """Render prompt template with bound arguments."""
        return render_template(self.prompt_template, **bound_args)
    
    def _should_use_schema_override(self) -> bool:
        """Determine if schema override should be used based on return type and config."""
        # Check explicit config first
        if 'use_schema_override' in self.config:
            return self.config['use_schema_override']
        
        # Default to True for all structured types, False for str/Any
        from typing import Any
        if self.return_type in [str, type(None)] or self.return_type is Any:
            return False
        
        # True for all other types (BaseModel, dict, list, custom types)
        return True
    
    def on_error(self, exceptions):
        """Decorator for registering error handlers."""
        if not isinstance(exceptions, (list, tuple)):
            exceptions = [exceptions]
        
        def decorator(handler_func):
            for exc_type in exceptions:
                self.error_handlers[exc_type] = handler_func
            return handler_func
        return decorator
    
    def _handle_error(self, exception: Exception, original_args, original_kwargs,
                      attempt_index: int, last_response: Optional[str] = None) -> HandlerResult:
        """Handle exceptions using v2 structured error handling."""
        from egregore.core.messaging import ProviderResponse, TextContent
        import logging

        logger = logging.getLogger(f"semantic_function.{self.func.__name__}.error_handler")
        
        # Log the error occurrence
        logger.debug(f"Error occurred in semantic function '{self.func.__name__}': {exception}")
        logger.debug(f"Attempt {attempt_index + 1} of {self.config.get('max_retries', 3) + 1}")
        
        # Create error context with all available information
        try:
            provider_name, model_name = self._parse_provider_and_model()
            context = ErrorContext(
                exception=exception,
                attempt_index=attempt_index,
                max_retries=self.config.get('max_retries', 3),
                provider=provider_name,
                model=model_name,
                return_type=self.return_type,
                last_assistant=ProviderResponse(content=[TextContent(content=last_response)]) if last_response else None,
                user_prompt=self.prompt_template,
                system_prompt=self._build_system_prompt() or ""
            )
            
            logger.debug(f"Created ErrorContext: attempt {context.attempt_index}, provider {context.provider}")
            
        except Exception as ctx_error:
            logger.error(f"Failed to create ErrorContext: {ctx_error}")
            # Fallback to minimal context if creation fails
            context = ErrorContext(
                exception=exception,
                attempt_index=attempt_index,
                max_retries=self.config.get('max_retries', 3),
                provider="unknown",
                model="unknown", 
                return_type=str,  # Safe fallback
                user_prompt="",
                system_prompt=""
            )
        
        # Find most specific handler for this exception type
        handler = self._find_error_handler(exception)
        
        if handler:
            logger.debug(f"Found error handler: {handler.__name__}")
            try:
                # Call v2 handler with context + original function arguments
                result = handler(context, *original_args, **original_kwargs)
                
                if isinstance(result, HandlerResult):
                    logger.debug(f"Handler returned action: {result.action}")
                    return result
                elif isinstance(result, str):
                    # Legacy v1 handler compatibility
                    logger.debug("Handler returned string (legacy v1 format)")
                    return HandlerResult(action=HandlerAction.RETRY, user_feedback=result)
                else:
                    logger.warning(f"Handler returned unexpected type: {type(result)}")
                    
            except Exception as handler_error:
                logger.error(f"Error handler failed: {handler_error}")
                # Fall through to default behavior
        else:
            logger.debug("No specific error handler found, using default")
        
        # Default retry behavior if no handler found or handler failed
        default_result = HandlerResult(
            action=HandlerAction.RETRY,
            user_feedback=f"Your response had an error: {str(exception)}. Please provide a valid response that matches the expected format."
        )
        
        logger.debug(f"Using default error handling: {default_result.action}")
        return default_result
    
    def _extract_model_from_provider(self) -> str:
        """Extract model name from provider configuration."""
        provider_string = self.config.get('provider', 'anthropic:claude-3-sonnet')
        
        if ':' in provider_string:
            _, model = provider_string.split(':', 1)
            return model
        else:
            return "default"
    
    def _parse_provider_and_model(self):
        """Parse provider configuration into provider name and model."""
        provider_string = self.config.get('provider', 'anthropic:claude-3-sonnet')
        
        if ':' in provider_string:
            provider_name, model = provider_string.split(':', 1)
            return provider_name.strip(), model.strip()
        else:
            return provider_string.strip(), "default"
    
    def _find_error_handler(self, exception: Exception):
        """Find the most specific error handler for the given exception."""
        # Look for exact type match first
        exc_type = type(exception)
        if exc_type in self.error_handlers:
            return self.error_handlers[exc_type]
        
        # Look for parent class matches (most specific first)
        for registered_type, handler in self.error_handlers.items():
            if isinstance(exception, registered_type):
                return handler
        
        return None

    def alias(self, name: str) -> 'SemanticFunction':
        """Create an alias of this semantic function with a different name.
        
        Args:
            name: New name for the aliased function
            
        Returns:
            SemanticFunction: A new instance with the same configuration but different name
        """
        # Create a copy with new label for workflow reuse
        alias_func = SemanticFunction(self.func, self.config)
        alias_func.label = name
        alias_func.error_handlers = self.error_handlers.copy()
        return alias_func


class SemanticFunctionDecorator:
    """
    Global semantic function decorator that creates LLM-powered functions from regular Python functions.
    
    This decorator transforms functions with docstring templates into intelligent functions that:
    1. Use the docstring as an LLM prompt template with {{parameter}} substitution
    2. Call an LLM provider (Anthropic, OpenAI, Google) with the rendered prompt
    3. Parse the LLM response according to the function's return type annotation
    4. Handle errors with structured retry mechanisms and custom error handlers
    
    The decorator can be used with or without parameters:
    - @semantic_function (uses default configuration)
    - @semantic_function(provider="openai:gpt-4", max_retries=5) (with custom config)
    
    Global configuration can be set using the .config() method to avoid repeating
    common settings across multiple semantic functions.
    
    Example:
    ```python
    # Set global defaults
    semantic_function.config(provider="anthropic:claude-3-sonnet", temperature=0.7)
    
    # This function will inherit the global config
    @semantic_function
    def analyze_text(content: str) -> dict:
        '''Analyze the content and return insights: {{content}}'''
        pass
    
    # This function overrides the global provider
    @semantic_function(provider="openai:gpt-4", max_retries=5)  
    def complex_extraction(data: str) -> List[dict]:
        '''Extract complex data structures: {{data}}'''
        pass
    ```
    """
    
    def __init__(self):
        self._config = {}
    
    def config(self, **kwargs: Any) -> 'SemanticFunctionDecorator':
        """Set global defaults for all semantic functions.
        
        Args:
            **kwargs: Configuration options to set as defaults
            
        Returns:
            SemanticFunctionDecorator: Self for method chaining
        """
        self._config.update(kwargs)
        return self
    
    def __call__(self, func: Optional[Callable] = None, **override_kwargs: Any) -> Union[SemanticFunction, Callable[[Callable], SemanticFunction]]:
        """Use as @semantic_function or @semantic_function(...).
        
        Args:
            func: Function to decorate (when used without parentheses)
            **override_kwargs: Configuration overrides
            
        Returns:
            Either a SemanticFunction (direct decoration) or decorator function
        """
        if func is None:
            # Called with args: @semantic_function(provider="...")
            return lambda f: self._create_wrapper(f, override_kwargs)
        else:
            # Called without args: @semantic_function
            return self._create_wrapper(func, {})
    
    def _create_wrapper(self, func: Callable, override_config: Dict[str, Any]) -> SemanticFunction:
        """Create semantic function wrapper.
        
        Args:
            func: Function to wrap
            override_config: Configuration overrides for this function
            
        Returns:
            SemanticFunction: Wrapped function
        """
        # Merge global config with override config
        merged_config = self._config.copy()
        merged_config.update(override_config)
        
        return SemanticFunction(func, merged_config)

# Global decorator instance
semantic = SemanticFunctionDecorator()