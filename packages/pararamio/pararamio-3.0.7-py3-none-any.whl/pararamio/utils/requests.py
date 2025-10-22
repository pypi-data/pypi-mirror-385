from __future__ import annotations

import json
import logging
import mimetypes
import time
from io import BytesIO
from json import JSONDecodeError
from pathlib import Path
from typing import TYPE_CHECKING, Any, BinaryIO, NoReturn, cast
from urllib.parse import quote

import httpx
from pararamio._core.api_schemas.responses import DeleteFileResponse, FileResponse
from pararamio._core.constants import BASE_API_URL, FILE_UPLOAD_URL, UPLOAD_TIMEOUT, VERSION
from pararamio._core.constants import REQUEST_TIMEOUT as TIMEOUT
from pararamio._core.exceptions import PararamioHTTPRequestError
from pararamio._core.utils.logging_config import (
    LoggerManager,
    get_logger,
    log_performance,
    sanitize_cookies,
    sanitize_headers,
)

if TYPE_CHECKING:
    from pararamio._core._types import HeaderLikeT

__all__ = (
    'api_request',
    'bot_request',
    'delete_file',
    'download_file',
    'raw_api_request',
    'upload_file',
    'xupload_file',
)
# Get component-specific loggers
log = logging.getLogger('pararamio')  # Keep for backward compatibility
http_logger = get_logger(LoggerManager.HTTP_CLIENT)
retry_logger = get_logger(LoggerManager.RETRY)
UA_HEADER = f'pararamio lib version {VERSION}'
DEFAULT_HEADERS = {
    'Content-type': 'application/json',
    'Accept': 'application/json',
    'User-agent': UA_HEADER,
}


def _handle_http_status_error(
    e: httpx.HTTPStatusError,
    url: str,
    method: str,
    duration: float,
    context: str = 'HTTP Error',
) -> NoReturn:
    """Handle HTTP status error and raise PararamioHTTPRequestError.

    Args:
        e: The HTTP status error
        url: Request URL
        method: HTTP method
        duration: Request duration in seconds
        context: Error context for logging (e.g., 'HTTP Error', 'File Request Error')
    """
    http_logger.error(
        '%s: %s %s - Status: %d, Duration: %.3fs',
        context,
        method,
        url,
        e.response.status_code,
        duration,
    )
    log.exception('%s - %s', url, method)
    raise PararamioHTTPRequestError(
        url,
        e.response.status_code,
        str(e),
        list(e.response.headers.items()),
        BytesIO(e.response.content),
    ) from e


def multipart_encode(
    fd: BinaryIO,
    fields: list[tuple[str, str | None | int]] | None = None,
    boundary: str | None = None,
    form_field_name: str = 'data',
    filename: str | None = None,
    content_type: str | None = None,
) -> bytes:
    """
    Encodes a file and additional fields into a multipart/form-data payload.

    Args:
        fd: A file-like object opened in binary mode that is to be included in the payload.
        fields: An optional list of tuples representing additional form fields,
                with each tuple containing a field name and its value.
        boundary: An optional string used to separate parts of the multipart message.
                  If not provided, a default boundary ('FORM-BOUNDARY') is used.
        form_field_name: The name of the form field for the file being uploaded. Defaults to 'data'.
        filename: An optional string representing the filename for the file being uploaded.
                  If not provided, the name is derived from the file-like object.
        content_type: An optional string representing the content type of the file being uploaded.
                      If not provided, the content type will be guessed from the filename.

    Returns:
        A bytes' object representing the encoded multipart/form-data payload.
    """
    if fields is None:
        fields = []
    if boundary is None:
        boundary = 'FORM-BOUNDARY'

    body = BytesIO()

    # Add form fields
    if fields:
        for key, value in fields:
            if value is None:
                continue
            body.write(f'--{boundary}\r\n'.encode())
            body.write(f'Content-Disposition: form-data; name="{key}"\r\n\r\n{value}\r\n'.encode())

    # Add the file
    if not filename:
        filename = Path(fd.name).name
    if not content_type:
        content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'

    fd.seek(0)
    body.write(f'--{boundary}\r\n'.encode())
    body.write(
        f'Content-Disposition: form-data; name="{form_field_name}"; filename="{filename}"\r'
        f'\n'.encode()
    )
    body.write(f'Content-Type: {content_type}\r\n\r\n'.encode())
    body.write(fd.read())
    body.write(f'\r\n--{boundary}--\r\n\r\n'.encode())

    return body.getvalue()


