"""Core User model without lazy loading."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, ClassVar, Generic, TypeVar, Unpack, cast

from pararamio._core.api_schemas.responses import UserResponse, UserSearchResultItem
from pararamio._core.utils.helpers import parse_iso_datetime

from .base import CoreBaseModel

if TYPE_CHECKING:
    from datetime import datetime

    from pararamio._core._types import FormatterT

__all__ = ('CoreUser', 'CoreUserSearchResult')


# Attribute formatters for User
USER_ATTR_FORMATTERS: FormatterT = {
    'time_created': parse_iso_datetime,
    'time_updated': parse_iso_datetime,
}

ClientT = TypeVar('ClientT')


class CoreUser(CoreBaseModel[UserResponse], Generic[ClientT]):
    """Core User model with common functionality."""

    _client: ClientT
    _data: UserResponse
    # User attributes
    id: int
    name: str
    unique_name: str
    name_trans: str | None
    info: str | None
    info_parsed: list[dict[str, Any]] | None
    info_chat: int | None
    email: str
    phonenumber: str | None
    phoneconfirmed: bool
    is_google: bool
    two_step_enabled: bool
    has_password: bool
    active: bool
    deleted: bool
    is_bot: bool
    find_strict: bool
    organizations: list[int]
    time_created: datetime | None
    time_updated: datetime | None
    timezone_offset_minutes: int | None

    _attr_formatters: ClassVar[FormatterT] = USER_ATTR_FORMATTERS

    def __init__(  # type: ignore[misc]
        self,
        client: ClientT,
        user_id: int | None = None,
        **kwargs: Unpack[UserResponse],
    ) -> None:
        """Initialize the user model with data.

        Args:
            client: Client instance (Pararamio or AsyncPararamio)
            user_id: User ID (optional positional or keyword argument)
            **kwargs: User data
        """
        # Handle positional user_id
        if user_id is not None:
            if 'id' in kwargs:
                kwargs.pop('id')
            kwargs['id'] = user_id
        self._data = cast('UserResponse', kwargs)
        super().__init__(client, **kwargs)  # type: ignore[call-arg]

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CoreUser):
            return id(other) == id(self)
        return self.id == other.id

    @staticmethod
    def validate_ids_for_get_by_ids(ids: Sequence[int]) -> str:
        """Validate and prepare IDs for get_by_ids API call.

        Args:
            ids: List of user IDs to validate

        Returns:
            Comma-separated string of IDs for the API URL

        Raises:
            ValueError: If ids' list is empty or contains more than 100 ids
        """
        if len(ids) == 0:
            raise ValueError('ids list cannot be empty')
        if len(ids) > 100:
            raise ValueError('too many ids, max 100')
        return ','.join(map(str, ids))


# Attribute formatters for UserSearchResult
USER_SEARCH_RESULT_ATTR_FORMATTERS: FormatterT = {
    'time_created': parse_iso_datetime,
    'time_updated': parse_iso_datetime,
}


class CoreUserSearchResult(CoreBaseModel[UserSearchResultItem], Generic[ClientT]):
    """Core UserSearchResult model with common functionality."""

    _client: ClientT
    _data: UserSearchResultItem
    # Search result attributes
    id: int
    avatar: str | None
    name: str
    unique_name: str
    custom_name: str | None
    time_created: datetime | None
    time_updated: datetime | None
    other_blocked: bool
    pm_chat_id: int | None
    is_bot: bool

    _attr_formatters: ClassVar[FormatterT] = USER_SEARCH_RESULT_ATTR_FORMATTERS

    def __init__(self, client: ClientT, **kwargs: Unpack[UserSearchResultItem]) -> None:
        """Initialize the user search result model with data.

        Args:
            client: Client instance (Pararamio or AsyncPararamio)
            **kwargs: User search result data
        """
        self._data = kwargs
        super().__init__(client, **kwargs)  # type: ignore[misc, call-arg]

    @property
    def has_pm(self) -> bool:
        """Check if user has PM thread."""
        return self.pm_chat_id is not None

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CoreUserSearchResult):
            return id(other) == id(self)
        return self.id == other.id
