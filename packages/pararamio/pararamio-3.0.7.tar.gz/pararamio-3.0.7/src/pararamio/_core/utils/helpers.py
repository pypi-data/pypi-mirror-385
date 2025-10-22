from __future__ import annotations

import hashlib
import math
import uuid
from collections.abc import Mapping
from datetime import UTC, datetime
from html import unescape
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    cast,
)

from pararamio._core.constants import DATETIME_FORMAT
from pararamio._core.exceptions import PararamioValidationError, PararamModelNotLoadedError

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence
    from datetime import timedelta

    from pararamio._core._types import FormatterT

__all__ = (
    'check_login_opts',
    'encode_chat_id',
    'encode_digit',
    'format_datetime',
    'format_or_none',
    'get_empty_vars',
    'get_formatted_attr_or_load',
    'get_utc',
    'join_ids',
    'parse_datetime',
    'parse_iso_datetime',
    'unescape_dict',
)


def check_login_opts(login: str | None, password: str | None) -> bool:
    """
    Check if both login and password options are provided and not empty.

    Parameters:
    login (Optional[str]): The login string to check.
    password (Optional[str]): The password string to check.

    Returns:
    bool: True if both login and password are provided and not empty, False otherwise.
    """
    return all(map(bool, [login, password]))


def get_empty_vars(**kwargs: str) -> str:
    """
    Identifies and returns a comma-separated string of keys from the keyword
    arguments where the corresponding values are empty.

    Parameters:
        **kwargs (Any): Arbitrary keyword arguments with values to be checked.

    Returns:
        str: A comma-separated string of keys with empty values.
    """
    return ', '.join([k for k, v in kwargs.items() if not v])


def encode_digit(digit: int, res: str = '') -> str:
    """
    Encodes a given integer into a custom base-64-like string.

    Parameters:
    digit (int): The integer to be encoded.
    res (str): The resulting encoded string, used internally for recursion.

    Returns:
    str: The encoded string representation of the given integer.
    """
    if not isinstance(digit, int):
        digit = int(digit)
    # noinspection SpellCheckingInspection
    code_string = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_.'
    result = math.floor(digit / len(code_string))
    res = code_string[int(digit % len(code_string))] + res
    return encode_digit(result, res) if result > 0 else res


def encode_chat_id(chat_id: int, posts_count: int, last_read_post_no: int) -> str:
    """
    Encodes the given chat details into a single string.

    This function takes a chat ID, the count of posts in the chat, and the number
    of the last read post, and combines them into a single string separated by hyphens.

    Parameters:
    chat_id (int): The unique identifier for the chat.
    posts_count (int): The total number of posts in the chat.
    last_read_post_no (int): The number of the last post read by the user.

    Returns:
    str: A single string containing the encoded chat details separated by hyphens.
    """
    return '-'.join(map(str, [chat_id, posts_count, last_read_post_no]))


def encode_chats_ids(chats_ids: list[tuple[int, int, int]]) -> str:
    """
    Encodes a list of chat IDs into a single string representation.

    This function takes a list of chat ID tuples and converts each tuple into an encoded string
    using the encode_chat_id function.
    The encoded strings are then joined together by a '/' delimiter.

    Parameters:
        chats_ids (List[Tuple[int, int, int]]): A list of tuples, where each tuple contains
        three integers representing a chat ID.

    Returns:
        str: A single string containing all encoded chat IDs joined by '/'.
    """
    return '/'.join(encode_chat_id(*chat_id) for chat_id in chats_ids)


def join_ids(items: Sequence[Any]) -> str:
    """
    Converts a list of items into a single comma-separated string.

    Args:
        items (List[Any]): A list containing elements of any type to be joined.

    Returns:
        str: A comma-separated string representation of the elements in the list.
    """
    return ','.join(map(str, items))


def get_utc(date: datetime) -> datetime:
    """
    Converts an offset-aware datetime object to its UTC equivalent.

    Parameters:
    date (datetime): The datetime object to convert.
    """
    if date.tzinfo is None:
        msg = 'is not offset-aware datetime'
        raise PararamioValidationError(msg)
    return date - cast('timedelta', date.utcoffset())


def parse_datetime(
    data: Mapping[str, Any],
    key: str,
    format_: str = DATETIME_FORMAT,
) -> datetime | None:
    """
    Parse a datetime object from a dictionary.

    Parameters:
    data (Dict[str, Any]): The dictionary containing the datetime string to parse.
    key (str): The key in the dictionary where the datetime string is stored.
    format_ (str): The format in which the datetime string is stored.

    Returns:
    datetime | None: The parsed datetime object with UTC timezone, or None if value is None.

    Raises:
        KeyError: If the key is not found in data.
    """
    value = data[key]  # Raises KeyError if key not in data
    if value is None:
        return None
    return datetime.strptime(value, format_).replace(tzinfo=UTC)


