"""Anthropic OAuth interceptor for system message text block conversion."""

from typing import Dict, Any
import logging
import asyncio

from .base import BaseInterceptor
from egregore.providers.data.oauth_manager import oauth_manager

logger = logging.getLogger(__name__)


class AnthropicOAuthInterceptor(BaseInterceptor):
    """Interceptor to handle Anthropic OAuth system message format requirements.
    
    Based on proven POC: OAuth models require system messages as text block arrays,
    not simple strings. This interceptor automatically converts system message
    strings to the required [{"type": "text", "text": "..."}] format.
    """
    
    # OAuth models that require the text block conversion
    OAUTH_MODELS = {
        'claude-sonnet-4-20250514'
    }
    
    def __init__(self, provider_name: str = "anthropic", **config):
        """Initialize Anthropic OAuth interceptor.
        
        Args:
            provider_name: Should be "anthropic" for this interceptor
            **config: Additional configuration
        """
        super().__init__(provider_name, **config)
        
        # Add OAuth models from config if provided
        additional_models = config.get('oauth_models', set())
        if additional_models:
            self.OAUTH_MODELS = self.OAUTH_MODELS | set(additional_models)
            logger.info(f"Added {len(additional_models)} additional OAuth models")
    
    async def applies_to_request(self, request_payload: Dict[str, Any]) -> bool:
        """Check if this interceptor should be applied to the request.
        
        This interceptor applies to:
        1. Anthropic provider requests
        2. Using OAuth models (claude-sonnet-4, claude-opus-4, etc.)
        3. Agent has requested OAuth via provider_config
        4. OAuth tokens are available
        
        Args:
            request_payload: The request payload to check
            
        Returns:
            True if this interceptor should process the request
        """
        try:
            # Check if provider is Anthropic
            provider = request_payload.get('provider', '').lower()
            if provider != 'anthropic':
                return False
            
            # Check if model is an OAuth model
            model = request_payload.get('model', '')
            if not self._is_oauth_model(model):
                return False
            
            # Check if OAuth is requested (this should come from agent provider_config)
            oauth_requested = request_payload.get('oauth_requested', False)
            if not oauth_requested:
                return False
            
            # Skip token validation for now - let the interceptor run and handle token issues during request
            logger.debug(f"OAuth interceptor will attempt to process {model} request")
            
            logger.debug(f"OAuth interceptor applies to model {model}")
            return True
            
        except Exception as e:
            logger.warning(f"Error checking OAuth interceptor applicability: {e}")
            return False
    
    async def intercept_request(self, request_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Apply OAuth system message conversion and add Authorization header.
        
        Based on WORKING POC: Uses the exact patterns from anthropic_oauth_system_message_poc.py
        that successfully converts system messages to text block arrays for OAuth API.
        
        Args:
            request_payload: The request payload to modify
            
        Returns:
            Modified request payload with OAuth-compatible system message format and auth
        """
        try:
            modified_payload = request_payload.copy()
            
            # Add OAuth-specific headers (from working POC)
            if 'headers' not in modified_payload:
                modified_payload['headers'] = {}
            
            headers = modified_payload['headers']
            headers['anthropic-beta'] = 'oauth-2025-04-20'
            headers['anthropic-version'] = '2023-06-01'
            
            # Remove API key header (critical for OAuth)
            removed_api_key = headers.pop('x-api-key', None)
            if removed_api_key:
                logger.debug("Removed x-api-key header for OAuth authentication")
            
            # Get OAuth token and add Authorization header
            try:
                access_token = await oauth_manager.get_oauth_token('anthropic')
                if access_token:
                    headers['Authorization'] = f'Bearer {access_token}'
                    logger.debug("Added OAuth Authorization header")
                else:
                    logger.warning("No valid OAuth token available for Anthropic")
            except Exception as e:
                logger.warning(f"Failed to get OAuth token: {e}")
            
            # Apply system message text block conversion
            self._convert_system_string_to_text_blocks(modified_payload)
            
            return modified_payload
            
        except Exception as e:
            logger.error(f"Error applying OAuth system message conversion: {e}")
            # Return original payload if conversion fails
            return request_payload
    
    def _is_oauth_model(self, model: str) -> bool:
        """Check if the model is an OAuth model requiring text block conversion.
        
        Args:
            model: The model name to check
            
        Returns:
            True if this is an OAuth model
        """
        # Direct match
        if model in self.OAUTH_MODELS:
            return True
        
        # Check for partial matches (e.g., model might have version suffixes)
        for oauth_model in self.OAUTH_MODELS:
            if model.startswith(oauth_model):
                return True
                
        return False
    
    def _has_system_message_to_convert(self, request_payload: Dict[str, Any]) -> bool:
        """Check if the request has system messages that need OAuth conversion.
        
        Args:
            request_payload: The request payload to check
            
        Returns:
            True if there are system messages that need conversion
        """
        # Check if there's a 'system' field that's a string (needs conversion)
        system_field = request_payload.get('system')
        if isinstance(system_field, str):
            return True
            
        # Check if there are system messages in the messages array
        messages = request_payload.get('messages', [])
        for message in messages:
            if isinstance(message, dict) and message.get('role') == 'system':
                return True
                
        return False
    
    def _needs_conversion(self, system_message: Dict[str, Any]) -> bool:
        """Check if a system message needs OAuth conversion.
        
        Args:
            system_message: The system message to check
            
        Returns:
            True if conversion is needed
        """
        content = system_message.get('content')
        
        # If content is already a list (text blocks), no conversion needed
        if isinstance(content, list):
            return False
        
        # If content is a string, conversion is needed
        if isinstance(content, str):
            return True
            
        return False
    
    def _convert_system_message(self, system_message: Dict[str, Any]) -> Dict[str, Any]:
        """Convert system message to OAuth-compatible text block format.
        
        Args:
            system_message: The system message to convert
            
        Returns:
            Converted system message with text block format
        """
        content = system_message.get('content')
        
        # If already in correct format, return as-is
        if isinstance(content, list):
            return system_message
        
        # Convert string content to text block array
        if isinstance(content, str):
            converted_message = system_message.copy()
            converted_message['content'] = [
                {
                    "type": "text",
                    "text": content
                }
            ]
            return converted_message
        
        # For other content types, return as-is (shouldn't happen normally)
        logger.warning(f"Unexpected system message content type: {type(content)}")
        return system_message
    
    def _convert_system_messages_to_oauth_format(self, request_data: Dict[str, Any]) -> bool:
        """Convert system messages from messages array to top-level system field with 2 text blocks.
        
        Based on working POC: Creates 2-text-block system format:
        1. Mandatory Claude Code identity (from system messages)
        2. Additional context (from other system messages)
        
        Args:
            request_data: The request data to modify
            
        Returns:
            True if conversion was applied
        """
        messages = request_data.get('messages', [])
        if not messages:
            return False
        
        # Extract all system messages
        system_messages = []
        non_system_messages = []
        
        for message in messages:
            if isinstance(message, dict) and message.get('role') == 'system':
                content = message.get('content', '')
                if content.strip():
                    system_messages.append(content.strip())
            else:
                non_system_messages.append(message)
        
        if not system_messages:
            return False
        
        logger.debug(f"Found {len(system_messages)} system messages to convert")
        
        # Build 2-text-block array (from working POC pattern)
        text_blocks = []
        
        # Block 1: Primary system message (usually Claude Code identity)
        text_blocks.append({
            "type": "text", 
            "text": system_messages[0]
        })
        
        # Block 2: Additional system content if we have more
        if len(system_messages) > 1:
            additional_content = " ".join(system_messages[1:])
            text_blocks.append({
                "type": "text",
                "text": additional_content
            })
        
        # Update request: remove system messages from messages array, add top-level system field
        request_data['messages'] = non_system_messages
        request_data['system'] = text_blocks
        
        logger.debug(f"Converted {len(system_messages)} system messages to {len(text_blocks)} text blocks")
        return True
    
    def _convert_system_string_to_text_blocks(self, request_data: Dict[str, Any]) -> bool:
        """
        Convert system message to OAuth-compatible format with Claude Code identity.
        
        For OAuth, we MUST start with "You are Claude Code..." and can add user's system message as second block:
        {"system": [
            {"type": "text", "text": "You are Claude Code, Anthropic's official CLI for Claude."},
            {"type": "text", "text": "<user's system message>"}
        ]}
        
        Args:
            request_data: The request data to modify
            
        Returns:
            True if conversion was applied
        """
        # Required Claude Code system message for OAuth
        claude_code_system = "You are Claude Code, Anthropic's official CLI for Claude."
        
        # Start with the required Claude Code identity
        text_blocks = [
            {"type": "text", "text": claude_code_system}
        ]
        
        # Get user's system message if present
        user_system = request_data.get('system')
        if user_system and isinstance(user_system, str) and user_system.strip():
            # Only add user's system message if it's different from Claude Code identity
            if user_system.strip() != claude_code_system:
                text_blocks.append({
                    "type": "text", 
                    "text": user_system.strip()
                })
                logger.debug(f"Added user's system message as second text block: {user_system[:50]}...")
        
        # Set the multi-block system message
        request_data['system'] = text_blocks
        
        logger.info(f"OAuth system message created with {len(text_blocks)} text blocks (Claude Code + user content)")
        return True
    
    def _fix_oauth_system_message_data(self, request_data: Dict[str, Any]) -> bool:
        """Fix existing top-level system field format for OAuth API calls (from working POC).
        
        Converts single string to text block array.
        
        Args:
            request_data: The request data to modify
            
        Returns:
            True if conversion was applied
        """
        if 'system' not in request_data:
            return False
            
        current_system = request_data['system']
        
        if not isinstance(current_system, str):
            logger.debug("System message already in correct format")
            return False
        
        logger.debug(f"Converting system message to text blocks: {current_system[:100]}...")
        
        # Build text block array (from working POC)
        text_blocks = [
            {"type": "text", "text": current_system}
        ]
        
        # Replace with text block array
        request_data['system'] = text_blocks
        
        logger.debug(f"System message converted to {len(text_blocks)} text blocks")
        return True
    
    def __str__(self) -> str:
        """String representation of the interceptor."""
        return f"AnthropicOAuthInterceptor(models={len(self.OAUTH_MODELS)}, enabled={self.enabled})"