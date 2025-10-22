"""Common authentication flow logic for sync and async clients."""

from __future__ import annotations

import base64
import binascii
import contextlib
import hashlib
import hmac
import time
from datetime import datetime

__all__ = (
    'AuthenticationFlow',
    'AuthenticationResult',
    'generate_otp',
)

from typing import Any


def generate_otp(key: str) -> str:
    """Generate one-time password from a TOTP key.

    Args:
        key: TOTP secret key

    Returns:
        6-digit OTP code

    Raises:
        binascii.Error: If key is invalid
    """
    digits = 6
    digest = hashlib.sha1
    interval = 30

    def byte_secret(s: str) -> bytes:
        missing_padding = len(s) % 8
        if missing_padding != 0:
            s += '=' * (8 - missing_padding)
        return base64.b32decode(s, casefold=True)

    def int_to_byte_string(i: int, padding: int = 8) -> bytes:
        result = bytearray()
        while i != 0:
            result.append(i & 0xFF)
            i >>= 8
        return bytes(bytearray(reversed(result)).rjust(padding, b'\0'))

    def time_code(for_time: datetime) -> int:
        i = time.mktime(for_time.timetuple())
        return int(i / interval)

    hmac_hash_bytes = hmac.new(
        byte_secret(key),
        int_to_byte_string(time_code(datetime.now())),  # noqa: DTZ005
        digest,
    ).digest()

    hmac_hash = bytearray(hmac_hash_bytes)
    offset = hmac_hash[-1] & 0xF
    code = (
        (hmac_hash[offset] & 0x7F) << 24
        | (hmac_hash[offset + 1] & 0xFF) << 16
        | (hmac_hash[offset + 2] & 0xFF) << 8
        | (hmac_hash[offset + 3] & 0xFF)
    )
    str_code = str(code % 10**digits)
    while len(str_code) < digits:
        str_code = '0' + str_code

    return str_code


class AuthenticationResult:
    """Result of an authentication attempt."""

    def __init__(  # pylint: disable=too-many-positional-arguments
        self,
        success: bool,
        xsrf_token: str | None = None,
        user_id: int | None = None,
        error: str | None = None,
        error_type: str | None = None,
        requires_captcha: bool = False,
        requires_totp: bool = False,
    ):
        self.success = success
        self.xsrf_token = xsrf_token
        self.user_id = user_id
        self.error = error
        self.error_type = error_type
        self.requires_captcha = requires_captcha
        self.requires_totp = requires_totp


class AuthenticationFlow:
    """Common authentication flow logic.

    This class provides the core authentication flow that can be used
    by both sync and async implementations.

    Rate limits for login attempts:
    - 3 attempts per minute
    - 10 attempts per 30 minutes
    """

    @staticmethod
    def prepare_login_data(email: str, password: str) -> dict[str, str]:
        """Prepare login data payload.

        Args:
            email: User email
            password: User password

        Returns:
            Dict with login data
        """
        return {'email': email, 'password': password}

    @staticmethod
    def prepare_totp_data(code: str) -> dict[str, str]:
        """Prepare TOTP data payload.

        Args:
            code: 6-digit TOTP code or key

        Returns:
            Dict with TOTP data
        """
        # If it's longer than 6 chars, it's likely a key
        if len(code) > 6:
            with contextlib.suppress(ValueError, binascii.Error):
                code = generate_otp(code)

        return {'code': code}

    @staticmethod
    def parse_error_response(response: dict[str, Any]) -> tuple[str, str]:
        """Parse error from API response.

        Args:
            response: API response dict

        Returns:
            Tuple of (error_type, error_message)
        """
        # Check for various error formats
        if 'error' in response:
            return 'error', response['error']

        if 'codes' in response:
            codes = response['codes']
            if isinstance(codes, dict):
                # Check for specific error codes
                if codes.get('non_field') == 'captcha_required':
                    return 'captcha_required', 'Captcha required'
                # Return-first error found
                for field, error in codes.items():
                    if error:
                        return field, error

        if 'message' in response:
            return 'message', response['message']

        return 'unknown', 'Unknown error'

    @staticmethod
    def should_retry_with_new_xsrf(error_type: str, error_message: str) -> bool:  # noqa: ARG004  # pylint: disable=unused-argument
        """Check if we should retry with a new XSRF token.

        Args:
            error_type: Type of error
            error_message: Error message

        Returns:
            True if you should retry
        """
        # Common XSRF-related errors
        xsrf_errors = ['xsrf', 'csrf', 'token']
        error_lower = error_message.lower()

        return any(err in error_lower for err in xsrf_errors)

    @staticmethod
    def parse_rate_limit_info(headers: dict[str, str]) -> int | None:
        """Parse rate limit information from response headers.

        Args:
            headers: Response headers

        Returns:
            Retry-after seconds if rate limited, None otherwise
        """
        retry_after = headers.get('Retry-After', headers.get('retry-after'))
        if retry_after:
            try:
                return int(retry_after)
            except ValueError:
                # Default to 60 seconds if you can't parse
                return 60
        # Default retry after for rate limits
        return 60
