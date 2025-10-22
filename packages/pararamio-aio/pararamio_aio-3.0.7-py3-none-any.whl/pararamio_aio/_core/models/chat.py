"""Core Chat model without lazy loading."""

from __future__ import annotations

import re
from datetime import datetime
from typing import TYPE_CHECKING, Any, ClassVar, Generic, TypeVar, Unpack, cast
from urllib.parse import quote_plus

from pararamio_aio._core.api_schemas import ChatResponseItem
from pararamio_aio._core.constants import POSTS_LIMIT
from pararamio_aio._core.exceptions import PararamioValidationError
from pararamio_aio._core.utils.helpers import parse_iso_datetime

from .base import CoreBaseModel
from .post import CorePost

if TYPE_CHECKING:
    from pararamio_aio._core._types import FormatterT


__all__ = ('CoreChat',)


# Attribute formatters for Chat
CHAT_ATTR_FORMATTERS: FormatterT = {
    'time_edited': parse_iso_datetime,
    'time_updated': parse_iso_datetime,
    'time_created': parse_iso_datetime,
    'user_time_edited': parse_iso_datetime,
}

ClientT = TypeVar('ClientT')


class CoreChat(CoreBaseModel[ChatResponseItem], Generic[ClientT]):
    """Core Chat model with common functionality.

    Deprecated Attributes:
        The following attributes are deprecated and may be removed in future versions:
        - pm (bool): Use `type == 'pm'` instead to check for private messages
        - e2e (bool): Use `type == 'e2e'` instead to check for encrypted chats
        - allow_api (bool): No longer used by the API
        - adm_flag (bool): Use `is_admin` or check thread_admins list instead
        - meta (dict): Deprecated metadata field, no longer populated
        - last_msg_author (str): Use last_msg_author_id instead
        - last_msg_bot_name (str): Use last_msg_author_id to get bot info
        - last_msg_text (str): Use last_msg instead for last message text
    """

    _client: ClientT
    _data: ChatResponseItem
    # Chat attributes from API GET /core/chat
    id: int
    type: str  # 'pm' | 'e2e' | 'info' | 'group'
    title: str
    history_mode: str  # 'all' | 'since_join'
    description: str | None
    posts_count: int
    pm: bool  # DEPRECATED: Use type == 'pm' instead
    e2e: bool  # DEPRECATED: Use type == 'e2e' instead
    time_created: datetime
    time_updated: datetime
    time_edited: datetime | None
    author_id: int | None
    two_step_required: bool
    org_visible: bool
    organization_id: int | None
    posts_live_time: int | None
    allow_api: bool  # DEPRECATED: No longer used by the API
    read_only: bool
    parent_id: int | None
    is_common: bool
    is_voice: bool
    thread_groups: list[int]
    thread_users: list[int]
    thread_admins: list[int]
    tnew: bool
    adm_flag: bool  # DEPRECATED: Use is_admin or check thread_admins list instead
    is_favorite: bool
    tshow: bool
    mute: str | None  # 'group' | 'total' | None
    custom_title: str | None
    inviter_id: int | None
    user_time_edited: datetime | None
    history_start: int
    thread_guests: list[int]
    pinned: list[int]
    thread_users_all: list[int]
    meta: dict[str, Any] | None  # DEPRECATED: Metadata field no longer populated
    last_read_post_no: int
    last_msg_author_id: int
    last_msg_author: str | None  # DEPRECATED: Use last_msg_author_id instead
    last_msg_bot_name: str | None  # DEPRECATED: Use last_msg_author_id to get bot info
    last_msg_text: str | None  # DEPRECATED: Use last_msg instead
    last_msg: str
    keys: dict[int, str] | None  # Only for e2e chats

    _attr_formatters: ClassVar[FormatterT] = CHAT_ATTR_FORMATTERS

    def __init__(  # type: ignore[misc]
        self,
        client: ClientT,
        chat_id: int | None = None,
        **kwargs: Unpack[ChatResponseItem],
    ) -> None:
        # Handle positional chat_id
        if chat_id is not None:
            if 'chat_id' in kwargs:
                kwargs.pop('chat_id')
            kwargs['chat_id'] = chat_id
        self._data = cast('ChatResponseItem', kwargs)

        # Validate that required ID is present (either chat_id or id)
        if 'chat_id' not in self._data and 'id' not in self._data:
            raise PararamioValidationError(
                'Chat requires chat_id or id to be present in data. '
                'Cannot create a Chat without a valid chat identifier.'
            )

        # NOTE: id and chat_id are the same value - API returns both for compatibility
        # Ensure both fields are populated for consistent attribute access
        if 'chat_id' in self._data and 'id' not in self._data:
            self._data['id'] = self._data['chat_id']
        elif 'id' in self._data and 'chat_id' not in self._data:
            self._data['chat_id'] = self._data['id']

        super().__init__(client, **kwargs)  # type: ignore[call-arg]

    @property
    def client(self) -> ClientT:
        return self._client

    @property
    def is_private(self) -> bool:
        """Check if chat is the private message."""
        return self.pm

    def __str__(self) -> str:
        return self.title

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CoreChat):
            return id(other) == id(self)
        return self.id == other.id

    def __contains__(self, item: object) -> bool:
        """Check if a post belongs to this chat."""
        if isinstance(item, CorePost):
            return item.chat_id == self.id
        return False

    @classmethod
    def _build_search_url(
        cls,
        q: str,
        order_type: str,
        page: int,
        chat_ids: list[int] | None,
        limit: int | None,
    ) -> str:
        """Build search URL with parameters.

        Args:
            q: Search query
            order_type: Order type for results
            page: Page number
            chat_ids: Optional list of chat IDs to search within
            limit: Optional limit for results

        Returns:
            Formatted URL string
        """
        url = f'/posts/search?q={quote_plus(q)}'
        if order_type:
            url += f'&order_type={order_type}'
        if page:
            url += f'&page={page}'

        # API requires limit to be at least 10
        api_limit = max(limit or POSTS_LIMIT, 10) if limit else None
        if api_limit:
            url += f'&limit={api_limit}'

        # Handle chat_ids parameter if provided
        if chat_ids is not None:
            url += f'&chat_ids={",".join(map(str, chat_ids))}'

        return url

    @staticmethod
    def prepare_create_chat_data(
        title: str,
        description: str = '',
        users: list[int] | None = None,
        groups: list[int] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Prepare data for creating a chat.

        Args:
            title: Chat title
            description: Chat description
            users: List of user IDs to add
            groups: List of group IDs to add
            **kwargs: Additional chat data

        Returns:
            Dictionary with chat creation data
        """
        if users is None:
            users = []
        if groups is None:
            groups = []

        return {
            'title': title,
            'description': description,
            'users': users,
            'groups': groups,
            **kwargs,
        }

    @staticmethod
    def _validate_tag_name(tag_name: str) -> None:
        """Validate tag name according to API requirements.

        Args:
            tag_name: Name of the tag to validate

        Raises:
            PararamioValidationError: If tag name doesn't meet requirements
        """
        if not tag_name:
            raise PararamioValidationError('Tag name cannot be empty')
        if len(tag_name) < 2 or len(tag_name) > 15:
            raise PararamioValidationError(
                f'Tag name must be 2-15 characters long, got {len(tag_name)}'
            )
        if not re.match(r'^[a-zA-Z0-9_-]+$', tag_name):
            raise PararamioValidationError(
                'Tag name can only contain Latin letters (a-z), '
                'numbers (0-9), underscores (_) and dashes (-)'
            )
