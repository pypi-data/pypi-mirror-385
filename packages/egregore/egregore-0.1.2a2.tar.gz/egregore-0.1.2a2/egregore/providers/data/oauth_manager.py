"""OAuth token manager for cross-platform token storage and management."""

import json
import asyncio
import os
import stat
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class OAuthManager:
    """Manages OAuth tokens for all providers with cross-platform storage."""
    
    def __init__(self):
        """Initialize OAuth manager with cross-platform token storage."""
        self.oauth_dir = self._get_oauth_directory()
        self.oauth_dir.mkdir(parents=True, exist_ok=True, mode=0o700)  # Private directory
        
        # Token cache
        self._cached_tokens: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"OAuth manager initialized with token directory: {self.oauth_dir}")
    
    def _get_oauth_directory(self) -> Path:
        """Get cross-platform OAuth token storage directory."""
        if os.name == 'nt':  # Windows
            base_dir = Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming'))
            return base_dir / 'egregore' / 'oauth'
        else:  # Linux/macOS
            # Use XDG Base Directory specification
            config_home = os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config')
            return Path(config_home) / 'egregore' / 'oauth'
    
    async def get_oauth_token(self, provider: str) -> Optional[str]:
        """Get valid OAuth access token for provider.
        
        Args:
            provider: Provider name (e.g., 'anthropic', 'google')
            
        Returns:
            Valid access token or None if not available/expired
        """
        try:
            tokens = await self._get_provider_tokens(provider)
            if not tokens:
                return None
            
            access_token = tokens.get('access_token')
            if not access_token:
                return None
            
            # Check if token is still valid
            if await self._is_token_valid(provider, tokens):
                return access_token
            
            # Try to refresh if possible
            if await self._refresh_token_if_needed(provider, tokens):
                refreshed_tokens = await self._get_provider_tokens(provider)
                return refreshed_tokens.get('access_token') if refreshed_tokens else None
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get OAuth token for {provider}: {e}")
            return None
    
    async def save_oauth_tokens(self, provider: str, tokens: Dict[str, Any]) -> bool:
        """Save OAuth tokens for provider.
        
        Args:
            provider: Provider name
            tokens: Token data (access_token, refresh_token, expires_at, etc.)
            
        Returns:
            True if saved successfully
        """
        try:
            token_file = self.oauth_dir / f"{provider}_oauth.json"
            
            # Add metadata
            token_data = {
                'tokens': tokens,
                'provider': provider,
                'saved_at': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            # Write atomically
            temp_file = token_file.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(token_data, f, indent=2)
            
            # Set secure permissions (readable only by owner)
            os.chmod(temp_file, stat.S_IRUSR | stat.S_IWUSR)
            
            # Atomic move
            temp_file.replace(token_file)
            
            # Update cache
            self._cached_tokens[provider] = tokens
            
            logger.info(f"Successfully saved OAuth tokens for {provider}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save OAuth tokens for {provider}: {e}")
            return False
    
    async def is_provider_oauth_enabled(self, provider: str) -> bool:
        """Check if provider has OAuth tokens available.
        
        Args:
            provider: Provider name
            
        Returns:
            True if OAuth tokens are available and valid
        """
        token = await self.get_oauth_token(provider)
        return token is not None
    
    async def get_oauth_headers(self, provider: str) -> Dict[str, str]:
        """Get OAuth headers for provider.
        
        Args:
            provider: Provider name
            
        Returns:
            Headers dict with Authorization header if available
        """
        try:
            access_token = await self.get_oauth_token(provider)
            if access_token:
                return {'Authorization': f'Bearer {access_token}'}
            return {}
        except Exception as e:
            logger.error(f"Failed to get OAuth headers for {provider}: {e}")
            return {}
    
    async def invalidate_tokens(self, provider: str) -> bool:
        """Invalidate cached tokens for provider.
        
        Args:
            provider: Provider name
            
        Returns:
            True if invalidated successfully
        """
        try:
            # Remove from cache
            self._cached_tokens.pop(provider, None)
            
            # Remove token file
            token_file = self.oauth_dir / f"{provider}_oauth.json"
            if token_file.exists():
                token_file.unlink()
            
            logger.info(f"Invalidated OAuth tokens for {provider}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to invalidate tokens for {provider}: {e}")
            return False
    
    async def list_oauth_providers(self) -> list[str]:
        """List providers with OAuth tokens available.
        
        Returns:
            List of provider names with OAuth tokens
        """
        try:
            providers = []
            for token_file in self.oauth_dir.glob("*_oauth.json"):
                provider = token_file.stem.replace('_oauth', '')
                if await self.is_provider_oauth_enabled(provider):
                    providers.append(provider)
            return providers
        except Exception as e:
            logger.error(f"Failed to list OAuth providers: {e}")
            return []
    
    async def _get_provider_tokens(self, provider: str) -> Optional[Dict[str, Any]]:
        """Get tokens for provider from cache or file."""
        # Check cache first
        if provider in self._cached_tokens:
            return self._cached_tokens[provider]
        
        # Load from file
        try:
            token_file = self.oauth_dir / f"{provider}_oauth.json"
            if not token_file.exists():
                return None
            
            with open(token_file, 'r') as f:
                token_data = json.load(f)
            
            tokens = token_data.get('tokens', {})
            if tokens:
                self._cached_tokens[provider] = tokens
                return tokens
            
        except Exception as e:
            logger.warning(f"Failed to load tokens for {provider}: {e}")
        
        return None
    
    async def _is_token_valid(self, provider: str, tokens: Dict[str, Any]) -> bool:
        """Check if token is still valid."""
        try:
            expires_at = tokens.get('expires_at')
            if not expires_at:
                # No expiry info, assume valid
                return True
            
            # Parse expiry time
            if isinstance(expires_at, str):
                expires_dt = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                # Convert to naive datetime for comparison
                if expires_dt.tzinfo is not None:
                    expires_dt = expires_dt.replace(tzinfo=None)
            elif isinstance(expires_at, (int, float)):
                expires_dt = datetime.fromtimestamp(expires_at)
            else:
                return True  # Unknown format, assume valid
            
            # Check if expires in next 5 minutes (buffer for refresh)
            buffer_time = datetime.now() + timedelta(minutes=5)
            return expires_dt > buffer_time
            
        except Exception as e:
            logger.warning(f"Failed to check token validity for {provider}: {e}")
            return True  # Assume valid if can't check
    
    async def _refresh_token_if_needed(self, provider: str, tokens: Dict[str, Any]) -> bool:
        """Refresh token if refresh_token is available."""
        try:
            refresh_token = tokens.get('refresh_token')
            if not refresh_token:
                return False
            
            # Provider-specific refresh logic
            if provider == 'anthropic':
                return await self._refresh_anthropic_token(tokens)
            elif provider == 'google':
                return await self._refresh_google_token(tokens)
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to refresh token for {provider}: {e}")
            return False
    
    async def _refresh_anthropic_token(self, tokens: Dict[str, Any]) -> bool:
        """Refresh Anthropic OAuth token."""
        try:
            refresh_token = tokens.get('refresh_token')
            if not refresh_token:
                logger.warning("No refresh token available for Anthropic")
                return False
            
            # Use the client_id from the tokens if available
            client_id = tokens.get('client_id', '9d1c250a-e61b-44d9-88ed-5944d1962f5e')
            
            refresh_data = {
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'client_id': client_id
            }
            
            logger.info("Refreshing Anthropic OAuth token...")
            
            import requests
            response = requests.post(
                'https://console.anthropic.com/v1/oauth/token',
                data=refresh_data,
                timeout=30
            )
            
            if response.status_code == 200:
                new_tokens = response.json()
                
                # Keep refresh token if not provided in response
                if 'refresh_token' not in new_tokens:
                    new_tokens['refresh_token'] = refresh_token
                
                # Keep client_id
                if 'client_id' not in new_tokens:
                    new_tokens['client_id'] = client_id
                
                # Add expiry info
                if 'expires_in' in new_tokens:
                    from datetime import datetime, timedelta
                    expires_at = datetime.now() + timedelta(seconds=new_tokens['expires_in'])
                    new_tokens['expires_at'] = expires_at.isoformat()
                
                # Save refreshed tokens
                await self.save_oauth_tokens('anthropic', new_tokens)
                logger.info("Successfully refreshed Anthropic OAuth token")
                return True
            elif response.status_code == 400:
                error_data = response.json() if response.content else {}
                if error_data.get('error') == 'invalid_grant':
                    logger.error("Refresh token is invalid or expired - need to re-authenticate")
                    # Remove invalid tokens
                    await self.invalidate_tokens('anthropic')
                else:
                    logger.error(f"Anthropic token refresh failed: {response.status_code} - {response.text}")
                return False
            else:
                logger.error(f"Anthropic token refresh failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to refresh Anthropic token: {e}")
            return False
    
    async def _refresh_google_token(self, tokens: Dict[str, Any]) -> bool:
        """Refresh Google OAuth token."""
        from httpx import AsyncClient
        try:
            refresh_token = tokens.get('refresh_token')
            if not refresh_token:
                logger.error("No refresh token available for Google")
                return False
            
            # Google OAuth2 endpoint
            url = "https://oauth2.googleapis.com/token"
            
            # Use client_id from tokens or environment
            client_id = tokens.get('client_id') or os.getenv('GOOGLE_CLIENT_ID')
            client_secret = tokens.get('client_secret') or os.getenv('GOOGLE_CLIENT_SECRET')
            
            if not client_id or not client_secret:
                logger.error("Missing Google OAuth client credentials")
                return False
            
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'client_id': client_id,
                'client_secret': client_secret
            }
            
            async with AsyncClient() as client:
                response = await client.post(url, data=data)
            
            if response.status_code == 200:
                new_tokens = response.json()
                
                # Merge with existing token data
                new_tokens.update({
                    'refresh_token': tokens.get('refresh_token'),  # Keep existing refresh token
                    'client_id': client_id,
                    'client_secret': client_secret
                })
                
                # Add expiry info
                if 'expires_in' in new_tokens:
                    from datetime import datetime, timedelta
                    expires_at = datetime.now() + timedelta(seconds=new_tokens['expires_in'])
                    new_tokens['expires_at'] = expires_at.isoformat()
                
                # Save refreshed tokens
                await self.save_oauth_tokens('google', new_tokens)
                logger.info("Successfully refreshed Google OAuth token")
                return True
            elif response.status_code == 400:
                error_data = response.json() if response.content else {}
                if error_data.get('error') == 'invalid_grant':
                    logger.error("Google refresh token is invalid or expired - need to re-authenticate")
                    # Remove invalid tokens
                    await self.invalidate_tokens('google')
                else:
                    logger.error(f"Google token refresh failed: {response.status_code} - {response.text}")
                return False
            else:
                logger.error(f"Google token refresh failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to refresh Google token: {e}")
            return False


# Global instance
oauth_manager = OAuthManager()