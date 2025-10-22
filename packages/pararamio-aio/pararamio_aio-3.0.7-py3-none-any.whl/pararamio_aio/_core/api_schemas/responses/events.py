"""Post-event schemas."""

from __future__ import annotations

from typing import Any, Literal, TypedDict


class UserInfo(TypedDict):
    """User info in events."""

    id: int
    name: str
    unique_name: str


class GroupInfo(TypedDict):
    """Group info in events."""

    id: int
    name: str
    unique_name: str | None


class TeamInfo(TypedDict):
    """Team/Organization info in events."""

    id: int
    title: str


class ChatInfo(TypedDict):
    """Chat info in events."""

    id: int
    title: str
    posts_qty: int | None


# Event data types for different event types


class NewThreadEventData(TypedDict):
    """NEW_THREAD event data."""

    users_add: list[UserInfo]
    groups_add: list[GroupInfo]


class EditThreadEventData(TypedDict):
    """EDIT_THREAD event data."""

    users_add: list[UserInfo]
    users_del: list[UserInfo]
    admins_add: list[UserInfo]
    admins_del: list[UserInfo]
    groups_add: list[GroupInfo]
    groups_del: list[GroupInfo]


class EnterToThreadEventData(TypedDict):
    """ENTER_TO_THREAD event data."""

    user_id: int


class QuitFromThreadEventData(TypedDict):
    """QUIT_FROM_THREAD event data."""

    user: UserInfo
    groups_exist: list[dict[str, Any]]


class GroupsQuitFromThreadEventData(TypedDict):
    """GROUPSQUIT_FROM_THREAD event data."""

    __root__: list[GroupInfo]


class WelcomeToOrgEventData(TypedDict):
    """WELCOME_TO_ORG event data."""

    organization: TeamInfo
    welcome_text: str


class ForkThreadEventData(TypedDict):
    """FORK_THREAD event data."""

    to_chat: ChatInfo
    from_chat: dict[str, Any]  # Contains id, title, posts


class ChatTitleEventData(TypedDict):
    """CHAT_TITLE event data."""

    new_title: str
    old_title: str


class TransferChatEventData(TypedDict):
    """TRANSFER_CHAT event data."""

    chat: ChatInfo
    to_team: TeamInfo | None
    from_team: TeamInfo | None


class UserDeactivatedEventData(TypedDict):
    """USER_DEACTIVATED event data."""

    user: UserInfo


class NewCommonChatEventData(TypedDict):
    """NEW_COMMON_CHAT event data."""

    # Empty data


class DelCommonChatEventData(TypedDict):
    """DEL_COMMON_CHAT event data."""

    # Empty data


class ChangeSettingsEventData(TypedDict):
    """CHANGE_SETTINGS event data."""

    user_id: int
    change_settings: dict[str, Any]


class NewBranchChatEventData(TypedDict):
    """NEW_BRANCH_CHAT event data."""

    chat_id: int
    parent_id: int
    post_no: int


class ConversionBranchChatEventData(TypedDict):
    """CONVERSION_BRANCH_CHAT event data."""

    chat_id: int
    parent_id: int
    post_no: int


class PostPinnedEventData(TypedDict):
    """POST_PINNED/POST_UNPINNED event data."""

    user_unique_name: str
    user_id: int
    post_no: int


class GroupEventData(TypedDict):
    """GROUP_CREATED/GROUP_UPDATED/GROUP_DELETED/GROUP_LEAVED event data."""

    user: UserInfo
    group: GroupInfo
    role: Literal['user', 'admin', 'delete'] | None
    users: list[UserInfo] | None


class OrgQuitEventData(TypedDict):
    """ORG_QUIT event data."""

    user: UserInfo
    organization: TeamInfo


class OrgMembersEventData(TypedDict):
    """ORG_MEMBERS event data."""

    add_users: list[UserInfo]
    del_users: list[UserInfo]
    organization: TeamInfo


# Main event structure


class PostEvent(TypedDict):
    """Post-event structure."""

    type: Literal[
        'NEW_THREAD',
        'EDIT_THREAD',
        'ENTER_TO_THREAD',
        'QUIT_FROM_THREAD',
        'GROUPSQUIT_FROM_THREAD',
        'WELCOME_TO_ORG',
        'FORK_THREAD',
        'CHAT_TITLE',
        'TRANSFER_CHAT',
        'USER_DEACTIVATED',
        'NEW_COMMON_CHAT',
        'DEL_COMMON_CHAT',
        'CHANGE_SETTINGS',
        'NEW_BRANCH_CHAT',
        'CONVERSION_BRANCH_CHAT',
        'POST_PINNED',
        'POST_UNPINNED',
        'GROUP_CREATED',
        'GROUP_UPDATED',
        'GROUP_DELETED',
        'GROUP_LEAVED',
        'ORG_QUIT',
        'ORG_MEMBERS',
    ]
    data: (
        NewThreadEventData
        | EditThreadEventData
        | EnterToThreadEventData
        | QuitFromThreadEventData
        | list[GroupInfo]
        | WelcomeToOrgEventData
        | ForkThreadEventData
        | ChatTitleEventData
        | TransferChatEventData
        | UserDeactivatedEventData
        | dict[str, Any]  # For empty events
        | ChangeSettingsEventData
        | NewBranchChatEventData
        | ConversionBranchChatEventData
        | PostPinnedEventData
        | GroupEventData
        | OrgQuitEventData
        | OrgMembersEventData
    )


__all__ = [
    'ChangeSettingsEventData',
    'ChatInfo',
    'ChatTitleEventData',
    'ConversionBranchChatEventData',
    'DelCommonChatEventData',
    'EditThreadEventData',
    'EnterToThreadEventData',
    'ForkThreadEventData',
    'GroupEventData',
    'GroupInfo',
    'GroupsQuitFromThreadEventData',
    'NewBranchChatEventData',
    'NewCommonChatEventData',
    'NewThreadEventData',
    'OrgMembersEventData',
    'OrgQuitEventData',
    'PostEvent',
    'PostPinnedEventData',
    'QuitFromThreadEventData',
    'TeamInfo',
    'TransferChatEventData',
    'UserDeactivatedEventData',
    'UserInfo',
    'WelcomeToOrgEventData',
]
