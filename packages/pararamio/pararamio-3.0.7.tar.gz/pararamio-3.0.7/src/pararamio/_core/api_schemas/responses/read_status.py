"""Read status response schema."""

from __future__ import annotations

from typing import TypedDict


class ReadStatusResponse(TypedDict, total=False):
    """Response from /core/chat/{id}/read_status endpoint."""

    last_read_post_no: int
    posts_count: int
    unread_count: int


__all__ = ['ReadStatusResponse']
