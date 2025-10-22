"""Poll API response schemas."""

from __future__ import annotations

from typing import Any, TypedDict


class PollResponse(TypedDict, total=False):
    """Schema for Poll API response."""

    # IDs
    id: int
    vote_uid: str  # Vote unique identifier

    # Info
    question: str
    description: str | None

    # Options
    options: list[dict[str, Any]]

    # Settings
    multi_choice: bool
    anonymous: bool
    closed: bool

    # Timestamps (as ISO strings from API)
    time_created: str
    time_closed: str | None


class PollOptionData(TypedDict):
    """Schema for a poll option in API responses."""

    id: int
    text: str
    count: int
    vote_users: list[int]


class PollVoteData(TypedDict, total=False):
    """Schema for poll vote data from API."""

    vote_uid: str
    chat_id: int
    user_id: int
    question: str
    options: list[PollOptionData]
    mode: str  # 'one' or 'more'
    anonymous: bool
    total_user: int
    total_answer: int


class PollGetResponse(TypedDict):
    """Response for GET /msg/vote/{vote_uid}."""

    vote: PollVoteData


class PollCreateResponse(TypedDict):
    """Response for POST /msg/vote."""

    vote_uid: str
    post_no: int  # Post number where the poll was created


class PollVoteResponse(TypedDict):
    """Response for PUT /msg/vote/{vote_uid}."""

    vote: PollVoteData


__all__ = [
    'PollCreateResponse',
    'PollGetResponse',
    'PollOptionData',
    'PollResponse',
    'PollVoteData',
    'PollVoteResponse',
]
