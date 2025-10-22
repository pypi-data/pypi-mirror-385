"""Async file operations for the Pararamio client."""

from __future__ import annotations

import asyncio
import mimetypes
from io import BytesIO
from pathlib import Path
from typing import Any, BinaryIO, cast
from urllib.parse import quote

import httpx
from pararamio_aio._core import (
    REQUEST_TIMEOUT,
    UPLOAD_TIMEOUT,
    PararamioHTTPRequestError,
)
from pararamio_aio._core.api_schemas.responses.file import DeleteFileResponse

# File upload base URL
FILE_UPLOAD_URL = 'https://file.pararam.io'


__all__ = (
    'delete_file',
    'download_file',
    'upload_file',
)


def _build_multipart_body(
    fd: BinaryIO | BytesIO,
    fields: list[tuple[str, str | None | int]],
    boundary: str,
    form_field_name: str,
    filename: str | None,
    content_type: str | None,
) -> bytes:
    """Build multipart body from a file and fields."""
    body = BytesIO()

    # Write fields
    for key, value in fields:
        if value is None:
            continue
        body.write(f'--{boundary}\r\n'.encode())
        body.write(f'Content-Disposition: form-data; name="{key}"'.encode())
        body.write(f'\r\n\r\n{value}\r\n'.encode())

    # Write file data
    fd.seek(0)
    body.write(f'--{boundary}\r\n'.encode())
    body.write(
        f'Content-Disposition: form-data; name="{form_field_name}"; '
        f'filename="{filename}"\r\n'.encode()
    )
    body.write(f'Content-Type: {content_type or "application/octet-stream"}\r\n\r\n'.encode())
    body.write(fd.read())
    body.write(f'\r\n--{boundary}--\r\n\r\n'.encode())

    return body.getvalue()


async def multipart_encode(
    fd: BinaryIO | BytesIO,
    *,
    fields: list[tuple[str, str | None | int]] | None = None,
    boundary: str | None = None,
    form_field_name: str = 'data',
    filename: str | None = None,
    content_type: str | None = None,
) -> bytes:
    """
    Encode multipart/form-data for file uploads.

    Args:
        fd: A file-like object opened in binary mode that is to be included in the payload.
        fields: An optional list of tuples representing additional form fields.
        boundary: An optional string used to separate parts of the multipart message.
        form_field_name: The name of the form field for the file being uploaded.
        filename: An optional string representing the filename for the file being uploaded.
        content_type: An optional string representing the content type of the file.

    Returns:
        A byte object representing the encoded multipart/form-data payload.
    """
    if fields is None:
        fields = []
    if boundary is None:
        boundary = 'FORM-BOUNDARY'

    # Get filename if not provided
    if not filename and hasattr(fd, 'name'):
        filename = Path(fd.name).name

    if not content_type and filename:
        content_type = mimetypes.guess_type(filename)[0]

    # For BytesIO (already in memory), no need for executor
    if isinstance(fd, BytesIO):
        return _build_multipart_body(fd, fields, boundary, form_field_name, filename, content_type)

    # For real files (BinaryIO), use executor to avoid blocking
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        _build_multipart_body,
        fd,
        fields,
        boundary,
        form_field_name,
        filename,
        content_type,
    )


async def upload_file(
    client: httpx.AsyncClient,
    fp: BinaryIO | BytesIO,
    fields: list[tuple[str, str | None | int]],
    *,
    filename: str | None = None,
    content_type: str | None = None,
    headers: dict[str, str] | None = None,
    request_timeout: int = UPLOAD_TIMEOUT,
) -> dict[str, Any]:
    """
    Upload files to Pararamio.

    Args:
        client: httpx async client
        fp: A binary file-like object to upload
        fields: A list of tuples containing field names and values
        filename: Optional filename for the upload
        content_type: Optional MIME type of the file
        headers: Optional additional headers
        request_timeout: Timeout in seconds for the upload

    Returns:
        Dictionary with upload response data
    """
    url = f'{FILE_UPLOAD_URL}/upload'
    boundary = 'FORM-BOUNDARY'

    # Prepare headers
    _headers = {
        'User-agent': 'pararamio-aio',
        'Accept': 'application/json',
        'Content-Type': f'multipart/form-data; boundary={boundary}',
    }
    if headers:
        _headers.update(headers)

    # Encode multipart data
    data = await multipart_encode(
        fp,
        fields=fields,
        filename=filename,
        content_type=content_type,
        boundary=boundary,
    )

    # Make request with proper timeout
    response = await client.post(
        url, content=data, headers=_headers, timeout=httpx.Timeout(request_timeout)
    )
    if response.status_code == 200:
        return cast('dict[str, Any]', response.json())
    raise PararamioHTTPRequestError(
        url,
        response.status_code,
        f'HTTP {response.status_code}',
        list(response.headers.items()),
        BytesIO(response.text.encode()),
    )


async def delete_file(
    client: httpx.AsyncClient,
    guid: str,
    *,
    headers: dict[str, str] | None = None,
    request_timeout: int = REQUEST_TIMEOUT,
) -> DeleteFileResponse:
    """
    Delete files from Pararamio.

    Args:
        client: httpx async client
        guid: The GUID of the file to delete
        headers: Optional additional headers
        request_timeout: Timeout in seconds for the request

    Returns:
        DeleteFileResponse with deletion status
    """
    url = f'{FILE_UPLOAD_URL}/delete/{guid}'

    _headers = {
        'User-agent': 'pararamio-aio',
        'Accept': 'application/json',
    }
    if headers:
        _headers.update(headers)

    response = await client.delete(url, headers=_headers, timeout=httpx.Timeout(request_timeout))
    if response.status_code in (200, 204):
        if response.status_code == 204:
            result: DeleteFileResponse = {'status': 'success', 'message': None}
            return result
        return cast('DeleteFileResponse', response.json())
    raise PararamioHTTPRequestError(
        url,
        response.status_code,
        f'HTTP {response.status_code}',
        list(response.headers.items()),
        BytesIO(response.text.encode()),
    )


async def download_file(
    client: httpx.AsyncClient,
    guid: str,
    filename: str,
    *,
    headers: dict[str, str] | None = None,
    request_timeout: int = REQUEST_TIMEOUT,
) -> BytesIO:
    """
    Download files from Pararamio.

    Args:
        client: httpx async client
        guid: The GUID of the file-to-download
        filename: The filename for the download
        headers: Optional additional headers
        request_timeout: Timeout in seconds for the request

    Returns:
        BytesIO object containing the downloaded file content
    """
    url = f'{FILE_UPLOAD_URL}/download/{guid}/{quote(filename)}'

    _headers = {
        'User-agent': 'pararamio-aio',
    }
    if headers:
        _headers.update(headers)

    response = await client.get(url, headers=_headers, timeout=httpx.Timeout(request_timeout))
    if response.status_code == 200:
        return BytesIO(response.content)
    raise PararamioHTTPRequestError(
        url,
        response.status_code,
        f'HTTP {response.status_code}',
        list(response.headers.items()),
        BytesIO(response.text.encode()),
    )
