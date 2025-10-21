"""
Provider Interface Specification for Egregore v2 Architecture

This module defines the standardized interface that all providers must implement.
Providers only see 3 Core Message Types and handle translation to/from native APIs.
Includes standardized parameter handling for consistent cross-provider behavior.
"""

from abc import ABC, abstractmethod
from typing import Iterator, AsyncIterator, Optional, Dict, Any, List, Union, Type
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from egregore.core.messaging import ProviderThread, ProviderResponse, ClientRequest
from .structured_output import StructuredResponse
from .model_manager import BaseModelManager
from .model_types import ModelList

from .parameters import (
    StandardParameters, 
    ProviderParameterDefaults,
    extract_standard_and_specific_params,
    merge_parameters,
    get_provider_defaults
)
from .token_counting import TokenCountingManager


class ChunkType(str, Enum):
    """Enumeration of chunk types for streaming responses."""
    CONTENT = "content"
    TOOL_START = "tool_start"
    TOOL_DELTA = "tool_delta"
    TOOL_RESULT = "tool_result" 
    METADATA = "metadata"
    UNKNOWN = "unknown"


class ToolCallState(str, Enum):
    """Enumeration of tool call streaming states."""
    STARTING = "starting"
    STREAMING = "streaming"
    COMPLETE = "complete"
    ERROR = "error"


class StreamChunk(BaseModel):
    """Enhanced streaming response accumulator from providers with tool execution support."""
    
    # Core content fields (backward compatibility)
    delta: str = Field(..., description="Incremental content for this chunk")
    content: str = Field(default="", description="Accumulated content so far")
    finish_reason: Optional[str] = Field(None, description="Final reason when stream ends")
    
    # Enhanced chunk classification
    chunk_type: ChunkType = Field(default=ChunkType.CONTENT, description="Type of streaming chunk")
    timestamp: datetime = Field(default_factory=datetime.now, description="When chunk was created")
    
    # Tool calling fields (enhanced)
    tool_calls: Optional[List[Any]] = Field(None, description="Complete tool calls when finished")
    partial_tool_calls: Optional[List[Any]] = Field(None, description="Partial tool calls being streamed")
    tool_call_state: Optional[ToolCallState] = Field(None, description="Tool call streaming state")
    tool_call_id: Optional[str] = Field(None, description="Active tool call ID")
    function_name: Optional[str] = Field(None, description="Function being called")
    arguments_delta: Optional[str] = Field(None, description="Incremental function arguments")
    tool_result: Optional[Any] = Field(None, description="Tool execution result")
    
    # Usage and model info
    usage: Optional[Dict[str, Any]] = Field(None, description="Token usage information")
    model: Optional[str] = Field(None, description="Model information")
    
    # Enhanced metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Chunk-specific metadata")
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
    
    @classmethod
    def from_content(cls, delta: str, content: str = "", **kwargs) -> "StreamChunk":
        """Create content chunk from text delta."""
        return cls(
            chunk_type=ChunkType.CONTENT,
            delta=delta,
            content=content,
            **kwargs
        )
    
    @classmethod
    def from_tool_start(cls, tool_call_id: str, function_name: str, **kwargs) -> "StreamChunk":
        """Create tool start chunk."""
        return cls(
            chunk_type=ChunkType.TOOL_START,
            delta="",  # Required field
            tool_call_id=tool_call_id,
            function_name=function_name,
            tool_call_state=ToolCallState.STARTING,
            **kwargs
        )
    
    @classmethod
    def from_tool_delta(cls, tool_call_id: str, arguments_delta: str, **kwargs) -> "StreamChunk":
        """Create tool delta chunk."""
        return cls(
            chunk_type=ChunkType.TOOL_DELTA,
            delta="",  # Required field
            tool_call_id=tool_call_id,
            arguments_delta=arguments_delta,
            tool_call_state=ToolCallState.STREAMING,
            **kwargs
        )
    
    @classmethod
    def from_tool_result(cls, tool_call_id: str, result: Any, success: bool = True, **kwargs) -> "StreamChunk":
        """Create tool result chunk."""
        return cls(
            chunk_type=ChunkType.TOOL_RESULT,
            delta="",  # Required field
            tool_call_id=tool_call_id,
            tool_result=result,
            tool_call_state=ToolCallState.COMPLETE if success else ToolCallState.ERROR,
            **kwargs
        )
    
    @classmethod
    def from_metadata(cls, finish_reason: str = None, usage: Dict[str, Any] = None, **kwargs) -> "StreamChunk":
        """Create metadata chunk."""
        return cls(
            chunk_type=ChunkType.METADATA,
            delta="",  # Required field
            finish_reason=finish_reason,
            usage=usage,
            **kwargs
        )
    
    def is_content(self) -> bool:
        """Check if this is a content chunk."""
        return self.chunk_type == ChunkType.CONTENT
    
    def is_tool_related(self) -> bool:
        """Check if this chunk is tool-related."""
        return self.chunk_type in [ChunkType.TOOL_START, ChunkType.TOOL_DELTA, ChunkType.TOOL_RESULT]
    
    def is_metadata(self) -> bool:
        """Check if this is a metadata chunk."""
        return self.chunk_type == ChunkType.METADATA
    
    def get_tool_info(self) -> Optional[Dict[str, Any]]:
        """Extract tool information if this is a tool-related chunk."""
        if not self.is_tool_related():
            return None
            
        return {
            'tool_call_id': self.tool_call_id,
            'function_name': self.function_name,
            'state': self.tool_call_state,
            'arguments_delta': self.arguments_delta,
            'result': self.tool_result
        }


