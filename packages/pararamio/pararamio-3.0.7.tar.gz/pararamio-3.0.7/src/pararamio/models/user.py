from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, TypedDict, Unpack
from urllib.parse import quote

from pararamio._core import PararamMultipleFoundError, PararamNotFoundError
from pararamio._core.api_schemas import (
    UserActivityResponse,
    UserPrivateMessageResponse,
    UserResponseItem,
    UserSearchResponse,
    UsersResponse,
)
from pararamio._core.constants.endpoints import PRIVATE_MESSAGE_URL
from pararamio._core.models import CoreUser, SerializationMixin
from pararamio._core.utils.helpers import unescape_dict

from .activity import Activity, ActivityAction
from .base import SyncClientMixin
from .chat import Chat
from .post import Post

if TYPE_CHECKING:
    from datetime import datetime

    from pararamio._core._types import QuoteRangeT

    from pararamio.client import Pararamio

__all__ = ('User', 'UserInfoParsedItem', 'UserSearchResult')


@dataclass
class UserSearchResult:
    id: int
    avatar: str | None
    name: str
    unique_name: str
    custom_name: str | None
    time_created: str
    time_updated: str
    other_blocked: bool
    pm_thread_id: int | None
    is_bot: bool
    user: User

    @property
    def has_pm(self) -> bool:
        return self.pm_thread_id is not None

    def get_pm_chat(self) -> Chat:
        if self.pm_thread_id is not None:
            return Chat(self.user._client, id=self.pm_thread_id)
        return Chat.create_private_chat(self.user._client, self.id)

    def post(
        self,
        text: str,
        quote_range: QuoteRangeT | None = None,
        reply_no: int | None = None,
    ) -> Post:
        chat = self.get_pm_chat()
        return chat.post(text=text, quote_range=quote_range, reply_no=reply_no)


class UserInfoParsedItem(TypedDict):
    type: str
    value: str


INTERSECTION_KEYS = (
    'id',
    'name',
    'unique_name',
    'time_created',
    'time_updated',
    'is_bot',
)


class User(
    CoreUser['Pararamio'],
    SyncClientMixin[UserResponseItem],
    SerializationMixin['Pararamio', UserResponseItem],
):
    """Sync User model with lazy loading support."""

    def __init__(  # type: ignore[misc]
        self,
        client: Pararamio,
        user_id: int | None = None,
        **kwargs: Unpack[UserResponseItem],
    ) -> None:
        """Initialize sync user.

        Args:
            client: Pararamio client
            user_id: User ID (optional positional or keyword argument)
            **kwargs: User data from API response
        """
        super().__init__(client, user_id, **kwargs)

    def load(self) -> User:
        """Load user data with caching."""
        # Try to load from cache first if available
        if self.client._cache:
            cache_key = f'user.{self.id}'
            cached = self.client._cache.get(cache_key)
            if cached:
                self._data = cached
                return self

        # Load from API if not cached
        resp = list(self.client.get_users_by_ids([self.id]))
        if len(resp) == 0:
            raise PararamNotFoundError(f'User not found: id {self.id}')
        if len(resp) > 1:
            raise PararamMultipleFoundError(
                f'Multiple users found ({len(resp)}) for user id {self.id}'
            )
        self._data = resp[0]._data

        # Cache the user data if cache is available
        if self.client._cache:
            cache_key = f'user.{self.id}'
            self.client._cache.set(cache_key, self._data)

        return self

    @classmethod
    def load_users(cls, client: Pararamio, ids: Sequence[int]) -> list[User]:
        try:
            ids_str = CoreUser.validate_ids_for_get_by_ids(ids)
        except ValueError as e:
            if str(e) == 'ids list cannot be empty':
                return []
            raise
        url = f'/user/list?ids={ids_str}'
        response = client.api_get(url, response_model=UsersResponse)
        return [
            cls(client=client, **unescape_dict(data, ['name']))
            for data in response.get('users', [])
        ]

    def post(
        self,
        text: str,
        quote_range: QuoteRangeT | None = None,
        reply_no: int | None = None,
    ) -> Post:
        for res in self.search(self.client, self.unique_name):
            if res.unique_name == self.unique_name:
                return res.post(text=text, quote_range=quote_range, reply_no=reply_no)
        raise PararamNotFoundError(f'User {self.unique_name} not found')

    def send_private_message(self, text: str) -> Post:
        """Send a private message to this user.

        Args:
            text: Message text

        Returns:
            Created post
        """
        url = PRIVATE_MESSAGE_URL
        response = self._client.api_post(
            url, {'text': text, 'user_id': self.id}, response_model=UserPrivateMessageResponse
        )

        # Load the created post
        return Post(Chat(self._client, id=response['chat_id']), post_no=response['post_no'])

    def __str__(self) -> str:
        if 'name' not in self._data:
            self.load()
        name = self._data.get('name', '')
        return str(name) if name is not None else ''

    @classmethod
    def search(
        cls,
        client: Pararamio,
        query: str,
        include_self: bool = False,
    ) -> list[UserSearchResult]:
        url = f'/user/search?flt={quote(query)}'
        if not include_self:
            url += '&self=false'

        search_response = client.api_get(url, response_model=UserSearchResponse)

        result: list[UserSearchResult] = [
            UserSearchResult(
                id=user_data['id'],
                avatar=user_data.get('avatar'),
                name=user_data['name'],
                unique_name=user_data['unique_name'],
                custom_name=user_data.get('custom_name'),
                time_created=user_data['time_created'],
                time_updated=user_data['time_updated'],
                other_blocked=user_data['other_blocked'],
                pm_thread_id=user_data.get('pm_thread_id'),
                is_bot=user_data['is_bot'],
                user=cls(client, id=user_data['id']),
            )
            for user_data in (
                unescape_dict(data, keys=['name', 'custom_name'])
                for data in search_response.get('users', [])
            )
        ]

        return result

    def _activity_page_loader(self) -> Callable[..., UserActivityResponse]:
        def loader(action: ActivityAction | None = None, page: int = 1) -> UserActivityResponse:
            action_ = action.value if action else ''
            url = f'/activity?user_id={self.id}&action={action_}&page={page}'

            return self.client.api_get(url, response_model=UserActivityResponse)

        return loader

    def get_activity(
        self,
        start: datetime,
        end: datetime,
        actions: list[ActivityAction] | None = None,
    ) -> list[Activity]:
        """Get user activity.

        :param start: Start time
        :param end: End time
        :param actions: List of action types (all actions if None)
        :returns: Activity list
        """
        return Activity.get_activity(self._activity_page_loader(), start, end, actions)
