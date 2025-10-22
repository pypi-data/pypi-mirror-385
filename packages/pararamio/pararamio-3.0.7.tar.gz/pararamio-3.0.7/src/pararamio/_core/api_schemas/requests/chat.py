"""Chat API request schemas."""

from __future__ import annotations

from typing import NotRequired, TypedDict


class ChatCreateRequest(TypedDict):
    """Schema for chat creation request."""

    title: str
    description: NotRequired[str]
    organization_id: NotRequired[int | None]
    posts_live_time: NotRequired[str | None]  # timedelta-sec format
    two_step_required: NotRequired[bool]
    history_mode: NotRequired[str]  # 'all' | 'since_join'
    org_visible: NotRequired[bool]
    allow_api: NotRequired[bool]  # deprecated
    read_only: NotRequired[bool]
    mode_read_only: NotRequired[bool]
    users: NotRequired[list[int]]  # For bots only
    groups: NotRequired[list[int]]  # For bots only


class ChatUpdateSettingsRequest(TypedDict):
    """Schema for chat update settings request (PUT /core/chat/{chat_id})."""

    title: NotRequired[str]
    description: NotRequired[str]
    posts_live_time: NotRequired[str | None]  # timedelta-sec format
    two_step_required: NotRequired[bool]
    history_mode: NotRequired[str]  # 'all' | 'since_join', default='all'
    org_visible: NotRequired[bool]
    allow_api: NotRequired[bool]  # default=True
    read_only: NotRequired[bool]


__all__ = ['ChatCreateRequest', 'ChatUpdateSettingsRequest']