def bot_request(
    url: str,
    key: str,
    method: str = 'GET',
    data: dict[str, Any] | None = None,
    headers: dict[str, Any] | None = None,
    timeout: int = TIMEOUT,
) -> dict[str, Any]:
    """
    Sends a request to a bot API endpoint with the specified parameters.

    Parameters:
    url (str): The endpoint URL of the bot API.
    key (str): The API token for authentication.
    method (str): The HTTP method to use for the request. Defaults to 'GET'.
    data (Optional[dict]): The data payload for the request. Defaults to None.
    headers (Optional[dict]): Additional headers to include in the request. Defaults to None.
    timeout (int): The timeout setting for the request. Defaults to TIMEOUT.

    Returns:
    dict: Response object from the API request.
    """
    _headers = {'X-APIToken': key, **DEFAULT_HEADERS}
    if headers:
        _headers = {**_headers, **headers}
    return api_request(url=url, method=method, data=data, headers=_headers, timeout=timeout)


def _should_retry(status_code: int, attempt: int, max_retries: int = 3) -> bool:
    """
    Determine if request should be retried based on status code and attempt count.

    Args:
        status_code: HTTP response status code
        attempt: Current attempt number (0-based)
        max_retries: Maximum number of retries

    Returns:
        True if it should retry, False otherwise
    """
    # Status codes that should trigger retry
    retry_codes = {429, 502, 503, 504}

    if attempt >= max_retries:
        return False

    return status_code in retry_codes


def _calculate_retry_delay(attempt: int, retry_after: str | None = None) -> float:
    """
    Calculate delay before retry using exponential backoff.

    Args:
        attempt: Current attempt number (0-based)
        retry_after: Optional Retry-After header value

    Returns:
        Delay in seconds
    """
    # If we have Retry-After header, use it
    if retry_after:
        try:
            return float(retry_after)
        except (ValueError, TypeError):
            pass

    # Exponential backoff: 0.5s, 1s, 2s
    base_delay = 0.5
    return float(base_delay * (2**attempt))


