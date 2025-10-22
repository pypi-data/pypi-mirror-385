from __future__ import annotations

import binascii
import json
import logging
import time
from typing import TYPE_CHECKING, Any
from urllib.error import HTTPError

from pararamio._core import exceptions as ex
from pararamio._core.constants import XSRF_HEADER_NAME
from pararamio._core.exceptions import RateLimitError
from pararamio._core.utils.auth_flow import generate_otp
from pararamio._core.utils.http_client import RateLimitHandler
from pararamio._core.utils.logging_config import (
    LoggerManager,
    get_logger,
)

try:
    from pararamio._core.utils.captcha import show_captcha

    HAS_CAPTCHA = True
except ImportError:
    HAS_CAPTCHA = False
    show_captcha = None

from .requests import api_request, raw_api_request

if TYPE_CHECKING:
    import httpx
    from pararamio._core._types import HeaderLikeT, SecondStepFnT

__all__ = (
    'authenticate',
    'do_second_step',
    'do_second_step_with_code',
    'get_xsrf_token',
)

XSRF_URL = INIT_URL = '/auth/init'
LOGIN_URL = '/auth/login/password'
TWO_STEP_URL = '/auth/totp'
AUTH_URL = '/auth/next'

# Get component-specific loggers
log = logging.getLogger('pararamio')  # Keep for backward compatibility
auth_logger = get_logger(LoggerManager.AUTH)
rate_limit_logger = get_logger(LoggerManager.RATE_LIMIT)
session_logger = get_logger(LoggerManager.SESSION)


def get_xsrf_token(client: httpx.Client) -> str:
    auth_logger.debug('Requesting XSRF token from %s', XSRF_URL)
    _, headers = raw_api_request(XSRF_URL, client=client)
    for key, value in headers:
        if key.lower() == 'x-xsrftoken':
            # Only log first 8 chars for security
            auth_logger.debug('XSRF token obtained: %s...', value[:8] if len(value) > 8 else '***')
            return value
    auth_logger.error('XSRF token not found in response headers')
    msg = f'XSRF Header was not found in {XSRF_URL} url'
    raise ex.PararamioXSRFRequestError(msg)


def do_init(client: httpx.Client, headers: dict[str, str]) -> tuple[bool, dict[str, Any]]:
    auth_logger.debug('Initializing authentication session')
    try:
        result = api_request(
            INIT_URL,
            method='GET',
            headers=headers,
            client=client,
        )
        auth_logger.debug('Authentication session initialized successfully')
        return True, result
    except HTTPError as e:
        if e.code < 500:
            auth_logger.warning('Session init failed with status %d', e.code)
            return False, json.loads(e.read())
        auth_logger.error('Session init server error: %d', e.code)
        raise


def do_login(
    login: str, password: str, client: httpx.Client, headers: dict[str, str]
) -> tuple[bool, dict[str, Any]]:
    auth_logger.info('Attempting login for user: %s', login)
    try:
        result = api_request(
            LOGIN_URL,
            method='POST',
            data={'email': login, 'password': password},
            headers=headers,
            client=client,
        )
        auth_logger.info('Login successful for user: %s', login)
        return True, result
    except HTTPError as e:
        if e.code < 500:
            auth_logger.warning('Login failed for user %s with status %d', login, e.code)
            return False, json.loads(e.read())
        auth_logger.error('Login server error for user %s: %d', login, e.code)
        raise


def do_taking_secret(client: httpx.Client, headers: dict[str, str]) -> tuple[bool, dict[str, Any]]:
    try:
        return True, api_request(
            AUTH_URL,
            method='GET',
            headers=headers,
            client=client,
        )
    except HTTPError as e:
        if e.code < 500:
            return False, json.loads(e.read())
        raise


def do_second_step(
    client: httpx.Client, headers: dict[str, str], key: str
) -> tuple[bool, dict[str, str]]:
    """
    do second step pararam login with a TFA key or raise Exception
    :param client: httpx client
    :param headers: headers to send
    :param key: key to generate one time code
    :return: True if login success
    """
    auth_logger.debug('Starting 2FA with TOTP key')
    if not key:
        auth_logger.error('2FA key is empty')
        msg = 'key can not be empty'
        raise ex.PararamioSecondFactorAuthenticationError(msg)
    try:
        key = generate_otp(key)
        auth_logger.debug('Generated OTP code from key')
    except binascii.Error as e:
        auth_logger.error('Invalid 2FA key format')
        msg = 'Invalid second step key'
        raise ex.PararamioSecondFactorAuthenticationError(msg) from e
    try:
        resp = api_request(
            TWO_STEP_URL,
            method='POST',
            data={'code': key},
            headers=headers,
            client=client,
        )
        auth_logger.debug('2FA code accepted')
    except HTTPError as e:
        if e.code < 500:
            auth_logger.warning('2FA failed with status %d', e.code)
            return False, json.loads(e.read())
        auth_logger.error('2FA server error: %d', e.code)
        raise
    return True, resp


