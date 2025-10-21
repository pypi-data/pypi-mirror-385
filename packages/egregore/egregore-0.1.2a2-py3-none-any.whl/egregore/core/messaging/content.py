"""
Core types for ProviderThread architecture.

Implements the 3-message-type system with ContentBlock-based content handling
for clean provider interfaces.
"""

from abc import ABC, abstractmethod
from pydantic import BaseModel, Field, ConfigDict, Discriminator
from typing import Optional, List, Dict, Any, Union, ClassVar
from enum import Enum


# Media data structures
class MediaData(BaseModel):
    """Media content with embedded data"""

    data: str = Field(..., description="Base64 encoded media data")
    encoding: str = Field(default="base64", description="Data encoding format")


class MediaUrl(BaseModel):
    """Media content referenced by URL"""

    url: str = Field(..., description="URL to media content")


# MessagePart base class and hierarchy
class MessagePart(BaseModel, ABC):
    """Abstract base for all message components"""

    timestamp: Optional[float] = None
    token_count: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class ContentBlock(MessagePart):
    """Content blocks with text representation"""

    content: str = Field(..., description="Text representation of content")


class TextContent(ContentBlock):
    """Plain text content"""

    pass


class ProviderToolCall(MessagePart):
    """Tool invocation from assistant - no content field needed"""

    tool_name: str = Field(..., description="Name of tool to call")
    tool_call_id: str = Field(..., description="Unique identifier for this tool call")
    parameters: Dict[str, Any] = Field(..., description="Parameters to pass to tool")


class ClientToolResponse(ContentBlock):
    """Tool execution result"""

    tool_call_id: str = Field(..., description="ID of original tool call")
    tool_name: str = Field(..., description="Name of tool that was called")
    success: bool = Field(..., description="Whether tool execution succeeded")
    message: str = Field(..., description="Tool result or error message")

    def __init__(self, **kwargs):
        # Set content to message for ContentBlock compatibility
        if "content" not in kwargs and "message" in kwargs:
            kwargs["content"] = kwargs["message"]
        super().__init__(**kwargs)


class MultiMediaContent(ContentBlock):
    """Base class for multimedia content"""

    media_content: Union[MediaData, MediaUrl] = Field(..., description="Media content")
    mime_type: str = Field(..., description="MIME type of content")
    filename: Optional[str] = None


class ImageContent(MultiMediaContent):
    """Image content"""

    width: Optional[int] = None
    height: Optional[int] = None


class AudioContent(MultiMediaContent):
    """Audio content"""

    duration: Optional[float] = None
    format: Optional[str] = None


class VideoContent(MultiMediaContent):
    """Video content"""

    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[float] = None
    format: Optional[str] = None


class DocumentContent(MultiMediaContent):
    """Document content"""

    page_count: Optional[int] = None
    format: Optional[str] = None


# Core message types
class BaseMessage(BaseModel, ABC):
    """Abstract base for message collections containing MessagePart"""

    content: List[MessagePart] = Field(
        ..., description="Collection of MessagePart items"
    )
    timestamp: Optional[float] = None
    token_count: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class SystemHeader(BaseMessage):
    """System header and context"""

    message_type: str = Field(
        default="system_header", description="Message type discriminator"
    )
    content: List[TextContent] = Field(
        ..., description="System messages are always text content"
    )


class ProviderResponse(BaseMessage):
    """AI responses from providers"""

    message_type: str = Field(
        default="provider_response", description="Message type discriminator"
    )
    content: List[Union[TextContent, ProviderToolCall]] = Field(
        ..., description="Can contain text and tool calls"
    )


class ProviderResponseStream(ProviderResponse):
    """Streaming/partial AI responses - inherits from ProviderResponse"""

    message_type: str = Field(
        default="provider_response_stream", description="Message type discriminator"
    )
    is_stream: bool = True
    interrupted: bool = False


class ClientRequest(BaseMessage):
    """Container for aggregated ContentBlock messages"""

    message_type: str = Field(
        default="client_request", description="Message type discriminator"
    )
    content: List[Union[TextContent, ImageContent, AudioContent, VideoContent, DocumentContent, ClientToolResponse]] = Field(
        ..., description="Can contain any content except ProviderToolCall"
    )


# ProviderThread container
