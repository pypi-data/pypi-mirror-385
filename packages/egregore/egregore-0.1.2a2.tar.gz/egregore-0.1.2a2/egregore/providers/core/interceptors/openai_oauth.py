#!/usr/bin/env python3
"""
OpenAI OAuth Request Interceptor for Egregore V2
===============================================

Handles OAuth authentication for OpenAI ChatGPT models via official OpenAI OAuth endpoints.
Based on working POC that uses legitimate OpenAI OAuth 2.0 + PKCE flow.
"""

import asyncio
import json
import requests
import os
from typing import Dict, Any, Optional
from pathlib import Path
import logging

from .base import BaseInterceptor

logger = logging.getLogger(__name__)


class OpenAIOAuthInterceptor(BaseInterceptor):
    """
    Request interceptor for OpenAI OAuth authentication.
    
    Handles OAuth token management for ChatGPT models using legitimate
    OpenAI OAuth 2.0 + PKCE flow with official endpoints.
    """
    
    # OAuth configuration from working POC
    CLIENT_ID = "app_EMoamEEZ73f0CkXaXp7hrann"
    ISSUER = "https://auth.openai.com"
    SCOPES = "openid profile email offline_access"
    
    # ChatGPT models that work with OAuth (GPT-5 series only)
    OAUTH_MODELS = {
        'gpt-5',
        'gpt-5-mini',
        'gpt-5-nano',
        'gpt-5-chat',
        'gpt-5-chat-latest',
        'gpt-5-2025-08-07',
        'gpt-5-mini-2025-08-07',
        'gpt-5-nano-2025-08-07'
    }
    
    def __init__(self, provider_name: str = "openai", **config):
        super().__init__(provider_name, **config)
        
        # OAuth token management
        self.credentials_file = config.get('credentials_file', '~/.egregore/openai_oauth.json')
        self.auth_data = None
        
        # Load cached tokens
        self._load_cached_tokens()
    
    async def applies_to_request(self, request_data: Dict[str, Any]) -> bool:
        """
        Check if this interceptor applies to the request.
        Applies to OpenAI provider requests with OAuth-enabled models.
        """
        provider = request_data.get('provider', '').lower()
        model = request_data.get('model', '')
        oauth_requested = request_data.get('oauth_requested', False)
        
        if provider != 'openai' or not oauth_requested:
            return False
        
        # Extract base model name (remove provider prefix if present)
        base_model = model.replace('openai:', '').replace('openai/', '')
        
        if base_model not in self.OAUTH_MODELS:
            print(f"❌ OpenAI OAuth only supports specific models. Requested: {model}")
            print(f"✅ Supported models: {', '.join(sorted(self.OAUTH_MODELS))}")
            return False
        
        return True
    
    async def intercept_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform the request for OpenAI ChatGPT backend API with OAuth authentication.
        """
        print("🔧 OpenAI OAuth interceptor processing request...")
        
        # Ensure we have valid tokens
        if not await self._ensure_valid_tokens():
            raise Exception("Failed to obtain valid OpenAI OAuth tokens")
        
        tokens = self.auth_data['tokens']
        access_token = tokens['access_token']
        account_id = tokens.get('account_id')
        
        if not account_id:
            raise Exception("No ChatGPT account ID available for OAuth")
        
        print(f"🎯 Using OpenAI account: {account_id}")
        
        modified_request = request_data.copy()
        
        # Transform to ChatGPT backend format
        self._convert_to_chatgpt_format(modified_request)
        
        # Add OAuth headers (from working POC)
        modified_request['headers'] = {
            'Authorization': f'Bearer {access_token}',
            'chatgpt-account-id': account_id,
            'Content-Type': 'application/json',
            'User-Agent': 'EgregoreV2-OpenAI-OAuth/1.0',
            'Accept': 'text/event-stream',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Referer': 'https://chatgpt.com/',
            'Origin': 'https://chatgpt.com'
        }
        
        # Set ChatGPT backend endpoint
        modified_request['url'] = 'https://chatgpt.com/backend-api/conversation'
        
        print("✅ Request transformed for ChatGPT backend API with OAuth")
        return modified_request
    
    def _convert_to_chatgpt_format(self, request_data: Dict[str, Any]):
        """Convert request to ChatGPT backend API format."""
        
        messages = request_data.get('messages', [])
        system_message = request_data.get('system')
        model = request_data.get('model', 'gpt-4')
        
        # Extract base model name
        base_model = model.replace('openai:', '').replace('openai/', '')
        
        # Build ChatGPT conversation format
        conversation_messages = []
        
        # Add system message if present
        if system_message:
            if isinstance(system_message, list):
                # Multi-block system message (like from other providers)
                system_text = ' '.join(
                    block.get('text', '') for block in system_message 
                    if isinstance(block, dict) and 'text' in block
                )
            else:
                system_text = str(system_message)
            
            if system_text.strip():
                conversation_messages.append({
                    "id": self._generate_message_id(),
                    "role": "system",
                    "content": {
                        "content_type": "text",
                        "parts": [system_text]
                    }
                })
        
        # Add conversation messages
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            
            # Handle different content formats
            if isinstance(content, list):
                parts = []
                for item in content:
                    if isinstance(item, dict):
                        if item.get('type') == 'text':
                            parts.append(item.get('text', ''))
                        # TODO: Handle other content types (image, etc.)
                    else:
                        parts.append(str(item))
                content_parts = parts
            else:
                content_parts = [str(content)]
            
            conversation_messages.append({
                "id": self._generate_message_id(),
                "role": role,
                "content": {
                    "content_type": "text",
                    "parts": content_parts
                }
            })
        
        # Build ChatGPT API request (from working POC)
        chatgpt_request = {
            "action": "next",
            "messages": conversation_messages,
            "parent_message_id": self._generate_message_id(),
            "model": base_model,
            "timezone_offset_min": -480,  # PST offset
            "history_and_training_disabled": False,
            "conversation_mode": {
                "kind": "primary_assistant"
            },
            "websocket_request_id": self._generate_message_id()
        }
        
        # Add generation parameters if present
        if 'temperature' in request_data:
            chatgpt_request['temperature'] = request_data['temperature']
        if 'max_tokens' in request_data:
            chatgpt_request['max_tokens'] = request_data['max_tokens']
        
        # Replace the original request data
        request_data.clear()
        request_data.update(chatgpt_request)
        
        logger.debug(f"Converted to ChatGPT format with {len(conversation_messages)} messages")
    
    def _generate_message_id(self) -> str:
        """Generate message ID in ChatGPT format."""
        import uuid
        return str(uuid.uuid4())
    
    def _load_cached_tokens(self):
        """Load cached OAuth tokens from file."""
        try:
            credentials_path = Path(os.path.expanduser(self.credentials_file))
            if credentials_path.exists():
                with open(credentials_path, 'r') as f:
                    self.auth_data = json.load(f)
                    if self._is_token_valid():
                        print("✅ Loaded cached OpenAI OAuth tokens")
                        return True
                    else:
                        print("⚠️  Cached OpenAI tokens are invalid")
        except Exception as e:
            logger.warning(f"Failed to load cached OpenAI tokens: {e}")
        return False
    
    def _is_token_valid(self) -> bool:
        """Check if current OAuth token is valid."""
        if not self.auth_data or 'tokens' not in self.auth_data:
            return False
        
        tokens = self.auth_data['tokens']
        if 'access_token' not in tokens:
            return False
        
        # Could add token expiry check here
        return True
    
    async def _refresh_token_if_needed(self) -> bool:
        """Refresh access token if expired and refresh token available."""
        if not self.auth_data or 'tokens' not in self.auth_data:
            return False
        
        tokens = self.auth_data['tokens']
        if 'refresh_token' not in tokens:
            return False
        
        if self._is_token_valid():
            return True  # Token is still valid
        
        print("🔄 Refreshing expired OpenAI access token...")
        
        refresh_data = {
            'client_id': self.CLIENT_ID,
            'grant_type': 'refresh_token',
            'refresh_token': tokens['refresh_token'],
            'scope': self.SCOPES
        }
        
        try:
            response = requests.post(
                f'{self.ISSUER}/oauth/token',
                json=refresh_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                new_tokens = response.json()
                
                # Update tokens
                tokens.update(new_tokens)
                
                # Save updated tokens
                self._save_tokens()
                print("✅ OpenAI access token refreshed successfully")
                return True
        except Exception as e:
            logger.error(f"OpenAI token refresh failed: {e}")
        
        return False
    
    def _save_tokens(self):
        """Save OAuth tokens to file."""
        try:
            import time
            
            # Update last refresh time
            self.auth_data['last_refresh'] = time.time()
            
            credentials_path = Path(os.path.expanduser(self.credentials_file))
            credentials_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(credentials_path, 'w') as f:
                json.dump(self.auth_data, f, indent=2)
            
            # Set secure permissions
            os.chmod(credentials_path, 0o600)
            print("✅ OpenAI OAuth tokens cached successfully")
        except Exception as e:
            logger.warning(f"Failed to save OpenAI tokens: {e}")
    
    async def _ensure_valid_tokens(self) -> bool:
        """Ensure we have valid OAuth tokens."""
        if self.auth_data and await self._refresh_token_if_needed():
            return True
        
        print("❌ No valid OpenAI OAuth tokens found")
        print("💡 Run the OpenAI OAuth setup script to authenticate:")
        print("   poetry run python internal/poc/openai_oauth_poc.py")
        return False
    
    def __str__(self) -> str:
        """String representation of the interceptor."""
        return f"OpenAIOAuthInterceptor(models={len(self.OAUTH_MODELS)}, enabled={self.enabled})"