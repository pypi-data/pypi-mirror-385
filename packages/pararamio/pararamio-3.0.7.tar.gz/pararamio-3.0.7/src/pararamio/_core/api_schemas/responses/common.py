"""Common API response schemas used across multiple endpoints."""

from __future__ import annotations

from typing import TypedDict


class OkResponse(TypedDict):
    """Response with result: OK status."""

    result: str  # Should be "OK"


class EmptyResponse(TypedDict, total=False):
    """Empty response (empty dict)."""


class ChatIdResponse(TypedDict):
    """Response containing chat_id."""

    chat_id: int


class GenericResponse(TypedDict, total=False):
    """Generic response that can contain any fields."""

    # This allows any additional fields
    # Use when the exact response structure is dynamic


__all__ = [
    'ChatIdResponse',
    'EmptyResponse',
    'GenericResponse',
    'OkResponse',
]
