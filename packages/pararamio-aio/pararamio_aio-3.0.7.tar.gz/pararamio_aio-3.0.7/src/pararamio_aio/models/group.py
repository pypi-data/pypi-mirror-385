"""Async Group model."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Literal, Unpack, cast

from pararamio_aio._core.api_schemas import (
    GroupEditRequest,
)
from pararamio_aio._core.api_schemas.responses import (
    GroupIdResponse,
    GroupOperationResponse,
    GroupResponseItem,
    GroupsResponse,
    OkResponse,
)
from pararamio_aio._core.models import CoreGroup, SerializationMixin
from pararamio_aio._core.utils.helpers import join_ids

# Imports from core
from pararamio_aio.exceptions import (
    PararamioHTTPRequestError,
    PararamioRequestError,
    PararamNotFoundError,
)

from .base import AsyncClientMixin

if TYPE_CHECKING:
    from pararamio_aio.client import AsyncPararamio

__all__ = ('Group',)


class Group(
    CoreGroup,
    AsyncClientMixin[GroupResponseItem],
    SerializationMixin['AsyncPararamio', GroupResponseItem],
):
    """Async Group model with explicit loading."""

    def __init__(  # type: ignore[misc]
        self,
        client: AsyncPararamio,
        id: int | None = None,
        **kwargs: Unpack[GroupResponseItem],
    ) -> None:
        """Initialize the async group.

        Args:
            client: AsyncPararamio client
            id: Group ID (optional positional or keyword argument)
            **kwargs: Group data including id
        """
        super().__init__(client, id, **kwargs)

    async def load(self) -> Group:
        """Load full group data from API.

        Returns:
            Self with updated data
        """
        # Try cache first if available
        if self.client._cache:
            cache_key = f'group.{self.id}'
            cached = await self.client._cache.get(cache_key)
            if cached:
                self._data.update(cached)
                self._set_loaded()
                return self

        # Load from API if not in cache
        groups = await self.client.get_groups_by_ids([self.id])
        groups_list = [g async for g in groups]
        if not groups_list:
            raise PararamNotFoundError(f'Group {self.id} not found')

        group_data = groups_list[0]._data

        # Update our data with loaded data
        self._data.update(group_data)
        self._set_loaded()

        # Cache the data if cache is available
        if self.client._cache:
            cache_key = f'group.{self.id}'
            await self.client._cache.set(cache_key, group_data)

        return self

    @property
    def members(self) -> list[int]:
        """Get group member user IDs.

        Returns:
            List of user IDs
        """
        # Ensure group data is loaded (it contains users' list)
        if 'users' not in self._data:
            # Properties cannot be async, so we check if data is loaded
            raise AttributeError('Group data not loaded. Call await group.load() first.')

        users: list[int] = self._data.get('users', [])
        return users

    async def get_admins(self) -> list[int]:
        """Get group admin user IDs.

        Returns:
            List of admin user IDs
        """
        # Ensure group data is loaded (it contains the admins' list)
        if 'admins' not in self._data:
            await self.load()

        admins: list[int] = self._data.get('admins', [])
        return admins

    async def add_member(self, user_id: int, reload: bool = True) -> None:
        """Add a single member to group.

        Args:
            user_id: User ID to add
            reload: Whether to reload group data after operation

        Raises:
            PararamioRequestError: If operation fails
        """
        url = f'/core/group/{self.id}/users/{user_id}'
        response = await self.client.api_post(url, response_model=OkResponse)

        if response.get('result') == 'OK':
            # Update local cache if we have the users' data
            if 'users' in self._data and user_id not in self._data['users']:
                self._data['users'].append(user_id)

            if reload:
                await self.load()
        else:
            raise PararamioRequestError(f'Failed to add user {user_id} to group {self.id}')

    async def remove_member(self, user_id: int, reload: bool = True) -> None:
        """Remove a single member from the group.

        Args:
            user_id: User ID to remove
            reload: Whether to reload group data after operation

        Raises:
            PararamioRequestError: If operation fails
        """
        url = f'/core/group/{self.id}/users/{user_id}'
        response = await self.client.api_delete(url, None, response_model=OkResponse)

        if response.get('result') == 'OK':
            # Update local cache if we have the users' data
            if 'users' in self._data and user_id in self._data['users']:
                self._data['users'].remove(user_id)

            # Also remove from admins if present
            if 'admins' in self._data and user_id in self._data['admins']:
                self._data['admins'].remove(user_id)

            if reload:
                await self.load()
        else:
            raise PararamioRequestError(f'Failed to remove user {user_id} from group {self.id}')

    async def add_admins(self, admin_ids: list[int], reload: bool = True) -> bool:
        """Add admin users to the group.

        Args:
            admin_ids: List of user IDs to make admins
            reload: Whether to reload group data after operation

        Returns:
            True if successful
        """
        url = f'/core/group/{self.id}/admins/{join_ids(admin_ids)}'
        response = await self.client.api_post(url, response_model=OkResponse)
        success = bool(response.get('result') == 'OK')
        if success:
            if 'users' not in self._data:
                self._data['users'] = []
            if 'admins' not in self._data:
                self._data['admins'] = []
            for user_id in admin_ids:
                if user_id not in self._data['users']:
                    self._data['users'].append(user_id)
                if user_id not in self._data['admins']:
                    self._data['admins'].append(user_id)
            if reload:
                await self.load()
        return success

    async def get_access(self) -> bool:
        """Check if current user has access to the group.

        Returns:
            True if user has access to the group, False otherwise

        Note:
            Returns True if API returns {"access": "OK"}.
            If the group doesn't exist or user has no access, HTTP 404 will be raised.
        """
        url = f'/core/group/{self.id}/access'
        try:
            result = await self.client.api_get(url, response_model=OkResponse)
            return result.get('access') == 'OK'
        except (PararamNotFoundError, PararamioHTTPRequestError):
            return False

    async def leave(self) -> GroupOperationResponse:
        """Leave the group (current user leaves).

        Returns:
            GroupOperationResponse with group_id confirmation
        """
        url = f'/core/group/{self.id}/leave'
        return await self.client.api_delete(url, None, response_model=GroupOperationResponse)

    async def add_members_bulk(
        self, user_ids: list[int], role: Literal['users', 'admins'] = 'users'
    ) -> GroupOperationResponse:
        """Add multiple members to the group with specified role.

        Args:
            user_ids: List of user IDs to add
            role: Role to assign ('users' or 'admins')

        Returns:
            GroupOperationResponse with group_id confirmation

        Raises:
            ValueError: If the role is not 'users' or 'admins'
        """
        if role not in ('users', 'admins'):
            raise ValueError(f"Role must be 'users' or 'admins', got '{role}'")
        ids_str = join_ids(user_ids)
        url = f'/core/group/{self.id}/{role}/{ids_str}'
        return await self.client.api_post(url, response_model=GroupOperationResponse)

    async def remove_members_bulk(
        self,
        user_ids: list[int],
        role: Literal['users', 'admins'] = 'users',
    ) -> GroupOperationResponse:
        """Remove multiple members from the group with a specified role.

        Args:
            user_ids: List of user IDs to remove
            role: Role to remove ('users' or 'admins')

        Returns:
            GroupOperationResponse with the operation result

        Raises:
            ValueError: If the role is not 'users' or 'admins'
        """
        if role not in ('users', 'admins'):
            raise ValueError(f"Role must be 'users' or 'admins', got '{role}'")
        ids_str = join_ids(user_ids)
        url = f'/core/group/{self.id}/{role}/{ids_str}'
        return await self.client.api_delete(url, None, response_model=GroupOperationResponse)

    async def update_settings(self, **kwargs: Unpack[GroupEditRequest]) -> bool:
        """Update group settings.

        Args:
            **kwargs: Settings to update (name, description, etc.)

        Returns:
            True if successful
        """
        if not kwargs:
            return False

        url = f'/core/group/{self.id}'
        response = await self.client.api_put(url, dict(kwargs), response_model=GroupIdResponse)

        # Update local data if we got group_id back (success)
        if response.get('group_id') == self.id:
            await self.load()
            return True

        return False

    async def edit(self, changes: GroupEditRequest, reload: bool = True) -> None:
        """Edit group properties.

        Args:
            changes: Dictionary with fields to change (name is required)
            reload: Whether to reload group data after edit
        """
        # Ensure name is always present (it's required by API)
        if 'name' not in changes:
            # Load current data if needed
            if 'name' not in self._data:
                await self.load()
            changes = dict(changes)
            changes['name'] = self._data['name']

        url = f'/core/group/{self.id}'
        await self.client.api_put(url, dict(changes), response_model=GroupOperationResponse)

        self._data.update(cast('GroupResponseItem', changes))

        if reload:
            await self.load()

    async def delete(self) -> bool:
        """Delete this group.

        Returns:
            True if successful
        """
        url = f'/core/group/{self.id}'
        # API returns {...} which we interpret as generic success response
        await self.client.api_delete(url, None, response_model=OkResponse)
        # Since API docs show {...}, we assume it returns some success indicator
        # Check for any response as success (API doesn't specify the exact format)
        return True

    @classmethod
    async def create(
        cls,
        client: AsyncPararamio,
        organization_id: int,
        name: str,
        description: str | None = None,
    ) -> Group:
        """Create a new group.

        Args:
            client: AsyncPararamio client
            organization_id: Organization ID
            name: Group name
            description: Optional group description

        Returns:
            Created group
        """
        resp = await client.api_post(
            '/core/group',
            data={
                'organization_id': organization_id,
                'name': name,
                'description': description or '',
            },
            response_model=GroupResponseItem,
        )
        return cls(client, id=resp['group_id'])

    @classmethod
    async def load_groups(cls, client: AsyncPararamio, ids: Sequence[str | int]) -> list[Group]:
        """Load multiple groups by IDs.

        Args:
            client: AsyncPararamio client
            ids: List of group IDs (max 100)

        Returns:
            List of Group objects
        """
        if not ids:
            return []
        if len(ids) > 100:
            raise ValueError('too many ids, max 100')
        url = '/core/group?ids=' + ','.join(map(str, ids))
        response = await client.api_get(url, response_model=GroupsResponse)
        return [cls(client=client, **data) for data in response.get('groups', [])]
