from typing import List, Union, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

# Import and re-export all core types
from .content import (
    # Media data structures
    MediaData, MediaUrl,
    # ContentBlock hierarchy
    ContentBlock, TextContent, ProviderToolCall, ClientToolResponse,
    MultiMediaContent, ImageContent, AudioContent, VideoContent, DocumentContent,
    # Core message types
    BaseMessage, SystemHeader, ProviderResponse, ProviderResponseStream, ClientRequest
)

# Re-export all classes for external use
__all__ = [
    'MediaData', 'MediaUrl', 'ContentBlock', 'TextContent', 'ProviderToolCall', 
    'ClientToolResponse', 'MultiMediaContent', 'ImageContent', 'AudioContent', 
    'VideoContent', 'DocumentContent', 'BaseMessage', 'SystemHeader', 
    'ProviderResponse', 'ProviderResponseStream', 'ClientRequest', 'ProviderThread'
]


class ProviderThread(BaseModel):
    """Container for core message thread - provider-agnostic"""
    messages: List[Union[
        SystemHeader, 
        ProviderResponse, 
        ProviderResponseStream, 
        ClientRequest
    ]] = Field(..., description="List of 3 core message types")
    
    def get_token_count(self) -> int:
        """Get total token count for thread"""
        total = 0
        for message in self.messages:
            if message.token_count:
                total += message.token_count
        return total
    
    def add_message(self, message: Union[SystemHeader, ProviderResponse, ClientRequest]):
        """Add message to thread"""
        self.messages.append(message)
    
    def get_last_n_messages(self, n: int) -> List[Union[SystemHeader, ProviderResponse, ClientRequest]]:
        """Get last n messages"""
        return self.messages[-n:] if n > 0 else []
    
    def get_system_messages(self) -> List[SystemHeader]:
        """Get all system messages"""
        return [msg for msg in self.messages if isinstance(msg, SystemHeader)]
    
    def get_provider_responses(self) -> List[ProviderResponse]:
        """Get all provider responses"""
        return [msg for msg in self.messages if isinstance(msg, ProviderResponse)]
    
    def get_client_requests(self) -> List[ClientRequest]:
        """Get all client requests"""
        return [msg for msg in self.messages if isinstance(msg, ClientRequest)]
    
    model_config = ConfigDict(
        # Allow arbitrary types for BaseMessage subclasses
        arbitrary_types_allowed=True
    )