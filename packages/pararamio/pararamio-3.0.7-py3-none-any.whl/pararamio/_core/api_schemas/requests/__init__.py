"""API request schemas."""

from .chat import ChatCreateRequest, ChatUpdateSettingsRequest
from .deferred_post import DeferredPostCreateRequest
from .group import GroupEditRequest
from .post import MarkReadRequest, PostCreateRequest, PostSendMessageRequest

__all__ = [
    'ChatCreateRequest',
    'ChatUpdateSettingsRequest',
    'DeferredPostCreateRequest',
    'GroupEditRequest',
    'MarkReadRequest',
    'PostCreateRequest',
    'PostSendMessageRequest',
]
