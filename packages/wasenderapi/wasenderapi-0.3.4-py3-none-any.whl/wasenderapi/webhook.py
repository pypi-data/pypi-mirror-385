import json
from enum import Enum
from typing import Dict, Any, Optional, List, Union, TypeVar, Generic, Literal
from pydantic import BaseModel, Field, ConfigDict
from .groups import GroupParticipant

# NOTE: All webhook event model fields are now optional to handle the dynamic 
# nature of webhook events. Different webhook events may contain different 
# subsets of fields, so making them optional allows for more flexible parsing
# without validation errors.

WEBHOOK_SIGNATURE_HEADER = 'x-webhook-signature'

def verify_wasender_webhook_signature(
    request_signature: Optional[str],
    configured_secret: str
) -> bool:
    """Verify the webhook signature from Wasender.
    
    IMPORTANT: The current Wasender documentation example shows a direct string comparison
    for the signature and secret. This is a very simple verification method. Most webhook 
    systems use HMAC-SHA256 or similar cryptographic hashes for security.
    
    Please VERIFY with Wasender's official documentation or support if this simple string
    comparison is indeed the correct and only method for signature verification.
    """
    if not request_signature or not configured_secret:
        return False
    return request_signature == configured_secret

class WasenderWebhookEventType(str, Enum):
    # Chat Events
    CHATS_UPSERT = 'chats.upsert'
    CHATS_UPDATE = 'chats.update'
    CHATS_DELETE = 'chats.delete'
    # Group Events
    GROUPS_UPSERT = 'groups.upsert'
    GROUPS_UPDATE = 'groups.update'
    GROUP_PARTICIPANTS_UPDATE = 'group-participants.update'
    # Contact Events
    CONTACTS_UPSERT = 'contacts.upsert'
    CONTACTS_UPDATE = 'contacts.update'
    # Message Events
    MESSAGES_UPSERT = 'messages.upsert'      # New upcoming message will include fromMe to identify if it's a sent or received message
    MESSAGES_UPDATE = 'messages.update'      # Message status update
    MESSAGES_DELETE = 'messages.delete'
    MESSAGES_REACTION = 'messages.reaction'
    MESSAGES_RECIEVED = 'messages.recieved'
    # Message Receipt
    MESSAGE_RECEIPT_UPDATE = 'message-receipt.update'
    # Session Events
    MESSAGE_SENT = 'message.sent'          # Message successfully sent
    SESSION_STATUS = 'session.status'
    QRCODE_UPDATED = 'qrcode.updated'
    # New Events
    CALL_RECEIVED = 'call.received'
    PERSONAL_MESSAGE_RECEIVED = 'messages-personal.received'
    NEWSLETTER_MESSAGE_RECEIVED = 'messages-newsletter.received'
    GROUP_MESSAGE_RECEIVED = 'messages-group.received'
    POLL_RESULTS = 'poll.results'

EventType = TypeVar('EventType', bound=WasenderWebhookEventType)
DataType = TypeVar('DataType')

class BaseWebhookEvent(BaseModel, Generic[EventType, DataType]):
    event: Optional[EventType] = None
    timestamp: Optional[int] = None
    data: Optional[DataType] = None
    session_id: Optional[str] = Field(None, alias="sessionId")

    def __getitem__(self, key: str) -> Any:
        try:
            return getattr(self, key)
        except AttributeError:
            for field_name, field_model in self.model_fields.items():
                if field_model.alias == key:
                    return getattr(self, field_name)
            raise KeyError(key)

class MessageKey(BaseModel):
    id: Optional[str] = None
    from_me: Optional[bool] = Field(None, alias="fromMe")
    remote_jid: Optional[str] = Field(None, alias="remoteJid")
    participant: Optional[str] = None

