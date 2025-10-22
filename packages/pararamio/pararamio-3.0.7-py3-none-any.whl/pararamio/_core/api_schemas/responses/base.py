"""Base API response schemas for generic data responses."""

from __future__ import annotations

from typing import Generic, TypedDict, TypeVar

# TypeVar for generic data content
T = TypeVar('T')


class DataResponse(TypedDict, Generic[T]):
    """Generic wrapper for API responses with 'data' field."""

    data: T


class DataListResponse(TypedDict, Generic[T]):
    """Generic wrapper for API responses with 'data' field containing a list."""

    data: list[T]


__all__ = ['DataListResponse', 'DataResponse', 'T']
