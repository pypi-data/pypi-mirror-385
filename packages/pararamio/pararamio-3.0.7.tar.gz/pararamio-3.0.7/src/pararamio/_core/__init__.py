"""Core components for pararamio packages."""

from ._types import (
    BaseEvent,
    FormatterT,
    HeaderLikeT,
    MetaReplyT,
    PostMention,
    PostMetaFileT,
    PostMetaT,
    PostMetaThreadT,
    PostMetaUserT,
    ProfileTypeT,
    QuoteRangeT,
    SecondStepFnT,
    TextParsedT,
)

# Import from constants
# Import client protocols
from .client_protocol import AsyncClientProtocol, ClientProtocol
from .constants.base import (
    POSTS_LIMIT,
    REQUEST_TIMEOUT,
    UPLOAD_TIMEOUT,
    VERSION,
    XSRF_HEADER_NAME,
)
from .constants.endpoints import (
    AUTH_ENDPOINTS,
    AUTH_INIT_URL,
    AUTH_LOGIN_URL,
    AUTH_NEXT_URL,
    AUTH_TOTP_URL,
    CHAT_ENDPOINTS,
    FILE_ENDPOINTS,
    POST_ENDPOINTS,
    USER_ENDPOINTS,
)

# Import utilities
from .cookie_manager import CookieManagerBaseMixin

# Import exceptions
from .exceptions.auth import (
    CaptchaRequiredError,
    InvalidCredentialsError,
    RateLimitError,
    SessionExpiredError,
    TwoFactorFailedError,
    TwoFactorRequiredError,
    XSRFTokenError,
)
from .exceptions.base import (
    PararamioAuthenticationError,
    PararamioException,
    PararamioHTTPRequestError,
    PararamioLimitExceededError,
    PararamioMethodNotAllowedError,
    PararamioRequestError,
    PararamioSecondFactorAuthenticationError,
    PararamioServerResponseError,
    PararamioTypeError,
    PararamioValidationError,
    PararamMultipleFoundError,
    PararamNotFoundError,
)

# Import models
from .models import (
    CoreAttachment,
    CoreBot,
    CoreChat,
    CoreFile,
    CoreGroup,
    CorePoll,
    CorePost,
    CoreTeam,
    CoreTeamMember,
    CoreUser,
    SerializationMixin,
)
from .utils.auth_flow import AuthenticationFlow, AuthenticationResult, generate_otp
from .utils.http_client import (
    HTTPClientConfig,
    RateLimitHandler,
    RequestResult,
    build_url,
    prepare_headers,
    should_retry_request,
)
from .validators import validate_filename, validate_ids_list, validate_post_load_range

__version__ = VERSION

__all__ = [
    'AUTH_ENDPOINTS',
    'AUTH_INIT_URL',
    'AUTH_LOGIN_URL',
    'AUTH_NEXT_URL',
    'AUTH_TOTP_URL',
    'CHAT_ENDPOINTS',
    'FILE_ENDPOINTS',
    'POSTS_LIMIT',
    'POST_ENDPOINTS',
    'REQUEST_TIMEOUT',
    'UPLOAD_TIMEOUT',
    'USER_ENDPOINTS',
    'VERSION',
    'XSRF_HEADER_NAME',
    'AsyncClientProtocol',
    'AuthenticationFlow',
    'AuthenticationResult',
    'BaseEvent',
    'CaptchaRequiredError',
    'ClientProtocol',
    'CookieManagerBaseMixin',
    'CoreAttachment',
    'CoreBot',
    'CoreChat',
    'CoreFile',
    'CoreGroup',
    'CorePoll',
    'CorePost',
    'CoreTeam',
    'CoreTeamMember',
    'CoreUser',
    'FormatterT',
    'HTTPClientConfig',
    'HeaderLikeT',
    'InvalidCredentialsError',
    'MetaReplyT',
    'PararamMultipleFoundError',
    'PararamNotFoundError',
    'PararamioAuthenticationError',
    'PararamioException',
    'PararamioHTTPRequestError',
    'PararamioLimitExceededError',
    'PararamioMethodNotAllowedError',
    'PararamioRequestError',
    'PararamioSecondFactorAuthenticationError',
    'PararamioServerResponseError',
    'PararamioTypeError',
    'PararamioValidationError',
    'PostMention',
    'PostMetaFileT',
    'PostMetaT',
    'PostMetaThreadT',
    'PostMetaUserT',
    'ProfileTypeT',
    'QuoteRangeT',
    'RateLimitError',
    'RateLimitHandler',
    'RequestResult',
    'SecondStepFnT',
    'SerializationMixin',
    'SessionExpiredError',
    'TextParsedT',
    'TwoFactorFailedError',
    'TwoFactorRequiredError',
    'XSRFTokenError',
    'build_url',
    'generate_otp',
    'prepare_headers',
    'should_retry_request',
    'validate_filename',
    'validate_ids_list',
    'validate_post_load_range',
]
