from typing import Optional, List, Dict, Any, Union
from typing import Literal
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime

class Contact(BaseModel):
    id: str
    name: Optional[str] = None
    notify: Optional[str] = None
    verified_name: Optional[str] = Field(None, alias="verifiedName")
    img_url: Optional[str] = Field(None, alias="imgUrl")
    status: Optional[str] = None

class BaseMessage(BaseModel):
    to: str
    text: Optional[str] = None

class TextOnlyMessage(BaseMessage):
    message_type: str = Field("text", alias="messageType")
    text: str

class ImageUrlMessage(BaseMessage):
    message_type: str = Field("image", alias="messageType")
    image_url: str = Field(..., alias="imageUrl")

class VideoUrlMessage(BaseMessage):
    message_type: str = Field("video", alias="messageType")
    video_url: str = Field(..., alias="videoUrl")

class DocumentUrlMessage(BaseMessage):
    message_type: str = Field("document", alias="messageType")
    document_url: str = Field(..., alias="documentUrl")

class AudioUrlMessage(BaseMessage):
    message_type: str = Field("audio", alias="messageType")
    audio_url: str = Field(..., alias="audioUrl")

class StickerUrlMessage(BaseMessage):
    message_type: str = Field("sticker", alias="messageType")
    sticker_url: str = Field(..., alias="stickerUrl")
    text: None = None

class ContactCardPayload(BaseModel):
    name: str
    phone: str

class ContactCardMessage(BaseMessage):
    message_type: str = Field("contact", alias="messageType")
    contact: ContactCardPayload

class LocationPinPayload(BaseModel):
    latitude: Union[float, str]
    longitude: Union[float, str]
    name: Optional[str] = None
    address: Optional[str] = None

class LocationPinMessage(BaseMessage):
    message_type: str = Field("location", alias="messageType")
    location: LocationPinPayload

# Union type for all message payloads
WasenderMessagePayload = Union[
    TextOnlyMessage,
    ImageUrlMessage,
    VideoUrlMessage,
    DocumentUrlMessage,
    AudioUrlMessage,
    StickerUrlMessage,
    ContactCardMessage,
    LocationPinMessage
]

# Re-export types for backward compatibility
TextMessage = TextOnlyMessage
ImageMessage = ImageUrlMessage
VideoMessage = VideoUrlMessage
DocumentMessage = DocumentUrlMessage
AudioMessage = AudioUrlMessage
StickerMessage = StickerUrlMessage
ContactMessage = ContactCardMessage
LocationMessage = LocationPinMessage
ContactCard = ContactCardPayload
LocationPin = LocationPinPayload

class WasenderMessageSentData(BaseModel):
    message_id: Union[str, int] = Field(alias="msgId")
    jid: str = Field(
        alias="jid",
        description='The WhatsApp JID (e.g., "<user_id>@s.whatsapp.net")'
    )
    status: Optional[Literal['in_progress', 'sent']] = None

class WasenderSuccessResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    # Make data a Union of possible successful data structures or Any
    data: Optional[Union[WasenderMessageSentData, Dict[str, Any], List[Any], str, None]] = None

class RateLimitInfo(BaseModel):
    limit: Optional[int] = None
    remaining: Optional[int] = None
    reset_timestamp: Optional[int] = None

    def get_reset_timestamp_as_date(self) -> Optional[datetime]:
        if self.reset_timestamp:
            return datetime.fromtimestamp(self.reset_timestamp)
        return None

class RetryConfig:
    def __init__(
        self,
        max_retries: Optional[int] = 0,
        enabled: Optional[bool] = False
    ):
        self.max_retries = max_retries
        self.enabled = enabled

class WasenderSendResult(BaseModel):
    response: WasenderSuccessResponse
    rate_limit: Optional[RateLimitInfo] = None


class WasenderOperationResult(BaseModel):
    response: WasenderSuccessResponse
    rate_limit: Optional[RateLimitInfo] = None


class MessageInfoResult(BaseModel):
    response: WasenderSuccessResponse
    rate_limit: Optional[RateLimitInfo] = None


class UploadMediaFileResult(BaseModel):
    response: WasenderSuccessResponse
    rate_limit: Optional[RateLimitInfo] = None


class DecryptMediaResult(BaseModel):
    response: WasenderSuccessResponse
    rate_limit: Optional[RateLimitInfo] = None


class CheckWhatsAppNumberResult(BaseModel):
    response: WasenderSuccessResponse
    rate_limit: Optional[RateLimitInfo] = None