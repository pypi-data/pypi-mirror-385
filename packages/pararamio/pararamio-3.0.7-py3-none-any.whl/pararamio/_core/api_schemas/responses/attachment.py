"""Attachment API response schemas."""

from __future__ import annotations

from typing import TypedDict


class AttachmentResponse(TypedDict, total=False):
    """Schema for Attachment API response."""

    # IDs
    guid: str
    name: str

    # Info
    size: int
    mime_type: str

    # Location
    url: str

    # Metadata
    post_no: int | None
    chat_id: int | None


__all__ = ['AttachmentResponse']
