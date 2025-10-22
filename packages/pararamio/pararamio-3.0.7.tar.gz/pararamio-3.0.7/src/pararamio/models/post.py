from __future__ import annotations

from collections import OrderedDict
from typing import TYPE_CHECKING, Any, Unpack
from uuid import uuid4

# Imports from core
from pararamio._core import (
    PararamioRequestError,
    PararamioTypeError,
    PararamioValidationError,
    PararamMultipleFoundError,
    PararamNotFoundError,
)
from pararamio._core.api_schemas import (
    DataListResponse,
    PostCreateResponse,
    PostDeleteResponse,
    PostEditResponse,
    PostResponseItem,
    PostsResponse,
    RerereResponse,
    WhoReadResponse,
)
from pararamio._core.models import CoreFile as File
from pararamio._core.models import CorePost
from pararamio._core.utils.helpers import (
    encode_digit,
    rand_id,
)
from pararamio._core.utils.ranges import combine_ranges

from .base import SyncClientMixin

if TYPE_CHECKING:
    from pararamio._core._types import PostMention

    from pararamio.client import Pararamio
    from pararamio.models.chat import Chat

__all__ = ('Post',)


def get_post_mention(item: Any) -> PostMention | None:
    """Convert dict to PostMention if it has required fields.

    Args:
        item: Dictionary with mention data

    Returns:
        PostMention or None if missing required fields
    """
    if 'id' not in item or 'name' not in item or 'value' not in item:
        return None
    return {
        'id': item['id'],
        'name': item['name'],
        'value': item['value'],
    }


