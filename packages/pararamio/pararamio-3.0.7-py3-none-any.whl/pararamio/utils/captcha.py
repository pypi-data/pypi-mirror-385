from __future__ import annotations

import base64
from typing import TYPE_CHECKING
from urllib.error import HTTPError
from urllib.parse import urlencode

from pararamio._core.constants import REQUEST_TIMEOUT as TIMEOUT

from .requests import _base_request, api_request

if TYPE_CHECKING:
    import httpx

__all__ = ['get_captcha_img', 'verify_captcha']


def get_captcha_img(
    id_: str,
    headers: dict[str, str] | None = None,
    client: httpx.Client | None = None,
    timeout: int = TIMEOUT,
) -> bytes:  # returns tk.PhotoImage
    """
    Fetch and return a captcha image as bytes from the server based on the provided id.
    The function retries the request a predetermined number of times if met with HTTPError,
    and encodes the resulting image data in base64 format before returning it.

    Parameters:
        id_ (str): The unique identifier for the captcha to be retrieved.
        headers (dict | None, optional): Additional headers to include in the request.
        client (httpx.Client | None, optional): httpx Client for handling session cookies.
        timeout (int, optional): Duration (in seconds) before the request times out.

    Returns:
        bytes: The base64-encoded bytes of the captcha image.
    """
    args = urlencode({'id': id_})
    url = f'/auth/captcha?{args}'
    tc = 3
    data = None
    while True:
        try:
            data = _base_request(url, headers=headers, client=client, timeout=timeout).content
            break
        except HTTPError:
            if not tc:
                raise
            tc -= 1
            continue
    return base64.b64encode(data)


def verify_captcha(
    code: str,
    headers: dict[str, str] | None = None,
    client: httpx.Client | None = None,
    timeout: int = TIMEOUT,
) -> bool:
    """
    Verify CAPTCHA with the server.

    This function sends a POST request to the '/auth/captcha' endpoint to
    verify a given CAPTCHA code. It allows passing optional headers, an
    httpx client, and a timeout value for the request. The function returns
    a boolean indicating whether the CAPTCHA verification was successful.

    Parameters:
        code: str
            The CAPTCHA code to be verified.
        headers: dict | None
            Optional HTTP headers to be included in the request.
        client: httpx.Client | None
            Optional httpx Client to manage cookies during the request.
        timeout: int
            The timeout for the request in seconds.

    Returns:
        bool
            True if the CAPTCHA verification was successful, False otherwise.
    """
    url = '/auth/captcha'
    resp = api_request(
        url,
        'POST',
        data={'code': code},
        headers=headers,
        client=client,
        timeout=timeout,
    )
    return str.lower(resp.get('status', '')) == 'ok'
