"""Translation layer for General Purpose provider - converts between ProviderThread and any-llm format."""

from typing import Dict, List, Any, Optional, Union, cast, TYPE_CHECKING
import json
import logging

if TYPE_CHECKING:
    from egregore.core.tool_calling.tool_declaration import ToolDeclaration

# Import corev2 message types
from egregore.core.messaging import (
    ProviderResponse, ClientRequest, SystemHeader, ProviderThread,
    ContentBlock, TextContent, ProviderToolCall, ClientToolResponse,
    ImageContent, AudioContent, VideoContent, DocumentContent, MediaUrl, MediaData
)
from .structured_output import StructuredResponse

logger = logging.getLogger(__name__)


class GeneralPurposeTranslator:
    """Handles translation between ProviderThread format and any-llm API format."""
    
    def __init__(self, provider_name: str, model_manager=None):
        """Initialize translator for specific provider.
        
        Args:
            provider_name: Name of the specific provider backend (e.g., 'openai', 'anthropic', 'google')
            model_manager: Model manager instance
        """
        self.provider_name = provider_name
        self.model_manager = model_manager
    
    def translate_to_native(self, provider_thread: ProviderThread, model: Optional[str] = None,
                           tools: Optional[List['ToolDeclaration']] = None,
                           result_type: Any = None, **kwargs) -> Dict[str, Any]:
        """Convert ProviderThread to any-llm format.
        
        Args:
            provider_thread: ProviderThread containing messages to convert
            model: Model name to use
            tools: Tool declarations to include
            result_type: Type for structured output
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Dict formatted for any-llm completion() call
        """
        try:
            # Build base request following any-llm completion() signature
            request = {
                "model": model or "gpt-3.5-turbo",  # Default model
                "provider": self.provider_name,
                "messages": self._convert_messages(provider_thread),
            }
            
            # Add tools if provided
            if tools:
                request["tools"] = tools
                logger.debug(f"Added {len(tools)} tools to any-llm request")
            
            # Add structured output if provided
            if result_type:
                # OpenAI-style response_format for structured output
                # Note: Not all providers support this (e.g., Anthropic)
                # Unsupported providers will reject it and we'll use JSON parsing fallback
                response_format = self._create_response_format(result_type)
                request["response_format"] = response_format
                logger.debug(f"Added structured output for {result_type.__name__ if hasattr(result_type, '__name__') else result_type}")
            
            # Add optional parameters from kwargs
            optional_params = [
                'temperature', 'top_p', 'max_tokens', 'stream', 'n', 'stop',
                'presence_penalty', 'frequency_penalty', 'seed', 'api_key',
                'api_base', 'api_timeout', 'user', 'parallel_tool_calls',
                'logprobs', 'top_logprobs', 'logit_bias', 'stream_options',
                'max_completion_tokens', 'reasoning_effort'
            ]
            
            for param in optional_params:
                if param in kwargs and kwargs[param] is not None:
                    request[param] = kwargs[param]
            
            logger.debug(f"Converted ProviderThread to any-llm format for provider {self.provider_name}")
            return request
            
        except Exception as e:
            logger.error(f"Error converting ProviderThread to any-llm format: {e}")
            raise
    
    def translate_from_native(self, anyllm_response: Any) -> ProviderResponse:
        """Convert any-llm response to ProviderResponse.
        
        Args:
            anyllm_response: Response from any-llm completion()
            
        Returns:
            Egregore ProviderResponse
        """
        try:
            # Handle both dict and any-llm object responses
            if hasattr(anyllm_response, 'model_dump'):
                response_dict = anyllm_response.model_dump()
            elif hasattr(anyllm_response, 'dict'):
                response_dict = anyllm_response.dict()
            elif isinstance(anyllm_response, dict):
                response_dict = anyllm_response
            else:
                response_dict = dict(anyllm_response)
            
            # Extract content from first choice
            choices = response_dict.get('choices', [])
            if not choices:
                raise ValueError("No choices in any-llm response")
            
            first_choice = choices[0]
            message = first_choice.get('message', {})
            
            # Convert message content to ContentBlock list
            content_blocks = self._convert_content_from_anyllm(message)
            
            # Create ProviderResponse with usage tracking
            provider_response = self._create_provider_response(response_dict, content_blocks)
            
            logger.debug(f"Converted any-llm response to ProviderResponse for provider {self.provider_name}")
            return provider_response
            
        except Exception as e:
            logger.error(f"Error converting any-llm response to ProviderResponse: {e}")
            raise
    
    def convert_tool_calls_to_provider_format(self, tool_calls: List[Dict[str, Any]]) -> List[ContentBlock]:
        """
        Public helper to convert tool calls to ProviderToolCall format.
        
        Args:
            tool_calls: List of tool call dicts in OpenAI format
            
        Returns:
            List of ContentBlocks including ProviderToolCall objects
        """
        try:
            # Use internal conversion method with a mock message
            message_dict = {'tool_calls': tool_calls}
            return self._convert_content_from_anyllm(message_dict)
        except Exception as e:
            logger.error(f"Error converting tool calls to provider format: {e}")
            # Return empty list as fallback
            return []
    
    # Helper methods following OpenAI translator pattern
    
    def _convert_messages(self, provider_thread: ProviderThread) -> List[Dict[str, Any]]:
        """Convert ProviderThread messages to any-llm message format."""
        messages = []
        
        for message in provider_thread.messages:
            if isinstance(message, SystemHeader):
                messages.append(self._convert_system_message(message))
            elif isinstance(message, ClientRequest):
                messages.append(self._convert_client_request(message))
            elif isinstance(message, ProviderResponse):
                messages.append(self._convert_provider_response(message))
            else:
                logger.warning(f"Unknown message type: {type(message)}")
        
        return messages
    
    def _convert_system_message(self, message: SystemHeader) -> Dict[str, Any]:
        """Convert SystemHeader to any-llm system message format."""
        # SystemHeader should have content blocks, extract text content
        content_text = ""
        for content_block in message.content:
            if isinstance(content_block, TextContent):
                content_text += content_block.content
        
        return {
            "role": "system",
            "content": content_text.strip() or "You are a helpful assistant."
        }
    
    def _convert_client_request(self, message: ClientRequest) -> Dict[str, Any]:
        """Convert ClientRequest to any-llm user message format."""
        # Handle simple text content for now (multi-modal in Task 2.3)
        content_text = ""
        
        for content_block in message.content:
            if isinstance(content_block, TextContent):
                content_text += content_block.content + "\n"
            elif isinstance(content_block, ClientToolResponse):
                # Tool responses will be handled in Task 2.3
                content_text += f"[Tool Result: {content_block.tool_name}]\n"
            else:
                # Other content types (images, audio, etc.) in Task 2.3
                content_text += f"[{type(content_block).__name__}]\n"
        
        return {
            "role": "user", 
            "content": content_text.strip() or "Hello"
        }
    
    def _convert_provider_response(self, message: ProviderResponse) -> Dict[str, Any]:
        """Convert ProviderResponse to any-llm assistant message format."""
        # Handle simple text content for now (tool calls in Task 2.3)
        content_text = ""
        
        for content_block in message.content:
            if isinstance(content_block, TextContent):
                content_text += content_block.content + "\n"
            elif isinstance(content_block, ProviderToolCall):
                # Tool calls will be handled in Task 2.3
                content_text += f"[Tool Call: {content_block.tool_name}]\n"
            else:
                # Other content types in Task 2.3
                content_text += f"[{type(content_block).__name__}]\n"
        
        return {
            "role": "assistant",
            "content": content_text.strip() or "I understand."
        }
    
    def _convert_content_blocks(self, content_blocks: List[ContentBlock]) -> List[Dict[str, Any]]:
        """Convert ContentBlock list to any-llm content format."""
        converted_content = []
        
        for block in content_blocks:
            if isinstance(block, TextContent):
                # Text content is handled directly in message conversion
                converted_content.append({
                    "type": "text",
                    "text": block.content
                })
            elif isinstance(block, ImageContent):
                converted_content.append(self._convert_image_content(block))
            elif isinstance(block, AudioContent):
                converted_content.append(self._convert_audio_content(block))
            elif isinstance(block, ProviderToolCall):
                converted_content.append(self._convert_tool_call(block))
            elif isinstance(block, ClientToolResponse):
                converted_content.append(self._convert_tool_response(block))
            else:
                logger.warning(f"Unsupported content block type: {type(block)}")
                # Fallback to text representation
                converted_content.append({
                    "type": "text", 
                    "text": f"[{type(block).__name__}: {block.content}]"
                })
        
        return converted_content
    
    def _convert_image_content(self, image_content: ImageContent) -> Dict[str, Any]:
        """Convert ImageContent to any-llm image format."""
        # any-llm supports OpenAI-compatible image format
        image_data = {
            "type": "image_url",
            "image_url": {}
        }
        
        # Handle different image source types
        if hasattr(image_content, 'media_content') and image_content.media_content:
            if hasattr(image_content.media_content, 'data'):
                # Embedded base64 data
                mime_type = getattr(image_content, 'mime_type', 'image/jpeg')
                data_url = f"data:{mime_type};base64,{image_content.media_content.data}"
                image_data["image_url"]["url"] = data_url
            elif hasattr(image_content.media_content, 'url'):
                # URL reference
                image_data["image_url"]["url"] = image_content.media_content.url
        else:
            # Fallback - use content as text description
            return {
                "type": "text",
                "text": f"[Image: {image_content.content}]"
            }
        
        return image_data
    
    def _convert_audio_content(self, audio_content: AudioContent) -> Dict[str, Any]:
        """Convert AudioContent to any-llm audio format."""
        # Most any-llm providers don't support audio directly yet
        # Provide a text representation for now
        return {
            "type": "text",
            "text": f"[Audio Content: {audio_content.content}]"
        }
    
    def _convert_tool_call(self, tool_call: ProviderToolCall) -> Dict[str, Any]:
        """Convert ProviderToolCall to any-llm tool call format."""
        # Basic tool call support - any-llm uses OpenAI format
        return {
            "type": "function",
            "function": {
                "name": tool_call.tool_name,
                "arguments": json.dumps(tool_call.parameters) if tool_call.parameters else "{}"
            }
        }
    
    def _convert_tool_response(self, tool_response: ClientToolResponse) -> Dict[str, Any]:
        """Convert ClientToolResponse to any-llm tool result format."""
        # Tool responses are typically represented as text content
        status = "success" if tool_response.success else "error"
        return {
            "type": "text",
            "text": f"Tool '{tool_response.tool_name}' result ({status}): {tool_response.content}"
        }
    
    def _convert_content_from_anyllm(self, anyllm_message: Dict[str, Any]) -> List[ContentBlock]:
        """Convert any-llm response content to ContentBlock list."""
        content_blocks = []
        
        # Extract text content
        content_text = anyllm_message.get('content', '')
        if content_text and isinstance(content_text, str):
            content_blocks.append(TextContent(content=content_text.strip()))
        
        # Extract tool calls (if any)
        tool_calls = anyllm_message.get('tool_calls', [])
        if tool_calls:  # Check if tool_calls is not None
            for tool_call in tool_calls:
                if isinstance(tool_call, dict) and tool_call.get('type') == 'function':
                    function_data = tool_call.get('function', {})
                    try:
                        # Parse arguments from JSON string
                        arguments_str = function_data.get('arguments', '{}')
                        arguments = json.loads(arguments_str) if arguments_str else {}
                        
                        tool_call_block = ProviderToolCall(
                            tool_name=function_data.get('name', 'unknown'),
                            tool_call_id=tool_call.get('id', 'unknown'),
                            parameters=arguments
                        )
                        content_blocks.append(tool_call_block)
                    except (json.JSONDecodeError, Exception) as e:
                        logger.warning(f"Failed to parse tool call: {e}")
                        # Fallback to text representation
                        content_blocks.append(TextContent(
                            content=f"[Tool Call: {function_data.get('name', 'unknown')}]"
                        ))
        
        # If no content was found, add a default response
        if not content_blocks:
            content_blocks.append(TextContent(content=""))
        
        return content_blocks
    
    def _create_provider_response(self, anyllm_response: Dict[str, Any], 
                                 content_blocks: List[ContentBlock]) -> ProviderResponse:
        """Create ProviderResponse from any-llm response and content blocks."""
        # Extract usage information
        usage_info = self._extract_usage_info(anyllm_response)
        
        # Extract metadata
        metadata = {
            'provider': self.provider_name,
            'model': anyllm_response.get('model', 'unknown'),
            'response_id': anyllm_response.get('id', 'unknown'),
            'finish_reason': None,
            'usage': usage_info
        }
        
        # Get finish reason from first choice
        choices = anyllm_response.get('choices', [])
        if choices:
            metadata['finish_reason'] = choices[0].get('finish_reason', 'stop')
        
        # Create ProviderResponse
        provider_response = ProviderResponse(
            content=content_blocks,
            token_count=usage_info.get('total_tokens', 0),
            metadata=metadata
        )
        
        return provider_response
    
    def _extract_usage_info(self, anyllm_response: Dict[str, Any]) -> Dict[str, Any]:
        """Extract usage information from any-llm response."""
        usage = anyllm_response.get('usage', {})
        
        return {
            'prompt_tokens': usage.get('prompt_tokens', 0),
            'completion_tokens': usage.get('completion_tokens', 0),
            'total_tokens': usage.get('total_tokens', 0),
            'provider_specific': {
                'provider': self.provider_name,
                'raw_usage': usage
            }
        }
    
    def _create_response_format(self, result_type: Any) -> Dict[str, Any]:
        """Create any-llm response_format for structured output (OpenAI-compatible)."""
        try:
            # Generate JSON schema from Pydantic model
            if hasattr(result_type, 'model_json_schema'):
                # Pydantic v2 model
                schema = result_type.model_json_schema()
                model_name = getattr(result_type, "__name__", "response")
            elif hasattr(result_type, 'schema'):
                # Pydantic v1 model
                schema = result_type.schema()
                model_name = getattr(result_type, "__name__", "response")
            else:
                # Fallback for non-Pydantic types
                logger.warning(f"Cannot generate schema for non-Pydantic type: {result_type}")
                return {"type": "text"}

            # Ensure schema has additionalProperties: false for strict mode
            if "additionalProperties" not in schema:
                schema["additionalProperties"] = False

            # OpenAI strict mode requires ALL properties to be in required array
            # Optional fields maintain nullability through anyOf: [{"type": "..."}, {"type": "null"}]
            if "properties" in schema:
                schema["required"] = list(schema["properties"].keys())

            # Return OpenAI-compatible response format (works with any-llm)
            response_format = {
                "type": "json_schema",
                "json_schema": {
                    "name": model_name,
                    "schema": schema,
                    "strict": True  # Enable strict mode for better validation
                }
            }

            logger.debug(f"Created structured output format for {model_name} with {self.provider_name}")
            return response_format

        except Exception as e:
            logger.error(f"Error creating response format for {result_type}: {e}")
            # Fallback to text format
            return {"type": "text"}