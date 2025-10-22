"""Core DeferredPost model without lazy loading."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Generic, TypeVar, Unpack

from pararamio._core.api_schemas.responses import DeferredPostResponse
from pararamio._core.utils.helpers import parse_iso_datetime

from .base import CoreBaseModel

if TYPE_CHECKING:
    from datetime import datetime

    from pararamio._core._types import FormatterT

__all__ = ('CoreDeferredPost',)


# Attribute formatters for DeferredPost
DEFERRED_POST_ATTR_FORMATTERS: FormatterT = {
    'time_created': parse_iso_datetime,
    'time_sending': parse_iso_datetime,
}
ClientT = TypeVar('ClientT')


class CoreDeferredPost(CoreBaseModel[DeferredPostResponse], Generic[ClientT]):
    """Core DeferredPost model with common functionality."""

    _client: ClientT
    _data: DeferredPostResponse
    # DeferredPost attributes
    id: int
    chat_id: int
    user_id: int
    text: str
    reply_no: int | None
    quote_range: tuple[int, int] | None
    time_created: datetime | None
    time_sending: datetime | None
    data: dict[str, Any]

    _attr_formatters: ClassVar[FormatterT] = DEFERRED_POST_ATTR_FORMATTERS

    def __init__(
        self,
        client: ClientT,
        **kwargs: Unpack[DeferredPostResponse],
    ) -> None:
        """Initialize the deferred post model with data.

        Args:
            client: Client instance (Pararamio or AsyncPararamio)
            **kwargs: Deferred post data
        """
        self._data = kwargs
        super().__init__(client, **kwargs)  # type: ignore[misc, call-arg]

    def __str__(self) -> str:
        return self.text

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CoreDeferredPost):
            return id(other) == id(self)
        return self.id == other.id
