from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from typing import TYPE_CHECKING, Any, TypeVar, cast

from pararamio._core._types import BotProfileT, ChatT, ProfileTypeT, TasksResponseT
from pararamio._core.api_schemas.responses.bot import (
    BotMessageResponse,
    TaskStatusResponse,
)
from pararamio._core.api_schemas.responses.chat import ChatListResponse, ChatsResponse
from pararamio._core.api_schemas.responses.user import UserActivityResponse, UsersResponse
from pararamio._core.constants.endpoints import PRIVATE_MESSAGE_URL
from pararamio._core.models.bot import CoreBot
from pararamio._core.utils.helpers import join_ids, unescape_dict

# Imports from core
from pararamio.exceptions import PararamioRequestError
from pararamio.utils.lazy_loader import lazy_loader
from pararamio.utils.requests import bot_request

from .activity import Activity, ActivityAction

if TYPE_CHECKING:
    from datetime import datetime


__all__ = ('PararamioBot',)


def _load_chats(cls: PararamioBot, ids: Sequence[int]) -> list[ChatT]:
    url = f'/core/chat?ids={join_ids(ids)}'
    res = cls.request(url, ChatsResponse)
    if res and 'chats' in res:
        # Convert ChatResponseItem to ChatT (they're compatible types)
        return cast('list[ChatT]', res.get('chats', []))
    raise PararamioRequestError(f'failed to load data for chats ids: {",".join(map(str, ids))}')


T = TypeVar('T')


def _one_or_value_error(fn: Callable[[], list[T]], msg: str, *args: Any) -> T:
    try:
        return fn()[0]
    except IndexError:
        pass
    raise ValueError(msg.format(*args))