def _base_request(  # pylint: disable=too-many-statements
    url: str,
    method: str = 'GET',
    data: bytes | None = None,
    headers: dict[str, str] | None = None,
    client: httpx.Client | None = None,
    timeout: int = TIMEOUT,
    max_retries: int = 3,
) -> httpx.Response:
    """
    Sends an HTTP request and returns a httpx Response object with automatic retry logic.

    Parameters:
        url (str): The URL endpoint to which the request is sent.
        method (str): The HTTP method to use for the request (default is 'GET').
        data (Optional[bytes]): The payload to include in the request body (default is None).
        headers (Optional[dict]): A dictionary of headers to include in the request
                                  (default is None).
        client (Optional[httpx.Client]): httpx Client to use for requests.
                                         If None, creates a temporary client.
        timeout (int): The timeout for the request in seconds (TIMEOUT defines default).
        max_retries (int): Maximum number of retry attempts (default is 3).

    Returns:
        httpx.Response: The response object containing the server's response to the HTTP request.

    Raises:
        PararamioHTTPRequestError: An exception is raised if there is
                                       an issue with the HTTP request.
    """
    _url = f'{BASE_API_URL}{url}'
    _headers = DEFAULT_HEADERS.copy()
    if headers:
        _headers.update(headers)

    last_error: Exception | None = None
    # Track if we need to clean up the client
    cleanup_client = False
    if client is None:
        client = httpx.Client(timeout=timeout)
        cleanup_client = True

    try:
        for attempt in range(max_retries + 1):
            # Log request details
            if attempt == 0:
                http_logger.debug('HTTP Request: %s %s, timeout=%ds', method, _url, timeout)
                if http_logger.isEnabledFor(logging.DEBUG):
                    http_logger.debug('Request headers: %s', sanitize_headers(_headers))
                    http_logger.debug('Request cookies: %s', sanitize_cookies(client.cookies))
                    if data:
                        data_size = len(data) if data else 0
                        http_logger.debug('Request body size: %d bytes', data_size)
            else:
                retry_logger.info(
                    'Retry attempt %d/%d for %s %s', attempt, max_retries, method, _url
                )

            start_time = time.time()
            try:
                response = client.request(method, _url, content=data, headers=_headers)

                duration = time.time() - start_time

                # Log response details
                http_logger.debug(
                    'HTTP Response: %s %s - Status: %d, Duration: %.3fs',
                    method,
                    _url,
                    response.status_code,
                    duration,
                )

                if http_logger.isEnabledFor(logging.DEBUG):
                    http_logger.debug('Response headers: %s', dict(response.headers))
                    content_length = response.headers.get('content-length', 'unknown')
                    http_logger.debug('Response size: %s bytes', content_length)

                # Check if we should retry
                if _should_retry(response.status_code, attempt, max_retries):
                    retry_after = response.headers.get('Retry-After')
                    delay = _calculate_retry_delay(attempt, retry_after)

                    retry_logger.warning(
                        'Got status %d, will retry after %.2fs (attempt %d/%d)',
                        response.status_code,
                        delay,
                        attempt + 1,
                        max_retries,
                    )

                    time.sleep(delay)
                    continue

                # Log performance if slow
                log_performance(http_logger, f'{method} {url}', duration)

                response.raise_for_status()
                return response

            except httpx.HTTPStatusError as e:
                duration = time.time() - start_time
                last_error = e

                # Check if we should retry on HTTP errors
                if _should_retry(e.response.status_code, attempt, max_retries):
                    retry_after = e.response.headers.get('Retry-After')
                    delay = _calculate_retry_delay(attempt, retry_after)

                    retry_logger.warning(
                        'HTTP Error %d, retrying after %.2fs (attempt %d/%d)',
                        e.response.status_code,
                        delay,
                        attempt + 1,
                        max_retries,
                    )

                    time.sleep(delay)
                    continue

                # Final error, no more retries
                _handle_http_status_error(
                    e, _url, method, duration, f'HTTP Error (after {attempt + 1} attempts)'
                )

            except httpx.HTTPError as e:
                duration = time.time() - start_time
                last_error = e

                # Network errors - retry if not last attempt
                if attempt < max_retries:
                    delay = _calculate_retry_delay(attempt)

                    retry_logger.warning(
                        'Network error, retrying after %.2fs (attempt %d/%d): %s',
                        delay,
                        attempt + 1,
                        max_retries,
                        str(e),
                    )

                    time.sleep(delay)
                    continue

                # Final error, no more retries
                http_logger.error(
                    'HTTP Connection Error: %s %s - Duration: %.3fs, Error: %s (after %d attempts)',
                    method,
                    _url,
                    duration,
                    str(e),
                    attempt + 1,
                )
                log.exception('%s - %s', _url, method)
                raise PararamioHTTPRequestError(_url, 0, str(e), [], BytesIO()) from e

        # Should not reach here, but handle just in case
        if last_error:
            raise PararamioHTTPRequestError(_url, 0, str(last_error), [], BytesIO()) from last_error
        raise PararamioHTTPRequestError(_url, 0, 'Max retries exceeded', [], BytesIO())
    finally:
        if cleanup_client:
            client.close()


