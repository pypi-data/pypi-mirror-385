"""Chat API response schemas."""

from __future__ import annotations

from typing import Any, TypedDict


class ChatResponseItem(TypedDict, total=False):
    """Schema for a single Chat item in API response."""

    # IDs
    id: int
    chat_id: int

    # Type
    type: str  # 'pm' | 'e2e' | 'info' | 'group'

    # Basic info
    title: str
    description: str | None
    custom_title: str | None

    # Type and mode
    history_mode: str  # 'all' | 'since_join'
    pm: bool  # DEPRECATED - Is private message
    e2e: bool  # DEPRECATED - End-to-end encrypted

    # Counts
    posts_count: int
    history_start: int
    last_read_post_no: int

    # Timestamps (as ISO strings from API)
    time_created: str
    time_updated: str
    time_edited: str
    user_time_edited: str | None

    # User IDs
    author_id: int | None
    inviter_id: int | None
    last_msg_author_id: int

    # Organization
    organization_id: int | None
    org_visible: bool

    # Settings
    two_step_required: bool
    posts_live_time: str | None  # timedelta-sec format
    allow_api: bool  # DEPRECATED
    read_only: bool
    parent_id: int | None
    is_common: bool
    is_voice: bool

    # State flags
    tnew: bool
    adm_flag: bool  # DEPRECATED
    is_favorite: bool
    tshow: bool
    mute: str | None  # 'group' | 'total' | None

    # Lists
    pinned: list[int]
    thread_groups: list[int]
    thread_users: list[int]
    thread_admins: list[int]
    thread_users_all: list[int]
    thread_guests: list[int]

    # Last message info
    last_msg_author: str | None  # DEPRECATED
    last_msg_bot_name: str | None  # DEPRECATED
    last_msg_text: str | None  # DEPRECATED
    last_msg: str

    # Additional fields
    meta: dict[str, Any] | None  # DEPRECATED
    keys: dict[str, str] | None  # Only for e2e chats


class ChatsResponse(TypedDict):
    """Schema for Chats API response wrapper."""

    chats: list[ChatResponseItem]


class ChatSearchResponse(TypedDict):
    """Schema for /core/chat/search API response."""

    flt: str
    threads: list[ChatResponseItem]


class KeywordsResponse(TypedDict, total=False):
    """Response from chat keywords endpoint."""

    kw: str  # Keywords' string (optional)


class ChatStatusItem(TypedDict):
    """Status info for a single chat in sync response."""

    posts_count: int  # Total number of posts
    last_read_post_no: int  # Last read post-number
    last_msg: str  # Last message text
    time_updated: str  # ISO datetime string


class ChatSyncResponse(TypedDict):
    """Response from POST /core/chat/sync endpoint."""

    new: list[int]  # New chat IDs
    updated: list[int]  # Updated chat IDs
    removed: list[int]  # Removed chat IDs
    status: dict[str, ChatStatusItem]  # Status updates keyed by chat ID


class ChatListResponse(TypedDict):
    """Response from GET /core/chat/sync endpoint."""

    chats: list[int]  # List of chat IDs


__all__ = [
    'ChatListResponse',
    'ChatResponseItem',
    'ChatSearchResponse',
    'ChatStatusItem',
    'ChatSyncResponse',
    'ChatsResponse',
    'KeywordsResponse',
]
