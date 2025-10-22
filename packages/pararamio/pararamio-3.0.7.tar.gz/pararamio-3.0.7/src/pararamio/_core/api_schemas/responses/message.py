"""API response schemas for message/post operations."""

from __future__ import annotations

from typing import TypedDict


class PostCreateResponse(TypedDict):
    """Response from creating a new post via POST /msg/post/{chat_id}.

    Returns the created post's identifiers.
    """

    uuid: str  # Unique identifier provided by client or generated
    chat_id: int  # Chat ID where post was created
    post_no: int  # Post number assigned to the new post


class PostEditResponse(TypedDict):
    """Response from editing a post via PUT /msg/post/{chat_id}/{post_no}.

    Returns the edited post's identifiers and version.
    """

    uuid: str  # Unique identifier
    chat_id: int  # Chat ID of the post
    post_no: int  # Post number
    ver: int | None  # Version number after edit


class PostDeleteResponse(TypedDict):
    """Response from deleting a post via DELETE /msg/post/{chat_id}/{post_no}.

    Returns the deleted post's identifiers and version.
    """

    uuid: str  # Unique identifier
    chat_id: int  # Chat ID of the post
    post_no: int  # Post number
    ver: int | None  # Version number after deletion


__all__ = [
    'PostCreateResponse',
    'PostDeleteResponse',
    'PostEditResponse',
]
