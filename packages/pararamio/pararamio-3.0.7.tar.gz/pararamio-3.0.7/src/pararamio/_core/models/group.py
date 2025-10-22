"""Core Group model without lazy loading."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Unpack, cast

from pararamio._core.api_schemas.responses import GroupResponseItem
from pararamio._core.exceptions import PararamioValidationError
from pararamio._core.utils.helpers import parse_iso_datetime

from .base import CoreBaseModel

if TYPE_CHECKING:
    from datetime import datetime

    from pararamio._core._types import FormatterT
__all__ = ('CoreGroup',)


# Attribute formatters for Group
GROUP_ATTR_FORMATTERS: FormatterT = {
    'time_created': parse_iso_datetime,
    'time_updated': parse_iso_datetime,
}


class CoreGroup(CoreBaseModel[GroupResponseItem]):
    """Core Group model with common functionality."""

    _data: GroupResponseItem
    # Group attributes
    id: int
    name: str
    slug: str | None
    description: str | None
    info: str | None
    public: bool
    verified: bool
    users_count: int
    time_created: datetime | None
    time_updated: datetime | None

    _attr_formatters: ClassVar[FormatterT] = GROUP_ATTR_FORMATTERS

    def __init__(  # type: ignore[misc]
        self,
        client: Any | None = None,
        id: int | None = None,
        **kwargs: Unpack[GroupResponseItem],
    ) -> None:
        """Initialize group model with data.

        Args:
            client: Client instance (Pararamio or AsyncPararamio)
            id: Group ID (optional positional or keyword argument)
            **kwargs: Group data
        """
        # Handle positional id
        if id is not None:
            if 'id' in kwargs:
                kwargs.pop('id')
            kwargs['id'] = id
        # Handle ID aliases
        elif 'group_id' in kwargs and 'id' not in kwargs:
            kwargs['id'] = kwargs.pop('group_id')
        self._data = cast('GroupResponseItem', kwargs)

        # Validate that required ID is present
        if 'id' not in self._data:
            raise PararamioValidationError(
                'Group requires id to be present in data. '
                'Cannot create a Group without a valid group identifier.'
            )

        super().__init__(client, **kwargs)  # type: ignore[call-arg]

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CoreGroup):
            return id(other) == id(self)
        return self.id == other.id

    @property
    def members(self) -> list[int]:
        """Get group member user IDs.

        Returns:
            List of user IDs
        """
        users: list[int] = self._data.get('users', [])
        return users if isinstance(users, list) else []
