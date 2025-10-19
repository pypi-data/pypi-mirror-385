"""
Chat service module for the Basalam SDK.

This module provides access to Basalam's chat service APIs.
"""

from .client import ChatService
from .models import (
    Attachment,
    AttachmentFile,
    ChatListData,
    ChatListResponse,
    ChatResponse,
    Contact,
    CreateChatRequest,
    GetChatsRequest,
    GetMessagesRequest,
    GetMessagesResponse,
    MessageContent,
    MessageFile,
    MessageInput,
    MessageLink,
    MessageRequest,
    MessageSender,
    MessageTypeEnum,
    MessageOrderByEnum,
    MessageFiltersEnum,
    ChatListResponse,
)

__all__ = [
    "ChatService",
    "Attachment",
    "AttachmentFile",
    "ChatListData",
    "ChatListResponse",
    "ChatResponse",
    "Contact",
    "CreateChatRequest",
    "GetChatsRequest",
    "GetMessagesRequest",
    "GetMessagesResponse",
    "MessageContent",
    "MessageFile",
    "MessageInput",
    "MessageLink",
    "MessageRequest",
    "MessageSender",
    "MessageTypeEnum",
    "MessageOrderByEnum",
    "MessageFiltersEnum",
    "ChatListResponse",
]