# Chat Event Models
class ChatEntry(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    conversation_timestamp: Optional[int] = Field(None, alias="conversationTimestamp")
    unread_count: Optional[int] = Field(None, alias="unreadCount")
    mute_end_time: Optional[int] = Field(None, alias="muteEndTime")
    is_spam: Optional[bool] = Field(None, alias="isSpam")

# Group Event Models
class GroupMetadata(BaseModel):
    jid: Optional[str] = None
    subject: Optional[str] = None
    creation: Optional[int] = None
    owner: Optional[str] = None
    desc: Optional[str] = None
    participants: Optional[List[GroupParticipant]] = None
    announce: Optional[bool] = None
    restrict: Optional[bool] = None

class GroupParticipantsUpdateData(BaseModel):
    jid: Optional[str] = None
    participants: Optional[List[Union[str, GroupParticipant]]] = None
    action: Optional[Literal['add', 'remove', 'promote', 'demote']] = None

# Contact Event Models
class ContactEntry(BaseModel):
    jid: Optional[str] = None
    name: Optional[str] = None
    notify: Optional[str] = None
    verified_name: Optional[str] = Field(None, alias="verifiedName")
    status: Optional[str] = None
    img_url: Optional[str] = Field(None, alias="imgUrl")

# Message Event Models
class MessageContent(BaseModel):
    conversation: Optional[str] = None
    image_message: Optional[Dict[str, Any]] = Field(None, alias="imageMessage")
    video_message: Optional[Dict[str, Any]] = Field(None, alias="videoMessage")
    document_message: Optional[Dict[str, Any]] = Field(None, alias="documentMessage")
    audio_message: Optional[Dict[str, Any]] = Field(None, alias="audioMessage")
    sticker_message: Optional[Dict[str, Any]] = Field(None, alias="stickerMessage")
    contact_message: Optional[Dict[str, Any]] = Field(None, alias="contactMessage")
    location_message: Optional[Dict[str, Any]] = Field(None, alias="locationMessage")

class MessagesUpsertData(BaseModel):
    key: Optional[MessageKey] = None
    message: Optional[MessageContent] = None
    push_name: Optional[str] = Field(None, alias="pushName")
    message_timestamp: Optional[int] = Field(None, alias="messageTimestamp")

class MessageUpdate(BaseModel):
    status: Optional[str] = None

class MessagesUpdateDataEntry(BaseModel):
    key: Optional[MessageKey] = None
    update: Optional[MessageUpdate] = None

class MessagesDeleteData(BaseModel):
    keys: Optional[List[MessageKey]] = None

class Reaction(BaseModel):
    text: Optional[str] = None
    key: Optional[MessageKey] = None
    sender_timestamp_ms: Optional[str] = Field(None, alias="senderTimestampMs")
    read: Optional[bool] = None

class MessagesReactionDataEntry(BaseModel):
    key: Optional[MessageKey] = None
    reaction: Optional[Reaction] = None

# Message Receipt Models
class Receipt(BaseModel):
    user_jid: Optional[str] = Field(None, alias="userJid")
    status: Optional[str] = None
    t: Optional[int] = None

class MessageReceiptUpdateDataEntry(BaseModel):
    key: Optional[MessageKey] = None
    receipt: Optional[Receipt] = None

# Session Event Models
class MessageSentData(BaseModel):
    key: Optional[MessageKey] = None
    message: Optional[MessageContent] = None
    status: Optional[str] = None

class SessionStatusData(BaseModel):
    status: Optional[Literal["CONNECTED", "DISCONNECTED", "NEED_SCAN", "CONNECTING", "LOGGED_OUT", "EXPIRED"]] = None
    session_id: Optional[str] = Field(None, alias="sessionId")
    reason: Optional[str] = None

class QrCodeUpdatedData(BaseModel):
    qr: Optional[str] = None
    session_id: Optional[str] = Field(None, alias="sessionId")

# Define specific event types using the generic BaseWebhookEvent
ChatsUpsertEvent = BaseWebhookEvent[Literal[WasenderWebhookEventType.CHATS_UPSERT], List[ChatEntry]]
ChatsUpdateEvent = BaseWebhookEvent[Literal[WasenderWebhookEventType.CHATS_UPDATE], List[ChatEntry]]
ChatsDeleteEvent = BaseWebhookEvent[Literal[WasenderWebhookEventType.CHATS_DELETE], List[str]]

GroupsUpsertEvent = BaseWebhookEvent[Literal[WasenderWebhookEventType.GROUPS_UPSERT], List[GroupMetadata]]
GroupsUpdateEvent = BaseWebhookEvent[Literal[WasenderWebhookEventType.GROUPS_UPDATE], List[GroupMetadata]]
GroupParticipantsUpdateEvent = BaseWebhookEvent[Literal[WasenderWebhookEventType.GROUP_PARTICIPANTS_UPDATE], GroupParticipantsUpdateData]

ContactsUpsertEvent = BaseWebhookEvent[Literal[WasenderWebhookEventType.CONTACTS_UPSERT], List[ContactEntry]]
ContactsUpdateEvent = BaseWebhookEvent[Literal[WasenderWebhookEventType.CONTACTS_UPDATE], List[ContactEntry]]

MessagesUpsertEvent = BaseWebhookEvent[Literal[WasenderWebhookEventType.MESSAGES_UPSERT], MessagesUpsertData]
MessagesUpdateEvent = BaseWebhookEvent[Literal[WasenderWebhookEventType.MESSAGES_UPDATE], List[MessagesUpdateDataEntry]]
MessagesDeleteEvent = BaseWebhookEvent[Literal[WasenderWebhookEventType.MESSAGES_DELETE], MessagesDeleteData]
MessagesReactionEvent = BaseWebhookEvent[Literal[WasenderWebhookEventType.MESSAGES_REACTION], List[MessagesReactionDataEntry]]
MessagesRecievedEvent = BaseWebhookEvent[Literal[WasenderWebhookEventType.MESSAGES_RECIEVED], Dict[str, Any]]

MessageReceiptUpdateEvent = BaseWebhookEvent[Literal[WasenderWebhookEventType.MESSAGE_RECEIPT_UPDATE], List[MessageReceiptUpdateDataEntry]]
MessageSentEvent = BaseWebhookEvent[Literal[WasenderWebhookEventType.MESSAGE_SENT], MessageSentData]
SessionStatusEvent = BaseWebhookEvent[Literal[WasenderWebhookEventType.SESSION_STATUS], SessionStatusData]
QrCodeUpdatedEvent = BaseWebhookEvent[Literal[WasenderWebhookEventType.QRCODE_UPDATED], QrCodeUpdatedData]

CallReceivedEvent = BaseWebhookEvent[Literal[WasenderWebhookEventType.CALL_RECEIVED], Dict[str, Any]]
PersonalMessageReceivedEvent = BaseWebhookEvent[Literal[WasenderWebhookEventType.PERSONAL_MESSAGE_RECEIVED], Dict[str, Any]]
NewsletterMessageReceivedEvent = BaseWebhookEvent[Literal[WasenderWebhookEventType.NEWSLETTER_MESSAGE_RECEIVED], Dict[str, Any]]
GroupMessageReceivedEvent = BaseWebhookEvent[Literal[WasenderWebhookEventType.GROUP_MESSAGE_RECEIVED], Dict[str, Any]]
PollResultsEvent = BaseWebhookEvent[Literal[WasenderWebhookEventType.POLL_RESULTS], Dict[str, Any]]


class UnknownWebhookEvent(BaseModel):
    model_config = ConfigDict(extra="allow")

    event: Optional[str] = None
    timestamp: Optional[int] = None
    data: Optional[Any] = None
    session_id: Optional[str] = Field(None, alias="sessionId")

# Discriminated union of all specific event types for parsing
WasenderWebhookEvent = Union[
    ChatsUpsertEvent, ChatsUpdateEvent, ChatsDeleteEvent,
    GroupsUpsertEvent, GroupsUpdateEvent, GroupParticipantsUpdateEvent,
    ContactsUpsertEvent, ContactsUpdateEvent,
    MessagesUpsertEvent, MessagesUpdateEvent, MessagesDeleteEvent, MessagesReactionEvent,
    MessageReceiptUpdateEvent, MessageSentEvent, SessionStatusEvent, QrCodeUpdatedEvent,
    MessagesRecievedEvent,
    CallReceivedEvent, PersonalMessageReceivedEvent, NewsletterMessageReceivedEvent,
    GroupMessageReceivedEvent, PollResultsEvent,
    UnknownWebhookEvent
]