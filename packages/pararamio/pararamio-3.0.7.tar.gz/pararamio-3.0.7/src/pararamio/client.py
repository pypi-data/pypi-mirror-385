from __future__ import annotations

import logging
import os
from collections.abc import Callable, Iterable, Sequence
from datetime import timedelta
from io import BytesIO
from pathlib import Path
from typing import (
    Any,
    BinaryIO,
    TypeVar,
    cast,
    overload,
)

import httpx

# Imports from core
from pararamio._core import (
    POSTS_LIMIT,
    XSRF_HEADER_NAME,
    PararamioException,
    PararamioHTTPRequestError,
    PararamioValidationError,
)
from pararamio._core._types import GroupSyncResponseT, ProfileTypeT, SecondStepFnT
from pararamio._core.api_schemas.requests import ChatCreateRequest
from pararamio._core.api_schemas.responses import (
    ChatListResponse,
    ChatTagsResponse,
    DeleteFileResponse,
    FileResponse,
    OkResponse,
    SessionItem,
    SessionsResponse,
    TeamsResponse,
)
from pararamio._core.constants.endpoints import PRIVATE_MESSAGE_URL
from pararamio._core.exceptions import PararamioAuthenticationError
from pararamio._core.models.post import CorePost
from pararamio._core.utils import process_cookie_for_storage
from pararamio._core.utils.helpers import (
    check_login_opts,
    get_empty_vars,
    unescape_dict,
)

from .cache.helpers import generate_cache_key
from .cookie_manager import CookieManager, InMemoryCookieManager
from .models import Chat, File, Group, Post, Team, User, UserSearchResult
from .protocols.cache import CacheProtocol
from .utils.authentication import (
    authenticate,
    do_second_step,
    do_second_step_with_code,
    get_xsrf_token,
)
from .utils.lazy_loader import lazy_loader
from .utils.requests import (
    api_request,
    delete_file,
    download_file,
    xupload_file,
)

__all__ = ('Pararamio',)
log = logging.getLogger('pararamio.client')

# TypeVar for response models
T = TypeVar('T')


