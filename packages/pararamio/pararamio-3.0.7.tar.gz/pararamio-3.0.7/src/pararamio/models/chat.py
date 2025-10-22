from __future__ import annotations

import logging
import time
from collections.abc import Callable, Iterable, Sequence
from datetime import datetime
from io import BytesIO
from os import PathLike
from typing import (
    TYPE_CHECKING,
    BinaryIO,
    Unpack,
    cast,
)
from urllib.parse import quote

# Imports from core
from pararamio._core import (
    POSTS_LIMIT,
    PararamioLimitExceededError,
    PararamioMethodNotAllowedError,
    PararamioRequestError,
    PararamioValidationError,
    PararamMultipleFoundError,
    PararamNotFoundError,
)
from pararamio._core.api_schemas import (
    ChatCreateRequest,
    ChatIdResponse,
    ChatResponseItem,
    ChatSearchResponse,
    ChatsResponse,
    ChatSyncResponse,
    ChatUpdateSettingsRequest,
    EmptyResponse,
    KeywordsResponse,
    MarkReadRequest,
    OkResponse,
    PostResponseItem,
    PostsResponse,
    ReadStatusResponse,
)
from pararamio._core.models import CoreChat, SerializationMixin
from pararamio._core.models import CoreFile as File
from pararamio._core.utils.helpers import (
    encode_chats_ids,
    format_datetime,
    join_ids,
)
from pararamio._core.utils.lazy_loading import (
    LazyLoadBatch,
    LazyLoadingConfig,
    generate_cache_key,
    get_retry_delay,
)
from pararamio._core.utils.logging_config import (
    LoggerManager,
    get_logger,
)
from pararamio._core.validators import validate_post_load_range

from .attachment import Attachment
from .base import SyncClientMixin
from .post import Post

if TYPE_CHECKING:
    from pararamio._core._types import QuoteRangeT

    from pararamio.client import Pararamio

__all__ = ('Chat',)

# Get component-specific loggers
lazy_logger = get_logger(LoggerManager.LAZY_LOADING)
batch_logger = get_logger(LoggerManager.BATCH_LOGIC)
cache_logger = get_logger(LoggerManager.CACHE)


# validate_post_load_range is now imported from pararamio_core


