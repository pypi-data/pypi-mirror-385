"""Team API response schemas."""

from __future__ import annotations

from typing import TypedDict


class TeamResponse(TypedDict, total=False):
    """Schema for Team API response."""

    # IDs
    id: int
    team_id: int  # Alias for id
    org_id: int  # Organization ID

    # Names
    title: str
    slug: str

    # Info
    description: str | None
    email_domain: str | None

    # Settings
    two_step_required: bool
    default_chat_id: int
    guest_chat_id: int | None
    state: str
    is_active: bool

    # Membership
    is_member: bool
    is_admin: bool
    inviter_id: int | None

    # Lists
    users: list[int]
    admins: list[int]
    groups: list[int]
    guests: list[int]

    # Timestamps (as ISO strings from API)
    time_created: str
    time_updated: str


class TeamMemberResponse(TypedDict, total=False):
    """Schema for Team Member API response."""

    # IDs
    id: int
    org_id: int

    # Info
    email: str
    phonenumber: str | None

    # Settings
    is_admin: bool
    is_member: bool
    two_step_enabled: bool
    inviter_id: int | None

    # Lists
    chats: list[int]
    groups: list[int]

    # State
    state: str
    last_activity: str | None

    # Timestamps (as ISO strings from API)
    time_created: str
    time_updated: str


class TeamMemberStatusResponse(TypedDict, total=False):
    """Schema for Team Member Status API response."""

    # IDs
    id: int
    user_id: int
    setter_id: int
    org_id: int

    # Info
    status: str

    # Timestamp (as ISO string from API)
    time_created: str


class TeamsResponse(TypedDict):
    """Response for GET /core/org with multiple teams."""

    orgs: list[TeamResponse]


class TeamMembersResponse(TypedDict):
    """Response for GET /core/org/{id}/member_info."""

    data: list[TeamMemberResponse]


class TeamStatusesResponse(TypedDict):
    """Response for GET /core/org/status."""

    data: list[TeamMemberStatusResponse]


class TeamSyncResponse(TypedDict):
    """Response for GET /core/org/sync."""

    ids: list[int]


__all__ = [
    'TeamMemberResponse',
    'TeamMemberStatusResponse',
    'TeamMembersResponse',
    'TeamResponse',
    'TeamStatusesResponse',
    'TeamSyncResponse',
    'TeamsResponse',
]
