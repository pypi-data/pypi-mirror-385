from __future__ import annotations

import asyncio
import json
import logging
import mimetypes
import time
from io import BytesIO
from json import JSONDecodeError
from pathlib import Path
from typing import TYPE_CHECKING, Any, BinaryIO, cast
from urllib.parse import quote

import httpx
from pararamio_aio._core.constants import BASE_API_URL, FILE_UPLOAD_URL, UPLOAD_TIMEOUT, VERSION
from pararamio_aio._core.constants import REQUEST_TIMEOUT as TIMEOUT
from pararamio_aio._core.exceptions import PararamioHTTPRequestError
from pararamio_aio._core.utils.logging_config import (
    LoggerManager,
    get_logger,
    sanitize_headers,
)

if TYPE_CHECKING:
    from pararamio_aio._core._types import HeaderLikeT
    from pararamio_aio._core.api_schemas.responses.file import DeleteFileResponse

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


async def bot_request(
    client: httpx.AsyncClient,
    url: str,
    key: str,
    method: str = 'GET',
    data: dict[str, Any] | None = None,
    headers: dict[str, Any] | None = None,
    timeout: int = TIMEOUT,
) -> dict[str, Any]:
    """
    Sends an async request to a bot API endpoint with the specified parameters.

    Parameters:
    client (httpx.AsyncClient): The httpx client to use for the request.
    url (str): The endpoint URL of the bot API.
    key (str): The API token for authentication.
    method (str): The HTTP method to use for the request. Defaults to 'GET'.
    data (Optional[dict]): The data payload for the request. Defaults to None.
    headers (Optional[dict]): Additional headers to include in the request. Defaults to None.
    timeout (int): The timeout setting for the request. Defaults to TIMEOUT.

    Returns:
    Response object from the API request.
    """
    _headers = {'X-APIToken': key, **DEFAULT_HEADERS}
    if headers:
        _headers = {**_headers, **headers}
    return await api_request(
        client=client, url=url, method=method, data=data, headers=_headers, timeout=timeout
    )


async def _base_request(
    client: httpx.AsyncClient,
    url: str,
    method: str = 'GET',
    data: bytes | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = TIMEOUT,
) -> httpx.Response:
    """
    Sends an async HTTP request and returns a Response object.

    Parameters:
        client (httpx.AsyncClient): The httpx client to use for the request.
        url (str): The URL endpoint to which the request is sent.
        method (str): The HTTP method to use for the request (default is 'GET').
        data (Optional[bytes]): The payload to include in the request body (default is None).
        headers (Optional[dict]): A dictionary of headers to include in the request
                                  (default is None).
        timeout (int): The timeout for the request in seconds (TIMEOUT defines default).

    Returns:
        httpx.Response: The response object containing the server's response to the HTTP
            request.

    Raises:
        PararamioHTTPRequestError: An exception is raised if there is
                                       an issue with the HTTP request.
    """
    _url = f'{BASE_API_URL}{url}'
    _headers = DEFAULT_HEADERS.copy()
    if headers:
        _headers.update(headers)

    return await _make_request(client, _url, method, data, _headers, timeout)


async def _base_file_request(
    client: httpx.AsyncClient,
    url: str,
    method: str = 'GET',
    data: bytes | dict[str, Any] | None = None,
    files: dict[str, Any] | None = None,
    headers: HeaderLikeT | None = None,
    timeout: int = TIMEOUT,
) -> httpx.Response:
    """
    Performs an async file request to the specified URL with the given parameters.

    Arguments:
        client (httpx.AsyncClient): The httpx client to use for the request.
        url (str): The URL endpoint to send the request to.
        method (str, optional): The HTTP method to use for the request (default is 'GET').
        data (Optional[Union[bytes, dict]], optional): The data to send in the request body
            (default is None).
        files (Optional[dict], optional): Files to upload (default is None).
        headers (Optional[HeaderLikeT], optional): The headers to include in the request
                                                   (default is None).
        timeout (int, optional): The timeout duration for the request (default value is TIMEOUT).

    Returns:
        httpx.Response: The response object from the file request.

    Raises:
        PararamioHTTPRequestError: If the request fails with an HTTP error code.
    """
    _url = f'{FILE_UPLOAD_URL}{url}'
    _headers = headers or {}

    return await _make_request(client, _url, method, data, _headers, timeout, files=files)


