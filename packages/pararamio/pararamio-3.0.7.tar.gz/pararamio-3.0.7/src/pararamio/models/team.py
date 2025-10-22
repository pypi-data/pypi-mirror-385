from __future__ import annotations

from typing import TYPE_CHECKING, Unpack

from pararamio._core import PararamioRequestError
from pararamio._core.api_schemas import (
    OkResponse,
    TeamMemberResponse,
    TeamMembersResponse,
    TeamMemberStatusResponse,
    TeamResponse,
    TeamsResponse,
    TeamStatusesResponse,
    TeamSyncResponse,
)
from pararamio._core.models import (
    CoreTeam,
    CoreTeamMember,
    SerializationMixin,
)

from .base import SyncClientMixin
from .group import Group
from .user import User

if TYPE_CHECKING:
    from pararamio.client import Pararamio
__all__ = (
    'Team',
    'TeamMember',
)


class TeamMember(
    CoreTeamMember['Pararamio'],
    SyncClientMixin[TeamMemberResponse],
    SerializationMixin['Pararamio', TeamMemberResponse],
):
    """Sync TeamMember model."""

    def __init__(
        self,
        client: Pararamio,
        **kwargs: Unpack[TeamMemberResponse],
    ) -> None:
        """Initialize sync team member.

        Args:
            client: Pararamio client
            **kwargs: Team member data
        """
        super().__init__(client, **kwargs)

    @property
    def user(self) -> User:
        return User(client=self.client, id=self.id)

    def get_last_status(self) -> TeamMemberStatusResponse | None:
        url = f'/core/org/status?user_ids={self.id}'
        res = self.client.api_get(url, response_model=TeamStatusesResponse).get('data', [])
        if not res:
            return None
        return res[0]

    def add_status(self, status: str) -> bool:
        url = '/core/org/status'
        data = {
            'org_id': self.org_id,
            'status': status,
            'user_id': self.id,
        }
        res = self.client.api_post(url, data=data, response_model=OkResponse)
        return bool(res.get('result') == 'OK')


class Team(
    CoreTeam['Pararamio'],
    SyncClientMixin[TeamResponse],
    SerializationMixin['Pararamio', TeamResponse],
):
    """Sync Team model with lazy loading support."""

    def __init__(
        self,
        client: Pararamio,
        **kwargs: Unpack[TeamResponse],
    ) -> None:
        """Initialize sync team.

        Args:
            client: Pararamio client
            **kwargs: Team data
        """
        super().__init__(client, **kwargs)

    def create_role(self, name: str, description: str | None = None) -> Group:
        return Group.create(
            self.client, organization_id=self.id, name=name, description=description
        )

    def load(self) -> Team:
        """
        Fetches data from the API for the current organization's ID
        and updates the object's data with caching.

        Requests data from the organization's endpoint using the object's ID,
        then updates the object's data with the response.

        Returns:
            self: The current object instance with updated data.
        """
        # Try to load from cache first if available
        if self.client._cache:
            cache_key = f'team.{self.id}'
            cached = self.client._cache.get(cache_key)
            if cached:
                self._data.update(cached)
                return self

        # Load from API if not cached
        url = f'/core/org?ids={self.id}'
        res = self.client.api_get(url, response_model=TeamsResponse)
        if res and 'orgs' in res and res['orgs']:
            self._data.update(res['orgs'][0])

            # Cache the team data if cache is available
            if self.client._cache:
                cache_key = f'team.{self.id}'
                self.client._cache.set(cache_key, res['orgs'][0])

        return self

    def get_member_info(self, user_id: int) -> TeamMember:
        url = f'/core/org/{self.id}/member_info/{user_id}'
        res = self.client.api_get(url, response_model=TeamMemberResponse)
        if not res:
            raise PararamioRequestError(f'empty response for user {user_id}')
        return TeamMember(self.client, **res)

    def get_members_info(self) -> list[TeamMember]:
        url = f'/core/org/{self.id}/member_info'
        res = self.client.api_get(url, response_model=TeamMembersResponse)
        if res:
            return [TeamMember(self.client, **m) for m in res.get('data', [])]
        return []

    @classmethod
    def get_my_team_ids(cls, client: Pararamio) -> list[int]:
        url = '/core/org/sync'
        res = client.api_get(url, response_model=TeamSyncResponse)
        return res.get('ids', [])

    @classmethod
    def load_teams(cls, client: Pararamio) -> list[Team]:
        """

        Loads teams from the Pararamio client.

        @param client: An instance of the Pararamio client.
        @return: A list of Team objects.
        """
        ids = cls.get_my_team_ids(client)

        if ids:
            url = '/core/org?ids=' + ','.join(map(str, ids))
            res = client.api_get(url, response_model=TeamsResponse)

            if res and 'orgs' in res:
                return [cls(client, **r) for r in res['orgs']]

        return []

    def mark_all_messages_as_read(self) -> bool:
        return self.client.mark_all_messages_as_read(self.id)
