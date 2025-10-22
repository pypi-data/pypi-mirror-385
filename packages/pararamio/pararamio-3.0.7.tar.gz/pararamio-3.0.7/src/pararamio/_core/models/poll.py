"""Core Poll model without lazy loading."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Unpack

from pararamio._core.api_schemas.responses import PollOptionData, PollResponse
from pararamio._core.utils.helpers import parse_iso_datetime

from .base import CoreBaseModel

if TYPE_CHECKING:
    from datetime import datetime

    from pararamio._core._types import FormatterT

__all__ = ('CorePoll',)


# Attribute formatters for Poll
POLL_ATTR_FORMATTERS: FormatterT = {
    'time_created': parse_iso_datetime,
    'time_closed': parse_iso_datetime,
}


class CorePoll(CoreBaseModel[PollResponse]):
    """Core Poll model with common functionality."""

    _data: PollResponse
    # Poll attributes from API
    vote_uid: str
    user_id: int
    chat_id: int
    anonymous: bool
    mode: str  # 'one' or 'more'
    question: str
    time_expiration: float | None
    options: list[PollOptionData]
    total_user: int
    total_answer: int
    post_no: int | None

    # Additional attributes that a client might add
    description: str | None
    multi_choice: bool | None  # Derived from mode
    closed: bool | None
    time_created: datetime | None
    time_closed: datetime | None

    _attr_formatters: ClassVar[FormatterT] = POLL_ATTR_FORMATTERS

    def __init__(self, client: Any, **kwargs: Unpack[PollResponse]) -> None:
        """Initialize poll model with data.

        Args:
            client: Client instance (Pararamio or AsyncPararamio)
            **kwargs: Poll data
        """
        self._data = kwargs
        super().__init__(client, **kwargs)  # type: ignore[misc, call-arg]

    def __str__(self) -> str:
        return f'Poll {self._data["vote_uid"]}: {self._data["question"]}'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CorePoll):
            return id(other) == id(self)
        return self._data['vote_uid'] == other._data['vote_uid']