class Chat(
    CoreChat['Pararamio'],
    SyncClientMixin[ChatResponseItem],
    SerializationMixin['Pararamio', ChatResponseItem],
):
    """Synchronous Chat model with lazy loading, caching, and iterator support.

    Represents a chat/conversation in Pararam.io with comprehensive message handling,
    search capabilities, and member management.

    Features:
        - Lazy loading: Posts load on demand with a cache-first approach
        - Iterator support: Iterate over all posts with automatic batching
        - Smart batching: Optimizes API calls by merging nearby uncached ranges
        - Search: Both lazy (iterator) and batch (list) post-search methods
        - Caching: Optional response caching for better performance

    Examples:
        Create and send messages:
            >>> chat = client.get_chat_by_id(123)
            >>> chat.post('Hello everyone!')

        Iterate over all posts (lazy loading):
            >>> for post in chat:
            ...     print(f'{post.user.name}: {post.text}')

        Load a specific range:
            >>> posts = chat.posts(1, 100)  # Posts 1-100
            >>> recent = chat.posts(-50, -1)  # Last 50 posts

        Search within chat:
            >>> for post in chat.search_posts_lazy('bug fix'):
            ...     print(post.text)

        Organize chats:
            >>> chat.add_tag('important')
            >>> chat.set_keywords('project deadline urgent')
            >>> chat.set_custom_title('Q1 Project')

        Manage members:
            >>> chat.add_users([123, 456])
            >>> chat.add_admins([123])
    """

    def __init__(  # type: ignore[misc]
        self,
        client: Pararamio,
        chat_id: int | None = None,
        **kwargs: Unpack[ChatResponseItem],
    ) -> None:
        """Initialize sync chat.

        Args:
            client: Pararamio client
            chat_id: Chat ID (optional positional or keyword argument)
            **kwargs: Additional chat data
        """
        super().__init__(client, chat_id, **kwargs)

    def __iter__(self) -> Iterable[Post]:
        """Iterate over all posts in the chat using lazy loading with cache-first approach.

        Returns:
            Iterator of Post objects
        """
        # Use the full range from 1 to posts_count
        # If posts_count is not available, use a large default range
        end_post = self.posts_count if self.posts_count else 999999
        return self._lazy_posts_loader(1, end_post)

    def load(self) -> Chat:
        """Load full chat data from API with caching.

        Returns:
            Self with updated data

        Raises:
            PararamioMethodNotAllowedError: If chat has no ID
            PararamNotFoundError: If chat not found
            PararamMultipleFoundError: If multiple chats found
        """
        # Get chat ID from data without triggering lazy loading
        chat_id = self._data.get('chat_id') or self._data.get('id')
        if chat_id is None:
            raise PararamioMethodNotAllowedError(
                f'Load is not allow for new {self.__class__.__name__}'
            )

        # Try to load from cache first if available
        if self._client._cache:
            cache_key = f'chat.{chat_id}'
            cached = self._client._cache.get(cache_key)
            if cached:
                self._data = cached
                self._set_loaded()  # Mark as loaded
                return self

        # Load from API if not cached
        chats = self.load_chats(self._client, [chat_id])
        if len(chats) == 0:
            raise PararamNotFoundError(f'Chat not found: id {chat_id}')
        if len(chats) > 1:
            raise PararamMultipleFoundError(
                f'Multiple chats found ({len(chats)}) for chat id {chat_id}'
            )
        self._data = chats[0]._data

        # Cache the chat data if cache is available
        if self._client._cache:
            cache_key = f'chat.{chat_id}'
            self._client._cache.set(cache_key, self._data)

        self._set_loaded()  # Mark as loaded
        return self

    def update_settings(self, **kwargs: Unpack[ChatUpdateSettingsRequest]) -> bool:
        """
        Updates the attributes of a chat instance with the provided keyword arguments.

        Parameters:
          kwargs: Chat settings to update (title, description, etc)

        Returns:
          True if successful

        Raises:
          Various exceptions based on the response from the API PUT request.
        """
        url = f'/core/chat/{self.id}'
        response = self._client.api_put(url, data=dict(kwargs), response_model=OkResponse)
        if response.get('result') == 'OK':
            # Invalidate cache for this chat
            if self._client._cache:
                cache_key = f'chat.{self.id}'
                self._client._cache.delete(cache_key)
            return True
        return False

    def transfer(self, org_id: int) -> bool:
        url = f'/core/chat/{self.id}/transfer/{org_id}'
        response = self._client.api_post(url, {}, response_model=ChatIdResponse)
        return 'chat_id' in response

    def delete(self) -> bool:
        url = f'/core/chat/{self.id}'
        response = self._client.api_delete(url, response_model=ChatIdResponse)
        if 'chat_id' in response:
            # Invalidate cache for this chat
            if self._client._cache:
                cache_key = f'chat.{self.id}'
                self._client._cache.delete(cache_key)
            return True
        return False

    def hide(self) -> bool:
        url = f'/core/chat/{self.id}/hide'
        response = self._client.api_post(url, {'chat_id': self.id}, response_model=OkResponse)
        return response.get('result') == 'OK'

    def show(self) -> bool:
        url = f'/core/chat/{self.id}/show'
        response = self._client.api_post(url, response_model=OkResponse)
        return response.get('result') == 'OK'

    def favorite(self) -> bool:
        url = f'/core/chat/{self.id}/favorite'
        response = self._client.api_post(url, response_model=OkResponse)
        return response.get('result') == 'OK'

    def unfavorite(self) -> bool:
        url = f'/core/chat/{self.id}/unfavorite'
        response = self._client.api_post(url, response_model=OkResponse)
        return response.get('result') == 'OK'

    def enter(self) -> bool:
        url = f'/core/chat/{self.id}/enter'
        response = self._client.api_post(url, response_model=OkResponse)
        return response.get('result') == 'OK'

    def quit(self) -> bool:
        url = f'/core/chat/{self.id}/quit'
        response = self._client.api_post(url, response_model=OkResponse)
        return response.get('result') == 'OK'

    def add_tag(self, tag_name: str) -> bool:
        """Add a tag to this chat.

        Args:
            tag_name: Name of the tag to add. Must contain only Latin letters (a-z),
                     numbers (0-9), underscores (_) and dashes (-).
                     Must be 2-15 characters long.

        Returns:
            True if the operation was successful, False otherwise.

        Raises:
            PararamioValidationError: If tag name doesn't meet requirements.
        """
        # Validate tag name using the method from CoreChat
        self._validate_tag_name(tag_name)

        url = f'/user/chat/tags?name={quote(tag_name)}&chat_id={self.id}'
        response = self._client.api_put(url, response_model=OkResponse)
        return response.get('result') == 'OK'

    def remove_tag(self, tag_name: str) -> bool:
        """Remove a tag from this chat.

        Args:
            tag_name: Name of the tag to remove. Must contain only Latin letters (a-z),
                     numbers (0-9), underscores (_) and dashes (-).
                     Must be 2-15 characters long.

        Returns:
            True if the operation was successful, False otherwise.

        Raises:
            PararamioValidationError: If tag name doesn't meet requirements.
        """
        # Validate tag name using the method from CoreChat
        self._validate_tag_name(tag_name)

        url = f'/user/chat/tags?name={quote(tag_name)}&chat_id={self.id}'
        response = self._client.api_delete(url, response_model=OkResponse)
        return response.get('result') == 'OK'

    def set_custom_title(self, title: str) -> bool:
        url = f'/core/chat/{self.id}/custom_title'
        response = self._client.api_post(url, {'title': title}, response_model=ChatIdResponse)
        return 'chat_id' in response

    def set_keywords(self, keywords: str) -> bool:
        """Set keywords for this chat.

        Args:
            keywords: Keywords to set for the chat

        Returns:
            True if the operation was successful, False otherwise.
        """
        url = '/msg/keywords'
        response = self._client.api_post(
            url, {'chat_id': self.id, 'kw': keywords}, response_model=EmptyResponse
        )
        # Successful response is an empty dict {}
        return response == {}

    def get_keywords(self) -> str | None:
        """Get keywords for this chat.

        Returns:
            Keywords string if set, None otherwise.
        """
        url = f'/msg/keywords?chat_id={self.id}'
        response = self._client.api_get(url, response_model=KeywordsResponse)
        return response.get('kw')

    def add_users(self, ids: list[int]) -> bool:
        url = f'/core/chat/{self.id}/user/{join_ids(ids)}'
        response = self._client.api_post(url, response_model=ChatIdResponse)
        return 'chat_id' in response

    def delete_users(self, ids: list[int]) -> bool:
        url = f'/core/chat/{self.id}/user/{join_ids(ids)}'
        response = self._client.api_delete(url, response_model=ChatIdResponse)
        return 'chat_id' in response

    def add_admins(self, ids: list[int]) -> bool:
        url = f'/core/chat/{self.id}/admin/{join_ids(ids)}'
        response = self._client.api_post(url, response_model=ChatIdResponse)
        return 'chat_id' in response

    def delete_admins(self, ids: list[int]) -> bool:
        url = f'/core/chat/{self.id}/admin/{join_ids(ids)}'
        response = self._client.api_delete(url, response_model=ChatIdResponse)
        return 'chat_id' in response

    def add_groups(self, ids: list[int]) -> bool:
        url = f'/core/chat/{self.id}/group/{join_ids(ids)}'
        response = self._client.api_post(url, response_model=ChatIdResponse)
        return 'chat_id' in response

    def delete_groups(self, ids: list[int]) -> bool:
        url = f'/core/chat/{self.id}/group/{join_ids(ids)}'
        response = self._client.api_delete(url, response_model=ChatIdResponse)
        return 'chat_id' in response

    def _load_posts_from_api(
        self,
        start_post_no: int = -50,
        end_post_no: int = -1,
        limit: int = POSTS_LIMIT,
    ) -> list[Post]:
        """Load posts from API without any caching - for fresh=True case."""
        url = f'/msg/post?chat_id={self.id}&range={start_post_no}x{end_post_no}'
        _absolute = abs(end_post_no - start_post_no)
        if start_post_no < 0:
            _absolute = +1
        if _absolute >= limit:
            raise PararamioLimitExceededError(f'max post load limit is {limit - 1}')
        response = self._client.api_get(url, response_model=PostsResponse)
        res = response.get('posts', [])
        if not res:
            return []
        return [Post(chat=self, **post) for post in res]

    def _load_posts(
        self,
        start_post_no: int = -50,
        end_post_no: int = -1,
        limit: int = POSTS_LIMIT,
        fresh: bool = False,
    ) -> list[Post]:
        """Internal method to load posts with smart caching.

        Optimization logic:
        - If all posts in cache - return from cache
        - If missing_ranges = 1 range - load only that range
        - If missing_ranges > 1 range - load entire range
          (more efficient to make 1 request than 2+)

        Args:
            start_post_no: Start post-number (negative = from the end)
            end_post_no: End post-number (negative = from the end)
            limit: Maximum number of posts to load
            fresh: If True, ignore cache and load from API

        Returns:
            List of loaded posts
        """
        # If fresh or no cache - load all from API
        if fresh or self._client._cache is None:
            return self._load_posts_from_api(start_post_no, end_post_no, limit)

        # For negative indices, first need to know total post-count
        actual_start = start_post_no
        actual_end = end_post_no

        if start_post_no < 0 or end_post_no < 0:
            # Need to load chat info to get post-count
            # This could be cached separately or fetched from self._data
            total_posts = self.posts_count  # Property of chat

            if start_post_no < 0:
                actual_start = max(1, total_posts + start_post_no + 1)
            if end_post_no < 0:
                actual_end = max(1, total_posts + end_post_no + 1)

        # Check limit
        _absolute = abs(actual_end - actual_start)
        if actual_start < 0:
            _absolute = +1
        if _absolute >= limit:
            raise PararamioLimitExceededError(f'max post load limit is {limit - 1}')

        # Check cache and collect missing_ranges
        cached_posts = {}
        missing_ranges: list[list[int]] = []

        for post_no in range(actual_start, actual_end + 1):
            cache_key = f'chat.{self.id}.post.{post_no}'
            cached_data = self._client._cache.get(cache_key)

            if cached_data:
                cached_posts[post_no] = Post(chat=self, **cached_data)
            else:
                # Add to missing ranges
                if not missing_ranges or post_no != missing_ranges[-1][1] + 1:
                    missing_ranges.append([post_no, post_no])
                else:
                    missing_ranges[-1][1] = post_no

        # If all in cache - return from cache
        if not missing_ranges:
            return [cached_posts[no] for no in sorted(cached_posts.keys())]

        # If missing_ranges has more than one range,
        # it's simpler to load entire range with one request
        if len(missing_ranges) > 1:
            # Load entire range
            url = f'/msg/post?chat_id={self.id}&range={actual_start}x{actual_end}'
            response = self._client.api_get(url, response_model=PostsResponse)
            res = response.get('posts', [])

            posts = []
            for post_data in res:
                post = Post(chat=self, **post_data)
                posts.append(post)

                # Cache each post
                cache_key = f'chat.{self.id}.post.{post.post_no}'
                self._client._cache.set(cache_key, post_data)

            return posts

        # If only one missing_range - load just that
        start, end = missing_ranges[0]
        url = f'/msg/post?chat_id={self.id}&range={start}x{end}'
        response = self._client.api_get(url, response_model=PostsResponse)
        res = response.get('posts', [])

        # Add loaded posts to cached ones
        for post_data in res:
            post = Post(chat=self, **post_data)
            post_no = post.post_no
            cached_posts[post_no] = post

            # Cache it
            cache_key = f'chat.{self.id}.post.{post_no}'
            self._client._cache.set(cache_key, post_data)

        # Return sorted list
        return [cached_posts[no] for no in sorted(cached_posts.keys())]

    def load_posts(
        self,
        start_post_no: int = -50,
        end_post_no: int = -1,
        limit: int = POSTS_LIMIT,
        fresh: bool = False,
    ) -> list[Post]:
        """Load posts from chat.

        Args:
            start_post_no: Start post-number (negative = from the end)
            end_post_no: End post-number (negative = from the end)
            limit: Maximum number of posts to load
            fresh: If True, ignore cache and load from API

        Returns:
            List of loaded posts
        """
        return self._load_posts(start_post_no, end_post_no, limit, fresh)

    def get_recent_posts(self, count: int = 50) -> list[Post]:
        """Get recent posts from chat.

        Args:
            count: Number of recent posts to get

        Returns:
            List of recent posts
        """
        return self.load_posts(start_post_no=-count, end_post_no=-1)

    def send_message(
        self,
        text: str,
        reply_to_post_no: int | None = None,
        quote_text: str | None = None,
    ) -> Post:
        """Send a message to this chat.

        Args:
            text: Message text
            reply_to_post_no: Optional post number to reply to
            quote_text: Optional quote text

        Returns:
            Created post
        """
        return self.post(
            text=text,
            quote_range={'text': quote_text} if quote_text else None,
            reply_no=reply_to_post_no,
        )

    def create_post(
        self,
        text: str,
        reply_to_post_no: int | None = None,
        quote_text: str | None = None,
    ) -> Post:
        """Create post in chat (alias for send_message).

        Args:
            text: Post text
            reply_to_post_no: Optional post number to reply to
            quote_text: Optional quote text

        Returns:
            Created post
        """
        return self.send_message(text, reply_to_post_no, quote_text)

    def get_post(self, post_no: int) -> Post:
        """Get post by number.

        Args:
            post_no: Post number to get

        Returns:
            Post object
        """
        posts = self.load_posts(start_post_no=post_no, end_post_no=post_no)
        return posts[0]

    @staticmethod
    def _assign_batch_to_uncached_posts(
        start: int,
        end: int,
        batch: LazyLoadBatch,
        config: LazyLoadingConfig,
        cache_check: Callable[[str], bool],
        post_to_batch: dict[int, LazyLoadBatch | None],
    ) -> None:
        """Assign batch to uncached posts in range."""
        for post_no in range(start, end + 1):
            cache_key = generate_cache_key(config.cache_key_template, config.chat_id, post_no)
            if not cache_check(cache_key):
                post_to_batch[post_no] = batch

    @staticmethod
    def _assign_split_batches(
        range_start: int,
        range_end: int,
        config: LazyLoadingConfig,
        cache_check: Callable[[str], bool],
        post_to_batch: dict[int, LazyLoadBatch | None],
    ) -> None:
        """Split large range into multiple batches and assign to posts."""
        current = range_start
        while current <= range_end:
            batch_start = current
            batch_end = min(current + config.per_request - 1, range_end)
            batch = LazyLoadBatch(batch_start, batch_end)

            Chat._assign_batch_to_uncached_posts(
                batch_start, min(batch_end, range_end), batch, config, cache_check, post_to_batch
            )

            current = batch_end + 1

    @staticmethod
    def _validate_batch_size(batch_size: int, limit: int) -> None:
        """Validate that batch size doesn't exceed the limit.

        Args:
            batch_size: Size of the batch
            limit: Maximum allowed batch size

        Raises:
            ValueError: If batch size exceeds limit
        """
        if batch_size > limit:
            raise ValueError(f'Batch size {batch_size} exceeds POSTS_LIMIT {limit}')

    @staticmethod
    def _calculate_lazy_batches(
        config: LazyLoadingConfig,
        cache_check: Callable[[str], bool],
    ) -> Iterable[tuple[int, LazyLoadBatch | None]]:
        """Calculate batches for lazy loading with cache-first approach and smart merging.

        This generator yields tuples of (post_no, batch) where:
        - If post is in cache: yields (post_no, None)
        - If post needs loading: yields (post_no, LazyLoadBatch)

        The algorithm groups consecutive missing posts into batches and merges close batches
        for efficient loading. If the gap between two batches is smaller than per_request/2,
        they will be merged into a single batch to reduce API calls.

        Args:
            config: Lazy loading configuration
            cache_check: Function to check if a key exists in cache

        Yields:
            Tuples of (post_number, batch_or_none)
        """
        batch_logger.debug(
            'Calculating lazy batches for range [%d, %d], batch_size=%d',
            config.start_post_no,
            config.end_post_no,
            config.per_request,
        )

        # First, collect all missing ranges
        missing_ranges: list[tuple[int, int]] = []
        current = config.start_post_no

        while current <= config.end_post_no:
            cache_key = generate_cache_key(config.cache_key_template, config.chat_id, current)

            if not cache_check(cache_key):
                # Start of a missing range
                range_start = current
                range_end = current

                # Find the end of this missing range
                while current + 1 <= config.end_post_no:
                    next_key = generate_cache_key(
                        config.cache_key_template, config.chat_id, current + 1
                    )
                    if cache_check(next_key):
                        break
                    current += 1
                    range_end = current

                missing_ranges.append((range_start, range_end))
                batch_logger.debug(
                    'Found missing range: [%d, %d] (%d posts)',
                    range_start,
                    range_end,
                    range_end - range_start + 1,
                )

            current += 1

        # Now merge close ranges and split into batches
        if not missing_ranges:
            # All posts are cached
            batch_logger.debug('All posts in range are cached, no batches needed')
            for post_no in range(config.start_post_no, config.end_post_no + 1):
                yield post_no, None
            return

        batch_logger.debug('Found %d missing ranges to process', len(missing_ranges))

        # Merge close ranges (gap less than per_request)
        merge_threshold = config.per_request
        merged_ranges: list[tuple[int, int]] = []

        for start, end in missing_ranges:
            if merged_ranges and start - merged_ranges[-1][1] - 1 < merge_threshold:
                # Merge with previous range
                old_range = merged_ranges[-1]
                merged_ranges[-1] = (merged_ranges[-1][0], end)
                batch_logger.debug(
                    'Merging ranges [%d, %d] + [%d, %d] -> [%d, %d]',
                    old_range[0],
                    old_range[1],
                    start,
                    end,
                    merged_ranges[-1][0],
                    merged_ranges[-1][1],
                )
            else:
                # Add as new range
                merged_ranges.append((start, end))
                batch_logger.debug('Adding new range: [%d, %d]', start, end)

        # Now create batches from merged ranges and yield
        post_to_batch: dict[int, LazyLoadBatch | None] = {}

        # Mark all posts - cached posts get None, others will be set later
        for post_no in range(config.start_post_no, config.end_post_no + 1):
            cache_key = generate_cache_key(config.cache_key_template, config.chat_id, post_no)
            if cache_check(cache_key):
                post_to_batch[post_no] = None
            else:
                # Will be set to a batch later
                post_to_batch[post_no] = None  # Temporary

        batch_logger.debug(
            'After merging: %d ranges (was %d)', len(merged_ranges), len(missing_ranges)
        )

        # Create batches for merged ranges
        batch_count = 0
        for range_start, range_end in merged_ranges:
            # Ensure the range doesn't exceed POSTS_LIMIT
            range_size = range_end - range_start + 1
            if range_size > config.per_request:
                # Split into multiple batches
                num_splits = (range_size + config.per_request - 1) // config.per_request
                batch_logger.debug(
                    'Range [%d, %d] too large (%d posts), splitting into %d batches',
                    range_start,
                    range_end,
                    range_size,
                    num_splits,
                )
                Chat._assign_split_batches(
                    range_start, range_end, config, cache_check, post_to_batch
                )
                batch_count += num_splits
            else:
                # Single batch for the entire range
                batch = LazyLoadBatch(range_start, range_end)
                batch_count += 1
                batch_logger.debug(
                    'Creating batch %d: [%d, %d] (%d posts)',
                    batch_count,
                    range_start,
                    range_end,
                    range_size,
                )
                Chat._assign_batch_to_uncached_posts(
                    range_start, range_end, batch, config, cache_check, post_to_batch
                )

        batch_logger.info(
            'Batch calculation complete: %d total batches for %d posts',
            batch_count,
            config.end_post_no - config.start_post_no + 1,
        )

        # Yield results in order
        for post_no in range(config.start_post_no, config.end_post_no + 1):
            yield post_no, post_to_batch[post_no]

    def _lazy_posts_loader(  # pylint: disable=too-many-statements
        self, start_post_no: int = -50, end_post_no: int = -1, per_request: int = POSTS_LIMIT
    ) -> Iterable[Post]:
        """Lazy iterator for posts with cache-first approach and retry logic.

        Args:
            start_post_no: Starting post-number (negative = from the end)
            end_post_no: Ending post-number (negative = from the end)
            per_request: Number of posts to load per batch request

        Yields:
            Post objects, either from cache or loaded from API
        """
        start_time = time.time()
        lazy_logger.debug(
            'Starting lazy posts loader for chat %s: range [%d, %d], batch_size=%d',
            self.id,
            start_post_no,
            end_post_no,
            per_request,
        )

        # Handle negative indices
        if start_post_no < 0 or end_post_no < 0:
            total_posts = self.posts_count or 0
            if start_post_no < 0:
                start_post_no = max(1, total_posts + start_post_no + 1)
            if end_post_no < 0:
                end_post_no = max(1, total_posts + end_post_no + 1)
            lazy_logger.debug(
                'Resolved negative indices: [%d, %d] (total_posts=%d)',
                start_post_no,
                end_post_no,
                total_posts,
            )

        # Validate range after resolving negative indices
        validate_post_load_range(start_post_no, end_post_no)

        # Configure lazy loading
        config = LazyLoadingConfig(
            start_post_no=start_post_no,
            end_post_no=end_post_no,
            per_request=per_request,
            cache_key_template='chat.{chat_id}.post.{post_no}',
            chat_id=self.id,
        )

        # Check if cache is available
        if not self._client._cache:
            lazy_logger.debug('No cache available, using direct batch loading')
            # No cache - just load everything in batches
            current = start_post_no
            batch_count = 0
            while current <= end_post_no:
                batch_end = min(current + per_request - 1, end_post_no)
                batch_count += 1
                lazy_logger.debug('Loading batch %d: [%d, %d]', batch_count, current, batch_end)

                # Retry logic for API failures
                posts = []
                for attempt in range(3):
                    try:
                        batch_start_time = time.time()
                        posts = self._load_posts(current, batch_end)
                        batch_duration = time.time() - batch_start_time
                        lazy_logger.debug(
                            'Loaded batch %d: %d posts in %.3fs',
                            batch_count,
                            len(posts),
                            batch_duration,
                        )
                        break
                    except Exception as e:
                        if attempt == 2:  # Last attempt
                            lazy_logger.error(
                                'Failed to load batch %d after 3 attempts: %s', batch_count, str(e)
                            )
                            raise  # Re-raise the exception
                        delay = get_retry_delay(attempt)
                        lazy_logger.warning(
                            'Batch %d load failed (attempt %d/3), retrying after %.2fs: %s',
                            batch_count,
                            attempt + 1,
                            delay,
                            str(e),
                        )
                        time.sleep(delay)

                yielded = 0
                for post in posts:
                    if start_post_no <= post.post_no <= end_post_no:
                        yielded += 1
                        yield post
                lazy_logger.debug('Yielded %d posts from batch %d', yielded, batch_count)

                current = batch_end + 1

            total_duration = time.time() - start_time
            lazy_logger.info(
                'Completed lazy loading (no cache): %d batches in %.3fs',
                batch_count,
                total_duration,
            )
            return

        # Use cache-first algorithm
        lazy_logger.debug('Using cache-first lazy loading algorithm')

        def cache_check(key: str) -> bool:
            exists = self._client._cache.get(key) is not None if self._client._cache else False
            # Only log in debug mode since this is called in a tight loop
            if cache_logger.isEnabledFor(logging.DEBUG):
                cache_logger.debug('Cache check for %s: %s', key, 'HIT' if exists else 'MISS')
            return exists

        current_batch = None
        loaded_posts = {}
        cache_hits = 0
        cache_misses = 0
        batches_loaded = 0

        for post_no, batch_info in self._calculate_lazy_batches(config, cache_check):
            if batch_info is None:
                # Post is in cache
                cache_key = f'chat.{self.id}.post.{post_no}'
                cached = self._client._cache.get(cache_key)
                if cached:
                    cache_hits += 1
                    yield Post(chat=self, **cached)
            else:
                # Need to load a batch
                cache_misses += 1
                if batch_info != current_batch:
                    # New batch to load
                    current_batch = batch_info
                    batches_loaded += 1
                    batch_logger.debug(
                        'Loading batch %d: [%d, %d] (size=%d)',
                        batches_loaded,
                        batch_info.start,
                        batch_info.end,
                        batch_info.end - batch_info.start + 1,
                    )

                    # Retry logic for API failures
                    for attempt in range(3):
                        try:
                            # Ensure we never exceed POSTS_LIMIT
                            batch_size = batch_info.end - batch_info.start + 1
                            self._validate_batch_size(batch_size, POSTS_LIMIT)

                            batch_start_time = time.time()
                            posts = self._load_posts(batch_info.start, batch_info.end)
                            batch_duration = time.time() - batch_start_time

                            loaded_posts = {p.post_no: p for p in posts}
                            batch_logger.debug(
                                'Loaded batch %d: %d posts in %.3fs',
                                batches_loaded,
                                len(posts),
                                batch_duration,
                            )
                            break
                        except Exception as e:
                            if attempt == 2:  # Last attempt
                                batch_logger.error(
                                    'Failed to load batch %d after 3 attempts: %s',
                                    batches_loaded,
                                    str(e),
                                )
                                raise  # Re-raise the exception
                            delay = get_retry_delay(attempt)
                            batch_logger.warning(
                                'Batch %d load failed (attempt %d/3), retrying after %.2fs: %s',
                                batches_loaded,
                                attempt + 1,
                                delay,
                                str(e),
                            )
                            time.sleep(delay)

                # Yield the post from loaded batch
                if post_no in loaded_posts:
                    yield loaded_posts[post_no]

        # Log final statistics
        total_duration = time.time() - start_time
        total_posts = cache_hits + cache_misses
        hit_rate = (cache_hits / total_posts * 100) if total_posts > 0 else 0

        lazy_logger.info(
            'Lazy loading: %d posts (%.1f%% cache hit), %d batches, %.3fs',
            total_posts,
            hit_rate,
            batches_loaded,
            total_duration,
        )

        if lazy_logger.isEnabledFor(logging.DEBUG):
            lazy_logger.debug(
                'Cache stats: %d hits, %d misses, %d batches',
                cache_hits,
                cache_misses,
                batches_loaded,
            )

    def posts(
        self,
        start_post_no: int = -50,
        end_post_no: int = -1,
    ) -> list[Post]:
        """Load posts in a specific range with cache-first lazy loading.

        Uses smart batching to optimize API calls by merging nearby uncached ranges.
        Supports both positive (from the start) and negative (from the end) indexing.

        Args:
            start_post_no: Starting post-number (default: -50 for last 50 posts).
                Negative values count from the end.
            end_post_no: Ending post-number (default: -1 for last post).
                Negative values count from the end.

        Returns:
            List of Post objects in the specified range.

        Examples:
            >>> chat.posts(1, 100)  # First 100 posts
            >>> chat.posts(-50, -1)  # Last 50 posts
            >>> chat.posts(100, 200)  # Posts 100-200

        Notes:
            - Checks cache before making API calls
            - Merges nearby uncached ranges into optimal batches
            - Maximum batch size: POSTS_LIMIT (default 100)
            - Retry logic: 3 attempts with exponential backoff (0.5 s, 1 s, 2 s)
        """
        if start_post_no == end_post_no:
            start_post_no = end_post_no - 1
        return list(self._lazy_posts_loader(start_post_no=start_post_no, end_post_no=end_post_no))

    def lazy_posts_load(
        self,
        start_post_no: int = -50,
        end_post_no: int = -1,
        per_request: int = POSTS_LIMIT,
    ) -> list[Post]:
        return list(
            self._lazy_posts_loader(
                start_post_no=start_post_no,
                end_post_no=end_post_no,
                per_request=per_request,
            )
        )

    def read_status(self, post_no: int) -> bool:
        return self.mark_read(post_no)

    def mark_read(self, post_no: int | None = None) -> bool:
        url = f'/msg/lastread/{self.id}'
        data: MarkReadRequest = {'read_all': True}
        if post_no is not None:
            data = {'post_no': post_no}
        # The mark_read endpoint returns a different structure than ReadStatusResponse
        response = self._client.api_post(url, dict(data), response_model=ReadStatusResponse)
        if 'last_read_post_no' in response:
            self._data['last_read_post_no'] = response['last_read_post_no']
        if 'posts_count' in response:
            self._data['posts_count'] = response['posts_count']
        return True

    def post(
        self,
        text: str,
        quote_range: QuoteRangeT | None = None,
        reply_no: int | None = None,
        attachments: list[Attachment] | None = None,
    ) -> Post:
        if self.id is None:
            raise ValueError('can not post file to new chat')
        _attachments = [
            self.upload_file(
                attachment.fp,
                filename=attachment.guess_filename,
                content_type=attachment.guess_content_type,
                reply_no=reply_no,
            )
            for attachment in (attachments or [])
        ]
        return Post.create(
            self,
            text=text,
            reply_no=reply_no,
            quote=cast('str', quote_range['text']) if quote_range else None,
            attachments=[attach.guid for attach in _attachments],
        )

    def upload_file(
        self,
        file: str | BytesIO | BinaryIO | PathLike[str],
        *,
        filename: str | None = None,
        content_type: str | None = None,
        reply_no: int | None = None,
        quote_range: str | None = None,
    ) -> File:
        if self.id is None:
            raise ValueError('can not upload file to new chat')
        if not isinstance(file, str | PathLike) and not filename:
            raise PararamioValidationError('can not determine filename for BinaryIO')
        attachment = Attachment(file, filename=filename, content_type=content_type)
        return self._client.upload_file(
            file=attachment.fp,
            chat_id=self.id,
            filename=attachment.guess_filename,
            content_type=attachment.guess_content_type,
            reply_no=reply_no,
            quote_range=quote_range,
        )

    @classmethod
    def load_chats(cls, client: Pararamio, ids: Sequence[int]) -> list[Chat]:
        url = f'/core/chat?ids={join_ids(ids)}'
        response = client.api_get(url, response_model=ChatsResponse)
        if response and 'chats' in response:
            return [cls(client, **data) for data in response.get('chats', [])]
        raise PararamioRequestError(f'failed to load data for chats ids: {",".join(map(str, ids))}')

    @classmethod
    def search_posts_lazy(
        cls,
        client: Pararamio,
        q: str,
        *,
        order_type: str = 'time',
        chat_ids: list[int] | None = None,
        max_results: int | None = None,
        per_page: int = POSTS_LIMIT,
    ) -> Iterable[Post]:
        """Search for posts with lazy loading pagination.

        This method returns an iterator that fetches posts page by page,
        yielding them one at a time. This is useful for processing large
        search results without loading everything into memory.

        Args:
            client: Pararamio client
            q: Search query
            order_type: Order type ('time' or 'relevance')
            chat_ids: Optional list of chat IDs to filter by
            max_results: Maximum total results to fetch (None = unlimited)
            per_page: Number of posts to fetch per page (default: POSTS_LIMIT)

        Yields:
            Post objects one at a time

        Example:
            >>> for post in Chat.search_posts_lazy(client, 'hello', max_results=100):
            ...     print(post.text)
        """
        page = 1
        total_yielded = 0
        created_chats = {}

        lazy_logger.debug(
            'Starting lazy search: query=%r, order=%s, chat_ids=%s, max_results=%s',
            q,
            order_type,
            chat_ids,
            max_results,
        )

        while True:
            # Calculate how many results to fetch in this batch
            batch_limit = per_page
            if max_results:
                remaining = max_results - total_yielded
                if remaining <= 0:
                    lazy_logger.debug('Reached max_results limit: %d', max_results)
                    break
                batch_limit = min(batch_limit, remaining)

            lazy_logger.debug('Fetching page %d with limit %d', page, batch_limit)

            url = cls._build_search_url(
                q=q,
                order_type=order_type,
                page=page,
                chat_ids=chat_ids,
                limit=batch_limit,
            )

            try:
                response = client.api_get(url, response_model=PostsResponse)
                if 'posts' not in response:
                    lazy_logger.warning('No posts in response for page %d', page)
                    break

                posts = response['posts']
                if not posts:
                    lazy_logger.debug('No more posts found at page %d', page)
                    break

                lazy_logger.debug('Received %d posts from page %d', len(posts), page)

                # Yield posts one by one
                for post_data in posts:
                    # API returns thread_id in search results, not chat_id
                    _chat_id = post_data.get('thread_id') or post_data.get('chat_id')
                    post_no = post_data['post_no']

                    if _chat_id not in created_chats:
                        created_chats[_chat_id] = cls(client, id=_chat_id)

                    yield Post(created_chats[_chat_id], post_no=post_no)
                    total_yielded += 1

                    if max_results and total_yielded >= max_results:
                        lazy_logger.debug('Reached max_results: %d', max_results)
                        return

                # If we got fewer results than requested, we're done
                if len(posts) < batch_limit:
                    lazy_logger.debug(
                        'Received fewer posts than requested (%d < %d), stopping',
                        len(posts),
                        batch_limit,
                    )
                    break

                page += 1

            except PararamioRequestError as e:
                lazy_logger.error('Search failed at page %d: %s', page, e)
                break

    @classmethod
    def search_posts(
        cls,
        client: Pararamio,
        q: str,
        *,
        order_type: str = 'time',
        page: int = 1,
        chat_ids: list[int] | None = None,
        limit: int | None = POSTS_LIMIT,
    ) -> tuple[int, Iterable[Post]]:
        """Search for posts.

        Args:
            client: Pararamio client
            q: Search query
            order_type: Order type ('time' or 'relevance')
            page: Page number (1-based)
            chat_ids: Optional list of chat IDs to filter by
            limit: Maximum number of results

        Returns:
            Tuple of (total_count, posts)
        """
        url = cls._build_search_url(
            q=q,
            order_type=order_type,
            page=page,
            chat_ids=chat_ids,
            limit=limit,
        )

        response = client.api_get(url, response_model=PostsResponse)
        res = response  # Keep res variable for compatibility
        if 'posts' not in res:
            raise PararamioRequestError('failed to perform search')
        created_chats = {}

        def create_post(data: PostResponseItem) -> Post:
            nonlocal created_chats
            # API returns thread_id in search results, not chat_id
            _chat_id = data.get('thread_id') or data.get('chat_id')
            if _chat_id is None:
                raise PararamioRequestError('thread_id/chat_id missing in search results')
            post_no = data['post_no']
            if _chat_id not in created_chats:
                created_chats[_chat_id] = cls(client, id=_chat_id)
            return Post(created_chats[_chat_id], post_no=post_no)

        posts = res['posts']
        # Apply client-side limit if requested limit is less than API minimum (10)
        if limit and limit < 10 and limit < len(posts):
            posts = posts[:limit]

        count = res.get('count')
        if count is None:
            count = len(posts)
        return count, (create_post(post) for post in posts)

    @classmethod
    def create(
        cls,
        client: Pararamio,
        **kwargs: Unpack[ChatCreateRequest],
    ) -> Chat:
        """Creates a new chat instance in the Pararamio application.

        Args:
            cls: The class itself (implicit first argument for class methods).
            client (Pararamio): An instance of the Pararamio client.
            **kwargs: ChatCreateRequest parameters including
                - title: The title of the chat.
                - description: A description of the chat (optional).
                - users: A list of user IDs to be added to the chat (optional).
                - groups: A list of group IDs to be added to the chat (optional).
                - organization_id: Organization ID (optional).
                - posts_live_time: Posts live time (optional).
                - two_step_required: Whether two-step auth is required (optional).
                - history_mode: History mode setting (optional).
                - org_visible: Organization visibility (optional).
                - allow_api: Whether API access is allowed (optional).
                - read_only: Whether chat is read-only (optional).

        Returns:
            Chat: An instance of the Chat class representing the newly created chat.
        """
        data = CoreChat.prepare_create_chat_data(**kwargs)

        response = client.api_post('/core/chat', data, response_model=ChatIdResponse)
        id_: int = response['chat_id']
        return cls(client, id=id_)

    @classmethod
    def create_private_chat(cls, client: Pararamio, user_id: int) -> Chat:
        url = f'/core/chat/pm/{user_id}'
        response = client.api_post(url, response_model=ChatIdResponse)
        id_: int = response['chat_id']
        return cls(client, id=id_)

    @staticmethod
    def sync_chats(
        client: Pararamio,
        chats_ids: list[tuple[int, int, int]],
        sync_time: datetime | None = None,
    ) -> ChatSyncResponse:
        url = '/core/chat/sync'
        data = {'ids': encode_chats_ids(chats_ids)}
        if sync_time:
            data['sync_time'] = format_datetime(sync_time)
        return client.api_post(url, data, response_model=ChatSyncResponse)

    @classmethod
    def search(
        cls,
        client: Pararamio,
        query: str,
        *,
        chat_type: str = 'all',
        visibility: str = 'all',
    ) -> list[Chat]:
        """Search for chats.

        Args:
            client: Pararamio client instance
            query: Search string
            chat_type: Filter by type (all, private, group, etc.)
            visibility: Filter by visibility (all, visible, hidden)

        Returns:
            List of Chat objects matching the search criteria
        """
        url = f'/core/chat/search?flt={quote(query)}&type={chat_type}&visibility={visibility}'
        # Search endpoint returns threads, not chats
        response = client.api_get(url, response_model=ChatSearchResponse)

        # Create Chat objects from the thread data
        threads = response.get('threads', [])
        return [cls(client, **thread_data) for thread_data in threads]