class Pararamio:  # pylint: disable=too-many-public-methods
    """Pararamio client class.

    Provides a synchronous client interface for interacting with the Pararamio API.

    Parameters:
        login: User email address for authentication.
        password: User password for authentication.
        key: TOTP/2FA secret key for two-factor authentication (optional).
        cookie_manager: Cookie storage manager for session persistence.
            Defaults to InMemoryCookieManager if not provided.
        cache: Cache instance implementing CacheProtocol for response caching.
            Supports InMemoryCache or custom implementations (optional).
        session: Custom httpx.Client instance for HTTP requests (optional).
        wait_auth_limit: If True, wait for rate limits to expire instead of raising
            PararamioAuthenticationError. Default: False.
            Rate limits: 3 attempts/minute, 10 attempts/30 minutes.
        load_on_key_error: Enable lazy loading of missing attributes on model objects.
            Default: True.

    Examples:
        Basic usage:
            >>> client = Pararamio(login='user@example.com', password='pass')
            >>> profile = client.get_profile()

        With persistent cookies:
            >>> from pararamio import FileCookieManager
            >>> cookie_mgr = FileCookieManager('cookies.txt')
            >>> client = Pararamio(cookie_manager=cookie_mgr)

        With caching enabled:
            >>> from pararamio import InMemoryCache
            >>> from datetime import timedelta
            >>> cache = InMemoryCache(max_size=1000, default_ttl=timedelta(minutes=5))
            >>> client = Pararamio(login='user@example.com', password='pass', cache=cache)

        With rate limit waiting:
            >>> client = Pararamio(  # pragma: allowlist secret
            ...     login='user@example.com', password='pass', wait_auth_limit=True
            ... )
    """

    _login: str | None
    _password: str | None
    _key: str | None
    _authenticated: bool
    _cookie_jar: httpx.Cookies
    _session: httpx.Client | None
    _cookie_manager: CookieManager | None
    _cache: CacheProtocol | None
    __profile: ProfileTypeT | None
    __headers: dict[str, str]

    def __init__(  # pylint: disable=too-many-branches
        self,
        login: str | None = None,
        password: str | None = None,
        key: str | None = None,
        *,
        cookie_manager: CookieManager | None = None,
        cache: CacheProtocol | None = None,
        session: httpx.Client | None = None,
        wait_auth_limit: bool = False,
        load_on_key_error: bool = True,
    ) -> None:
        self._login = login
        self._password = password
        self._key = key
        self._cache = cache
        self._wait_auth_limit = wait_auth_limit
        self.load_on_key_error = load_on_key_error
        self.__headers = {}
        self.__profile = None
        self._authenticated = False
        self._session = session
        self._cookie_jar = httpx.Cookies()
        self._cookie_manager = (
            cookie_manager if cookie_manager is not None else InMemoryCookieManager()
        )

        # Load cookies from cookie manager
        self._load_cookies_to_session()
        # Check for XSRF token in cookies
        self._check_xsrf_token()

    def _load_cookies_to_session(self) -> None:
        """Load cookies from cookie manager to session."""
        if not self._cookie_manager:
            return

        cookies = self._cookie_manager.get_all_cookies()
        if not cookies:
            # Try to load if no cookies yet
            self._cookie_manager.load_cookies()
            cookies = self._cookie_manager.get_all_cookies()

        if cookies:
            # Create session if needed
            self._ensure_session()
            # Add cookies directly to the jar to preserve all attributes
            for cookie in cookies:
                # Skip cookies with empty or None value
                if not cookie.value:
                    continue
                # Add cookie directly to session's jar
                if self._session:
                    self._session.cookies.jar.set_cookie(cookie)

    def _ensure_session(self) -> None:
        """Ensure session is created and open."""
        if self._session is None or self._session.is_closed:
            self._session = httpx.Client(
                cookies=self._cookie_jar,
                timeout=30.0,
                limits=httpx.Limits(max_connections=30, max_keepalive_connections=10),
            )

    def _check_xsrf_token(self) -> None:
        """Check for XSRF token in cookies and set authentication status."""
        if not self._cookie_manager:
            return

        cookies = self._cookie_manager.get_all_cookies()
        for cookie in cookies:
            if cookie.name == '_xsrf' and cookie.value is not None:
                self.__headers[XSRF_HEADER_NAME] = cookie.value
                self._authenticated = True
                break

    @property
    def session(self) -> httpx.Client:
        """Get the httpx client session."""
        self._ensure_session()
        if self._session is None:
            raise RuntimeError('Client session not initialized.')
        return self._session

    def __enter__(self) -> Pararamio:
        """Context manager entry."""
        return self.connect()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Context manager exit."""
        self.close()

    def connect(self) -> Pararamio:
        """Connect and initialize client session.

        This method allows using the client without context manager.
        You must call close() when done to clean up resources.

        Returns:
            Self for chaining

        Example:
            >>> client = Pararamio(  # pragma: allowlist secret
            ...     login='user@example.com', password='pass'
            ... )
            >>> client.connect()
            >>> try:
            ...     profile = client.get_profile()
            ... finally:
            ...     client.close()
        """
        # Ensure session is created
        self._ensure_session()
        # Load cookies from cookie manager to session
        self._load_cookies_to_session()
        # Check for XSRF token in cookies
        self._check_xsrf_token()
        return self

    def close(self) -> None:
        """Close the client session and save cookies.

        This method should be called when done with manual session management.
        Automatically called when using context manager.

        Example:
            >>> client = Pararamio(  # pragma: allowlist secret
            ...     login='user@example.com', password='pass'
            ... )
            >>> client.connect()
            >>> try:
            ...     profile = client.get_profile()
            ... finally:
            ...     client.close()
        """
        # Save cookies if we have a cookie manager
        self._save_cookie()
        # Close session if it exists
        if self._session:
            self._session.close()

    def get_cookies(self) -> httpx.Cookies:
        """
        Retrieve the cookie jar containing authentication cookies.

        Checks if the user is authenticated, and if not, performs the authentication process first.
        Once authenticated, returns the cookie jar.

        Returns:
            httpx Cookies object
        """
        if not self._authenticated:
            self.authenticate()

        return self.session.cookies

    def get_headers(self) -> dict[str, str]:
        """
        Get the headers to be used in requests.

        Checks if the user is authenticated, performs authentication if not authenticated,
        and returns the headers.

        Returns:
            Dict[str, str]: The headers to be used in the request.
        """
        if not self._authenticated:
            self.authenticate()
        return self.__headers

    def _save_cookie(self) -> None:
        """
        Save cookies from httpx cookie jar to cookie manager.
        """
        if not self._cookie_manager or not self._session:
            return

        # Only save if we have cookies in session
        if self._session.cookies:
            for cookie in self._session.cookies.jar:
                processed_cookie = process_cookie_for_storage(cookie)
                self._cookie_manager.add_cookie(processed_cookie)

            # Save cookies after updating
            self._cookie_manager.save_cookies()

    def _profile(self) -> ProfileTypeT:
        """

        Fetches the user profile data from the API.


        Returns:
        - ProfileTypeT: The unescaped user profile data retrieved from the API.

        """
        result = self.api_get('/user/me', response_model=ProfileTypeT)
        return unescape_dict(result, keys=['name'])

    def _do_auth(
        self,
        login: str,
        password: str,
        headers: dict[str, str],
        *,
        second_step_fn: SecondStepFnT,
        second_step_arg: str,
    ) -> None:
        """
        Authenticate the user and set the necessary headers for future requests.

        Args:
            login (str): The user's login name.
            password (str): The user's password.
            headers (Dict[str, str]): The headers to be included in the request.
            second_step_fn (SecondStepFnT): The function to handle
                                            the second step of authentication if required.
            second_step_arg (str): An argument for the second step function.

        Returns:
            None

        Sets:
            self._authenticated (bool): True if authentication is successful, False otherwise.
            self.__headers[XSRF_HEADER_NAME] (str): The XSRF token if authentication is successful.
        """
        self._authenticated, _, xsrf = authenticate(
            login,
            password,
            self.session,
            headers,
            second_step_fn=second_step_fn,
            second_step_arg=second_step_arg,
            wait_auth_limit=self._wait_auth_limit,
        )
        if self._authenticated:
            self.__headers[XSRF_HEADER_NAME] = xsrf
            self._save_cookie()

    def _authenticate(
        self,
        second_step_fn: SecondStepFnT,
        second_step_arg: str,
        login: str | None = None,
        password: str | None = None,
    ) -> bool:
        """
        Authenticate the user with the provided login and password,
        performing a secondary step if necessary.

        Arguments:
        second_step_fn: Function to execute for the second step of the authentication process
        second_step_arg: Argument to pass to the second step function
        login: Optional login name. If not provided,
               it will use login stored within the class instance.
        password: Optional password. If not provided,
                  it will use the password stored within the class instance.

        Returns:
        bool: True if authentication is successful, False otherwise

        Raises:
        PararamioAuthenticationError: If login or password is not provided or empty

        Exceptions:
        PararamioHTTPRequestError:
                        Raised if there is an error during the HTTP request in the profile check.

        """
        login = login or self._login or ''
        password = password or self._password or ''
        if not check_login_opts(login, password):
            raise PararamioAuthenticationError(
                f'{get_empty_vars(login=login, password=password)} must be set and not empty'
            )

        try:
            self._authenticated = True
            self._profile()
        except PararamioHTTPRequestError:
            self._authenticated = False
            self._do_auth(
                login,
                password,
                self.__headers,
                second_step_fn=second_step_fn,
                second_step_arg=second_step_arg,
            )
        return self._authenticated

    def authenticate(
        self,
        login: str | None = None,
        password: str | None = None,
        key: str | None = None,
    ) -> bool:
        """
        Authenticate a user using either a login and password or a key.

        This method attempts to authenticate a user through provided login credentials
        or a predefined key. If the key is not provided, it will use the instance key
        stored in `self._key`.

        Args:
            login (str, optional): The user's login name. Defaults to None.
            password (str, optional): The user's password. Defaults to None.
            key (str, optional): A predefined key for authentication. Defaults to None.

        Returns:
            bool: True if authentication is successful, False otherwise.

        Raises:
            PararamioAuthenticationError: If no key is provided.

        """
        key = key or self._key
        if not key:
            raise PararamioAuthenticationError('key must be set and not empty')
        return self._authenticate(do_second_step, key, login, password)

    def authenticate_with_code(
        self,
        code: str,
        login: str | None = None,
        password: str | None = None,
    ) -> bool:
        """

        Authenticates a user using a provided code and optionally login and password.

        Parameters:
          code (str): The authentication code. Must be set and not empty.
          login (str, optional): The user login. Default is None.
          password (str, optional): The user password. Default is None.

        Returns:
          bool: True if authentication is successful, otherwise raises an exception.

        Raises:
          PararamioAuthenticationError: If the code is not provided or is empty.
        """
        if not code:
            raise PararamioAuthenticationError('code must be set and not empty')
        return self._authenticate(do_second_step_with_code, code, login, password)

    def _api_request(  # pylint: disable=too-many-branches
        self,
        url: str,
        method: str = 'GET',
        data: dict[str, Any] | None = None,
        *,
        callback: Callable[..., Any] = lambda rsp: rsp,
    ) -> Any:
        """
        Performs an authenticated API request with XSRF token management and error handling.

        Args:
            url (str): The API endpoint URL to which the request is made.
            method (str): The HTTP method to use for the request. Defaults to 'GET'.
            data (Optional[dict]): The data payload for the request, if applicable.
                                   Defaults to None.
            callback (Callable): A callback function to process the response.
                                 Defaults to a lambda that returns the response.

        Returns:
            Any: The result of the callback processing on the API request response.

        Raises:
            PararamioHTTPRequestError: If an HTTP error occurs.

        Notes:
            - The function ensures that the user is authenticated before making the request.
            - Manages the XSRF token by retrieving and saving it as needed.
            - Handles specific error cases by attempting re-authentication or
              renewing the XSRF token.
        """
        if not self._authenticated:
            self.authenticate()
        if not self.__headers.get(XSRF_HEADER_NAME, None):
            self.__headers[XSRF_HEADER_NAME] = get_xsrf_token(self.session)
            self._save_cookie()
        try:
            return callback(
                api_request(
                    url,
                    method=method,
                    data=data,
                    client=self.session,
                    headers=self.__headers,
                )
            )
        except PararamioHTTPRequestError as e:
            message = e.message
            code = e.code

            # XSRF token errors should always be retried
            if message == 'xsrf':
                log.info('xsrf is expire, invalid or was not set, trying to get new one')
                self.__headers[XSRF_HEADER_NAME] = ''
                return self._api_request(
                    url=url,
                    method=method,
                    data=data,
                    callback=callback,
                )

            # Retry for rate limits (429) and server errors (500-599)
            if code == 429 or 500 <= code < 600:
                log.warning('Retryable error %d, attempting retry', code)
                return self._api_request(
                    url=url,
                    method=method,
                    data=data,
                    callback=callback,
                )

            # All other errors (401, 403, 404, etc.) should raise immediately
            raise

    @overload
    def api_get(
        self,
        url: str,
        *,
        cacheable: bool = False,
        cache_key: str | None = None,
        cache_key_fn: Callable[[str], str] | None = None,
        validator: Callable[[Any], str | None] | None = None,
    ) -> dict[str, Any]: ...

    @overload
    def api_get(
        self,
        url: str,
        *,
        response_model: type[T],
        cacheable: bool = False,
        cache_key: str | None = None,
        cache_key_fn: Callable[[str], str] | None = None,
        validator: Callable[[Any], str | None] | None = None,
    ) -> T: ...

    def api_get(
        self,
        url: str,
        *,
        response_model: type[T] | None = None,
        cacheable: bool = False,
        cache_key: str | None = None,
        cache_key_fn: Callable[[str], str] | None = None,
        validator: Callable[[Any], str | None] | None = None,
    ) -> T | dict[str, Any]:
        """
        Handles HTTP GET requests to the specified API endpoint with optional caching.

        Arguments:
            url (str): The URL of the API endpoint.
            response_model: Optional type to cast the response to.
            cacheable: Whether this request can be cached (default: False).
            cache_key: Explicit cache key to use.
            cache_key_fn: Function to generate a cache key from URL.
            validator: Optional function to validate response. Should return None on success
                      or an error message on failure.

        Returns:
            dict or cast to response_model: The JSON response from the API.

        Raises:
            PararamioValidationError: If validator returns an error message
        """
        # Determine a cache key if caching is enabled
        key = None
        if self._cache is not None and cacheable:
            if cache_key:
                key = cache_key
            elif cache_key_fn:
                key = cache_key_fn(url)

            # Try to get from cache
            if key:
                cached = self._cache.get(key)
                if cached is not None:
                    return cached if not response_model else cast('T', cached)

        # Make the API request
        response = self._api_request(url)

        # Validate response
        if validator:
            error = validator(response)
            if error is not None:
                raise PararamioValidationError(str(error))

        # Cache successful response if caching is enabled
        if self._cache is not None and cacheable and key:
            self._cache.set(key, response)  # TTL will be determined by cache

        if response_model:
            return cast('T', response)

        return cast('dict[str, Any]', response)

    def _process_mutation_response(
        self,
        response: Any,
        *,
        validator: Callable[[Any], str | None] | None = None,
        invalidate_tags: list[str] | None = None,
        response_model: type[T] | None = None,
    ) -> T | dict[str, Any]:
        """Process mutation response with validation and cache invalidation.

        Args:
            response: The response from API request
            validator: Optional function to validate response
            invalidate_tags: List of cache tags to invalidate after successful mutation
            response_model: Optional type to cast the response to

        Returns:
            Validated and optionally cast response

        Raises:
            PararamioValidationError: If validator returns an error message
        """
        if validator:
            error = validator(response)
            if error is not None:
                raise PararamioValidationError(str(error))

        # Invalidate cache tags after successful mutation
        if self._cache is not None and invalidate_tags:
            self._cache.invalidate_tags(invalidate_tags)

        if response_model:
            return cast('T', response)

        return cast('dict[str, Any]', response)

    @overload
    def api_post(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        *,
        validator: Callable[[Any], str | None] | None = None,
        invalidate_tags: list[str] | None = None,
    ) -> dict[str, Any]: ...

    @overload
    def api_post(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        *,
        response_model: type[T],
        validator: Callable[[Any], str | None] | None = None,
        invalidate_tags: list[str] | None = None,
    ) -> T: ...

    def api_post(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        *,
        response_model: type[T] | None = None,
        validator: Callable[[Any], str | None] | None = None,
        invalidate_tags: list[str] | None = None,
    ) -> T | dict[str, Any]:
        """
        Sends a POST request to the specified URL with the given data.

        Parameters:
            url (str): The endpoint URL where the POST request should be sent.
            data (Optional[Dict[Any, Any]], optional):
                                The payload to be sent in the POST request body.
                                Defaults to None.
            response_model: Optional type to cast the response to
            validator: Optional function to validate response. Should return None on success
                      or an error message on failure.
            invalidate_tags: List of cache tags to invalidate after successful mutation

        Returns:
            dict or cast to response_model: The response from the server.

        Raises:
            PararamioValidationError: If validator returns an error message
        """
        response = self._api_request(url, method='POST', data=data)
        return self._process_mutation_response(
            response,
            validator=validator,
            invalidate_tags=invalidate_tags,
            response_model=response_model,
        )

    @overload
    def api_put(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        *,
        validator: Callable[[Any], str | None] | None = None,
        invalidate_tags: list[str] | None = None,
    ) -> dict[str, Any]: ...

    @overload
    def api_put(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        *,
        response_model: type[T],
        validator: Callable[[Any], str | None] | None = None,
        invalidate_tags: list[str] | None = None,
    ) -> T: ...

    def api_put(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        *,
        response_model: type[T] | None = None,
        validator: Callable[[Any], str | None] | None = None,
        invalidate_tags: list[str] | None = None,
    ) -> T | dict[str, Any]:
        """
        Sends a PUT request to the specified URL with the provided data.

        Parameters:
        - url: The URL to send the PUT request to.
        - data: Optional dictionary containing the data to include in the request body.
        - response_model: Optional type to cast the response to
        - validator: Optional function to validate response. Should return None on success
                    or an error message on failure.
        - invalidate_tags: List of cache tags to invalidate after successful mutation

        Returns:
        dict or cast to response_model: The server's response to the PUT request.

        Raises:
            PararamioValidationError: If validator returns an error message
        """
        response = self._api_request(url, method='PUT', data=data)
        return self._process_mutation_response(
            response,
            validator=validator,
            invalidate_tags=invalidate_tags,
            response_model=response_model,
        )

    @overload
    def api_delete(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        *,
        validator: Callable[[Any], str | None] | None = None,
        invalidate_tags: list[str] | None = None,
    ) -> dict[str, Any]: ...

    @overload
    def api_delete(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        *,
        response_model: type[T],
        validator: Callable[[Any], str | None] | None = None,
        invalidate_tags: list[str] | None = None,
    ) -> T: ...

    def api_delete(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        *,
        response_model: type[T] | None = None,
        validator: Callable[[Any], str | None] | None = None,
        invalidate_tags: list[str] | None = None,
    ) -> T | dict[str, Any]:
        """
        Sends a DELETE request to the specified URL with optional data.

        Parameters:
        url (str): The URL to send the DELETE request to.
        data (Optional[Dict[str, Any]], optional): Optional payload to include in the request.
        response_model: Optional type to cast the response to
        validator: Optional function to validate response. Should return None on success
                  or an error message on failure.
        invalidate_tags: List of cache tags to invalidate after successful mutation

        Returns:
        dict or cast to response_model: The response from the API request.

        Raises:
            PararamioValidationError: If validator returns an error message
        """
        response = self._api_request(url, method='DELETE', data=data)
        return self._process_mutation_response(
            response,
            validator=validator,
            invalidate_tags=invalidate_tags,
            response_model=response_model,
        )

    def _upload_file(
        self,
        file: BinaryIO | BytesIO,
        chat_id: int,
        *,
        filename: str | None = None,
        type_: str | None = None,
        organization_id: int | None = None,
        reply_no: int | None = None,
        quote_range: str | None = None,
    ) -> FileResponse:
        """
        _upload_file is a method for uploading a file to a specified chat or organization.

        Arguments:
            file: A binary stream of the file to be uploaded.
            chat_id: The ID of the chat where the file will be uploaded.
            filename: An optional parameter that specifies the name of the file.
            type_: An optional parameter that specifies the type of file being uploaded.
                   If not provided, it will be inferred from the filename.
            organization_id: An optional parameter that specifies the ID of the organization
                             if the file is an organization avatar.
            reply_no: An optional parameter that specifies the reply number
                      associated with the file.
            quote_range: An optional parameter that specifies the range
                         of quotes associated with the file.

        Returns:
            FileResponse with the response from the xupload_file function.

        Raises:
            PararamioValidationError: If filename is not set when type is None,
            or if organization_id is not set when type is organization_avatar,
            or if chat_id is not set when type is chat_avatar.

        Notes:
            This method ensures that the necessary headers and
            tokens are set before attempting the file upload.
        """
        if not self._authenticated:
            self.authenticate()
        if not self.__headers.get(XSRF_HEADER_NAME, None):
            self.__headers[XSRF_HEADER_NAME] = get_xsrf_token(self.session)

        fields, content_type = CorePost.prepare_file_upload_fields(
            file=file,
            chat_id=chat_id,
            filename=filename,
            type_=type_,
            organization_id=organization_id,
            reply_no=reply_no,
            quote_range=quote_range,
        )
        # Convert FileUploadFields to a list of tuples for xupload_file
        fields_list: list[tuple[str, str | int | None]] = [
            (k, cast('str | int | None', v)) for k, v in fields.items()
        ]
        return xupload_file(
            fp=file,
            fields=fields_list,
            filename=filename,
            content_type=content_type,
            headers=self.__headers,
            client=self.session,
        )

    def upload_file(
        self,
        file: str | BytesIO | BinaryIO | os.PathLike[str],
        chat_id: int,
        *,
        filename: str | None = None,
        content_type: str | None = None,
        reply_no: int | None = None,
        quote_range: str | None = None,
    ) -> File:
        """
        upload_file uploads a file to a specified chat.

        Parameters:
        file: Union[str, BytesIO, os.PathLike] The file to be uploaded. It can be a file path,
              a BytesIO object, or an os.PathLike object.
        chat_id: int
            The ID of the chat where the file should be uploaded.
        filename: Optional[str]
            The name of the file.
            If not specified and the file is a path, the basename of the file path will be used.
        content_type: Optional[str]
            The MIME type of the file.
        reply_no: Optional[int]
            The reply number in the chat to which this file is in response.
        quote_range: Optional[str]
            The range of messages being quoted.

        Returns:
        File
            An instance of the File class representing the uploaded file.
        """
        if isinstance(file, str | os.PathLike):
            filename = filename or Path(file).name
            with Path(file).open('rb') as f:
                res = self._upload_file(
                    f,
                    chat_id,
                    filename=filename,
                    type_=content_type,
                    reply_no=reply_no,
                    quote_range=quote_range,
                )
        else:
            res = self._upload_file(
                file,
                chat_id,
                filename=filename,
                type_=content_type,
                reply_no=reply_no,
                quote_range=quote_range,
            )
        # res is FileResponse from _upload_file, pass it directly to File constructor
        return File(self, **res)

    def delete_file(self, guid: str) -> DeleteFileResponse:
        """
        Deletes a file identified by the provided GUID.

        Args:
            guid (str): The globally unique identifier of the file to be deleted.

        Returns:
            DeleteFileResponse: The result of the deletion operation.

        """
        return delete_file(guid, headers=self.__headers, client=self.session)

    def download_file(self, guid: str, filename: str) -> BytesIO:
        """
        Downloads and returns a file as a BytesIO object given its unique identifier and filename.

        Args:
            guid (str): The unique identifier of the file to be downloaded.
            filename (str): The name of the file to be downloaded.

        Returns:
            BytesIO: A BytesIO object containing the downloaded file content.
        """
        return download_file(guid, filename, headers=self.__headers, client=self.session)

    def get_profile(self) -> ProfileTypeT:
        """
        Get the user profile.

        If the profile is not yet initialized, this method will initialize it by calling the
        _profile method.

        Returns:
            ProfileTypeT: The profile object.
        """
        if not self.__profile:
            self.__profile = self._profile()
        return self.__profile

    def search_users(self, query: str, include_self: bool = False) -> list[UserSearchResult]:
        """Search for users based on the given query string.

        Parameters:
        query (str): The search query used to find matching users.
        include_self (bool): Whether to include current user in results. Default is False.

        Returns:
        List[UserSearchResult]: A list of User objects that match the search query.
        """
        return User.search(self, query, include_self)

    def search_chats(
        self, query: str, *, chat_type: str = 'all', visibility: str = 'all'
    ) -> list[Chat]:
        """Search for chats.

        Args:
            query: Search string
            chat_type: Filter by type (all, private, group, etc.)
            visibility: Filter by visibility (all, visible, hidden)

        Returns:
            List of Chat objects matching the search criteria
        """
        return Chat.search(self, query, chat_type=chat_type, visibility=visibility)

    def search_posts_lazy(
        self,
        query: str,
        *,
        order_type: str = 'time',
        chat_ids: list[int] | None = None,
        max_results: int | None = None,
        per_page: int = POSTS_LIMIT,
    ) -> Iterable[Post]:
        """Search for posts with lazy loading pagination.

        Args:
            query: A search query
            order_type: Order type ('time' or 'relevance')
            chat_ids: Optional list of chat IDs to filter by
            max_results: Maximum total results to fetch (None = unlimited)
            per_page: Number of posts to fetch per page

        Yields:
            Post objects one at a time

        Example:
            >>> for post in client.search_posts_lazy('hello', max_results=100):
            ...     print(post.text)
        """
        return Chat.search_posts_lazy(
            self,
            query,
            order_type=order_type,
            chat_ids=chat_ids,
            max_results=max_results,
            per_page=per_page,
        )

    def search_posts(
        self,
        query: str,
        *,
        order_type: str = 'time',
        page: int = 1,
        chat_ids: list[int] | None = None,
        limit: int | None = None,
    ) -> tuple[int, Iterable[Post]]:
        """

        search_posts searches for posts based on a given query and various optional parameters.

        Arguments:
        - query: The search term used to find posts.
        - order_type: Specifies the order of the search results. Default is 'time'.
        - page: The page number of the search results to retrieve. Default is 1.
        - chat_ids: Optional list of chat IDs to search within. If None, search in all chats.
        - limit: The maximum number of posts to return. If None, use the default limit.

        Returns:
        - A tuple containing the total number of posts matching
          the search query and an iterable of Post objects.
        """
        # Generate cache key
        cache_key = generate_cache_key(
            'posts',
            'search',
            query=query,
            order_type=order_type,
            page=page,
            chat_ids=str(chat_ids) if chat_ids else None,
            limit=limit,
        )

        # Check cache first if available
        if self._cache is not None:
            cached = self._cache.get(cache_key)
            if cached is not None:
                return cast('tuple[int, Iterable[Post]]', cached)

        # Fetch from API
        result = Chat.search_posts(
            self, query, order_type=order_type, page=page, chat_ids=chat_ids, limit=limit
        )

        # Cache the result
        if self._cache is not None:
            self._cache.set(cache_key, result, ttl=timedelta(minutes=2))

        return result

    def get_post(self, chat_id: int, post_no: int) -> Post | None:
        """Get a specific post by chat ID and post-number.

        Args:
            chat_id: Chat ID
            post_no: Post number

        Returns:
            Post object or None if not found
        """
        try:
            return Chat(self, chat_id=chat_id).get_post(post_no)
        except (IndexError, KeyError, PararamioHTTPRequestError):
            return None

    def get_chats_by_ids(self, ids: Sequence[int]) -> list[Chat]:
        """Get multiple chats by IDs.

        Args:
            ids: Sequence of chat IDs

        Returns:
            List of chat objects
        """
        if not ids:
            return []

        # Convert to sorted tuple for a consistent cache key
        ids_tuple = tuple(sorted(ids))

        # Generate a cache key
        cache_key = generate_cache_key('chats', 'get_by_ids', ids=str(ids_tuple))

        # Check cache first if available
        if self._cache is not None:
            cached = self._cache.get(cache_key)
            if cached is not None:
                return cast('list[Chat]', cached)

        # Fetch from API
        url = f'/core/chat?ids={",".join(map(str, ids))}'
        response = self.api_get(url)
        chats = []
        for chat_data in response.get('chats', []):
            chat = Chat.from_dict(self, chat_data)
            chats.append(chat)

        # Cache the result
        if self._cache is not None:
            self._cache.set(cache_key, chats, ttl=timedelta(minutes=5))

        return chats

    def list_chats(self) -> Iterable[Chat]:
        """
        Returns iterable that yields chat objects in a lazy-loading manner.
        The chats are fetched from the server using the specified URL and are returned in batches.

        Returns:
            Iterable: An iterable that yields chat objects.
        """
        url = '/core/chat/sync'
        chats_per_load = 50
        response = self.api_get(url, response_model=ChatListResponse)
        ids = response.get('chats', [])
        return lazy_loader(self, ids, Chat.load_chats, per_load=chats_per_load)

    def get_groups_ids(self) -> list[int]:
        """Get IDs of groups the current user belongs to.

        Returns:
            List of group IDs that the current user is a member of.
        """
        url = '/core/group/ids'
        response = self.api_get(url, response_model=dict[str, list[int]])
        return response.get('group_ids', [])

    def sync_groups(self, ids: list[int], sync_time: str) -> GroupSyncResponseT:
        """Synchronize groups with server.

        Args:
            ids: Current group IDs
            sync_time: Last synchronization time in UTC ISO datetime format

        Returns:
            Dict containing 'new', 'groups', and 'removed' group IDs
        """
        url = '/core/group/ids'
        data = {'ids': ids, 'sync_time': sync_time}
        response = self.api_post(url, data, response_model=GroupSyncResponseT)
        return {
            'new': response.get('new', []),
            'groups': response.get('groups', []),
            'removed': response.get('removed', []),
        }

    def get_groups_by_ids(self, ids: Sequence[int], load_per_request: int = 100) -> Iterable[Group]:
        """
        Fetches groups by their IDs.

        This method allows fetching groups by their IDs, using a
        lazy-loading technique which loads the data in smaller chunks to avoid high
        memory consumption.

        Args:
            ids: A sequence of group IDs to fetch.
            load_per_request: The number of groups to load per request. Defaults
                to 100.

        Returns:
            Iterable of Group objects.
        """
        # Convert to int sequence for lazy_loader
        int_ids = [int(id_) for id_ in ids]
        return lazy_loader(self, int_ids, Group.load_groups, per_load=load_per_request)

    def get_users_by_ids(self, ids: Sequence[int], load_per_request: int = 100) -> Iterable[User]:
        """
        Returns users by their IDs. Uses lazy loading in chunks to avoid
        high memory consumption.

        Args:
            ids: A sequence of user IDs to fetch.
            load_per_request: The number of users to load per request (max 100).

        Returns:
            Iterable of User objects.
        """
        return lazy_loader(self, ids, User.load_users, per_load=load_per_request)

    def get_user_by_id(self, user_id: int) -> User | None:
        """Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User object or None if not found
        """
        # Generate cache key
        cache_key = generate_cache_key('user', 'get', user_id)

        # Check cache first if available
        if self._cache is not None:
            cached = self._cache.get(cache_key)
            if cached is not None:
                return cast('User | None', cached)

        # Fetch from API
        try:
            users = list(self.get_users_by_ids([user_id]))
            result = users[0] if users else None
        except (PararamioException, IndexError, KeyError):
            result = None

        # Cache the result
        if self._cache is not None and result is not None:
            self._cache.set(cache_key, result, ttl=timedelta(minutes=5))

        return result

    def get_chat_by_id(self, chat_id: int) -> Chat | None:
        """Get a chat by ID.

        Args:
            chat_id: Chat ID

        Returns:
            Chat object or None if not found
        """
        try:
            # Direct instantiation since we know the ID
            chat = Chat(self, id=chat_id)
            # Try to load chat data to verify it exists
            chat.load()
            return chat
        except (PararamioException, IndexError, KeyError):
            return None

    def get_group_by_id(self, group_id: int) -> Group | None:
        """Get group by ID.

        Args:
            group_id: Group ID

        Returns:
            Group object or None if not found
        """
        try:
            groups = list(self.get_groups_by_ids([group_id]))
            return groups[0] if groups else None
        except (PararamioException, IndexError, KeyError):
            return None

    def create_chat(
        self,
        title: str,
        description: str = '',
        users: list[int] | None = None,
        groups: list[int] | None = None,
        organization_id: int | None = None,
        posts_live_time: str | None = None,
        two_step_required: bool | None = None,
        history_mode: str | None = None,
        org_visible: bool | None = None,
        allow_api: bool | None = None,
        read_only: bool | None = None,
    ) -> Chat:
        """Create a new chat.

        Args:
            title: Chat title
            description: Chat description
            users: Optional list of user IDs to add to the chat
            groups: Optional list of group IDs to add to the chat
            organization_id: Optional team ID
            posts_live_time: Optional posts lifetime in timedelta-sec format
            two_step_required: Optional two-step verification requirement
            history_mode: Optional history mode ('all' or 'since_join')
            org_visible: Optional organization visibility
            allow_api: Optional API access (deprecated)
            read_only: Optional read-only mode

        Returns:
            Created Chat instance
        """
        # Build kwargs with only non-None values using TypedDict
        kwargs: ChatCreateRequest = {
            'title': title,
            'description': description or '',
        }
        if users is not None:
            kwargs['users'] = users
        if groups is not None:
            kwargs['groups'] = groups
        if organization_id is not None:
            kwargs['organization_id'] = organization_id
        if posts_live_time is not None:
            kwargs['posts_live_time'] = posts_live_time
        if two_step_required is not None:
            kwargs['two_step_required'] = two_step_required
        if history_mode is not None:
            kwargs['history_mode'] = history_mode
        if org_visible is not None:
            kwargs['org_visible'] = org_visible
        if allow_api is not None:
            kwargs['allow_api'] = allow_api
        if read_only is not None:
            kwargs['read_only'] = read_only

        return Chat.create(self, **kwargs)

    def post_private_message_by_user_email(self, email: str, text: str) -> Post:
        """

        Posts a private message to a user identified by their email address.

        :param email: The email address of the user to whom the message will be sent.
        :type email: str
        :param text: The content of the message to be posted.
        :type text: str
        :return: A Post object representing the posted message.
        :rtype: Post
        """
        url = PRIVATE_MESSAGE_URL
        resp = self._api_request(url, method='POST', data={'text': text, 'user_email': email})
        return Post(Chat(self, chat_id=resp['chat_id']), post_no=resp['post_no'])

    def post_private_message_by_user_id(self, user_id: int, text: str) -> Post:
        """
        Send a private message to a specific user.

        Parameters:
        user_id (int): The ID of the user to whom the message will be sent.
        text (str): The content of the message to be sent.

        Returns:
        Post: The Post object containing information about the scent message.
        """
        url = PRIVATE_MESSAGE_URL
        resp = self._api_request(url, method='POST', data={'text': text, 'user_id': user_id})
        return Post(Chat(self, chat_id=resp['chat_id']), post_no=resp['post_no'])

    def post_private_message_by_user_unique_name(self, unique_name: str, text: str) -> Post:
        """
        Post a private message to a user identified by their unique name.

        Parameters:
        unique_name (str): The unique name of the user to whom the private message is to be sent.
        text (str): The content of the private message.

        Returns:
        Post: An instance of the Post class representing the posted message.
        """
        url = PRIVATE_MESSAGE_URL
        resp = self._api_request(
            url, method='POST', data={'text': text, 'user_unique_name': unique_name}
        )
        return Post(Chat(self, chat_id=resp['chat_id']), post_no=resp['post_no'])

    def mark_all_messages_as_read(self, org_id: int | None = None) -> bool:
        """

        Marks all messages as read for the organization or everywhere if org_id is None.

        Parameters:
        org_id (Optional[int]): The ID of the organization. This parameter is optional.

        Returns:
        bool: True if the operation was successful, False otherwise.
        """
        url = '/msg/lastread/all'
        data = {}
        if org_id is not None:
            data['org_id'] = org_id
        response = self.api_post(url, data, response_model=OkResponse)
        return response.get('result') == 'OK'

    def get_my_team_ids(self) -> list[int]:
        """Get IDs of teams the current user belongs to from the user profile.

        Returns:
            List of team IDs (organizations) that the current user is a member of.
        """
        # Always get fresh profile data
        profile = self.get_profile()
        return profile.get('organizations', [])

    def get_chat_tags(self) -> dict[str, list[int]]:
        """Get chat tags for the current user.

        Returns:
            Dictionary mapping tag names to lists of chat IDs.
        """
        response = self.api_get('/user/chat/tags', response_model=ChatTagsResponse)
        tags_dict: dict[str, list[int]] = {}
        for tag_data in response.get('chats_tags', []):
            tags_dict[tag_data['tag']] = tag_data['chat_ids']
        return tags_dict

    def get_teams_by_ids(self, ids: Sequence[int]) -> list[Team]:
        """Get teams (organizations) by their IDs.

        Args:
            ids: Sequence of team IDs to fetch.

        Returns:
            List of Team objects.
        """
        if not ids:
            return []

        teams = []
        # API supports max 50 IDs per request
        for i in range(0, len(ids), 50):
            chunk_ids = ids[i : i + 50]
            url = f'/core/org?ids={",".join(map(str, chunk_ids))}'
            response = self.api_get(url, response_model=TeamsResponse)
            for team_data in response.get('orgs', []):
                team = Team(self, **team_data)
                teams.append(team)
        return teams

    def get_my_teams(self) -> list[Team]:
        """Get all teams (organizations) that the current user belongs to.

        This is a convenience method that combines get_my_team_ids() and get_teams_by_ids().

        Returns:
            List of Team objects that the current user is a member of.
        """
        team_ids = self.get_my_team_ids()
        return self.get_teams_by_ids(team_ids)

    def get_sessions(self) -> list[SessionItem]:
        """Get all active sessions for the current user.

        Returns:
            List of session objects with details about each session including
            - Session ID
            - Browser and OS information
            - IP address and location
            - Login method used
            - Whether it's the current session
        """
        response = self.api_get('/auth/session', response_model=SessionsResponse)
        return response.get('data', [])
