"""File API response schemas."""

from __future__ import annotations

from typing import TypedDict


class FileResponse(TypedDict, total=False):
    """Schema for File API response."""

    # IDs
    guid: str
    name: str
    filename: str

    # Info
    size: int
    mime_type: str
    origin: tuple[int, int] | None

    # Location
    url: str | None
    path: str | None

    # Metadata
    chat_id: int | None
    post_no: int | None
    user_id: int | None

    # Timestamps (as ISO strings from API)
    time_created: str


class DeleteFileResponse(TypedDict):
    """Schema for delete file API response."""

    status: str
    message: str | None


class FileUploadFields(TypedDict, total=False):
    """Schema for file upload form fields."""

    type: str | None
    filename: str | None
    size: int | None
    chat_id: int | None
    organization_id: int | None
    reply_no: int | None
    quote_range: str | None


__all__ = ['DeleteFileResponse', 'FileResponse', 'FileUploadFields']
