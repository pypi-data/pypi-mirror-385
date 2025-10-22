"""DeferredPost API request schemas."""

from __future__ import annotations

from typing import NotRequired, TypedDict


class DeferredPostCreateRequest(TypedDict):
    """Schema for deferred post-creation request."""

    chat_id: int
    text: str
    time_sending: str  # ISO datetime string
    reply_no: NotRequired[int | None]
    quote_range: NotRequired[tuple[int, int] | None]


__all__ = ['DeferredPostCreateRequest']
