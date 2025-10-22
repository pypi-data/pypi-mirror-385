"""Core Team model without lazy loading."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Generic, TypeVar, Unpack

from pararamio_aio._core.api_schemas.responses import (
    TeamMemberResponse,
    TeamResponse,
)
from pararamio_aio._core.utils.helpers import parse_iso_datetime

from .base import CoreBaseModel
from .user import CoreUser

if TYPE_CHECKING:
    from datetime import datetime

    from pararamio_aio._core._types import FormatterT

__all__ = ('CoreTeam', 'CoreTeamMember')


# Attribute formatters for Team
TEAM_ATTR_FORMATTERS: FormatterT = {
    'time_created': parse_iso_datetime,
    'time_updated': parse_iso_datetime,
}

# Attribute formatters for TeamMember
TEAM_MEMBER_ATTR_FORMATTERS: FormatterT = {
    'time_created': parse_iso_datetime,
    'time_updated': parse_iso_datetime,
}

ClientT = TypeVar('ClientT')


class CoreTeamMember(CoreBaseModel[TeamMemberResponse], Generic[ClientT]):
    """Core TeamMember model with common functionality."""

    _client: ClientT
    _data: TeamMemberResponse
    # TeamMember attributes
    id: int
    org_id: int
    email: str
    phonenumber: str | None
    is_admin: bool
    is_member: bool
    two_step_enabled: bool
    inviter_id: int | None
    chats: list[int]
    groups: list[int]
    state: str
    last_activity: str | None
    time_created: str | None
    time_updated: str | None

    _attr_formatters: ClassVar[FormatterT] = TEAM_MEMBER_ATTR_FORMATTERS

    def __init__(self, client: ClientT, **kwargs: Unpack[TeamMemberResponse]) -> None:
        """Initialize team member model with data.

        Args:
            client: Client instance (Pararamio or AsyncPararamio)
            **kwargs: Team member data
        """
        self._data = kwargs
        super().__init__(client, **kwargs)  # type: ignore[misc, call-arg]

    def __str__(self) -> str:
        return self.email or str(self.id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CoreTeamMember | CoreUser):
            return False
        return self.id == other.id


class CoreTeam(CoreBaseModel[TeamResponse], Generic[ClientT]):
    """Core Team model with common functionality."""

    _client: ClientT
    _data: TeamResponse
    # Team attributes - matching TeamResponse fields
    id: int
    title: str
    slug: str
    description: str | None
    email_domain: str | None
    two_step_required: bool
    default_chat_id: int
    guest_chat_id: int | None
    state: str
    is_active: bool
    is_member: bool
    is_admin: bool
    inviter_id: int | None
    # Lists
    users: list[int]
    admins: list[int]
    groups: list[int]
    guests: list[int]
    # Timestamps
    time_created: datetime | None
    time_updated: datetime | None

    _attr_formatters: ClassVar[FormatterT] = TEAM_ATTR_FORMATTERS

    def __init__(self, client: ClientT, **kwargs: Unpack[TeamResponse]) -> None:
        """Initialize team model with data.

        Args:
            client: Client instance (Pararamio or AsyncPararamio)
            **kwargs: Team data
        """
        self._data = kwargs
        super().__init__(client, **kwargs)  # type: ignore[misc, call-arg]

    def __str__(self) -> str:
        return self.title or f'Team({self.id})'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CoreTeam):
            return False
        return self.id == other.id

    def __contains__(self, item: object) -> bool:
        """Check if user is in team.

        Supports checking for User and TeamMember objects.
        """
        if isinstance(item, CoreUser | CoreTeamMember):
            return item.id in self.users
        return False
