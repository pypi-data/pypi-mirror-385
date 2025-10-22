"""Bot API response schemas."""

from __future__ import annotations

from typing import Any, TypedDict


class BotMessageResponse(TypedDict):
    """Response from /bot/message and /msg/post/private endpoints."""

    chat_id: int
    post_no: int


class PrivateMessageResponse(TypedDict):
    """Response from /msg/post/private endpoint."""

    chat_id: int
    post_no: int


class TaskStatusResponse(TypedDict):
    """Response from task status endpoint."""

    result: str


class ActivitiesResponse(TypedDict):
    """Response from activity endpoint."""

    activities: list[dict[str, Any]]


__all__ = [
    'ActivitiesResponse',
    'BotMessageResponse',
    'PrivateMessageResponse',
    'TaskStatusResponse',
]
