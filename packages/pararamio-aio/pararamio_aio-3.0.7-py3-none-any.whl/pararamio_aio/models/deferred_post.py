"""Async DeferredPost model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Unpack

from pararamio_aio._core.api_schemas.requests import DeferredPostCreateRequest
from pararamio_aio._core.api_schemas.responses import (
    DeferredPostCreateResponse,
    DeferredPostDeleteResponse,
    DeferredPostResponse,
    DeferredPostsResponse,
)
from pararamio_aio._core.models.base import SerializationMixin
from pararamio_aio._core.models.deferred_post import CoreDeferredPost
from pararamio_aio._core.utils.helpers import format_datetime

# Imports from core
from pararamio_aio.exceptions import PararamNotFoundError

from .base import AsyncClientMixin

if TYPE_CHECKING:
    from pararamio_aio.client import AsyncPararamio


__all__ = ('DeferredPost',)


class DeferredPost(
    CoreDeferredPost['AsyncPararamio'],
    AsyncClientMixin[DeferredPostResponse],
    SerializationMixin['AsyncPararamio', DeferredPostResponse],
):
    """Async DeferredPost model for scheduled posts."""

    def __init__(self, client: AsyncPararamio, **kwargs: Unpack[DeferredPostResponse]) -> None:
        """Initialize async deferred post.

        Args:
            client: AsyncPararamio client
            **kwargs: Additional post data including id
        """
        # Extract id from kwargs if needed
        super().__init__(client, **kwargs)
        # Mark as loaded if we have the required fields
        if 'id' in kwargs:
            self._set_loaded()

    async def load(self) -> DeferredPost:
        """Load full deferred post-data from API.

        Returns:
            Self with updated data

        Raises:
            PararamNotFoundError: If post not found
        """
        posts = await self.get_deferred_posts(self.client)

        for post in posts:
            if post.id == self.id:
                self._data = post._data
                return self

        raise PararamNotFoundError(f'Deferred post with id {self.id} not found')

    async def delete(self) -> bool:
        """Delete this deferred post.

        Returns:
            True if successful
        """
        url = f'/msg/deferred/{self.id}'
        response = await self.client.api_delete(
            url, None, response_model=DeferredPostDeleteResponse
        )
        return response.get('result') == 'OK'

    @classmethod
    async def create(
        cls,
        client: AsyncPararamio,
        chat_id: int,
        text: str,
        *,
        time_sending: datetime,
        reply_no: int | None = None,
        quote_range: tuple[int, int] | None = None,
    ) -> DeferredPost:
        """Create a new deferred (scheduled) post.

        Args:
            client: AsyncPararamio client
            chat_id: Target chat ID
            text: Post text
            time_sending: When to send the post
            reply_no: Optional post number to reply to
            quote_range: Optional quote range as (start, end) tuple

        Returns:
            Created DeferredPost object
        """
        url = '/msg/deferred'

        # Use TypedDict for type-safe data construction
        data: DeferredPostCreateRequest = {
            'chat_id': chat_id,
            'text': text,
            'time_sending': format_datetime(time_sending),
        }

        # Add optional fields only if provided
        if reply_no is not None:
            data['reply_no'] = reply_no
        if quote_range is not None:
            data['quote_range'] = quote_range

        response = await client.api_post(url, dict(data), response_model=DeferredPostCreateResponse)

        return cls(
            client,
            id=int(response['deferred_post_id']),
            **data,
        )

    @classmethod
    async def get_deferred_posts(cls, client: AsyncPararamio) -> list[DeferredPost]:
        """Get all deferred posts for the current user.

        Args:
            client: AsyncPararamio client

        Returns:
            List of DeferredPost objects
        """
        url = '/msg/deferred'
        response = await client.api_get(url, response_model=DeferredPostsResponse)
        posts_data = response.get('posts', [])

        return [cls(client, **post_data) for post_data in posts_data]
