"""Utils package."""

# Re-export authentication utilities
# Note: show_captcha was removed from core as it's an example function
# Re-export helper utilities
from pararamio._core.utils.helpers import (
    encode_digit,
    parse_iso_datetime,
    rand_id,
)

from .authentication import (
    authenticate,
    do_second_step,
    do_second_step_with_code,
    get_xsrf_token,
)

# Re-export request utilities
from .requests import (
    api_request,
    raw_api_request,
)

__all__ = [
    # Requests
    'api_request',
    # Authentication
    'authenticate',
    'do_second_step',
    'do_second_step_with_code',
    # Helpers
    'encode_digit',
    'get_xsrf_token',
    'parse_iso_datetime',
    'rand_id',
    'raw_api_request',
]
