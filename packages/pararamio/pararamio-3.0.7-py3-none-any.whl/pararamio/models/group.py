from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Literal, Unpack, cast

# Imports from core
from pararamio._core import PararamioHTTPRequestError, PararamNotFoundError
from pararamio._core.api_schemas import (
    GroupEditRequest,
    GroupOperationResponse,
    GroupResponseItem,
    GroupsResponse,
    OkResponse,
)
from pararamio._core.models import CoreGroup, SerializationMixin
from pararamio._core.utils.helpers import join_ids

from .base import SyncClientMixin

if TYPE_CHECKING:
    from pararamio.client import Pararamio

__all__ = ('Group',)


class Group(
    CoreGroup,
    SyncClientMixin[GroupResponseItem],
    SerializationMixin['Pararamio', GroupResponseItem],
):
    """Sync Group model with lazy loading support."""

    def __init__(  # type: ignore[misc]
        self,
        client: Pararamio,
        id: int | None = None,
        **kwargs: Unpack[GroupResponseItem],
    ) -> None:
        """Initialize sync group.

        Args:
            client: Pararamio client
            id: Group ID (optional positional or keyword argument)
            **kwargs: Group data from API response
        """
        super().__init__(client, id, **kwargs)

    def load(self) -> Group:
        """Load full group data from API with caching.

        Returns:
            Self with updated data

        Raises:
            PararamNotFoundError: If the group not found
        """
        # Try to load from cache first if available
        if self._client._cache:
            cache_key = f'group.{self.id}'
            cached = self._client._cache.get(cache_key)
            if cached:
                self._data = cached
                return self

        # Load from API if not cached
        resp = self._client.get_groups_by_ids([self.id])
        if not resp:
            raise PararamNotFoundError(f'Failed to load group {self.id}')
        self._data = next(iter(resp))._data

        # Cache the group data if cache is available
        if self._client._cache:
            cache_key = f'group.{self.id}'
            self._client._cache.set(cache_key, self._data)

        return self

    @classmethod
    def create(
        cls,
        client: Pararamio,
        organization_id: int,
        name: str,
        description: str | None = None,
    ) -> Group:
        """Create a new group.

        Args:
            client: Pararamio client
            organization_id: Organization ID
            name: Group name
            description: Optional group description

        Returns:
            Created group
        """
        resp = client.api_post(
            '/core/group',
            data={
                'organization_id': organization_id,
                'name': name,
                'description': description or '',
            },
            response_model=GroupResponseItem,
        )
        return cls(client, id=resp['group_id'])

    @property
    def members(self) -> list[int]:
        """Get group member user IDs.

        Returns:
            List of user IDs
        """
        # Ensure group data is loaded (it contains the users' list)
        if 'users' not in self._data:
            self.load()

        users: list[int] = self._data.get('users', [])
        return users if isinstance(users, list) else []

    def edit(self, changes: GroupEditRequest, reload: bool = True) -> None:
        """Edit group properties.

        Args:
            changes: Dictionary with fields to change (name is required)
            reload: Whether to reload group data after edit
        """
        # Ensure name is always present (it's required by API)
        if 'name' not in changes:
            # Load current data if needed
            if 'name' not in self._data:
                self.load()
            changes = dict(changes)
            changes['name'] = self._data['name']

        self._client.api_put(
            f'/core/group/{self.id}', data=dict(changes), response_model=GroupOperationResponse
        )
        self._data.update(cast('GroupResponseItem', changes))
        if reload:
            self.load()

    def delete(self) -> bool:
        """Delete this group.

        Returns:
            True if successful
        """
        response = self._client.api_delete(f'/core/group/{self.id}', response_model=OkResponse)
        return bool(response.get('result') == 'OK')

    def remove_member(self, user_id: int, reload: bool = True) -> None:
        """Remove a member from the group.

        Args:
            user_id: User ID to remove
            reload: Whether to reload group data after operation
        """
        url = f'/core/group/{self.id}/users/{user_id}'
        self._client.api_delete(url, response_model=OkResponse)
        self._data['users'] = [user for user in self.users if user != user_id]
        self._data['admins'] = [admin for admin in self.admins if admin != user_id]
        if reload:
            self.load()

    def add_member(self, user_id: int, reload: bool = True) -> None:
        """Add a member to the group.

        Args:
            user_id: User ID to add
            reload: Whether to reload group data after operation
        """
        url = f'/core/group/{self.id}/users/{user_id}'
        self._client.api_post(url, response_model=OkResponse)
        if 'users' not in self._data:
            self._data['users'] = []
        self._data['users'].append(user_id)
        if reload:
            self.load()

    def add_admins(self, admin_ids: list[int], reload: bool = True) -> bool:
        """Add admin users to the group.

        Args:
            admin_ids: List of user IDs to make admins
            reload: Whether to reload group data after operation

        Returns:
            True if successful
        """
        url = f'/core/group/{self.id}/admins/{join_ids(admin_ids)}'
        response = self._client.api_post(url, response_model=OkResponse)
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
                self.load()
        return success

    def get_access(self) -> bool:
        """Check if current user has access to the group.

        Returns:
            True if user has access to the group, False otherwise

        Note:
            Returns True if API returns {"access": "OK"}.
            If the group doesn't exist or user has no access, HTTP 404 will be raised.
        """
        url = f'/core/group/{self.id}/access'
        try:
            result = self._client.api_get(url, response_model=OkResponse)
            return bool(result.get('access') == 'OK')
        except (PararamNotFoundError, PararamioHTTPRequestError):
            return False

    def _check_access(self) -> bool:
        """Internal method for access checking."""
        return self.get_access()

    def leave(self) -> GroupOperationResponse:
        """Leave the group (current user leaves).

        Returns:
            GroupOperationResponse with group_id confirmation
        """
        url = f'/core/group/{self.id}/leave'
        return self._client.api_delete(url, response_model=GroupOperationResponse)

    def get_admins(self) -> list[int]:
        """Get group admin user IDs.

        Returns:
            List of admin user IDs
        """
        # Ensure group data is loaded (it contains the admins' list)
        if 'admins' not in self._data:
            self.load()

        admins: list[int] = self._data.get('admins', [])
        return admins

    def update_settings(self, **kwargs: Unpack[GroupEditRequest]) -> bool:
        """Update group settings.

        Args:
            **kwargs: Settings to update (name, description, etc.)

        Returns:
            True if successful
        """
        if not kwargs:
            return False

        # Ensure name is always present (it's required by API)
        if 'name' not in kwargs:
            # Load current data if needed
            if 'name' not in self._data:
                self.load()
            kwargs['name'] = self._data.get('name', '')

        url = f'/core/group/{self.id}'
        resp = self._client.api_put(url, data=dict(kwargs), response_model=OkResponse)

        # Update local data
        if resp.get('result') == 'OK':
            self._data.update(cast('GroupResponseItem', kwargs))
            return True
        return False

    def add_members_bulk(
        self, user_ids: list[int], role: Literal['users', 'admins'] = 'users'
    ) -> GroupOperationResponse:
        """Add multiple members to the group with the specified role.

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
        ids_str = ','.join(map(str, user_ids))
        url = f'/core/group/{self.id}/{role}/{ids_str}'
        return self._client.api_post(url, response_model=GroupOperationResponse)

    def remove_members_bulk(
        self, user_ids: list[int], role: Literal['users', 'admins'] = 'users'
    ) -> GroupOperationResponse:
        """Remove multiple members from the group with the specified role.

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
        ids_str = ','.join(map(str, user_ids))
        url = f'/core/group/{self.id}/{role}/{ids_str}'
        return self._client.api_delete(url, response_model=GroupOperationResponse)

    @classmethod
    def load_groups(cls, client: Pararamio, ids: Sequence[str | int]) -> list[Group]:
        """Load multiple groups by IDs.

        Args:
            client: Pararamio client
            ids: List of group IDs

        Returns:
            List of Group objects

        Raises:
            ValueError: If more than 100 IDs provided
        """
        if not ids:
            return []
        if len(ids) > 100:
            raise ValueError('too many ids, max 100')
        url = '/core/group?ids=' + ','.join(map(str, ids))
        response = client.api_get(url, response_model=GroupsResponse)
        return [cls(client=client, **data) for data in response.get('groups', [])]
