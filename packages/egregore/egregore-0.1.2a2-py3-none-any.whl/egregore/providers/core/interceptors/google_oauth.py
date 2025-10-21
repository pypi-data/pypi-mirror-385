"""Google OAuth interceptor for Gemini 2.5 series models via Code Assist API."""

import asyncio
import json
import requests
import uuid
from typing import Dict, Any, Optional
from pathlib import Path
import logging

from .base import BaseInterceptor

logger = logging.getLogger(__name__)


class GoogleOAuthInterceptor(BaseInterceptor):
    """Interceptor to handle Google OAuth for Gemini 2.5 series models.
    
    Based on working POC: OAuth models require special Code Assist API endpoint
    and specific request format with contents/parts structure.
    Handles OAuth token management and automatic token refresh.
    """
    
    # OAuth models that require Code Assist API (from POC)
    OAUTH_MODELS = {
        'gemini-2.5-flash',
        'gemini-2.5-pro', 
        'gemini-2.5-pro-experimental'
    }
    
    CLIENT_ID = "681255809395-oo8ft2oprdrnp9e3aqf6av3hmdib135j.apps.googleusercontent.com"
    CLIENT_SECRET = "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"
    GOOGLE_REDIRECT_URI = "https://codeassist.google.com/authcode"
    SCOPES = [
        "https://www.googleapis.com/auth/cloud-platform",
        "https://www.googleapis.com/auth/userinfo.email", 
        "https://www.googleapis.com/auth/userinfo.profile"
    ]
    
    def __init__(self, provider_name: str = "google", **config):
        """Initialize Google OAuth interceptor.
        
        Args:
            provider_name: Should be "google" for this interceptor
            **config: Additional configuration
        """
        super().__init__(provider_name, **config)
        
        # OAuth token management
        self.credentials_file = config.get('credentials_file', 'gemini_oauth_tokens.json')
        self.tokens = None
        self.accessible_projects = None
        
        # Add OAuth models from config if provided
        additional_models = config.get('oauth_models', set())
        if additional_models:
            self.OAUTH_MODELS = self.OAUTH_MODELS | set(additional_models)
            logger.info(f"Added {len(additional_models)} additional OAuth models")
        
        # Load cached tokens
        self._load_cached_tokens()
    
    async def applies_to_request(self, request_payload: Dict[str, Any]) -> bool:
        """Check if this interceptor should be applied to the request.
        
        This interceptor applies to:
        1. Google provider requests
        2. Using OAuth models (gemini-2.5 series)  
        3. Agent has requested OAuth via provider_config
        
        Args:
            request_payload: The request payload to check
            
        Returns:
            True if this interceptor should process the request
        """
        try:
            # Check if provider is Google
            provider = request_payload.get('provider', '').lower()
            if provider != 'google':
                return False
            
            # Check if model is an OAuth model
            model = request_payload.get('model', '')
            if not self._is_oauth_model(model):
                return False
            
            # Check if OAuth is requested (this should come from agent provider_config)
            oauth_requested = request_payload.get('oauth_requested', False)
            if oauth_requested:
                logger.debug(f"Google OAuth interceptor applies to model {model}")
                return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Error checking Google OAuth interceptor applicability: {e}")
            return False
    
    async def intercept_request(self, request_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Apply Google OAuth request format conversion.
        
        Based on working POC: Converts any-llm format to Code Assist API format:
        - Changes endpoint to Code Assist API  
        - Converts messages to contents/parts structure
        - Adds OAuth Authorization header
        - Adds required project ID
        
        Args:
            request_payload: The request payload to modify
            
        Returns:
            Modified request payload with Google OAuth-compatible Code Assist format
        """
        try:
            print("🔧 Google OAuth interceptor processing request...")
            
            # Ensure we have valid tokens
            if not await self._ensure_valid_tokens():
                raise Exception("Failed to obtain valid Google OAuth tokens")
            
            # Get accessible projects
            if not self.accessible_projects:
                self.accessible_projects = await self._get_accessible_projects()
            
            if not self.accessible_projects:
                raise Exception("No accessible Google Cloud projects found")
            
            project_id = self.accessible_projects[0]
            print(f"🎯 Using Google Cloud project: {project_id}")
            
            modified_payload = request_payload.copy()
            
            # Extract base model name
            model = modified_payload.get('model', '')
            base_model = model.replace('google:', '').replace('google/', '')
            
            # Transform to Code Assist API format
            self._convert_to_code_assist_format(modified_payload, base_model, project_id)
            
            # Add OAuth headers (from working POC)
            modified_payload['headers'] = {
                'Authorization': f'Bearer {self.tokens["access_token"]}',
                'Content-Type': 'application/json',
                'User-Agent': 'EgregoreV2-GoogleOAuth/1.0'
            }
            
            # Set the Code Assist API endpoint
            modified_payload['url'] = 'https://cloudcode-pa.googleapis.com/v1internal:generateContent'
            
            print("✅ Request transformed for Google Code Assist API with OAuth")
            return modified_payload
            
        except Exception as e:
            logger.error(f"Error applying Google OAuth conversion: {e}")
            print(f"❌ Google OAuth conversion failed: {e}")
            # Return original payload if conversion fails
            return request_payload
    
    def _is_oauth_model(self, model: str) -> bool:
        """Check if the model is a Google OAuth model requiring Code Assist API.
        
        Args:
            model: The model name to check
            
        Returns:
            True if this is a Google OAuth model
        """
        # Direct match
        if model in self.OAUTH_MODELS:
            return True
        
        # Check for partial matches (e.g., model might have version suffixes)
        for oauth_model in self.OAUTH_MODELS:
            if model.startswith(oauth_model):
                return True
                
        return False
    
    def _has_content_to_convert(self, request_payload: Dict[str, Any]) -> bool:
        """Check if the request has content that needs OAuth conversion.
        
        Args:
            request_payload: The request payload to check
            
        Returns:
            True if there is content that needs conversion
        """
        # Check if there are messages to convert
        messages = request_payload.get('messages', [])
        if messages:
            return True
        
        # Check if there's a system message
        system_field = request_payload.get('system')
        if system_field:
            return True
            
        return False
    
    def _convert_to_code_assist_format(
        self, 
        request_data: Dict[str, Any], 
        model: str, 
        project_id: str
    ) -> bool:
        """Convert request to Google Code Assist API format.
        
        Based on working POC format:
        {
            "model": "gemini-2.5-flash",
            "project": "project-id",
            "user_prompt_id": "uuid",
            "request": {
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": "message"}]
                    }
                ]
            }
        }
        
        Args:
            request_data: The request data to modify
            model: The model name
            project_id: The GCP project ID
            
        Returns:
            True if conversion was applied
        """
        try:
            messages = request_data.get('messages', [])
            system_message = request_data.get('system')
            
            # Build contents array
            contents = []
            
            # Add system message if present
            if system_message:
                if isinstance(system_message, list):
                    # Multi-block system message (like from Anthropic)
                    system_text = ' '.join(
                        block.get('text', '') for block in system_message 
                        if isinstance(block, dict) and 'text' in block
                    )
                else:
                    system_text = str(system_message)
                
                if system_text.strip():
                    contents.append({
                        "role": "user",
                        "parts": [{"text": f"System: {system_text}"}]
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
                                parts.append({"text": item.get('text', '')})
                            # TODO: Handle other content types (image, etc.)
                        else:
                            parts.append({"text": str(item)})
                else:
                    parts = [{"text": str(content)}]
                
                # Map roles (Google uses 'user' and 'model')
                google_role = 'model' if role == 'assistant' else 'user'
                
                contents.append({
                    "role": google_role,
                    "parts": parts
                })
            
            # Build Code Assist API request
            code_assist_request = {
                "model": model,
                "project": project_id,
                "user_prompt_id": str(uuid.uuid4()),
                "request": {
                    "contents": contents
                }
            }
            
            # Add generation parameters if present
            generation_config = {}
            if 'temperature' in request_data:
                generation_config['temperature'] = request_data['temperature']
            if 'max_tokens' in request_data:
                generation_config['maxOutputTokens'] = request_data['max_tokens']
            if 'top_p' in request_data:
                generation_config['topP'] = request_data['top_p']
            if 'top_k' in request_data:
                generation_config['topK'] = request_data['top_k']
            
            if generation_config:
                code_assist_request["request"]["generationConfig"] = generation_config
            
            # Replace the original request data
            request_data.clear()
            request_data.update(code_assist_request)
            
            logger.debug(f"Converted to Code Assist API format with {len(contents)} contents")
            return True
            
        except Exception as e:
            logger.error(f"Failed to convert to Code Assist API format: {e}")
            return False
    
    def _get_project_id(self, request_data: Dict[str, Any]) -> str:
        """Get GCP project ID for Code Assist API.
        
        Args:
            request_data: The request data
            
        Returns:
            Project ID (from config or default)
        """
        # Try to get project ID from various sources
        project_id = request_data.get('project_id')
        if project_id:
            return project_id
        
        # Try from config
        if hasattr(self, 'config'):
            project_id = self.config.get('project_id')
            if project_id:
                return project_id
        
        # Default project ID (should be configured properly in production)
        logger.warning("No project ID configured for Google OAuth, using default")
        return "default-project-id"
    
    def _load_cached_tokens(self):
        """Load cached OAuth tokens from file."""
        try:
            credentials_path = Path(self.credentials_file)
            if credentials_path.exists():
                with open(credentials_path, 'r') as f:
                    cached_data = json.load(f)
                    self.tokens = cached_data.get('tokens')
                    if self._is_token_valid():
                        print("✅ Loaded cached Google OAuth tokens")
                        return True
                    else:
                        print("⚠️  Cached Google tokens are invalid")
        except Exception as e:
            logger.warning(f"Failed to load cached tokens: {e}")
        return False
    
    def _save_tokens(self, tokens: Dict[str, Any]):
        """Save OAuth tokens to file."""
        try:
            import time
            import os
            
            cache_data = {
                'tokens': tokens,
                'cached_at': time.time(),
                'client_id': self.CLIENT_ID
            }
            
            with open(self.credentials_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            # Set secure permissions
            os.chmod(self.credentials_file, 0o600)
            print("✅ Google OAuth tokens cached successfully")
        except Exception as e:
            logger.warning(f"Failed to save tokens: {e}")
    
    def _is_token_valid(self) -> bool:
        """Check if current OAuth token is valid."""
        if not self.tokens or 'access_token' not in self.tokens:
            return False
        
        try:
            headers = {'Authorization': f'Bearer {self.tokens["access_token"]}'}
            response = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', headers=headers)
            return response.status_code == 200
        except:
            return False
    
    async def _refresh_token_if_needed(self) -> bool:
        """Refresh access token if expired and refresh token available."""
        if not self.tokens or 'refresh_token' not in self.tokens:
            return False
        
        if self._is_token_valid():
            return True  # Token is still valid
        
        print("🔄 Refreshing expired Google access token...")
        
        refresh_data = {
            'client_id': self.CLIENT_ID,
            'client_secret': self.CLIENT_SECRET,
            'refresh_token': self.tokens['refresh_token'],
            'grant_type': 'refresh_token'
        }
        
        try:
            response = requests.post('https://oauth2.googleapis.com/token', data=refresh_data)
            if response.status_code == 200:
                new_tokens = response.json()
                
                # Keep refresh token if not provided in response
                if 'refresh_token' not in new_tokens:
                    new_tokens['refresh_token'] = self.tokens['refresh_token']
                
                self.tokens = new_tokens
                self._save_tokens(new_tokens)
                print("✅ Google access token refreshed successfully")
                return True
        except Exception as e:
            logger.error(f"Google token refresh failed: {e}")
        
        return False
    
    async def _ensure_valid_tokens(self) -> bool:
        """Ensure we have valid OAuth tokens."""
        if self.tokens and await self._refresh_token_if_needed():
            return True
        
        print("❌ No valid Google OAuth tokens found")
        print("💡 Run the Google OAuth setup script to authenticate:")
        print("   poetry run python internal/working_poc/test_full_gemini_flow.py")
        return False
    
    async def _get_accessible_projects(self) -> list:
        """Get list of accessible Google Cloud projects."""
        if not self.tokens:
            return []
        
        try:
            headers = {'Authorization': f'Bearer {self.tokens["access_token"]}'}
            response = requests.get(
                'https://cloudresourcemanager.googleapis.com/v1/projects', 
                headers=headers
            )
            
            if response.status_code == 200:
                projects = response.json()
                project_list = [
                    proj.get('projectId') 
                    for proj in projects.get('projects', []) 
                    if proj.get('projectId')
                ]
                print(f"📁 Found {len(project_list)} accessible Google Cloud projects")
                return project_list
        except Exception as e:
            logger.warning(f"Failed to get Google Cloud projects: {e}")
        
        return []

    def __str__(self) -> str:
        """String representation of the interceptor."""
        return f"GoogleOAuthInterceptor(models={len(self.OAUTH_MODELS)}, enabled={self.enabled})"