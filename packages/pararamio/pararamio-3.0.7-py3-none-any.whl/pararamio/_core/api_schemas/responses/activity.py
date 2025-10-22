"""Activity API response schemas."""

from __future__ import annotations

from typing import TypedDict


class ActivityResponse(TypedDict):
    """Schema for Activity API response."""

    action: str  # 'online', 'offline', 'away', etc.
    datetime: str  # ISO datetime string


WhoReadResponse = dict[str, str]
"""Mapping of user IDs to timestamps. Example: {"17187": "2025-09-25T10:16:10.170Z"}."""


__all__ = ['ActivityResponse', 'WhoReadResponse']