def _base_file_request(
    url: str,
    method: str = 'GET',
    data: bytes | None = None,
    headers: HeaderLikeT | None = None,
    client: httpx.Client | None = None,
    timeout: int = TIMEOUT,
) -> httpx.Response:
    """
    Performs a file request to the specified URL with the given parameters.

    Arguments:
        url (str): The URL endpoint to send the request to.
        method (str, optional): The HTTP method to use for the request (default is 'GET').
        data (Optional[bytes], optional): The data to send in the request body (default is None).
        headers (Optional[HeaderLikeT], optional): The headers to include in the request
                                                   (default is None).
        client (Optional[httpx.Client]): httpx Client to use for requests.
                                         If None, creates a temporary client.
        timeout (int, optional): The timeout duration for the request (default value is TIMEOUT).

    Returns:
        httpx.Response: The response object from the file request.

    Raises:
        PararamioHTTPRequestError: If the request fails with an HTTP error code.
    """
    _url = f'{FILE_UPLOAD_URL}{url}'

    # Track if we need to clean up the client
    cleanup_client = False
    if client is None:
        client = httpx.Client(timeout=timeout)
        cleanup_client = True

    # Log file request details
    http_logger.debug('File Request: %s %s, timeout=%ds', method, _url, timeout)
    if http_logger.isEnabledFor(logging.DEBUG) and headers:
        http_logger.debug('Request headers: %s', sanitize_headers(dict(headers)))
        if data:
            http_logger.debug('Upload size: %d bytes', len(data))

    start_time = time.time()
    try:
        response = client.request(method, _url, content=data, headers=headers or {})

        duration = time.time() - start_time

        # Log response
        http_logger.debug(
            'File Response: %s %s - Status: %d, Duration: %.3fs',
            method,
            _url,
            response.status_code,
            duration,
        )

        # Log performance for file operations
        log_performance(http_logger, f'File {method} {url}', duration)

        response.raise_for_status()
        return response

    except httpx.HTTPStatusError as e:
        duration = time.time() - start_time
        _handle_http_status_error(e, _url, method, duration, 'File Request Error')
    except httpx.HTTPError as e:
        duration = time.time() - start_time
        http_logger.error(
            'File Request Connection Error: %s %s - Duration: %.3fs', method, _url, duration
        )
        log.exception('%s - %s', _url, method)
        raise PararamioHTTPRequestError(_url, 0, str(e), [], BytesIO()) from e
    finally:
        if cleanup_client:
            client.close()


def upload_file(
    fp: BinaryIO,
    perm: str,
    filename: str | None = None,
    file_type: str | None = None,
    headers: HeaderLikeT | None = None,
    client: httpx.Client | None = None,
    timeout: int = UPLOAD_TIMEOUT,
) -> FileResponse:
    """
    Upload a file to a pararam server with specified permissions and optional parameters.

    Args:
        fp (BinaryIO): A file-like object to be uploaded.
        perm (str): The permission level for the uploaded file.
        filename (Optional[str], optional): Optional filename used during upload. Defaults to None.
        file_type (Optional[str], optional): Optional MIME type of the file. Defaults to None.
        headers (Optional[HeaderLikeT], optional): Optional headers to include in the request.
        Defaults to None.
        client (Optional[httpx.Client]): httpx Client to use for requests.
                                         If None, creates a temporary client.
        timeout (int, optional): Timeout duration for the upload request.
        Defaults to UPLOAD_TIMEOUT.

    Returns:
        FileResponse: A dictionary containing the server's response to the file upload.

    The function constructs a multipart form data request with the file contents,
    sends the POST request to the server and returns the parsed JSON response from the server.
    """
    url = f'/upload/{perm}'
    boundary = 'FORM-BOUNDARY'
    _headers = {
        'User-agent': UA_HEADER,
        **(headers or {}),
        'Accept': 'application/json',
        'Content-Type': f'multipart/form-data; boundary={boundary}',
    }
    data = multipart_encode(
        fp,
        boundary=boundary,
        form_field_name='file',
        filename=filename,
        content_type=file_type,
    )
    resp = _base_file_request(
        url,
        method='POST',
        data=data,
        headers=_headers,
        client=client,
        timeout=timeout,
    )
    return cast('FileResponse', resp.json())


