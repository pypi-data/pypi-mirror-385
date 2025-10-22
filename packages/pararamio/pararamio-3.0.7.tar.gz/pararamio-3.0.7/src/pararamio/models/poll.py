from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, Unpack, cast

# Imports from core
from pararamio._core import (
    PararamioRequestError,
    PararamioServerResponseError,
    PararamioValidationError,
)
from pararamio._core.api_schemas import PollResponse
from pararamio._core.api_schemas.responses import (
    PollCreateResponse,
    PollGetResponse,
    PollOptionData,
    PollVoteResponse,
)
from pararamio._core.models import CorePoll, SerializationMixin

from .base import SyncClientMixin

if TYPE_CHECKING:
    from pararamio.client import Pararamio

    from .chat import Chat

__all__ = ('Poll',)


# PollOption is just PollOptionData TypedDict from core
PollOption = PollOptionData


class Poll(
    CorePoll,
    SyncClientMixin[PollResponse],
    SerializationMixin['Pararamio', PollResponse],
):
    """Sync Poll model with lazy loading support."""

    _client: Pararamio

    def __init__(
        self,
        client: Pararamio,
        **kwargs: Unpack[PollResponse],
    ) -> None:
        """Initialize sync poll.

        Args:
            client: Pararamio client
            **kwargs: Poll data
        """
        super().__init__(client, **kwargs)
        self._client = client

    def _update(self, response: dict[str, Any]) -> Poll:
        """Update the Poll object with the response data.

        Args:
            response: A dictionary containing the response data.

        Returns:
            The updated Poll object.

        Raises:
            PararamioServerResponseError: If 'vote' key is not present in the response.
        """
        if 'vote' not in response:
            raise PararamioServerResponseError(
                f'failed to load data for vote {self._data["vote_uid"]}',
                response,
            )
        self._data = response['vote']
        # Update options with PollOptionData dicts
        self.options = response['vote'].get('options', [])
        return self

    def load(self) -> Poll:
        """Load the poll's data from the pararam server with caching.

        Returns:
            The updated instance of the poll.
        """
        vote_uid = self._data.get('vote_uid')
        if not vote_uid:
            # Fallback if vote_uid is not set
            res = self._client.api_get(
                f'/msg/vote/{self._data["vote_uid"]}', response_model=PollGetResponse
            )
            return self._update(cast('dict[str, Any]', res))

        # Try to load from cache first if available
        if self._client._cache:
            cache_key = f'poll.{vote_uid}'
            cached = self._client._cache.get(cache_key)
            if cached:
                return self._update(cast('dict[str, Any]', cached))

        # Load from API if not cached
        res = self._client.api_get(f'/msg/vote/{vote_uid}', response_model=PollGetResponse)

        # Cache the poll data if cache is available
        if self._client._cache:
            cache_key = f'poll.{vote_uid}'
            self._client._cache.set(cache_key, res)

        return self._update(cast('dict[str, Any]', res))

    @classmethod
    def create(
        cls,
        chat: Chat,
        question: str,
        *,
        mode: Literal['one', 'more'],
        anonymous: bool,
        options: list[str],
    ) -> Poll:
        """Create a new poll in the specified pararam chat.

        Args:
            chat: The chat in which the poll will be created.
            question: The question for the poll.
            mode: Options select mode of the poll ('one' for single or 'more' for multi).
            anonymous: Whether the poll should be anonymous or not.
            options: The list of options for the poll.

        Returns:
            The created Poll object.

        Raises:
            PararamioRequestError: If the request to create the poll fails.
            PararamioValidationError: If mode is invalid.
        """
        if mode not in ('one', 'more'):
            raise PararamioValidationError(f"Mode must be 'one' or 'more', got '{mode}'")

        # Get chat ID from data without triggering lazy loading
        chat_id = chat._data.get('chat_id') or chat._data.get('id')

        res = chat.client.api_post(
            '/msg/vote',
            {
                'chat_id': chat_id,
                'question': question,
                'options': options,
                'mode': mode,
                'anonymous': anonymous,
            },
            response_model=PollCreateResponse,
        )
        if not res:
            raise PararamioRequestError('Failed to create poll')
        # Create a minimal poll instance with vote_uid and load full data
        poll = cls(chat.client, vote_uid=res['vote_uid'])
        return poll.load()

    def _vote(self, option_ids: list[int]) -> Poll:
        """Vote on the poll by selecting the given option IDs.

        Args:
            option_ids: A list of integers representing the IDs of the options to vote for.

        Returns:
            The updated Poll object after voting.

        Raises:
            PararamioValidationError: If any of the option IDs are incorrect.
        """
        ids_ = [opt['id'] for opt in self._data['options']]
        if not all(opt_id in ids_ for opt_id in option_ids):
            raise PararamioValidationError('incorrect option')
        res = self._client.api_put(
            f'/msg/vote/{self._data["vote_uid"]}',
            {
                'variants': option_ids,
            },
            response_model=PollVoteResponse,
        )
        return self._update(cast('dict[str, Any]', res))

    def vote(self, option_id: int) -> Poll:
        """Vote for a specific option in the poll.

        Args:
            option_id: The ID of the option to vote for.

        Returns:
            The updated Poll object after voting.

        Raises:
            PararamioValidationError: If the option_id is invalid.
        """
        return self._vote([option_id])

    def vote_multi(self, option_ids: list[int]) -> Poll:
        """Vote for multiple options in a poll.

        Args:
            option_ids: A list of integers representing the IDs of the options to vote for.

        Returns:
            The updated instance of the poll.

        Raises:
            PararamioValidationError: If the poll mode is not 'more' or
                if any of the option IDs are incorrect.
        """
        if not self._data.get('multi_choice', False):
            raise PararamioValidationError('Poll does not support multiple choices')
        return self._vote(option_ids)

    def retract(self) -> Poll:
        """Retracts the vote from the poll.

        Returns:
            The updated instance of the poll.
        """
        return self._vote([])