class BaseProvider(ABC):
    """
    Abstract base class that all providers must implement.
    
    Key Principles:
    1. Providers only see ProviderThread with 3 Core Message Types
    2. All validation is done by ProviderManager before calling provider
    3. Providers only handle execution and response translation
    4. Each provider manages its own ModelList internally
    """
    
    def __init__(self, **config):
        """Initialize provider with configuration"""
        self.validate_provider_config(config)
        self.config = config
        self.model_manager = self._create_model_manager()
        self.token_counter = TokenCountingManager()
        
    # Core Interface Methods - All providers must implement these
    
    @abstractmethod
    def call(
        self, 
        provider_thread: 'ProviderThread', 
        model: Optional[str] = None,
        tools: bool = False,
        result_type: Optional[Type[Any]] = None,
        max_retries: int = 3,
        **kwargs
    ) -> Union['ProviderResponse', 'StructuredResponse']:
        """
        Synchronous completion with optional structured output.
        
        Args:
            provider_thread: ProviderThread containing 3 Core Message Types
            model: Specific model to use (already validated by ProviderManager)
            tools: Whether to enable tool calling (already validated by ProviderManager)
            result_type: Optional type for structured output (dict, dataclass, Pydantic, etc.)
            max_retries: Maximum retry attempts for structured output failures
            **kwargs: Standard parameters (max_tokens, temperature, etc.) + provider-specific config
            
        Standard Parameters:
            max_tokens: int - Maximum tokens to generate
            temperature: float - Sampling temperature (0.0-2.0)
            top_p: float - Nucleus sampling (0.0-1.0)
            frequency_penalty: float - Repetition penalty (-2.0 to 2.0)
            presence_penalty: float - Topic diversity penalty (-2.0 to 2.0)
            reasoning_effort: str - For reasoning models: "low"/"medium"/"high"
            stop: str|List[str] - Stop sequences
            seed: int - Random seed for reproducibility
            
        Implementation should use self._process_parameters(model, **kwargs) to standardize parameters.
            
        Returns:
            ProviderResponse with ContentBlock-based content, or StructuredResponse if result_type specified
        """
        pass
    
    @abstractmethod
    async def acall(
        self, 
        provider_thread: 'ProviderThread', 
        model: Optional[str] = None,
        tools: bool = False,
        result_type: Optional[Type[Any]] = None,
        max_retries: int = 3,
        **kwargs
    ) -> Union['ProviderResponse', 'StructuredResponse']:
        """
        Asynchronous completion with optional structured output.
        
        Args:
            provider_thread: ProviderThread containing 3 Core Message Types
            model: Specific model to use (already validated by ProviderManager)
            tools: Whether to enable tool calling (already validated by ProviderManager)
            result_type: Optional type for structured output (dict, dataclass, Pydantic, etc.)
            max_retries: Maximum retry attempts for structured output failures
            **kwargs: Standard parameters (max_tokens, temperature, etc.) + provider-specific config
            
        Standard Parameters:
            max_tokens: int - Maximum tokens to generate
            temperature: float - Sampling temperature (0.0-2.0)
            top_p: float - Nucleus sampling (0.0-1.0)
            frequency_penalty: float - Repetition penalty (-2.0 to 2.0)
            presence_penalty: float - Topic diversity penalty (-2.0 to 2.0)
            reasoning_effort: str - For reasoning models: "low"/"medium"/"high"
            stop: str|List[str] - Stop sequences
            seed: int - Random seed for reproducibility
            
        Implementation should use self._process_parameters(model, **kwargs) to standardize parameters.
            
        Returns:
            ProviderResponse with ContentBlock-based content, or StructuredResponse if result_type specified
        """
        pass
    
    @abstractmethod
    def stream(
        self, 
        provider_thread: 'ProviderThread', 
        model: Optional[str] = None,
        tools: bool = False,
        result_type: Optional[Type[Any]] = None,
        **kwargs
    ) -> Iterator[StreamChunk]:
        """
        Synchronous streaming completion with optional structured output.
        
        Note: Structured output for streaming only works with native provider support.
        No fallback mechanisms are available for streaming methods.
        
        Args:
            provider_thread: ProviderThread containing 3 Core Message Types
            model: Specific model to use (already validated by ProviderManager)
            tools: Whether to enable tool calling (already validated by ProviderManager)
            result_type: Optional type for structured output (native support only, no fallbacks)
            **kwargs: Standard parameters (max_tokens, temperature, etc.) + provider-specific config
            
        Standard Parameters:
            max_tokens: int - Maximum tokens to generate
            temperature: float - Sampling temperature (0.0-2.0)
            top_p: float - Nucleus sampling (0.0-1.0)
            frequency_penalty: float - Repetition penalty (-2.0 to 2.0)
            presence_penalty: float - Topic diversity penalty (-2.0 to 2.0)
            reasoning_effort: str - For reasoning models: "low"/"medium"/"high"
            stop: str|List[str] - Stop sequences
            seed: int - Random seed for reproducibility
            
        Implementation should use self._process_parameters(model, **kwargs) to standardize parameters.
            
        Yields:
            StreamChunk objects with incremental response data
        """
        pass
    
    @abstractmethod
    async def astream(
        self, 
        provider_thread: 'ProviderThread', 
        model: Optional[str] = None,
        tools: bool = False,
        result_type: Optional[Type[Any]] = None,
        **kwargs
    ) -> AsyncIterator[StreamChunk]:
        """
        Asynchronous streaming completion with optional structured output.
        
        Note: Structured output for streaming only works with native provider support.
        No fallback mechanisms are available for streaming methods.
        
        Args:
            provider_thread: ProviderThread containing 3 Core Message Types
            model: Specific model to use (already validated by ProviderManager)
            tools: Whether to enable tool calling (already validated by ProviderManager)
            result_type: Optional type for structured output (native support only, no fallbacks)
            **kwargs: Standard parameters (max_tokens, temperature, etc.) + provider-specific config
            
        Standard Parameters:
            max_tokens: int - Maximum tokens to generate
            temperature: float - Sampling temperature (0.0-2.0)
            top_p: float - Nucleus sampling (0.0-1.0)
            frequency_penalty: float - Repetition penalty (-2.0 to 2.0)
            presence_penalty: float - Topic diversity penalty (-2.0 to 2.0)
            reasoning_effort: str - For reasoning models: "low"/"medium"/"high"
            stop: str|List[str] - Stop sequences
            seed: int - Random seed for reproducibility
            
        Implementation should use self._process_parameters(model, **kwargs) to standardize parameters.
            
        Yields:
            StreamChunk objects with incremental response data
        """
        pass
    
    # Translation Methods - Required for provider-specific formatting
    
    @abstractmethod
    def format_provider_thread(self, provider_thread: 'ProviderThread', **kwargs) -> Dict[str, Any]:
        """
        Convert ProviderThread (3 Core Message Types) to provider's native API format.
        
        This method handles the conversion from standardized Core Message Types 
        to the specific format required by this provider's API.
        
        Args:
            provider_thread: ProviderThread with SystemHeader, ClientRequest, ProviderResponse
            **kwargs: Additional parameters including model, tools, result_type, etc.
            
        Returns:
            Dict formatted for this provider's native API
        """
        pass
    
    @abstractmethod
    def format_provider_response(self, native_response: Any) -> 'ProviderResponse':
        """
        Convert provider's native API response to ContentBlock-based ProviderResponse.
        
        This method handles the conversion from provider-specific response format
        to standardized ProviderResponse with ContentBlocks.
        
        Args:
            native_response: Raw response from provider's API
            
        Returns:
            ProviderResponse with ContentBlock-based content
        """
        pass
    
    @abstractmethod
    def format_structured_output(
        self,
        result_type: Type[Any],
        **provider_options
    ) -> Optional[Dict[str, Any]]:
        """
        Create provider-specific structured output format specification.
        
        This is the primary protocol method that providers must implement
        to support native structured output capabilities.
        
        Args:
            result_type: The Python type to generate structured output for
            **provider_options: Provider-specific formatting options
            
        Returns:
            Provider-specific format specification dict, or None if provider 
            doesn't support native structured output for this result_type.
            
        Examples:
            OpenAI: Returns {"type": "json_schema", "json_schema": {...}}
            Anthropic: Returns tool-based structured output format  
            Google: Returns response_schema for Gemini
            Others: Returns None (triggers _auto_structure_response fallback)
            
        Note:
            This method should be called by translate_to_native when result_type
            is provided to add structured output formatting to the API request.
        """
        pass
    
    @abstractmethod
    def format_tools(self, tools: List['ToolDeclaration']) -> List[Dict[str, Any]]:
        """
        Convert ToolDeclarations to provider-specific tool format.
        
        This method translates V2 ToolDeclarations into the specific tool schema
        format required by this provider's API.
        
        Args:
            tools: List of ToolDeclarations to convert
            
        Returns:
            List of provider-specific tool schemas
            
        Examples:
            OpenAI: Returns [{"type": "function", "function": {"name": "...", "parameters": {...}}}]
            Anthropic: Returns tool schemas in Anthropic's format
            Google: Returns function_declarations for Gemini
            
        Note:
            This method should extract parameter schemas from ToolDeclaration.parameters
            (which uses V1's Schema system) and convert to provider format.
        """
        pass
    
    # Model Management Methods
    
    def list_models(self):
        """List all available models for this provider"""
        return self.model_manager.list_models()
    
    def get_model(self, model_name: str):
        """Get detailed information about a specific model"""
        return self.model_manager.get_model(model_name)
    
    def validate_model(self, model_name: str) -> bool:
        """Validate that a model exists and is available"""
        return self.model_manager.validate(model_name)
    
    def calculate_request_cost(self, input_tokens: int, output_tokens: int, model_name: str) -> float:
        """Calculate cost for a request"""
        return self.model_manager.calculate_request_cost(input_tokens, output_tokens, model_name)
    
    @abstractmethod
    async def refresh_models(self) -> None:
        """
        Refresh model list from provider API.
        
        Each provider is responsible for fetching its latest model information
        and updating its internal ModelList.
        """
        pass
    
    # Standardized Parameter Processing
    
    def _process_parameters(
        self, 
        model: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process and standardize parameters for this provider.
        
        Parameter Priority (highest to lowest):
        1. **kwargs from agent.call() - highest priority, overrides everything
        2. model_config from provider_config - middle priority, set during agent init
        3. Provider defaults - lowest priority, built-in defaults
        
        This method:
        1. Extracts standard parameters (max_tokens, temperature, etc.)
        2. Applies 3-tier parameter merging: provider defaults < model_config < call kwargs
        3. Handles provider-specific parameter mappings
        4. Performs model-specific parameter adjustments
        
        Args:
            model: Model name for model-specific processing
            **kwargs: Mixed standard and provider-specific parameters from agent.call()
            
        Returns:
            Dictionary of processed parameters ready for native API
        """
        # Extract standard vs provider-specific parameters from call kwargs
        standard_params, provider_specific = extract_standard_and_specific_params(kwargs)
        
        # Get provider defaults (lowest priority)
        provider_defaults = self._get_provider_defaults()
        
        # Get model_config from provider config (middle priority)
        model_config_params = self.config.get('model_config', {})
        model_config_standard, model_config_specific = extract_standard_and_specific_params(model_config_params)
        
        # Merge with 3-tier priority: provider defaults < model_config < call kwargs
        merged_params = merge_parameters(
            standard_params, 
            provider_specific, 
            provider_defaults,
            model_config_standard=model_config_standard,
            model_config_specific=model_config_specific
        )
        
        # Apply model-specific adjustments
        if model:
            merged_params = self._adjust_parameters_for_model(model, merged_params)
        
        # Apply provider-specific parameter mappings
        native_params = self._map_parameters_to_native(merged_params)
        
        return native_params
    
    def _get_provider_defaults(self) -> ProviderParameterDefaults:
        """
        Get default parameter values for this provider.
        
        Override this method to provide custom defaults.
        Default implementation uses the provider name from config.
        
        Returns:
            ProviderParameterDefaults with default values and mappings
        """
        provider_name = self.config.get('provider_name', self.__class__.__name__.lower().replace('provider', ''))
        return get_provider_defaults(provider_name)
    
    def _adjust_parameters_for_model(self, model: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adjust parameters based on specific model requirements.
        
        Override this method to handle model-specific parameter adjustments.
        For example, OpenAI o1 models need max_completion_tokens instead of max_tokens.
        
        Args:
            model: Model name
            params: Current parameter dictionary
            
        Returns:
            Adjusted parameter dictionary
        """
        return params
    
    def _map_parameters_to_native(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map standardized parameter names to provider-specific native names.
        
        Override this method to handle provider-specific parameter mappings.
        For example, Google uses 'max_output_tokens' instead of 'max_tokens'.
        
        Args:
            params: Standardized parameter dictionary
            
        Returns:
            Parameter dictionary with native parameter names
        """
        defaults = self._get_provider_defaults()
        native_params = {}
        
        for key, value in params.items():
            # Use mapping if available, otherwise keep original name
            native_key = defaults.parameter_mappings.get(key, key)
            native_params[native_key] = value
        
        return native_params
    
    # Configuration and Capability Methods
    
    def get_supported_params(self) -> set:
        """
        Return set of supported configuration parameters.
        
        Override this method to specify which kwargs are supported by this provider.
        ProviderManager uses this for parameter validation.
        
        Returns:
            Set of supported parameter names
        """
        return set()
    
    
    # Configuration validation methods - implement per provider
    @abstractmethod
    def validate_provider_config(self, config: Dict[str, Any]) -> None:
        """Validate provider configuration against TypedDict schema"""
        pass
    
    @abstractmethod  
    def validate_model_config(self, config: Dict[str, Any]) -> None:
        """Validate model configuration against TypedDict schema"""
        pass
    
    @abstractmethod
    def _create_model_manager(self) -> 'BaseModelManager':
        """Create provider-specific model manager"""
        pass
    
    # Structured Output Helper Methods
    
    def _auto_structure_response(
        self, 
        raw_response: Any, 
        result_type: Optional[Type[Any]], 
        model: Optional[str] = None
    ) -> Union[Any, 'StructuredResponse']:
        """
        Automatically handle structured output conversion.
        
        This method implements the structured output protocol by checking
        model capabilities and applying appropriate fallback strategies.
        
        Args:
            raw_response: The raw response from the provider
            result_type: The requested result type
            model: The model used (for capability checking)
            
        Returns:
            Original response if no result_type, StructuredResponse if structured
        """
        if result_type is None:
            return raw_response
            
        # Import here to avoid circular imports
        from .structured_output import (
            StructuredResponse,
            _classify_result_type,
            _try_native_structured_parsing,
            _apply_json_parsing_fallback
        )
        import time
        
        start_time = time.time()
        
        try:
            # Check if model supports native structured output
            model_supports_native = self._check_native_structured_support(model)
            
            parsed_result = None
            fallback_used = None
            
            # Try native parsing first if supported
            if model_supports_native:
                parsed_result = _try_native_structured_parsing(raw_response, result_type)
                if parsed_result is not None:
                    fallback_used = "native"
            
            # Fall back to JSON parsing if native failed or not supported
            if parsed_result is None:
                parsed_result = _apply_json_parsing_fallback(raw_response, result_type)
                if parsed_result is not None:
                    fallback_used = "json_parse"
            
            # If all methods failed, return raw response
            if parsed_result is None:
                # Log the failure but return raw response gracefully
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Structured output failed for type {result_type}, returning raw response")
                return raw_response
            
            parse_time = time.time() - start_time
            
            return StructuredResponse(
                parsed_result=parsed_result,
                raw_response=raw_response,
                result_type=result_type,
                fallback_used=fallback_used,
                confidence=1.0 if fallback_used == "native" else 0.8,
                retries_used=0,  # This will be set by retry logic in concrete implementations
                parse_time=parse_time,
                metadata={"model_native_support": model_supports_native}
            )
            
        except Exception as e:
            # If anything goes wrong, log and return raw response
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Structured output processing failed: {e}")
            return raw_response
    
    def _check_native_structured_support(self, model: Optional[str] = None) -> bool:
        """
        Check if the specified model supports native structured output.
        
        Args:
            model: Model name to check
            
        Returns:
            True if model supports native structured output
        """
        try:
            model_list = self.model_manager.list_models()
            if model:
                model_info = next((m for m in model_list if m.name == model), None)
                if model_info and hasattr(model_info, 'capabilities'):
                    return getattr(model_info.capabilities, 'structured_output_native', False)
        except Exception:
            # If we can't determine capability, assume no native support
            pass
        return False
    
    def _validate_streaming_structured_support(
        self, 
        result_type: Optional[Type[Any]], 
        model: Optional[str] = None
    ) -> None:
        """
        Validate that streaming structured output is supported.
        
        Raises an error if result_type is specified but model doesn't support
        native structured output (since streaming has no fallbacks).
        
        Args:
            result_type: The requested result type
            model: The model to check
            
        Raises:
            ValueError: If structured output requested but not supported for streaming
        """
        if result_type is not None:
            if not self._check_native_structured_support(model):
                raise ValueError(
                    f"Streaming structured output requested for type {result_type} "
                    f"but model {model} does not support native structured output. "
                    "Streaming methods do not support fallback mechanisms."
                )
    
    # Media Validation Methods
    
    def _validate_media_content(self, provider_thread: 'ProviderThread', model: Optional[str] = None) -> None:
        """
        Validate media content against model capabilities before translation.
        
        This method checks all media content in the provider thread and raises
        appropriate exceptions for unsupported media types.
        
        Args:
            provider_thread: ProviderThread to validate
            model: Model name for capability checking
            
        Raises:
            UnsupportedMediaTypeError: If media type not supported by model
            InvalidMediaFormatError: If media format is invalid
        """
        # Import here to avoid circular imports
        from ..data_models.thread import (
            ImageContent, AudioContent, VideoContent, DocumentContent, ClientRequest
        )
        from .exceptions import UnsupportedMediaTypeError, InvalidMediaFormatError
        
        # Get model capabilities
        assert model is not None, "Model is required for media content validation"
        supported_media_types = self._get_supported_media_types(model)
        
        # Check all messages for media content
        for message in provider_thread.messages:
            if isinstance(message, ClientRequest):
                for content_block in message.content:
                    match content_block:
                        case ImageContent():
                            if 'image' not in supported_media_types:
                                raise UnsupportedMediaTypeError(
                                    'image', model, self.config.get('provider_name', ''),
                                    supported_media_types
                                )
                            self._validate_image_format(content_block)
                        case AudioContent() :
                            if 'audio' not in supported_media_types:
                                raise UnsupportedMediaTypeError(
                                    'audio', model, self.config.get('provider_name', ''),
                                    supported_media_types
                                )
                            self._validate_audio_format(content_block)
                        case VideoContent():
                            if 'video' not in supported_media_types:
                                raise UnsupportedMediaTypeError(
                                    'video', model, self.config.get('provider_name', ''),
                                    supported_media_types
                                )
                            self._validate_video_format(content_block)
                        case DocumentContent():
                            if 'document' not in supported_media_types:
                                raise UnsupportedMediaTypeError(
                                    'document', model, self.config.get('provider_name', ''),
                                    supported_media_types
                                )
                            self._validate_document_format(content_block)
                        case _:
                            pass
    
    def _get_supported_media_types(self, model: Optional[str] = None) -> list[str]:
        """
        Get list of media types supported by the specified model.
        
        Args:
            model: Model name to check capabilities
            
        Returns:
            List of supported media types ('image', 'audio', 'video', 'document')
        """
        supported_types = ['text']  # All models support text
        
        try:
            if model:
                model_list = self.model_manager.list_models()
                model_info = next((m for m in model_list if m.name == model), None)
                if model_info and hasattr(model_info, 'capabilities'):
                    caps = model_info.capabilities
                    if getattr(caps, 'vision', False):
                        supported_types.append('image')
                    if getattr(caps, 'audio', False):
                            supported_types.append('audio')
                        # Note: video and document support would need to be added to ModelCapabilities
        except Exception:
            # If we can't determine capabilities, return empty list to trigger validation errors
            pass
            
        return supported_types
    
    def _validate_image_format(self, image_content) -> None:
        """
        Validate image content format.
        
        Args:
            image_content: ImageContent to validate
            
        Raises:
            InvalidMediaFormatError: If image format is invalid
        """
        from .exceptions import InvalidMediaFormatError
        
        # Basic validation - check if we have data or URL
        if not hasattr(image_content, 'media_content'):
            raise InvalidMediaFormatError('image', 'Missing media_content')
        
        # Check MIME type is image
        if not image_content.mime_type.startswith('image/'):
            raise InvalidMediaFormatError('image', f'Invalid MIME type: {image_content.mime_type}')
    
    def _validate_audio_format(self, audio_content) -> None:
        """
        Validate audio content format.
        
        Args:
            audio_content: AudioContent to validate
            
        Raises:
            InvalidMediaFormatError: If audio format is invalid
        """
        from .exceptions import InvalidMediaFormatError
        
        # Basic validation - check if we have data or URL
        if not hasattr(audio_content, 'media_content'):
            raise InvalidMediaFormatError('audio', 'Missing media_content')
        
        # Check MIME type is audio
        if not audio_content.mime_type.startswith('audio/'):
            raise InvalidMediaFormatError('audio', f'Invalid MIME type: {audio_content.mime_type}')
        
        # For providers that only support specific audio formats (like OpenAI WAV)
        # Override this method in concrete implementations
    
    def _validate_video_format(self, video_content) -> None:
        """
        Validate video content format.
        
        Args:
            video_content: VideoContent to validate
            
        Raises:
            InvalidMediaFormatError: If video format is invalid
        """
        from .exceptions import InvalidMediaFormatError
        
        if not hasattr(video_content, 'media_content'):
            raise InvalidMediaFormatError('video', 'Missing media_content')
        
        if not video_content.mime_type.startswith('video/'):
            raise InvalidMediaFormatError('video', f'Invalid MIME type: {video_content.mime_type}')
    
    def _validate_document_format(self, document_content) -> None:
        """
        Validate document content format.
        
        Args:
            document_content: DocumentContent to validate
            
        Raises:
            InvalidMediaFormatError: If document format is invalid
        """
        from .exceptions import InvalidMediaFormatError
        
        if not hasattr(document_content, 'media_content'):
            raise InvalidMediaFormatError('document', 'Missing media_content')
        
        # Common document MIME types
        valid_document_types = [
            'application/pdf', 'text/plain', 'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/markdown'
        ]
        
        if document_content.mime_type not in valid_document_types:
            raise InvalidMediaFormatError('document', f'Unsupported document type: {document_content.mime_type}')
    
    # Error Handling Helper
    
    def _handle_provider_error(self, error: Exception) -> Exception:
        """
        Convert provider-specific errors to standardized exceptions.
        
        Override this method to map provider-specific errors to standard exceptions
        defined in provider_base.exceptions.
        
        Args:
            error: Provider-specific exception
            
        Returns:
            Standardized exception from provider_base.exceptions
        """
        # Import here to avoid circular imports
        from .exceptions import ProviderError
        return ProviderError(f"Provider error: {error}")
    
    # Token Counting - Universal capability for all providers
    
    def count_tokens(self, provider_thread: 'ProviderThread', model: str, provider: str) -> int:
        """
        Core token counting capability for any provider/model combination.
        
        This method provides accurate token counting using appropriate tokenizers
        based on the provider and model specifications. Supports:
        - OpenAI models with tiktoken (cl100k_base, o200k_base)
        - Anthropic models with Claude tokenizer
        - HuggingFace tokenizers with fallbacks
        - Message formatting overhead calculation
        - Multi-content messages (text + images)
        - Tool calling overhead
        
        Args:
            provider_thread: ProviderThread containing messages to count
            model: Model name for tokenizer selection
            provider: Provider name for tokenizer configuration
            
        Returns:
            Total token count including message formatting overhead
        """
        return self.token_counter.count_tokens(provider_thread, model, provider)


# Type hints for forward references
# These will be imported from their actual modules when available
if False:
    from ..context_management.context_types.thread_types import ProviderThread
    from ..context_management.context_types.messages import ProviderResponse
    from .model_types import ModelList
    from .structured_output import StructuredResponse
    from .model_manager import BaseModelManager