def xupload_file(
    fp: BinaryIO,
    fields: list[tuple[str, str | None | int]],
    filename: str | None = None,
    content_type: str | None = None,
    headers: HeaderLikeT | None = None,
    client: httpx.Client | None = None,
    timeout: int = UPLOAD_TIMEOUT,
) -> FileResponse:
    """
    Uploads a file to a predefined URL using a multipart/form-data request.

    Arguments:
    - fp: A binary file-like object to upload.
    - fields: A list of tuples where each tuple contains a field name
     and a value which can be a string, None or an integer.
    - filename: Optional; The name of the file being uploaded.
                If not provided, it defaults to None.
    - content_type: Optional; The MIME type of the file being uploaded.
                    If not provided, it defaults to None.
    - headers: Optional; Additional headers to include in the upload request.
               If not provided, defaults to None.
    - client: Optional; httpx Client to use for requests.
              If None, creates a temporary client.
    - timeout: Optional; The timeout in seconds for the request.
               Defaults to UPLOAD_TIMEOUT.

    Returns:
    - FileResponse: A dictionary parsed from the JSON response of the upload request.
    """
    url = '/upload'
    boundary = 'FORM-BOUNDARY'
    _headers = {
        'User-agent': UA_HEADER,
        **(headers or {}),
        'Accept': 'application/json',
        'Content-Type': f'multipart/form-data; boundary={boundary}',
    }
    data = multipart_encode(
        fp,
        fields,
        filename=filename,
        content_type=content_type,
        boundary=boundary,
    )
    resp = _base_file_request(
        url,
        method='POST',
        data=data,
        headers=_headers,
        client=client,
        timeout=timeout,
    )
    return cast('FileResponse', resp.json())


def delete_file(
    guid: str,
    headers: HeaderLikeT | None = None,
    client: httpx.Client | None = None,
    timeout: int = TIMEOUT,
) -> DeleteFileResponse:
    """Delete a file by GUID."""
    url = f'/delete/{guid}'
    resp = _base_file_request(url, method='DELETE', headers=headers, client=client, timeout=timeout)
    return cast('DeleteFileResponse', resp.json())


def download_file(
    guid: str,
    filename: str,
    headers: HeaderLikeT | None = None,
    client: httpx.Client | None = None,
    timeout: int = TIMEOUT,
) -> BytesIO:
    """Download a file by GUID and filename."""
    url = f'/download/{guid}/{quote(filename)}'
    return file_request(url, method='GET', headers=headers, client=client, timeout=timeout)


def file_request(
    url: str,
    method: str = 'GET',
    data: bytes | None = None,
    headers: HeaderLikeT | None = None,
    client: httpx.Client | None = None,
    timeout: int = TIMEOUT,
) -> BytesIO:
    """Make a file request and return BytesIO."""
    _headers = DEFAULT_HEADERS.copy()
    if headers:
        _headers.update(headers)
    resp = _base_file_request(
        url,
        method=method,
        data=data,
        headers=_headers,
        client=client,
        timeout=timeout,
    )
    return BytesIO(resp.content)


def raw_api_request(
    url: str,
    method: str = 'GET',
    data: bytes | None = None,
    headers: HeaderLikeT | None = None,
    client: httpx.Client | None = None,
    timeout: int = TIMEOUT,
) -> tuple[dict[str, Any], list[tuple[str, str]]]:
    """Make a raw API request and return response data and headers."""
    resp = _base_request(url, method, data, headers, client, timeout)
    if 200 <= resp.status_code < 300:
        return resp.json(), list(resp.headers.items())
    return {}, []


def api_request(
    url: str,
    method: str = 'GET',
    data: dict[str, Any] | None = None,
    headers: HeaderLikeT | None = None,
    client: httpx.Client | None = None,
    timeout: int = TIMEOUT,
) -> dict[str, Any]:
    """Make an API request with JSON data."""
    _data = None
    if data is not None:
        _data = json.dumps(data).encode('utf-8')

    resp = _base_request(url, method, _data, headers, client, timeout)
    resp_code = resp.status_code

    if resp_code == 204:
        return {}
    if 200 <= resp_code < 500:
        try:
            return cast('dict[str, Any]', resp.json())
        except JSONDecodeError as e:
            log.exception('%s - %s', url, method)
            raise PararamioHTTPRequestError(
                url,
                resp.status_code,
                'JSONDecodeError',
                list(resp.headers.items()),
                BytesIO(resp.content),
            ) from e
    return {}
