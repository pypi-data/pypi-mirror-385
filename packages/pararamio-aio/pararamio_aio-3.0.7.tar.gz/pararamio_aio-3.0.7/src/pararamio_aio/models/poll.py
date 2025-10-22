"""Async Poll model."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Unpack, cast

from pararamio_aio._core.api_schemas.responses import (
    PollCreateResponse,
    PollGetResponse,
    PollOptionData,
    PollResponse,
    PollVoteResponse,
)
from pararamio_aio._core.models import CorePoll, SerializationMixin

# Imports from core
from pararamio_aio.exceptions import (
    PararamioRequestError,
    PararamioServerResponseError,
    PararamioValidationError,
)

from .base import AsyncClientMixin

if TYPE_CHECKING:
    from pararamio_aio.client import AsyncPararamio

    from .chat import Chat

__all__ = ('Poll',)


# PollOption is just PollOptionData TypedDict from core
PollOption = PollOptionData


class Poll(
    CorePoll,
    AsyncClientMixin[PollResponse],
    SerializationMixin['AsyncPararamio', PollResponse],
):
    """Async Poll model with explicit loading."""

    def __init__(
        self,
        client: AsyncPararamio,
        **kwargs: Unpack[PollResponse],
    ) -> None:
        """Initialize async poll.

        Args:
            client: AsyncPararamio client
            **kwargs: Poll data
        """
        super().__init__(client, **kwargs)
        self._client = client

    async def load(self) -> Poll:
        """Load full poll data from API.

        Returns:
            Self with updated data
        """
        # Try cache first if available
        if self._client._cache:
            cache_key = f'poll.{self._data["vote_uid"]}'
            cached = await self._client._cache.get(cache_key)
            if cached:
                self._data.update(cached)
                self._set_loaded()
                return self

        # Load from API if not in cache
        response = await self.client.api_get(
            f'/msg/vote/{self._data["vote_uid"]}', response_model=PollGetResponse
        )

        # Update through the existing _update method which handles the response
        result = self._update(response)

        # Cache the data if cache is available
        if self._client._cache and 'vote' in response:
            cache_key = f'poll.{self._data["vote_uid"]}'
            await self._client._cache.set(cache_key, response['vote'])

        return result

    def _update(self, response: PollGetResponse | PollVoteResponse) -> Poll:
        """Update the Poll object with response data.

        Args:
            response: API response data

        Returns:
            Updated Poll object

        Raises:
            PararamioServerResponseError: If response is invalid
        """
        if 'vote' not in response:
            vote_uid = self._data['vote_uid']
            chat_id = self._data['chat_id']
            raise PararamioServerResponseError(
                f'failed to load data for vote {vote_uid} in chat {chat_id}',
                response,
            )

        # Process response data
        vote_data = response['vote']
        # Cast to proper type for update
        self._data.update(cast('PollResponse', vote_data))
        return self

    @classmethod
    async def create(
        cls,
        chat: Chat,
        question: str,
        *,
        mode: Literal['one', 'more'],
        anonymous: bool,
        options: list[str],
    ) -> Poll:
        """Create a new poll in the specified chat.

        Args:
            chat: The chat where the poll will be created
            question: The poll question
            mode: Options select mode ('one' for single, 'more' for multiple)
            anonymous: Whether the poll should be anonymous
            options: List of option texts

        Returns:
            Created the Poll object

        Raises:
            PararamioRequestError: If poll creation fails
        """
        # Get chat ID from data without triggering lazy loading
        chat_id = chat._data.get('chat_id') or chat._data.get('id')

        response = await chat.client.api_post(
            '/msg/vote',
            {
                'chat_id': chat_id,
                'question': question,
                'options': options,
                'mode': mode,
                'anonymous': anonymous,
            },
            response_model=PollCreateResponse,
        )

        if not response:
            raise PararamioRequestError('Failed to create poll')

        # Extract only the vote_uid from response, post_no is not needed for Poll
        poll = cls(chat.client, vote_uid=response['vote_uid'])
        return await poll.load()

    async def _vote(self, option_ids: list[int]) -> Poll:
        """Vote on the poll with selected option IDs.

        Args:
            option_ids: List of option IDs to vote for

        Returns:
            Updated Poll object

        Raises:
            PararamioValidationError: If option IDs are invalid
        """
        valid_ids = [opt['id'] for opt in self._data['options']]
        if option_ids and not all(opt_id in valid_ids for opt_id in option_ids):
            raise PararamioValidationError('incorrect option')

        response = await self.client.api_put(
            f'/msg/vote/{self._data["vote_uid"]}',
            {'variants': option_ids},
            response_model=PollVoteResponse,
        )
        return self._update(response)

    async def vote(self, option_id: int) -> Poll:
        """Vote for a single option.

        Args:
            option_id: The option ID to vote for

        Returns:
            Updated Poll object

        Raises:
            PararamioValidationError: If option_id is invalid
        """
        return await self._vote([option_id])

    async def vote_multi(self, option_ids: list[int]) -> Poll:
        """Vote for multiple options.

        Args:
            option_ids: List of option IDs to vote for

        Returns:
            Updated Poll object

        Raises:
            PararamioValidationError: If poll mode is not 'more' or option IDs are invalid
        """
        if not self._data.get('multi_choice', False):
            raise PararamioValidationError('Poll does not support multiple choices')
        return await self._vote(option_ids)

    async def retract(self) -> Poll:
        """Retract vote from the poll.

        Returns:
            Updated Poll object
        """
        return await self._vote([])

    def __str__(self) -> str:
        """String representation."""
        return self._data['question']

    def __eq__(self, other: object) -> bool:
        """Check equality."""
        if not isinstance(other, Poll):
            return False
        return self._data['vote_uid'] == other._data['vote_uid']
