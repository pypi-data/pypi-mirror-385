"""Group API response schemas."""

from __future__ import annotations

from typing import TypedDict


class GroupResponseItem(TypedDict, total=False):
    """Schema for a single Group item in API response."""

    # IDs
    id: int
    group_id: int  # Alias for id

    # Names
    name: str
    unique_name: str | None
    slug: str | None

    # Info
    description: str | None
    info: str | None
    email_domain: str | None

    # Settings
    public: bool
    verified: bool
    private: bool | None
    private_visible: bool | None
    adm_flag: bool | None

    # Members
    users: list[int]
    admins: list[int]
    threads: list[int]

    # Organization
    organization_id: int | None

    # Counts
    users_count: int

    # Timestamps (as ISO strings from API)
    time_created: str
    time_updated: str


class GroupsResponse(TypedDict):
    """Schema for Groups API response wrapper."""

    groups: list[GroupResponseItem]


class GroupIdResponse(TypedDict):
    """Response for group operations that return group_id."""

    group_id: int


# Alias for backward compatibility
GroupOperationResponse = GroupIdResponse


class GroupMembersResponse(TypedDict):
    """Response for the group members list."""

    members: list[int]


__all__ = [
    'GroupIdResponse',
    'GroupMembersResponse',
    'GroupOperationResponse',
    'GroupResponseItem',
    'GroupsResponse',
]
