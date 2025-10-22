"""Cookie handling utilities shared between sync and async implementations."""

from __future__ import annotations

from http.cookiejar import Cookie

__all__ = ['process_cookie_for_storage']


def process_cookie_for_storage(cookie: Cookie) -> Cookie:
    """Process a cookie for storage by removing quotes from value.

    Args:
        cookie: Original cookie from httpx session

    Returns:
        New Cookie object with unquoted value

    Note:
        This function creates a new Cookie object because the original
        cookie from httpx may have quoted values that need to be unquoted
        for proper storage in the cookie jar.
    """
    # Remove quotes from cookie value before saving
    cookie_value = cookie.value
    if cookie_value and cookie_value.startswith('"') and cookie_value.endswith('"'):
        cookie_value = cookie_value[1:-1]

    # Create new cookie with updated value
    return Cookie(
        version=cookie.version,
        name=cookie.name,
        value=cookie_value,
        port=cookie.port,
        port_specified=cookie.port_specified,
        domain=cookie.domain,
        domain_specified=cookie.domain_specified,
        domain_initial_dot=cookie.domain_initial_dot,
        path=cookie.path,
        path_specified=cookie.path_specified,
        secure=cookie.secure,
        expires=cookie.expires,
        discard=cookie.discard,
        comment=cookie.comment,
        comment_url=cookie.comment_url,
        # The _rest attribute is part of http.cookiejar.Cookie's internal API
        # It stores non-standard cookie attributes. We preserve these
        # for full cookie compatibility
        rest=getattr(cookie, '_rest', {}),
        rfc2109=cookie.rfc2109,
    )