class Post(
    CorePost['Chat'],
    SyncClientMixin[PostResponseItem],
):
    """Sync Post model with lazy loading support."""

    def __init__(  # type: ignore[misc]
        self,
        chat: Chat,
        post_no: int | None = None,
        **kwargs: Unpack[PostResponseItem],
    ) -> None:
        """Initialize sync post.

        Args:
            chat: Chat object
            post_no: Post number (optional positional or keyword argument)
            **kwargs: Post data
        """
        super().__init__(chat, post_no, **kwargs)

    @property
    def in_thread_no(self) -> int:
        """Alias for post_no for backward compatibility."""
        return self.post_no

    @property
    def file(self) -> File | None:
        """Get file attachment if present (property for backward compatibility)."""
        return self.get_file()

    def get_file(self) -> File | None:
        """Get attached file if any.

        Returns:
            File object or None if no file
        """
        _file = self.meta.get('file', None)
        if not _file:
            return None
        return File(self._chat._client, **_file)

    def get_attachments(self) -> list[File]:
        """Get all file attachments for this post.

        Returns:
            List of attached files
        """
        attachments = []
        main_file = self.get_file()
        if main_file:
            attachments.append(main_file)
        return attachments

    def download_file(self, filename: str | None = None) -> bytes:
        """Download the file attached to this post.

        Args:
            filename: Optional filename to use for download.
                     If not provided, uses the filename from the file metadata.

        Returns:
            File content as bytes

        Raises:
            PararamioTypeError: If the post doesn't have a file attachment
            PararamioValidationError: If filename cannot be determined
        """
        file = self.file
        if file is None:
            raise PararamioTypeError(f'Post {self.post_no} is not a file post')

        if filename is None:
            filename = getattr(file, 'filename', None) or getattr(file, 'name', None)
            if not filename:
                raise PararamioValidationError('Cannot determine filename')

        bio = self.client.download_file(file.guid, filename)
        return bio.read()

    @property
    def client(self) -> Pararamio:
        """Get client instance."""
        return self._chat._client

    @property
    def is_mention(self) -> bool:
        """Check if current user is mentioned."""
        if not self.text_parsed:
            return False
        for item in self.text_parsed:
            if item.get('type', '') == 'mention' and item.get(
                'id', None
            ) == self.client.get_profile().get('id', -1):
                return True
        return False

    @property
    def mentions(self) -> list[PostMention]:
        """Get post mentions with additional processing."""
        text_parsed = self.text_parsed
        if text_parsed is None:
            return []
        mentions_: list[PostMention] = []
        for item in text_parsed:
            if item.get('type', '') == 'mention':
                mention = get_post_mention(item)
                if not mention:
                    continue
                mentions_.append(mention)
        return mentions_

    @property
    def user_links(self) -> list[PostMention]:
        """Get user links with additional processing."""
        if not self.text_parsed:
            return []
        links: list[PostMention] = []
        for item in self.text_parsed:
            if item.get('type', '') == 'user_link':
                mention = get_post_mention(item)
                if not mention:
                    continue
                links.append(mention)
        return links

    def load(self) -> Post:
        """Load full post data from API with caching.

        Returns:
            Self with updated data

        Raises:
            PararamNotFoundError: If post not found
            PararamMultipleFoundError: If multiple posts found
        """
        # Try to load from cache first if available
        if self.client._cache:
            cache_key = f'chat.{self.chat.id}.post.{self.post_no}'
            cached = self.client._cache.get(cache_key)
            if cached:
                self._data = cached
                return self

        # Load from API if not cached
        url = f'/msg/post?ids={encode_digit(self.chat.id)}-{encode_digit(self.post_no)}'
        response = self.client.api_get(url, response_model=PostsResponse)
        res = response.get('posts', [])
        if len(res) == 0:
            raise PararamNotFoundError(
                f'Post not found: post_no {self.post_no} in chat {self._chat.id}'
            )
        if len(res) > 1:
            raise PararamMultipleFoundError(
                f'Multiple posts found ({len(res)}) for post {self.post_no} in chat {self._chat.id}'
            )
        self._data = res[0]

        # Cache the post data if cache is available
        if self.client._cache:
            cache_key = f'chat.{self.chat.id}.post.{self.post_no}'
            self.client._cache.set(cache_key, self._data)

        return self

    @property
    def replies(self) -> list[int]:
        """Get list of reply post numbers (property for backward compatibility).

        Returns:
            List of post numbers that reply to this post
        """
        return self.get_replies()

    def get_replies(self) -> list[int]:
        """Get list of reply post numbers.

        Returns:
            List of post numbers that reply to this post
        """
        url = f'/msg/post/{self._chat.id}/{self.post_no}/replies'
        response = self.client.api_get(url, response_model=DataListResponse[int])
        return response.get('data', [])

    def load_reply_posts(self) -> list[Post]:
        """Load all posts that reply to this post.

        Returns:
            List of reply posts
        """
        reply_numbers = self.get_replies()
        if not reply_numbers:
            return []

        # Load each reply post
        reply_posts = []
        for post_no in reply_numbers:
            try:
                post = Post(self._chat, post_no=post_no)
                post.load()
                reply_posts.append(post)
            except PararamNotFoundError:
                # Skip posts that were deleted or are not accessible
                continue

        return reply_posts

    def reply(self, text: str, quote: str | None = None) -> Post:
        """Reply to this post.

        Args:
            text: Reply to text
            quote: Optional quote text

        Returns:
            Created reply post
        """
        _url = f'/msg/post/{self._chat.id}'
        res = self.client.api_post(
            _url,
            {'uuid': rand_id(), 'text': text, 'quote': quote, 'reply_no': self.post_no},
            response_model=PostCreateResponse,
        )
        return Post(self._chat, post_no=res['post_no']).load()

    def rerere(self) -> list[Post]:
        """Get all replies in a thread recursively.

        Returns:
            List of all posts in the reply chain
        """
        url = f'/msg/post/{self._chat.id}/{self.post_no}/rerere'
        res = self.client.api_get(url, response_model=RerereResponse)

        post_numbers = res.get('data', [])
        if not post_numbers:
            return []

        # Group post numbers into ranges for batch loading
        ranges = combine_ranges(post_numbers, max_gap=50)

        posts_dict: dict[int, Post] = {}

        # Load posts in batches
        for start, end in ranges:
            if start == end:
                # Single post
                post = Post(self._chat, post_no=start)
                post.load()
                posts_dict[start] = post
            else:
                # Batch load posts in range
                batch_posts = self._chat._load_posts(
                    start_post_no=start,
                    end_post_no=end + 1,  # end_post_no is exclusive in API
                )
                for post in batch_posts:
                    if post.post_no in post_numbers:
                        posts_dict[post.post_no] = post

        # Return posts in the original order from rerere response
        return [posts_dict[post_no] for post_no in post_numbers if post_no in posts_dict]

    def get_tree(self, load_limit: int = 1000) -> OrderedDict[int, Post]:
        """Get post tree with replies.

        Args:
            load_limit: Maximum number of posts to load

        Returns:
            Ordered dictionary of posts in the tree
        """
        posts = {self.post_no: self}
        for post in self.rerere():
            posts[post.post_no] = post
        first = posts[min(posts.keys())]
        tree = OrderedDict(sorted(posts.items()))
        load_start = first.post_no + 1
        if self.post_no - first.post_no > load_limit:
            load_start = self.post_no - load_limit
        for post in self.chat._lazy_posts_loader(*sorted([load_start, self.post_no - 1])):
            posts[post.post_no] = post

        for post in sorted(posts.values()):
            if post.reply_no is None or post.reply_no not in tree:
                continue
            tree[post.post_no] = post
        return OrderedDict(sorted(tree.items()))

    def get_reply_to_post(self) -> Post | None:
        """Get the post this is replying to.

        Returns:
            Parent post or None if not a reply
        """
        reply_no = self.reply_no
        if reply_no is not None:
            return Post(self._chat, post_no=reply_no).load()
        return None

    def next(self, skip_event: bool = True) -> Post | None:
        """
        Get next post in thread.

        :param bool skip_event: Skip a message if this is an event
        :return: Next post or None if no next post exists
        """
        _next = self.post_no + 1
        if _next > self._chat.posts_count:
            return None
        post = Post(self._chat, post_no=_next)
        if skip_event and post.is_event:
            return post.next()
        return post

    def prev(self, skip_event: bool = True) -> Post | None:
        """
        Get previous post in thread.

        :param bool skip_event: Skip a message if this is an event
        :return: Previous post or None if no previous post exists
        """
        _prev = self.post_no - 1
        if _prev <= 0:
            return None
        post = Post(self._chat, post_no=_prev)
        if skip_event and post.is_event:
            return post.prev()
        return post

    def who_read(self) -> dict[int, str]:
        """Get who read this post with timestamps.

        Returns:
            Dictionary mapping user IDs to read timestamps (ISO format strings)
        """
        url = f'/activity/who-read?thread_id={self._chat.id}&post_no={self.post_no}'
        response = self.client.api_get(url, response_model=WhoReadResponse)
        # Convert string user IDs to integers
        return {int(user_id): timestamp for user_id, timestamp in response.items()}

    def mark_read(self) -> bool:
        """Mark post as read.

        Returns:
            True if successfully marked as read
        """
        return self.chat.read_status(self.post_no)

    def edit(self, text: str, quote: str | None = None, reply_no: int | None = None) -> bool:
        """Edit post content.

        Args:
            text: New text content
            quote: Optional quote
            reply_no: Optional reply number

        Returns:
            True if successfully edited
        """
        url = f'/msg/post/{self._chat.id}/{self.post_no}'

        res = self.client.api_put(
            url,
            {
                'uuid': self._data.get('uuid', rand_id()),
                'text': text,
                'quote': quote,
                'reply_no': reply_no,
            },
            response_model=PostEditResponse,
        )
        if res.get('ver'):
            # Invalidate cache for this post
            if self.client._cache:
                cache_key = f'chat.{self.chat.id}.post.{self.post_no}'
                self.client._cache.delete(cache_key)

            self.load()
            return True
        return False

    def delete(self) -> bool:
        """Delete this post.

        Returns:
            True if successfully deleted
        """
        url = f'/msg/post/{self._chat.id}/{self.post_no}'
        res = self.client.api_delete(url, None, response_model=PostDeleteResponse)
        if res.get('ver'):
            # Invalidate cache for this post
            if self.client._cache:
                cache_key = f'chat.{self.chat.id}.post.{self.post_no}'
                self.client._cache.delete(cache_key)

            self.load()
            return True
        return False

    def _find_attachment(
        self,
        attachments: set[str],
        start: int,
        end: int,
    ) -> tuple[list[File], set[str]]:
        """Find attachments in post range.

        Args:
            attachments: Set of attachment UUIDs to find
            start: Start post number
            end: End post number

        Returns:
            Tuple of (found files, found UUIDs)
        """
        results: list[File] = []
        found: set[str] = set()
        for post in self.chat._lazy_posts_loader(start, end):
            if post.uuid in attachments:
                found.add(post.uuid)
            file = post.file
            if file is not None:
                results.append(file)
        return results, found

    def load_attachments(self, max_deep: int = 100, raise_if_not_found: bool = True) -> list[File]:
        """Load attachment files.

        Args:
            max_deep: Maximum depth to search for attachments
            raise_if_not_found: Whether to raise error if not all attachments found

        Returns:
            List of File objects

        Raises:
            PararamioRequestError: If not all attachments are found and raise_if_not_found is True
        """
        attachments_list = super().attachments
        if not attachments_list:
            return []
        attachments_ = set(attachments_list)
        start, end = self.post_no - len(attachments_list), self.post_no
        results, found = self._find_attachment(attachments_, start, end)
        if len(found) == len(attachments_):
            return results
        results_fb, found_fb = self._find_attachment(attachments_, end - 1 - max_deep, end - 1)
        results.extend(results_fb)
        if not raise_if_not_found or len(found_fb) + len(found) == len(attachments_):
            return results
        raise PararamioRequestError('can not find all attachments')

    @property
    def attachment_files(self) -> list[File]:
        """Get attachment files (loads them if needed)."""
        return self.load_attachments()

    @property
    def attachments(self) -> list[str]:
        """Get attachment IDs."""
        return self.meta.get('attachments', [])

    @classmethod
    def create(
        cls,
        chat: Chat,
        text: str,
        *,
        reply_no: int | None = None,
        quote: str | None = None,
        uuid: str | None = None,
        attachments: list[str] | None = None,
    ) -> Post:
        url = f'/msg/post/{chat.id}'
        data: dict[str, Any] = {
            'uuid': uuid or str(uuid4().hex),
            'text': text,
            'quote': quote,
            'reply_no': reply_no,
        }
        if attachments:
            data['attachments'] = attachments
        res = chat._client.api_post(url, data, response_model=PostCreateResponse)
        if not res:
            raise PararamioRequestError('Failed to create post')
        return cls(chat, post_no=res['post_no']).load()
