"""Core Bot model without lazy loading."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

if TYPE_CHECKING:
    from pararamio._core._types import FormatterT

__all__ = ('CoreBot',)


# Attribute formatters for Bot
BOT_ATTR_FORMATTERS: FormatterT = {}


class CoreBot:
    """Core Bot model with common functionality.

    Note: This is a minimal bot model for data representation.
    The actual bot client with request methods is in AsyncPararamioBot/PararamioBot.
    """

    # Bot attributes
    _key: str
    name: str | None
    id: int | None
    chat_id: int | None
    organization_id: int | None

    _attr_formatters: ClassVar[FormatterT] = BOT_ATTR_FORMATTERS

    def __init__(self, key: str) -> None:
        """Initialize a bot model with data.

        Args:
            key: Bot API key
        """
        if len(key) > 50:
            key = key[20:]
        self._key = key

    @staticmethod
    def prepare_post_message_data(
        chat_id: int, text: str, reply_no: int | None = None
    ) -> dict[str, Any]:
        """Prepare data for post_message API call.

        Args:
            chat_id: Target chat ID
            text: Message text
            reply_no: Optional message number to reply to

        Returns:
            Dictionary with message data for API call
        """
        data: dict[str, Any] = {
            'chat_id': chat_id,
            'text': text,
        }
        if reply_no is not None:
            data['reply_no'] = reply_no
        return data
