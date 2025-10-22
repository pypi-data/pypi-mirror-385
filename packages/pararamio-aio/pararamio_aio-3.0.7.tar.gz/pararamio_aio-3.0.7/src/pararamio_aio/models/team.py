"""Async Team model."""

from __future__ import annotations

from typing import TYPE_CHECKING, Unpack

from pararamio_aio._core.api_schemas import TeamMemberStatusResponse
from pararamio_aio._core.api_schemas.responses import (
    OkResponse,
    TeamMemberResponse,
    TeamMembersResponse,
    TeamResponse,
    TeamsResponse,
    TeamStatusesResponse,
    TeamSyncResponse,
)
from pararamio_aio._core.models import CoreTeam, CoreTeamMember, SerializationMixin

# Imports from core
from pararamio_aio.exceptions import PararamioRequestError

from .base import AsyncClientMixin
from .group import Group

if TYPE_CHECKING:
    from pararamio_aio.client import AsyncPararamio

    from .user import User

__all__ = ('Team', 'TeamMember')


class TeamMember(
    CoreTeamMember['AsyncPararamio'],
    AsyncClientMixin[TeamMemberResponse],
    SerializationMixin['AsyncPararamio', TeamMemberResponse],
):
    """Team member model."""

    def __init__(self, client: AsyncPararamio, **kwargs: Unpack[TeamMemberResponse]) -> None:
        """Initialize team member.

        Args:
            client: AsyncPararamio client
            **kwargs: Additional member data including id and org_id
        """
        super().__init__(client, **kwargs)

    async def get_user(self) -> User | None:
        """Get associated User object.

        Returns:
            User object or None
        """
        return await self.client.get_user_by_id(self.id)

    async def get_last_status(self) -> TeamMemberStatusResponse | None:
        """Get last status for this member.

        Returns:
            TeamMemberStatus or None if no status
        """
        url = f'/core/org/status?user_ids={self.id}'
        response = await self.client.api_get(url, response_model=TeamStatusesResponse)
        data = response.get('data', [])

        if not data:
            return None

        return data[0]

    async def add_status(self, status: str) -> bool:
        """Add status for this member.

        Args:
            status: Status text

        Returns:
            True if successful
        """
        url = '/core/org/status'
        data = {
            'org_id': self.org_id,
            'status': status,
            'user_id': self.id,
        }
        response = await self.client.api_post(url, data=data, response_model=OkResponse)
        return response.get('result') == 'OK'


class Team(
    CoreTeam['AsyncPararamio'],
    AsyncClientMixin[TeamResponse],
    SerializationMixin['AsyncPararamio', TeamResponse],
):
    """Async Team model with explicit loading."""

    def __init__(self, client: AsyncPararamio, **kwargs: Unpack[TeamResponse]) -> None:
        """Initialize async team.

        Args:
            client: AsyncPararamio client
            **kwargs: Additional team data including id
        """
        super().__init__(client, **kwargs)

    async def load(self) -> Team:
        """Load full team data from API.

        Returns:
            Self with updated data
        """
        # Try cache first if available
        if self.client._cache:
            cache_key = f'team.{self.id}'
            cached = await self.client._cache.get(cache_key)
            if cached:
                self._data.update(cached)
                self._set_loaded()
                return self

        # Load from API if not in cache
        url = f'/core/org?ids={self.id}'
        response = await self.client.api_get(url, response_model=TeamsResponse)

        if response.get('orgs'):
            team_data = response['orgs'][0]
            self._data.update(team_data)
            self._set_loaded()

            # Cache the data if cache is available
            if self.client._cache:
                cache_key = f'team.{self.id}'
                await self.client._cache.set(cache_key, team_data)

        return self

    async def create_role(self, name: str, description: str | None = None) -> Group:
        """Create a new role (group) in this team.

        Args:
            name: Role name
            description: Role description

        Returns:
            Created Group object
        """
        # Get organization_id from the team (default to 0 if not set)
        org_id_raw = self._data.get('organization_id', 0)
        organization_id = org_id_raw if isinstance(org_id_raw, int) else 0
        return await Group.create(
            self.client,
            organization_id=organization_id,
            name=name,
            description=description,
        )

    async def get_member_info(self, user_id: int) -> TeamMember:
        """Get information about a specific member.

        Args:
            user_id: User ID

        Returns:
            TeamMember object

        Raises:
            PararamioRequestError: If member not found
        """
        url = f'/core/org/{self.id}/member_info/{user_id}'
        response = await self.client.api_get(url, response_model=TeamMemberResponse)

        if not response:
            raise PararamioRequestError(f'empty response for user {user_id}')

        response['org_id'] = self.id
        return TeamMember(self.client, **response)

    async def get_members_info(self) -> list[TeamMember]:
        """Get information about all team members.

        Returns:
            List of TeamMember objects
        """
        url = f'/core/org/{self.id}/member_info'
        response = await self.client.api_get(url, response_model=TeamMembersResponse)

        members = []
        for member_data in response.get('data', []):
            member_data['org_id'] = self.id
            members.append(TeamMember(self.client, **member_data))
        return members

    async def mark_all_messages_as_read(self) -> bool:
        """Mark all messages in this team as read.

        Returns:
            True if successful
        """
        return await self.client.mark_all_messages_as_read(self.id)

    @classmethod
    async def get_my_team_ids(cls, client: AsyncPararamio) -> list[int]:
        """Get IDs of teams the current user belongs to.

        Args:
            client: AsyncPararamio client

        Returns:
            List of team IDs
        """
        url = '/core/org/sync'
        response = await client.api_get(url, response_model=TeamSyncResponse)
        return response.get('ids', [])

    @classmethod
    async def load_teams(cls, client: AsyncPararamio) -> list[Team]:
        """Load all teams for the current user.

        Args:
            client: AsyncPararamio client

        Returns:
            List of Team objects
        """
        ids = await cls.get_my_team_ids(client)

        if not ids:
            return []

        url = '/core/org?ids=' + ','.join(map(str, ids))
        response = await client.api_get(url, response_model=TeamsResponse)

        return [cls(client, **team_data) for team_data in response.get('orgs', [])]
