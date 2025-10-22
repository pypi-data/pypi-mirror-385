"""Abstract client protocol for both sync and async implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, BinaryIO

__all__ = ['AsyncClientProtocol', 'ClientProtocol']


class ClientProtocol(ABC):
    """Abstract base class defining the interface for both sync and async clients."""

    @abstractmethod
    def api_get(self, url: str, **kwargs: Any) -> dict[str, Any]:
        """Make a GET request to the API."""

    @abstractmethod
    def api_post(
        self, url: str, data: dict[str, Any] | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        """Make a POST request to the API."""

    @abstractmethod
    def api_put(
        self, url: str, data: dict[str, Any] | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        """Make a PUT request to the API."""

    @abstractmethod
    def api_delete(
        self, url: str, data: dict[str, Any] | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        """Make a DELETE request to the API."""

    @abstractmethod
    def upload_file(
        self,
        file: BinaryIO | bytes,
        chat_id: int,
        filename: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Upload a file."""

    @property
    @abstractmethod
    def authenticated(self) -> bool:
        """Check if client is authenticated."""


class AsyncClientProtocol(ABC):
    """Abstract base class for async client implementations."""

    @abstractmethod
    async def api_get(self, url: str, **kwargs: Any) -> dict[str, Any]:
        """Make an async GET request to the API."""

    @abstractmethod
    async def api_post(
        self, url: str, data: dict[str, Any] | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        """Make an async POST request to the API."""

    @abstractmethod
    async def api_put(
        self, url: str, data: dict[str, Any] | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        """Make an async PUT request to the API."""

    @abstractmethod
    async def api_delete(
        self, url: str, data: dict[str, Any] | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        """Make an async DELETE request to the API."""

    @abstractmethod
    async def upload_file(
        self,
        file: BinaryIO | bytes,
        chat_id: int,
        filename: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Upload a file asynchronously."""

    @property
    @abstractmethod
    def authenticated(self) -> bool:
        """Check if client is authenticated."""
