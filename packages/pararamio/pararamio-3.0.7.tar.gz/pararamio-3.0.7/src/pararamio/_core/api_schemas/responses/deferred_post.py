"""DeferredPost API response schemas."""

from __future__ import annotations

from typing import Any, TypedDict


class DeferredPostResponse(TypedDict, total=False):
    """Schema for DeferredPost API response."""

    # IDs
    id: int
    chat_id: int
    user_id: int

    # Content
    text: str
    reply_no: int | None
    quote_range: tuple[int, int] | None

    # Timestamps (as ISO strings from API)
    time_created: str | None
    time_sending: str | None

    # Nested data
    data: dict[str, Any]


class DeferredPostsResponse(TypedDict):
    """Response for GET /msg/deferred."""

    posts: list[DeferredPostResponse]


class DeferredPostDeleteResponse(TypedDict):
    """Response for DELETE /msg/deferred/{id}."""

    result: str  # 'OK'
    deferred_post_id: int


__all__ = ['DeferredPostDeleteResponse', 'DeferredPostResponse', 'DeferredPostsResponse']