def parse_iso_datetime(data: Mapping[str, Any], key: str) -> datetime | None:
    """
    Parses an ISO 8601 formatted datetime string from a dictionary by a given key.

    Parameters:
    data (Dict[str, Any]): The dictionary containing the datetime string.
    key (str): The key used to extract the datetime string from the dictionary.

    Returns:
    Optional[datetime]: A datetime object if parsing is successful, otherwise None.
    """
    try:
        return parse_datetime(data, key, '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        return parse_datetime(data, key, '%Y-%m-%dT%H:%M:%SZ')


def format_datetime(date: datetime) -> str:
    """
    Formats the given datetime object to a string in UTC using a predefined format.

    Arguments:
        date (datetime): The datetime object to format.

    Returns:
        str: The formatted datetime string.
    """
    return get_utc(date).strftime(DATETIME_FORMAT)


def rand_id() -> str:
    """

    Generates a pseudo-random identifier.

    This function generates a pseudo-random identifier by using the UUID
    and MD5 hashing algorithm. The UUID is first converted to its hexadecimal
    representation and encoded into bytes.
    An MD5 hash is then computed from these bytes.
    The
    resulting hash is converted to an integer,
    scaled by a factor of 10^-21, and finally returned as a string.

    Returns:
        str: The generated pseudo-random identifier
    """
    _hash = hashlib.md5(bytes(uuid.uuid4().hex, 'utf8'))
    return str(int(int(_hash.hexdigest(), 16) * 10**-21))


T = TypeVar('T')


def unescape_dict(d: T, keys: list[str]) -> T:
    """
    Unescapes the values of specified keys in a dictionary.

    This function takes a dictionary and a list of keys,
    and returns a new dictionary where the values of the specified keys have been unescaped.
    All other keys and values remain unchanged.

    Args:
        d: The dictionary whose values are to be unescaped.
        keys: A list of keys for which the values should be unescaped.

    Returns:
        A new dictionary with the values of specified keys unescaped.
    """
    return cast(
        'T',
        {
            k: unescape(v) if k in keys and v is not None else v
            for k, v in cast('dict[str, Any]', d).items()
        },
    )


def format_or_none(key: str, data: dict[str, Any], formatter: FormatterT | None) -> Any:
    """
    Formats the value associated with the given key if a formatter is provided;
    otherwise, returns the unformatted value.

    Parameters:
    key (str): The key for which the value should be retrieved and optionally formatted.
    data (Dict[str, Any]): The dictionary containing the data.
    formatter (Optional[FormatterT]): An optional formatter dictionary where keys are the same as
                                      in data and values are formatting functions.

    Returns:
    Any: The formatted value associated with the key if a formatter exists for it;
    otherwise, the unformatted value.
    """
    if formatter is not None and key in formatter:
        return formatter[key](data, key)
    return data[key]


def get_formatted_attr_or_load(
    obj: object,
    key: str,
    formatter: FormatterT | None = None,
    load_fn: Callable[[], Any] | None = None,
) -> Any:
    """
    Fetches a formatted attribute from an object's `_data` attribute if it exists,
    using an optional formatter function. If the attribute does not exist and a
    `load_fn` function is provided, the function will be called to load the data,
    and the attribute will be fetched again.

    Args:
        obj (object): The object containing the `_data` attribute.
        key (str): The key to look up in the `_data` attribute.
        formatter (Optional[FormatterT], optional): An optional formatter function to
            format the retrieved attribute. Defaults to None.
        load_fn (Optional[Callable[[], Any]], optional): An optional function to call
            if the key does not exist in the `_data` attribute. Defaults to None.

    Returns:
        Any: The formatted attribute if found and formatted, else raises PararamModelNotLoadedError.

    Raises:
        PararamModelNotLoadedError: If the key does not exist in the `_data` attribute and no
            `load_fn` is provided.
    """
    try:
        return format_or_none(key, getattr(obj, '_data', {}), formatter)
    except KeyError as e:
        if load_fn is not None:
            load_fn()
            return format_or_none(key, getattr(obj, '_data', {}), formatter)
        msg = f"Attribute '{key}' has not been loaded yet"
        raise PararamModelNotLoadedError(msg) from e