class PararamioBot:
    key: str

    def __init__(self, key: str) -> None:
        if len(key) > 50:
            key = key[20:]
        self.key = key

    def request(
        self,
        url: str,
        response_model: type[T],  # noqa: ARG002
        method: str = 'GET',
        data: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
    ) -> T:
        """
        Sends an HTTP request and returns the response.

        Parameters:
        url: The endpoint to which the request is sent.
        response_model: Required type to cast the response to.
        method: The HTTP method to use for the request.
        Defaults to 'GET'.
        data: The payload to send with the request, for POST or PUT requests.
        Optional.
        headers: A dictionary of headers to send with the request.
        Optional.

        Returns:
        Response cast to the specified response_model type.
        """
        result = bot_request(url, self.key, method=method, data=data, headers=headers)
        return cast('T', result)

    def profile(self) -> BotProfileT:
        """
        Fetches the profile information of the authenticated bot user.

        Returns:
            BotProfileT: Dictionary containing the bot user's
                         profile information with "name" keys unescaped.
        """
        url = '/user/me'
        result = self.request(url, dict[str, Any])
        return cast('BotProfileT', unescape_dict(result, keys=['name']))

    def post_message(
        self, chat_id: int, text: str, reply_no: int | None = None
    ) -> BotMessageResponse:
        """
        Sends a message to a specified chat.

        Parameters:
            chat_id (int): The ID of the chat to which the message will be sent.
            text (str): The content of the message to be sent.
            reply_no (Optional[int]): The ID of the message to reply to,
                                      or None if no reply is required.

        Returns:
            BotMessageResponse: Response containing chat_id and post_no.
        """
        url = '/bot/message'
        data = CoreBot.prepare_post_message_data(chat_id, text, reply_no)
        return self.request(url, BotMessageResponse, method='POST', data=data)

    def post_private_message_by_user_id(
        self,
        user_id: int,
        text: str,
    ) -> BotMessageResponse:
        """
        Send a private message to a user by their user ID

        Args:
            user_id: The ID of the user to whom the message will be sent.
            text: The content of the message.

        Returns:
            BotMessageResponse: Response containing chat_id and post_no.
        """
        url = PRIVATE_MESSAGE_URL
        return self.request(
            url,
            BotMessageResponse,
            method='POST',
            data={'text': text, 'user_id': user_id},
        )

    def post_private_message_by_user_email(self, email: str, text: str) -> BotMessageResponse:
        url = PRIVATE_MESSAGE_URL
        return self.request(
            url,
            BotMessageResponse,
            method='POST',
            data={'text': text, 'user_email': email},
        )

    def post_private_message_by_user_unique_name(
        self, unique_name: str, text: str
    ) -> BotMessageResponse:
        url = PRIVATE_MESSAGE_URL
        return self.request(
            url,
            BotMessageResponse,
            method='POST',
            data={'text': text, 'user_unique_name': unique_name},
        )

    def get_tasks(self) -> TasksResponseT:
        url = '/msg/task'
        result = self.request(url, dict[str, Any])
        return cast('TasksResponseT', result)

    def set_task_status(self, chat_id: int, post_no: int, state: str) -> TaskStatusResponse:
        if str.lower(state) not in ('open', 'done', 'close'):
            raise ValueError(f'unknown state {state}')
        url = f'/msg/task/{chat_id}/{post_no}'
        data = {'state': state}
        return self.request(url, TaskStatusResponse, method='POST', data=data)

    def get_chat(self, chat_id: int) -> ChatT:
        url = f'/core/chat?ids={chat_id}'
        result = _one_or_value_error(
            lambda: self.request(url, ChatsResponse).get('chats', []),
            'chat with id {0} is not found',
            chat_id,
        )
        return cast('ChatT', result)

    def get_chats(self) -> Iterable[ChatT]:
        url = '/core/chat/sync'
        chats_per_load = 50
        ids = self.request(url, ChatListResponse).get('chats', [])
        return lazy_loader(self, cast('Sequence[int]', ids), _load_chats, per_load=chats_per_load)

    def get_users(self, users_ids: list[int]) -> list[ProfileTypeT]:
        url = f'/core/user?ids={join_ids(users_ids)}'
        resp = self.request(url, UsersResponse)
        users = resp.get('users', [])
        return [cast('ProfileTypeT', unescape_dict(u, keys=['name'])) for u in users]

    def get_user_by_id(self, user_id: int) -> ProfileTypeT:
        """
        Fetches a user by id.

        This method attempts to retrieve a user from a data source using the given user_id.
        If the user is not found, it raises a ValueError with an appropriate message.

        Parameters:
         user_id (int): The unique identifier of the user to be fetched.

        Returns:
         dict: The user data corresponding to the provided user_id.

        Raises:
         ValueError: If no user is found with the given user_id.
        """
        return _one_or_value_error(
            lambda: self.get_users([user_id]), 'user with id {0} is not found', user_id
        )

    def _user_activity_page_loader(self, user_id: int) -> Callable[..., UserActivityResponse]:
        """
        Creates a loader function to fetch the user's activity page based on given parameters.

        Parameters:
         user_id (int): The ID of the user whose activity page is to be fetched.

        Returns:
         Callable[..., Dict[str, Any]]: A loader function that accepts optional activity action
                                        and page number, then returns the corresponding activity
                                        page data in a dictionary.

        Loader function parameters:
         action (ActivityAction, optional): The action to filter the activities (default is None).
         page (int, optional): The page number of the activities to fetch (default is 1).
        """

        def loader(action: ActivityAction | None = None, page: int = 1) -> UserActivityResponse:
            action_ = action.value if action else ''
            url = f'/activity?user_id={user_id}&action={action_}&page={page}'
            return self.request(url, UserActivityResponse)

        return loader

    def get_user_activity(
        self,
        user_id: int,
        start: datetime,
        end: datetime,
        actions: list[ActivityAction] | None = None,
    ) -> list[Activity]:
        """
        Fetches user activity within a specified date range

        Args:
            user_id (int): The ID of the user whose activity is to be retrieved.
            start (datetime): The start date and time of the range to filter activities.
            end (datetime): The end date and time of the range to filter activities.
            actions (List[ActivityAction], optional): A list of specific activity actions to filter.
                                                      Defaults to None.

        Returns:
            List[Activity]: A list of Activity objects representing the user's actions
                            within the specified range.
        """
        return Activity.get_activity(self._user_activity_page_loader(user_id), start, end, actions)
