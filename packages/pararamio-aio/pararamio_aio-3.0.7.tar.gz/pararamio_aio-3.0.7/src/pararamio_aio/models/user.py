"""Async User model."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import TYPE_CHECKING, Unpack
from urllib.parse import quote

from pararamio_aio._core.api_schemas.responses import (
    UserActivityResponse,
    UserPMResponse,
    UserPrivateMessageResponse,
    UserResponse,
    UserSearchResponse,
    UserSearchResultItem,
    UsersResponse,
)
from pararamio_aio._core.constants.endpoints import PRIVATE_MESSAGE_URL
from pararamio_aio._core.models import CoreUser, CoreUserSearchResult, SerializationMixin
from pararamio_aio._core.utils.helpers import unescape_dict

# Imports from core
from pararamio_aio.exceptions import PararamNotFoundError

from .activity import Activity, ActivityAction
from .base import AsyncClientMixin

if TYPE_CHECKING:
    from pararamio_aio._core._types import QuoteRangeT

    from pararamio_aio.client import AsyncPararamio

    from .chat import Chat
    from .post import Post

__all__ = ('User', 'UserSearchResult')


class UserSearchResult(
    CoreUserSearchResult['AsyncPararamio'],
    AsyncClientMixin[UserSearchResultItem],
    SerializationMixin['AsyncPararamio', UserSearchResultItem],
):
    """Async User search result with explicit loading."""

    def __init__(self, client: AsyncPararamio, **kwargs: Unpack[UserSearchResultItem]) -> None:
        """Initialize the async user search result.

        Args:
            client: AsyncPararamio client
            **kwargs: User search result data
        """
        super().__init__(client, **kwargs)

    async def get_pm_chat(self) -> Chat:
        """Get PM chat for this user.

        Returns:
            A Chat object for PM
        """
        if self.pm_thread_id:
            chat = await self.client.get_chat_by_id(self.pm_thread_id)
            if chat is None:
                raise ValueError(f'Chat with id {self.pm_thread_id} not found')
            return chat
        # Create new PM chat
        return await self.create_pm_chat()

    async def create_pm_chat(self) -> Chat:
        """Create a new PM chat with this user.

        Returns:
            New chat object
        """

        url = f'/core/chat/pm/{self.id}'
        response = await self.client.api_post(url, response_model=UserPMResponse)
        chat_id = response['chat_id']
        chat = await self.client.get_chat_by_id(chat_id)
        if chat is None:
            raise ValueError(f'Failed to create or retrieve chat with id {chat_id}')
        return chat

    async def send_message(self, text: str) -> Post:
        """Send a private message to this user.

        Args:
            text: Message text

        Returns:
            Created post
        """
        chat = await self.get_pm_chat()
        return await chat.send_message(text)

    async def post(
        self,
        text: str,
        quote_range: QuoteRangeT | None = None,
        reply_no: int | None = None,
    ) -> Post:
        """Send a post to this user via PM.

        Args:
            text: Post text
            quote_range: Optional quote range
            reply_no: Optional reply post number

        Returns:
            Created Post
        """
        chat = await self.get_pm_chat()
        return await chat.post(text=text, quote_range=quote_range, reply_no=reply_no)


class User(
    CoreUser['AsyncPararamio'],
    AsyncClientMixin[UserResponse],
    SerializationMixin['AsyncPararamio', UserResponse],
):
    """Async User model with explicit loading."""

    def __init__(  # type: ignore[misc]
        self,
        client: AsyncPararamio,
        user_id: int | None = None,
        **kwargs: Unpack[UserResponse],
    ) -> None:
        """Initialize async user.

        Args:
            client: AsyncPararamio client
            user_id: User ID (optional positional or keyword argument)
            **kwargs: User data including id
        """
        super().__init__(client, user_id, **kwargs)

    async def load(self) -> User:
        """Load full user data from API.

        Returns:
            Self with updated data
        """
        # Try cache first if available
        if self._client._cache:
            cache_key = f'user.{self.id}'
            cached = await self._client._cache.get(cache_key)
            if cached:
                self._data.update(cached)
                self._set_loaded()
                return self

        # Load from API if not in cache
        users = await self.client.get_users_by_ids([self.id])
        users_list = list(users)
        if not users_list:
            raise PararamNotFoundError(f'User {self.id} not found')

        user_data = users_list[0]._data

        # Update our data with loaded data
        self._data.update(user_data)
        self._set_loaded()

        # Cache the data if cache is available
        if self._client._cache:
            cache_key = f'user.{self.id}'
            await self._client._cache.set(cache_key, user_data)

        return self

    async def send_private_message(self, text: str) -> Post:
        """Send a private message to this user.

        Args:
            text: Message text

        Returns:
            Created post
        """
        url = PRIVATE_MESSAGE_URL
        response = await self.client.api_post(
            url, {'text': text, 'user_id': self.id}, response_model=UserPrivateMessageResponse
        )

        # Load the created post
        post = await self.client.get_post(response['chat_id'], response['post_no'])
        if post is None:
            raise ValueError(
                f'Failed to retrieve post {response["post_no"]} from chat {response["chat_id"]}'
            )
        return post

    async def _activity_page_loader(
        self, action: ActivityAction | None = None, page: int = 1
    ) -> UserActivityResponse:
        """Load activity page from API.

        Args:
            action: Optional action type to filter
            page: Page number

        Returns:
            API response dict
        """
        url = f'/activity?user_id={self.id}&page={page}'
        if action:
            url += f'&action={action.value}'

        return await self.client.api_get(url, response_model=UserActivityResponse)

    async def get_activity(
        self, start: datetime, end: datetime, actions: list[ActivityAction] | None = None
    ) -> list[Activity]:
        """Get user activity within date range.

        Args:
            start: Start datetime
            end: End datetime
            actions: Optional list of ActivityAction types to filter

        Returns:
            List of Activity objects sorted by time
        """

        # Create async page loader
        async def page_loader(
            action: ActivityAction | None = None, page: int = 1
        ) -> UserActivityResponse:
            return await self._activity_page_loader(action, page)

        return await Activity.get_activity(page_loader, start, end, actions)

    @classmethod
    async def load_users(cls, client: AsyncPararamio, ids: Sequence[int]) -> list[User]:
        """Load multiple users by IDs.

        Args:
            client: AsyncPararamio client
            ids: List of user IDs (max 100)

        Returns:
            List of User objects
        """
        try:
            ids_str = CoreUser.validate_ids_for_get_by_ids(ids)
        except ValueError as e:
            if str(e) == 'ids list cannot be empty':
                return []
            raise
        url = f'/user/list?ids={ids_str}'
        response = await client.api_get(url, response_model=UsersResponse)
        users: list[User] = [
            cls(client=client, **unescape_dict(data, ['name']))
            for data in response.get('users', [])
        ]
        return users

    async def post(
        self,
        text: str,
        quote_range: QuoteRangeT | None = None,
        reply_no: int | None = None,
    ) -> Post:
        """Send a post to this user via PM.

        Args:
            text: Post text
            quote_range: Optional quote range
            reply_no: Optional reply post number

        Returns:
            Created Post
        """
        # Search for user to get UserSearchResult
        if not self.unique_name:
            raise PararamNotFoundError('User unique_name is not available')
        results = await self.search(self.client, self.unique_name)
        for res in results:
            if res.unique_name == self.unique_name:
                return await res.post(text=text, quote_range=quote_range, reply_no=reply_no)
        raise PararamNotFoundError(f'User {self.unique_name} not found')

    @classmethod
    async def search(
        cls, client: AsyncPararamio, query: str, include_self: bool = False
    ) -> list[UserSearchResult]:
        """Search for users.

        Args:
            client: AsyncPararamio client
            query: Search query
            include_self: Whether to include current user in results

        Returns:
            List of search results
        """
        url = f'/user/search?flt={quote(query)}'
        if not include_self:
            url += '&self=false'
        response = await client.api_get(url, response_model=UserSearchResponse)

        results: list[UserSearchResult] = [
            UserSearchResult(client=client, **unescape_dict(data, keys=['name', 'custom_name']))
            for data in response.get('users', [])
        ]

        return results