def do_second_step_with_code(
    client: httpx.Client, headers: dict[str, str], code: str
) -> tuple[bool, dict[str, str]]:
    """
    do second step pararam login with TFA code or raise Exception
    :param client: httpx client
    :param headers: headers to send
    :param code: 6 digits code
    :return:  True if login success
    """
    if not code:
        msg = 'code can not be empty'
        raise ex.PararamioSecondFactorAuthenticationError(msg)
    if len(code) != 6:
        msg = 'code must be 6 digits len'
        raise ex.PararamioSecondFactorAuthenticationError(msg)
    try:
        resp = api_request(
            TWO_STEP_URL,
            method='POST',
            data={'code': code},
            headers=headers,
            client=client,
        )
    except HTTPError as e:
        if e.code < 500:
            return False, json.loads(e.read())
        raise
    return True, resp


def _handle_rate_limit(wait_auth_limit: bool) -> None:
    """Handle rate limiting before authentication."""
    rate_limit_handler = RateLimitHandler()
    should_wait, wait_seconds = rate_limit_handler.should_wait()
    if should_wait:
        if wait_auth_limit:
            rate_limit_logger.warning(
                'Rate limit active, waiting %d seconds before authentication', wait_seconds
            )
            time.sleep(wait_seconds)
            rate_limit_logger.debug('Rate limit wait completed')
        else:
            rate_limit_logger.error(
                'Rate limit exceeded, would need to wait %d seconds', wait_seconds
            )
            msg = f'Rate limit exceeded. Retry after {wait_seconds} seconds'
            raise RateLimitError(msg, retry_after=wait_seconds)


def _handle_captcha(
    login: str, password: str, client: httpx.Client, headers: dict[str, Any], resp: dict[str, Any]
) -> tuple[bool, tuple[bool, dict[str, Any]]]:
    """Handle captcha requirement during authentication.

    Returns:
        Tuple of (was_captcha_required, (success, response))
    """
    if resp.get('codes', {}).get('non_field', '') != 'captcha_required':
        return False, (False, resp)

    auth_logger.info('Captcha required for user: %s', login)

    if not HAS_CAPTCHA:
        auth_logger.error('Captcha module not available')
        msg = 'Captcha required, but captcha module not available'
        raise ex.PararamioCaptchaAuthenticationError(msg)

    # show_captcha is guaranteed to be callable here (HAS_CAPTCHA is True)
    assert show_captcha is not None
    auth_logger.debug('Showing captcha for user: %s', login)
    success = show_captcha(f'login:{login}', headers, client.cookies.jar)
    if not success:
        auth_logger.error('Captcha verification failed for user: %s', login)
        msg = 'Captcha required'
        raise ex.PararamioCaptchaAuthenticationError(msg)

    auth_logger.info('Captcha solved, retrying login for user: %s', login)
    return True, do_login(login, password, client, headers)


def authenticate(
    login: str,
    password: str,
    client: httpx.Client,
    headers: HeaderLikeT | None = None,
    second_step_fn: SecondStepFnT | None = do_second_step,
    second_step_arg: str | None = None,
    wait_auth_limit: bool = False,
) -> tuple[bool, dict[str, Any], str]:
    auth_logger.info(
        'Starting authentication for user: %s (2FA: %s)',
        login,
        'enabled' if second_step_arg else 'disabled',
    )
    start_time = time.perf_counter()

    # Handle rate limiting
    _handle_rate_limit(wait_auth_limit)

    if not headers or XSRF_HEADER_NAME not in headers:
        if headers is None:
            headers = {}
        auth_logger.debug('XSRF token not in headers, fetching new one')
        headers[XSRF_HEADER_NAME] = get_xsrf_token(client)

    success, resp = do_login(login, password, client, headers)

    # Handle captcha if required
    captcha_handled, captcha_result = _handle_captcha(login, password, client, headers, resp)
    if captcha_handled:
        success, resp = captcha_result

    if not success and resp.get('error', 'xsrf'):
        log.debug('invalid xsrf trying to get new one')
        auth_logger.warning('XSRF token invalid, fetching new one')
        headers[XSRF_HEADER_NAME] = get_xsrf_token(client)
        auth_logger.info('Retrying login with new XSRF token')
        success, resp = do_login(login, password, client, headers)

    if not success:
        error = resp.get('error', 'unknown')
        log.error('authentication failed: %s', error)
        auth_logger.error('Authentication failed for user %s: %s', login, error)
        msg = 'Login, password authentication failed'
        raise ex.PararamioPasswordAuthenticationError(msg)

    if second_step_fn is not None and second_step_arg:
        auth_logger.info('Performing second factor authentication')
        success, resp = second_step_fn(client, headers, second_step_arg)
        if not success:
            auth_logger.error('Second factor authentication failed for user: %s', login)
            msg = 'Second factor authentication failed'
            raise ex.PararamioSecondFactorAuthenticationError(msg)
        auth_logger.info('Second factor authentication successful')

    auth_logger.debug('Completing authentication flow')
    success, resp = do_taking_secret(client, headers)
    if not success:
        auth_logger.error('Failed to obtain authentication secret')
        msg = 'Taking secret failed'
        raise ex.PararamioAuthenticationError(msg)

    success, resp = do_init(client, headers)

    elapsed_ms = (time.perf_counter() - start_time) * 1000
    auth_logger.info(
        'Authentication completed successfully for user %s in %.2fms', login, elapsed_ms
    )

    # Log session establishment
    session_logger.info(
        'Session established for user: %s (user_id: %s)', login, resp.get('user_id', 'unknown')
    )

    return True, {'user_id': resp.get('user_id')}, headers[XSRF_HEADER_NAME]