async def _read_json_response(response: httpx.Response) -> dict[str, Any]:
    """Read response content and parse as JSON."""
    return cast('dict[str, Any]', response.json())


async def _upload_with_form_data(
    client: httpx.AsyncClient,
    url: str,
    data: dict[str, Any],
    files: dict[str, Any],
    headers: HeaderLikeT | None = None,
    request_timeout: int = TIMEOUT,
) -> dict[str, Any]:
    """Upload form data and return JSON response."""
    _headers = {
        'User-agent': UA_HEADER,
        'Accept': 'application/json',
        **(headers or {}),
    }

    response = await _base_file_request(
        client,
        url,
        method='POST',
        data=data,
        files=files,
        headers=_headers,
        timeout=request_timeout,
    )

    return await _read_json_response(response)


async def upload_file(
    client: httpx.AsyncClient,
    fp: BinaryIO,
    perm: str,
    filename: str | None = None,
    file_type: str | None = None,
    headers: HeaderLikeT | None = None,
    timeout: int = UPLOAD_TIMEOUT,
) -> dict[str, Any]:
    """
    Upload a file to a pararam server asynchronously with specified permissions and optional
    parameters.

    Args:
        client (httpx.AsyncClient): The httpx client to use for the request.
        fp (BinaryIO): A file-like object to be uploaded.
        perm (str): The permission level for the uploaded file.
        filename (Optional[str], optional): Optional filename used during upload. Defaults to None.
        file_type (optional): Optional MIME type of the file. Defaults to None.
        headers (Optional[HeaderLikeT], optional): Optional headers to include in the request.
        Defaults to None.
        timeout (int, optional): Timeout duration for the upload request.
        Defaults to UPLOAD_TIMEOUT.

    Returns:
        dict: A dictionary containing the server's response to the file upload.
    """
    url = f'/upload/{perm}'

    if not filename:
        filename = Path(getattr(fp, 'name', 'file')).name
    if not file_type:
        file_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'

    fp.seek(0)
    files = {'file': (filename, fp, file_type)}

    return await _upload_with_form_data(client, url, {}, files, headers, timeout)


async def xupload_file(
    client: httpx.AsyncClient,
    fp: BinaryIO,
    fields: list[tuple[str, str | None | int]],
    filename: str | None = None,
    content_type: str | None = None,
    headers: HeaderLikeT | None = None,
    timeout: int = UPLOAD_TIMEOUT,
) -> dict[str, Any]:
    """
    Uploads a file asynchronously to a predefined URL using a multipart/form-data request.

    Arguments:
    - client: The httpx client to use for the request.
    - fp: A binary file-like object to upload.
    - fields: A list of tuples where each tuple contains a field name and a value which can be
    a string, None, or an integer.
    - filename: Optional; The name of the file being uploaded.
                If not provided, it defaults to None.
    - content_type: Optional; The MIME type of the file being uploaded.
                    If not provided, it defaults to None.
    - headers: Optional; Additional headers to include in the upload request.
               If not provided, defaults to None.
    - timeout: Optional; The timeout in seconds for the request.
               Defaults to UPLOAD_TIMEOUT.

    Returns:
    - A dictionary parsed from the JSON response of the upload request.
    """
    url = '/upload'

    if not filename:
        filename = Path(getattr(fp, 'name', 'file')).name
    if not content_type:
        content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'

    # Build form data
    data = {}
    for key, value in fields:
        if value is not None:
            data[key] = str(value)

    # Add the file
    fp.seek(0)
    files = {'data': (filename, fp, content_type)}

    return await _upload_with_form_data(client, url, data, files, headers, timeout)


