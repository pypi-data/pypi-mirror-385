from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Unpack

from pararamio._core.api_schemas.requests import DeferredPostCreateRequest
from pararamio._core.api_schemas.responses import (
    DeferredPostCreateResponse,
    DeferredPostDeleteResponse,
    DeferredPostResponse,
    DeferredPostsResponse,
)
from pararamio._core.models.base import SerializationMixin
from pararamio._core.models.deferred_post import CoreDeferredPost
from pararamio._core.utils.helpers import format_datetime

# Imports from core
from pararamio.exceptions import PararamNotFoundError

from .base import SyncClientMixin

if TYPE_CHECKING:
    from pararamio.client import Pararamio

__all__ = ('DeferredPost',)


class DeferredPost(
    CoreDeferredPost['Pararamio'],
    SyncClientMixin[DeferredPostResponse],
    SerializationMixin['Pararamio', DeferredPostResponse],
):
    """Sync DeferredPost model for scheduled posts."""

    def __init__(self, client: Pararamio, **kwargs: Unpack[DeferredPostResponse]) -> None:
        """Initialize sync deferred post.

        Args:
            client: Pararamio client
            **kwargs: Additional post data including id
        """
        # Ensure id is set
        if 'id' not in kwargs:
            kwargs['id'] = 0

        # Use super() to initialize both parent classes properly
        super().__init__(client, **kwargs)
        # Mark as loaded if we have the required fields
        if 'id' in kwargs:
            self._set_loaded()

    def __str__(self) -> str:
        text = self._data.get('text', None)
        if text is None:
            self.load()
            text = self._data['text']
        return text

    def load(self) -> DeferredPost:
        for post in self.get_deferred_posts(self._client):
            if post.id == self.id:
                self._data = post._data
                return self
        raise PararamNotFoundError(f'Deferred post with id {self.id} not found')

    def delete(self) -> bool:
        """Delete this deferred post.

        Returns:
            True if successful
        """
        url = f'/msg/deferred/{self.id}'
        response = self._client.api_delete(url, response_model=DeferredPostDeleteResponse)
        return response.get('result') == 'OK'

    @classmethod
    def create(
        cls,
        client: Pararamio,
        chat_id: int,
        text: str,
        *,
        time_sending: datetime,
        reply_no: int | None = None,
        quote_range: tuple[int, int] | None = None,
    ) -> DeferredPost:
        """Create a new deferred (scheduled) post.

        Args:
            client: Pararamio client
            chat_id: Target chat ID
            text: Post text
            time_sending: When to send the post
            reply_no: Optional post number to reply to
            quote_range: Optional quote range as (start, end) tuple

        Returns:
            Created DeferredPost object
        """
        url = '/msg/deferred'

        # Use TypedDict for type-safe data construction
        data: DeferredPostCreateRequest = {
            'chat_id': chat_id,
            'text': text,
            'time_sending': format_datetime(time_sending),
        }

        # Add optional fields only if provided
        if reply_no is not None:
            data['reply_no'] = reply_no
        if quote_range is not None:
            data['quote_range'] = quote_range

        response = client.api_post(url, dict(data), response_model=DeferredPostCreateResponse)

        return cls(
            client,
            id=int(response['deferred_post_id']),
            **data,
        )

    @classmethod
    def get_deferred_posts(cls, client: Pararamio) -> list[DeferredPost]:
        """Get all deferred posts for the current user.

        Args:
            client: Pararamio client

        Returns:
            List of DeferredPost objects
        """
        url = '/msg/deferred'
        response = client.api_get(url, response_model=DeferredPostsResponse)
        posts_data = response.get('posts', [])

        return [cls(client, **post_data) for post_data in posts_data]
