"""User API response schemas."""

from __future__ import annotations

from typing import Any, TypedDict


class UserPMResponse(TypedDict):
    """Response for user PM creation."""

    chat_id: int


class UserPrivateMessageResponse(TypedDict):
    """Response for sending a private message."""

    chat_id: int
    post_no: int


class UserActivityResponse(TypedDict):
    """Response for user activity."""

    data: list[dict[str, Any]]
    activities: list[dict[str, Any]]  # Alternate field name


class UserSearchResultItem(TypedDict, total=False):
    """Schema for a single user search result item."""

    id: int
    avatar: str | None
    name: str
    unique_name: str
    custom_name: str | None
    time_created: str
    time_updated: str
    other_blocked: bool
    pm_thread_id: int | None  # According to docs, it's pm_thread_id not pm_chat_id
    is_bot: bool


class UserSearchResponse(TypedDict):
    """Schema for /user/search API response."""

    flt: str
    users: list[UserSearchResultItem]


class UserResponseItem(TypedDict, total=False):
    """Schema for a single User item in API response."""

    # IDs
    id: int
    user_id: int  # Alias for id

    # Names
    name: str
    unique_name: str
    name_trans: str | None

    # Info
    info: str | None
    info_parsed: list[dict[str, Any]] | None
    info_chat: int | None

    # Contact info
    email: str
    phonenumber: str | None
    phoneconfirmed: bool

    # Auth settings
    is_google: bool
    two_step_enabled: bool
    has_password: bool

    # Status
    active: bool
    deleted: bool
    is_bot: bool
    find_strict: bool

    # Organizations
    organizations: list[int]

    # Timestamps (as ISO strings from API)
    time_created: str
    time_updated: str

    # Timezone
    timezone_offset_minutes: int | None


class UsersResponse(TypedDict):
    """Schema for Users API response wrapper."""

    users: list[UserResponseItem]


# Keep old name for backward compatibility
UserResponse = UserResponseItem


class SessionItem(TypedDict):
    """Schema for a single user session."""

    name: str | None
    sid: str  # Session ID
    is_current: bool
    os: str
    browser: str
    last_use_ip: str
    last_use_dt: str  # ISO datetime string
    city: str
    country: str
    login_method: str  # 'password', 'google-oauth2', etc.


class SessionsResponse(TypedDict):
    """Schema for sessions API response."""

    data: list[SessionItem]


class ChatTagItem(TypedDict):
    """Schema for a single chat tag item."""

    tag: str
    chat_ids: list[int]


class ChatTagsResponse(TypedDict):
    """Schema for chat tags API response."""

    chats_tags: list[ChatTagItem]


__all__ = [
    'ChatTagItem',
    'ChatTagsResponse',
    'SessionItem',
    'SessionsResponse',
    'UserActivityResponse',
    'UserPMResponse',
    'UserPrivateMessageResponse',
    'UserResponse',
    'UserResponseItem',
    'UserSearchResponse',
    'UserSearchResultItem',
    'UsersResponse',
]
