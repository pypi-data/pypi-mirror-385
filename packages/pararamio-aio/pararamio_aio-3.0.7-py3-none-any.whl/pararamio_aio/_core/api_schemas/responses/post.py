"""Post-API response schemas."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from pararamio_aio._core import PostMetaT, TextParsedT

    from .events import PostEvent


class PostResponseItem(TypedDict, total=False):
    """Schema for a single Post item in API response."""

    # IDs from actual API response
    uuid: str
    id: int | None
    post_no: int
    user_id: int
    chat_id: int

    # Content
    text: str
    text_parsed: list[TextParsedT]

    # Reply info
    reply_no: int | None

    # Timestamps (as ISO strings from API)
    time_created: str
    time_edited: str | None

    # Metadata
    meta: PostMetaT
    event: PostEvent | None
    ver: int | None

    # Flag
    is_deleted: bool


class PostsResponse(TypedDict):
    """Schema for Posts API response wrapper."""

    posts: list[PostResponseItem]
    count: int | None  # Total count of posts


class Mention(TypedDict):
    """Mention in post."""

    id: int
    name: str
    value: str


class UserLink(Mention):
    """User link in post."""


__all__ = ['Mention', 'PostResponseItem', 'PostsResponse', 'UserLink']
