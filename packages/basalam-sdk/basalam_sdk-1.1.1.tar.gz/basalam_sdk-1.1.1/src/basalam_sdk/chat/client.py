"""
Client for the Chat service API.
"""
from typing import Optional

from .models import (
    MessageRequest,
    CreateChatRequest,
    ChatListResponse,
    MessageResponse,
    CreateChatResponse,
    GetMessagesRequest,
    GetMessagesResponse,
    GetChatsRequest
)
from ..base_client import BaseClient


class ChatService(BaseClient):
    """Client for the Chat service API."""

    def __init__(self, **kwargs):
        """Initialize the chat service client."""
        super().__init__(service="chat", **kwargs)

    async def create_message(
            self,
            request: MessageRequest,
            user_agent: Optional[str] = None,  # Just for Basalam internal team usage!!!
            x_client_info: Optional[str] = None,  # Just for Basalam internal team usage!!!
    ) -> MessageResponse:
        """
        Create a message.

        Args:
            request: The message request model.
            user_agent: The User-Agent header value.
            x_client_info: The X-Client-Info header value.

        Returns:
            MessageResponse: The response from the API.
        """
        headers = {}
        if user_agent:
            headers["User-Agent"] = user_agent
        if x_client_info:
            headers["X-Client-Info"] = x_client_info

        endpoint = f"/v1/chats/{request.chat_id}/messages"
        response = await self._post(endpoint, json_data=request.model_dump(exclude_none=True), headers=headers)
        return MessageResponse(**response)

    def create_message_sync(
            self,
            request: MessageRequest,
            user_agent: Optional[str] = None,  # Just for Basalam internal team usage!!!
            x_client_info: Optional[str] = None,  # Just for Basalam internal team usage!!!
    ) -> MessageResponse:
        """
        Create a message (synchronous version).

        Args:
            request: The message request model.
            user_agent: The User-Agent header value.
            x_client_info: The X-Client-Info header value.

        Returns:
            MessageResponse: The response from the API.
        """
        endpoint = f"/v1/chats/{request.chat_id}/messages"
        headers = {}
        if user_agent:
            headers["User-Agent"] = user_agent
        if x_client_info:
            headers["X-Client-Info"] = x_client_info

        response = self._post_sync(endpoint, json_data=request.model_dump(exclude_none=True), headers=headers)
        return MessageResponse(**response)

    async def create_chat(
            self,
            request: CreateChatRequest,
            x_creation_tags: Optional[str] = None,  # Just for Basalam internal team usage!!!
            x_user_session: Optional[str] = None,  # Just for Basalam internal team usage!!!
            x_client_info: Optional[str] = None  # Just for Basalam internal team usage!!!
    ) -> CreateChatResponse:
        """
        Create a private chat.

        Args:
            request: The create chat request model.
            x_creation_tags: Optional X-Creation-Tags header value.
            x_user_session: Optional X-User-Session header value.
            x_client_info: Optional X-Client-Info header value.

        Returns:
            CreateChatResponse: The response from the API.
        """
        endpoint = "/v1/chats"
        headers = {}
        if x_creation_tags:
            headers["X-Creation-Tags"] = x_creation_tags
        if x_user_session:
            headers["X-User-Session"] = x_user_session
        if x_client_info:
            headers["X-Client-Info"] = x_client_info

        response = await self._post(endpoint, json_data=request.model_dump(exclude_none=True), headers=headers)
        return CreateChatResponse(**response)

    def create_chat_sync(
            self,
            request: CreateChatRequest,
            x_creation_tags: Optional[str] = None,  # Just for Basalam internal team usage!!!
            x_user_session: Optional[str] = None,  # Just for Basalam internal team usage!!!
            x_client_info: Optional[str] = None  # Just for Basalam internal team usage!!!
    ) -> CreateChatResponse:
        """
        Create a private chat (synchronous version).

        Args:
            request: The create chat request model.
            x_creation_tags: Optional X-Creation-Tags header value.
            x_user_session: Optional X-User-Session header value.
            x_client_info: Optional X-Client-Info header value.

        Returns:
            CreateChatResponse: The response from the API.
        """
        endpoint = "/v1/chats"
        headers = {}
        if x_creation_tags:
            headers["X-Creation-Tags"] = x_creation_tags
        if x_user_session:
            headers["X-User-Session"] = x_user_session
        if x_client_info:
            headers["X-Client-Info"] = x_client_info

        response = self._post_sync(endpoint, json_data=request.model_dump(exclude_none=True), headers=headers)
        return CreateChatResponse(**response)

    async def get_messages(
            self,
            request: Optional[GetMessagesRequest] = None,
    ) -> GetMessagesResponse:
        """
        Get messages from a chat.

        Args:
            request: Optional request model containing query parameters (limit, order, cmp, message_id).

        Returns:
            GetMessagesResponse: The response containing the list of messages.
        """
        endpoint = f"/v1/chats/{request.chat_id}/messages"
        params = {
            "limit": request.limit,
            "order": request.order,
            "cmp": request.cmp
        }
        if request.message_id is not None:
            params["message_id"] = request.message_id

        response = await self._get(endpoint, params=params)
        return GetMessagesResponse(**response)

    def get_messages_sync(
            self,
            request: Optional[GetMessagesRequest] = None,
    ) -> GetMessagesResponse:
        """
        Get messages from a chat (synchronous version).

        Args:
            request: Optional request model containing query parameters (limit, order, cmp, message_id).

        Returns:
            GetMessagesResponse: The response containing the list of messages.
        """
        endpoint = f"/v1/chats/{request.chat_id}/messages"
        params = {
            "limit": request.limit,
            "order": request.order,
            "cmp": request.cmp
        }
        if request.message_id is not None:
            params["message_id"] = request.message_id

        response = self._get_sync(endpoint, params=params)
        return GetMessagesResponse(**response)

    async def get_chats(
            self,
            request: GetChatsRequest,
    ) -> ChatListResponse:
        """
        Get list of chats.

        Args:
            request: The get chats request model containing query parameters.

        Returns:
            ChatListResponse: The list of chats based on OpenAPI specification.
        """
        params = {
            "limit": request.limit,
            "order_by": request.order_by.value
        }
        if request.updated_from is not None:
            params["updated_from"] = request.updated_from
        if request.updated_before is not None:
            params["updated_before"] = request.updated_before
        if request.modified_from is not None:
            params["modified_from"] = request.modified_from
        if request.modified_before is not None:
            params["modified_before"] = request.modified_before
        if request.filters is not None:
            params["filters"] = request.filters.value

        endpoint = f"/v1/chats"
        response = await self._get(endpoint, params=params)
        return ChatListResponse(**response)

    def get_chats_sync(
            self,
            request: GetChatsRequest,
    ) -> ChatListResponse:
        """
        Get list of chats (synchronous version).

        Args:
            request: The get chats request model containing query parameters.

        Returns:
            ChatListResponse: The list of chats based on OpenAPI specification.
        """
        params = {
            "limit": request.limit,
            "order_by": request.order_by.value
        }
        if request.updated_from is not None:
            params["updated_from"] = request.updated_from
        if request.updated_before is not None:
            params["updated_before"] = request.updated_before
        if request.modified_from is not None:
            params["modified_from"] = request.modified_from
        if request.modified_before is not None:
            params["modified_before"] = request.modified_before
        if request.filters is not None:
            params["filters"] = request.filters.value

        endpoint = f"/v1/chats"
        response = self._get_sync(endpoint, params=params)
        return ChatListResponse(**response)
