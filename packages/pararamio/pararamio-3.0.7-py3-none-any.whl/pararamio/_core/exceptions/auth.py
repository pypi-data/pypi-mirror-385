"""Authentication-specific exceptions."""

from __future__ import annotations

from .base import PararamioAuthenticationError

__all__ = (
    'CaptchaRequiredError',
    'InvalidCredentialsError',
    'RateLimitError',
    'SessionExpiredError',
    'TwoFactorFailedError',
    'TwoFactorRequiredError',
    'XSRFTokenError',
)


class InvalidCredentialsError(PararamioAuthenticationError):
    """Invalid login credentials."""

    def __init__(self, message: str = 'Invalid email or password'):
        super().__init__(message, error_code='invalid_credentials')


class XSRFTokenError(PararamioAuthenticationError):
    """XSRF token related errors."""

    def __init__(self, message: str = 'XSRF token validation failed'):
        super().__init__(message, error_code='xsrf_token_error')


class TwoFactorRequiredError(PararamioAuthenticationError):
    """Two-factor authentication is required."""

    def __init__(self, message: str = 'Two-factor authentication required'):
        super().__init__(message, error_code='2fa_required')


class TwoFactorFailedError(PararamioAuthenticationError):
    """Two-factor authentication failed."""

    def __init__(self, message: str = 'Invalid two-factor authentication code'):
        super().__init__(message, error_code='2fa_failed')


class CaptchaRequiredError(PararamioAuthenticationError):
    """Captcha verification required."""

    def __init__(
        self,
        message: str = 'Captcha verification required',
        captcha_url: str | None = None,
    ):
        super().__init__(message, error_code='captcha_required')
        self.captcha_url = captcha_url


class RateLimitError(PararamioAuthenticationError):
    """Rate limit exceeded (429 Too Many Requests)."""

    def __init__(
        self,
        message: str = 'Rate limit exceeded',
        retry_after: int | None = None,
    ):
        super().__init__(message, error_code='rate_limit', retry_after=retry_after)


class SessionExpiredError(PararamioAuthenticationError):
    """Session has expired."""

    def __init__(self, message: str = 'Session has expired, please authenticate again'):
        super().__init__(message, error_code='session_expired')