async def delete_file(
    client: httpx.AsyncClient,
    guid: str,
    headers: HeaderLikeT | None = None,
    timeout: int = TIMEOUT,
) -> DeleteFileResponse:
    url = f'/delete/{guid}'
    response = await _base_file_request(
        client, url, method='DELETE', headers=headers, timeout=timeout
    )
    result = await _read_json_response(response)
    return cast('DeleteFileResponse', result)


async def download_file(
    client: httpx.AsyncClient,
    guid: str,
    filename: str,
    headers: HeaderLikeT | None = None,
    timeout: int = TIMEOUT,
) -> BytesIO:
    url = f'/download/{guid}/{quote(filename)}'
    response = await file_request(client, url, method='GET', headers=headers, timeout=timeout)
    return BytesIO(response.content)


async def file_request(
    client: httpx.AsyncClient,
    url: str,
    method: str = 'GET',
    data: bytes | None = None,
    headers: HeaderLikeT | None = None,
    timeout: int = TIMEOUT,
) -> httpx.Response:
    _headers = DEFAULT_HEADERS.copy()
    if headers:
        _headers.update(headers)
    return await _base_file_request(
        client,
        url,
        method=method,
        data=data,
        headers=_headers,
        timeout=timeout,
    )


async def _make_request(  # pylint: disable=too-many-statements
    client: httpx.AsyncClient,
    url: str,
    method: str = 'GET',
    data: Any = None,
    headers: HeaderLikeT | None = None,
    timeout: int = TIMEOUT,
    files: dict[str, Any] | None = None,
    max_retries: int = 3,
) -> httpx.Response:
    """
    Common request handler for both API and file requests with retry logic.

    Args:
        client: The httpx client to use for the request
        url: The full URL to send the request to
        method: The HTTP method to use
        data: The data to send in the request body
        headers: Headers to include in the request
        timeout: Request timeout in seconds
        files: Files to upload in multipart requests
        max_retries: Maximum number of retry attempts

    Returns:
        The response object from the request

    Raises:
        PararamioHTTPRequestError: If the request fails
    """
    # Log request details
    http_logger.debug('Async HTTP Request: %s %s, timeout=%ds', method, url, timeout)
    if http_logger.isEnabledFor(logging.DEBUG) and headers:
        http_logger.debug('Request headers: %s', sanitize_headers(dict(headers)))
        if data:
            data_size = (
                len(data)
                if isinstance(data, bytes)
                else len(json.dumps(data) if isinstance(data, dict) else str(data))
            )
            http_logger.debug('Request body size: %d bytes', data_size)

    last_error: Exception | None = None
    for attempt in range(max_retries):
        if attempt > 0:
            retry_logger.info(
                'Retry attempt %d/%d for %s %s', attempt + 1, max_retries, method, url
            )

        start_time = time.perf_counter()
        try:
            # Prepare request parameters
            kwargs: dict[str, Any] = {
                'method': method,
                'url': url,
                'headers': headers or {},
                'timeout': timeout,
            }

            if files:
                # For multipart requests with files
                kwargs['files'] = files
                if data and isinstance(data, dict):
                    kwargs['data'] = data
            elif data is not None:
                # For regular requests with data
                kwargs['content'] = data

            response = await client.request(**kwargs)
            duration = time.perf_counter() - start_time

            # Log response details
            http_logger.debug(
                'Async HTTP Response: %s %s - Status: %d, Duration: %.3fs',
                method,
                url,
                response.status_code,
                duration,
            )

            if http_logger.isEnabledFor(logging.DEBUG):
                content_length = response.headers.get('content-length', 'unknown')
                http_logger.debug('Response size: %s bytes', content_length)

            # Check if we should retry on error status
            if response.status_code >= 400:
                # Check if we should retry
                retry_codes = {429, 502, 503, 504}
                if response.status_code in retry_codes and attempt < max_retries - 1:
                    delay = 0.5 * (2**attempt)  # Exponential backoff
                    retry_logger.warning(
                        'Got status %d, will retry after %.2fs (attempt %d/%d)',
                        response.status_code,
                        delay,
                        attempt + 1,
                        max_retries,
                    )
                    await asyncio.sleep(delay)
                    continue

                # No retry, raise error
                headers_list = list(response.headers.items())
                http_logger.error(
                    'Async HTTP Error: %s %s - Status: %d, Duration: %.3fs',
                    method,
                    url,
                    response.status_code,
                    duration,
                )
                raise PararamioHTTPRequestError(
                    url,
                    response.status_code,
                    response.reason_phrase or 'Unknown error',
                    headers_list,
                    BytesIO(response.content),
                )

            # Log performance if slow
            await log_performance_async(http_logger, f'{method} {url}', duration)
            return response

        except httpx.TimeoutException as e:
            duration = time.perf_counter() - start_time
            last_error = e
            if attempt < max_retries - 1:
                delay = 0.5 * (2**attempt)
                retry_logger.warning(
                    'Timeout error, retrying after %.2fs (attempt %d/%d)',
                    delay,
                    attempt + 1,
                    max_retries,
                )
                await asyncio.sleep(delay)
                continue

            http_logger.error(
                'Async HTTP Timeout: %s %s - Duration: %.3fs (after %d attempts)',
                method,
                url,
                duration,
                attempt + 1,
            )
            log.exception('%s - %s - timeout', url, method)
            raise PararamioHTTPRequestError(url, 408, 'Request Timeout', [], BytesIO()) from e

        except httpx.HTTPError as e:
            duration = time.perf_counter() - start_time
            last_error = e
            if attempt < max_retries - 1:
                delay = 0.5 * (2**attempt)
                retry_logger.warning(
                    'Network error, retrying after %.2fs (attempt %d/%d): %s',
                    delay,
                    attempt + 1,
                    max_retries,
                    str(e),
                )
                await asyncio.sleep(delay)
                continue

            http_logger.error(
                'Async HTTP Error: %s %s - %.3fs, %s (attempt %d)',
                method,
                url,
                duration,
                str(e),
                attempt + 1,
            )
            log.exception('%s - %s', url, method)
            raise PararamioHTTPRequestError(url, 0, str(e), [], BytesIO()) from e

    # Should not reach here
    if last_error:
        raise PararamioHTTPRequestError(url, 0, str(last_error), [], BytesIO()) from last_error
    raise PararamioHTTPRequestError(url, 0, 'Max retries exceeded', [], BytesIO())


