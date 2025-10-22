"""Post API request schemas."""

from __future__ import annotations

from typing import NotRequired, TypedDict


class PostCreateRequest(TypedDict):
    """Schema for post-creation request."""

    text: str
    uuid: NotRequired[str]
    reply_no: NotRequired[int]
    quote: NotRequired[str]
    quote_range: NotRequired[tuple[int, int]]
    attachments: NotRequired[list[str]]


class PostSendMessageRequest(TypedDict):
    """Schema for simple message sending (POST /msg/post/{chat_id})."""

    uuid: str
    text: str
    reply_no: NotRequired[int]
    quote: NotRequired[str]


class MarkReadRequest(TypedDict):
    """Schema for marking chat as read."""

    read_all: NotRequired[bool]
    post_no: NotRequired[int]


__all__ = ['MarkReadRequest', 'PostCreateRequest', 'PostSendMessageRequest']
