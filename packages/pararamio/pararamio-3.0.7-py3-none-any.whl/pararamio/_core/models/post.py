"""Core Post model without lazy loading."""

from __future__ import annotations

import os
from datetime import datetime
from typing import TYPE_CHECKING, Any, Generic, Self, TypeVar, Unpack, cast

from pararamio._core.api_schemas.responses import FileUploadFields, PostResponseItem
from pararamio._core.exceptions import (
    PararamioTypeError,
    PararamioValidationError,
    PararamioValueError,
)
from pararamio._core.utils.helpers import parse_iso_datetime

from .base import CoreBaseModel

if TYPE_CHECKING:
    from pararamio._core._types import FormatterT, PostMetaT, TextParsedT
    from pararamio._core.api_schemas import PostEvent
    from pararamio._core.api_schemas.responses import Mention, UserLink

    from .chat import CoreChat

__all__ = ('CorePost',)


# Attribute formatters for Post
POST_ATTR_FORMATTERS: FormatterT = {
    'post_no': lambda data, key: int(data[key]),
    'time_edited': parse_iso_datetime,
    'time_created': parse_iso_datetime,
}


ChatT = TypeVar('ChatT', bound='CoreChat[Any]')


class CorePost(CoreBaseModel[PostResponseItem], Generic[ChatT]):
    """Core Post model with common functionality."""

    # Post attributes from actual API response
    _chat: ChatT
    _data: PostResponseItem
    uuid: str
    id: int | None
    post_no: int
    user_id: int
    reply_no: int | None
    event: PostEvent | None
    meta: PostMetaT
    ver: int | None
    is_deleted: bool
    time_created: datetime
    time_edited: datetime | None
    text: str
    text_parsed: list[TextParsedT]
    _attr_formatters = POST_ATTR_FORMATTERS

    def __init__(  # type: ignore[misc]
        self,
        chat: ChatT,
        post_no: int | None = None,
        **kwargs: Unpack[PostResponseItem],
    ) -> None:
        self._chat = chat
        # Handle positional post_no
        if post_no is not None:
            if 'post_no' in kwargs:
                kwargs.pop('post_no')
            kwargs['post_no'] = post_no
        self._data = cast('PostResponseItem', kwargs)

        # Validate that required ID is present
        if 'post_no' not in self._data:
            raise PararamioValidationError(
                'Post requires post_no to be present in data. '
                'Cannot create a Post without a valid post number.'
            )

        super().__init__(chat._client, **kwargs)  # type: ignore[call-arg]

    @classmethod
    def from_dict(
        cls,
        chat: ChatT,
        data: PostResponseItem,
    ) -> Self:
        """Create Post instance from dict data.

        Args:
            chat: Parent chat object
            data: Post response data

        Returns:
            Post instance marked as loaded
        """
        # Note: CorePost doesn't have _set_loaded, but sync/async implementations do
        # This is called on the actual subclass (Post), not CorePost directly
        return cls(chat, **data)

    def to_dict(self) -> PostResponseItem:
        """Convert Post to dictionary.

        Returns:
            Post data as dict
        """
        return self._data.copy()

    @property
    def chat(self) -> ChatT:
        """Get chat object."""
        return self._chat

    @property
    def chat_id(self) -> int:
        """Get chat ID. Prefer from _data if present, otherwise from parent chat."""
        # Try to get from post data first
        if 'chat_id' in self._data:
            return self._data['chat_id']

        # Try chat._data directly to avoid triggering load (if it's a dict)
        if hasattr(self._chat, '_data') and isinstance(self._chat._data, dict):
            if 'chat_id' in self._chat._data:
                return self._chat._data['chat_id']
            if 'id' in self._chat._data:
                return self._chat._data['id']

        # Last resort - may trigger lazy loading or use mock attribute
        return self._chat.id

    @property
    def is_reply(self) -> bool:
        """Check if this post is a reply."""
        return self.reply_no is not None

    @property
    def is_event(self) -> bool:
        """Check if this is an event post."""
        return bool(self.event)

    @property
    def mentions(self) -> list[Mention]:
        """Get post-mentions."""
        return [
            {
                'id': item['id'],
                'name': item['name'],
                'value': item['value'],
            }
            for item in self.text_parsed
            if item.get('type') == 'mention'
        ]

    @property
    def is_bot(self) -> bool:
        """Check if post is from a bot."""
        return self.meta.get('user', {}).get('is_bot', False)

    @property
    def is_file(self) -> bool:
        """Check if post contains file attachment."""
        return 'file' in self.meta

    @property
    def is_mention(self) -> bool:
        """Check if post contains mentions.

        Returns:
            True if post has mentions
        """
        if self.text_parsed is None:
            return False
        return any(item.get('type') == 'mention' for item in self.text_parsed)

    @property
    def user_links(self) -> list[UserLink]:
        """Get user links in post."""
        return [
            {
                'id': item['id'],
                'name': item['name'],
                'value': item['value'],
            }
            for item in self.text_parsed
            if item.get('type') == 'user_link' or item.get('type') == 'userlink'
        ]

    @property
    def attachments(self) -> list[str]:
        """Get attachments in post."""
        return self.meta.get('attachments', [])

    def _compare_validations(self, other: object) -> None:
        """Validate that posts can be compared."""
        if not isinstance(other, CorePost):
            raise PararamioTypeError(f'can not compare post and {other.__class__.__name__}')
        if self.chat_id != other.chat_id:
            raise PararamioValueError('can not compare posts from different chats')

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CorePost):
            return id(other) == id(self)
        return self.chat_id == other.chat_id and self.post_no == other.post_no

    def __lt__(self, other: object) -> bool:
        self._compare_validations(other)
        assert isinstance(other, CorePost)  # for type checker
        return self.post_no < other.post_no

    def __le__(self, other: object) -> bool:
        self._compare_validations(other)
        assert isinstance(other, CorePost)  # for type checker
        return self.post_no <= other.post_no

    def __gt__(self, other: object) -> bool:
        self._compare_validations(other)
        assert isinstance(other, CorePost)  # for type checker
        return self.post_no > other.post_no

    def __ge__(self, other: object) -> bool:
        self._compare_validations(other)
        assert isinstance(other, CorePost)  # for type checker
        return self.post_no >= other.post_no

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f'<Post(client={hex(id(self.chat.client))}, chat_id={self.chat_id}, post_no'
            f'={self.post_no})>'
        )

    @staticmethod
    def prepare_file_upload_fields(
        file: Any,  # BinaryIO | BytesIO
        chat_id: int | None,
        *,
        filename: str | None = None,
        type_: str | None = None,
        organization_id: int | None = None,
        reply_no: int | None = None,
        quote_range: str | None = None,
    ) -> tuple[FileUploadFields, str | None]:
        """Prepare fields and validate parameters for file upload.

        Args:
            file: File-like object to upload
            chat_id: Chat ID for the upload
            filename: Optional filename
            type_: Optional file type (can be 'organization_avatar', 'chat_avatar', or content type)
            organization_id: Optional organization ID (required for organization_avatar)
            reply_no: Optional reply number
            quote_range: Optional quote range

        Returns:
            Tuple of (FileUploadFields dict, content_type)

        Raises:
            PararamioValidationError: If validation fails
        """
        # Validate required parameters
        if type_ is None and not filename:
            raise PararamioValidationError('filename must be set when type is None')

        if type_ == 'organization_avatar' and organization_id is None:
            raise PararamioValidationError(
                'organization_id must be set when type is organization_avatar'
            )

        if type_ == 'chat_avatar' and chat_id is None:
            raise PararamioValidationError('chat_id must be set when type is chat_avatar')

        # Determine content type
        content_type = None
        if type_ not in ('organization_avatar', 'chat_avatar'):
            content_type = type_

        # Get file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0, 0)

        # Prepare fields
        fields = FileUploadFields(
            type=type_,
            filename=filename,
            size=file_size,
            chat_id=chat_id,
            organization_id=organization_id,
            reply_no=reply_no,
            quote_range=quote_range,
        )

        return fields, content_type