async def log_performance_async(logger: logging.Logger, operation: str, duration: float) -> None:
    """Async version of log_performance."""
    if duration > 1.0:
        logger.warning('%s took %.2f seconds', operation, duration)
    elif duration > 0.5 and logger.isEnabledFor(logging.INFO):
        logger.info('%s took %.2f seconds', operation, duration)
    elif logger.isEnabledFor(logging.DEBUG):
        logger.debug('%s took %.2f seconds', operation, duration)


async def raw_api_request(
    client: httpx.AsyncClient,
    url: str,
    method: str = 'GET',
    data: bytes | None = None,
    headers: HeaderLikeT | None = None,
    timeout: int = TIMEOUT,
) -> tuple[dict[str, Any], list[tuple[str, str]]]:
    response = await _base_request(client, url, method, data, headers, timeout)
    if 200 <= response.status_code < 300:
        headers_list = list(response.headers.items())
        return cast('dict[str, Any]', response.json()), headers_list
    return {}, []


async def api_request(
    client: httpx.AsyncClient,
    url: str,
    method: str = 'GET',
    data: dict[str, Any] | None = None,
    headers: HeaderLikeT | None = None,
    timeout: int = TIMEOUT,
) -> dict[str, Any]:
    _data = None
    if data is not None:
        _data = json.dumps(data).encode('utf-8')

    response = await _base_request(client, url, method, _data, headers, timeout)

    if response.status_code == 204:
        return {}

    if 200 <= response.status_code < 500:
        try:
            return cast('dict[str, Any]', response.json())
        except JSONDecodeError as e:
            log.exception('%s - %s', url, method)
            headers_list = list(response.headers.items())
            raise PararamioHTTPRequestError(
                url,
                response.status_code,
                'JSONDecodeError',
                headers_list,
                BytesIO(response.content),
            ) from e
    return {}
