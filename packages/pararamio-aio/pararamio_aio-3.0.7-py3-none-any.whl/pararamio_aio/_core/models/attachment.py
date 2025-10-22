"""Core Attachment model without lazy loading."""

from __future__ import annotations

import mimetypes
import os
from io import BufferedRandom, BufferedReader, BytesIO
from os import PathLike
from pathlib import Path
from typing import TYPE_CHECKING, Any, BinaryIO, ClassVar, Unpack

from pararamio_aio._core.api_schemas.responses import AttachmentResponse

from .base import CoreBaseModel

if TYPE_CHECKING:
    from pararamio_aio._core._types import FormatterT

__all__ = ('CoreAttachment', 'guess_mime_type')


def guess_mime_type(filename: str | PathLike[str]) -> str:
    """Guess MIME type from filename.

    Args:
        filename: File name or path

    Returns:
        MIME type string
    """
    if not mimetypes.inited:
        mimetypes.init(files=os.environ.get('PARARAMIO_MIME_TYPES_PATH', None))
    return mimetypes.guess_type(str(filename))[0] or 'application/octet-stream'


# Attribute formatters for Attachment
ATTACHMENT_ATTR_FORMATTERS: FormatterT = {}


class CoreAttachment(CoreBaseModel[AttachmentResponse]):
    """Core Attachment model with common functionality."""

    _data: AttachmentResponse
    # Attachment attributes
    guid: str
    name: str
    size: int
    mime_type: str
    url: str
    post_no: int | None
    chat_id: int | None

    _attr_formatters: ClassVar[FormatterT] = ATTACHMENT_ATTR_FORMATTERS

    def __init__(
        self,
        client: Any | None = None,  # noqa: ARG002
        **kwargs: Unpack[AttachmentResponse],
    ) -> None:
        """Initialize attachment model with data.

        Args:
            client: Client instance (Pararamio or AsyncPararamio)
            **kwargs: Attachment data
        """
        self._data = kwargs

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CoreAttachment):
            return id(other) == id(self)
        return self.guid == other.guid

    @staticmethod
    def guess_filename_from_file(
        file: str | bytes | PathLike[str] | BytesIO | BinaryIO, filename: str | None = None
    ) -> str:
        """Guess filename from a file object.

        Args:
            file: File object (path, BytesIO, or BinaryIO)
            filename: Optional explicit filename

        Returns:
            Guessed filename or 'unknown'
        """
        if filename:
            return filename

        if isinstance(file, str | PathLike):
            return Path(file).name

        if isinstance(file, BytesIO | BinaryIO | BufferedReader | BufferedRandom):
            try:
                name = getattr(file, 'name', None)
                if name:
                    return Path(name).name
            except AttributeError:
                pass

        return 'unknown'

    @staticmethod
    def guess_content_type_from_file(
        file: str | bytes | PathLike[str] | BytesIO | BinaryIO | BufferedReader | BufferedRandom,
        content_type: str | None = None,
    ) -> str:
        """Guess content type from a file object.

        Args:
            file: File object
            content_type: Optional explicit content type

        Returns:
            MIME type string
        """
        if content_type:
            return content_type

        if isinstance(file, str | PathLike):
            return guess_mime_type(file)

        if isinstance(file, BytesIO | BinaryIO | BufferedReader | BufferedRandom):
            name = getattr(file, 'name', None)
            if name:
                return guess_mime_type(name)

        return 'application/octet-stream'

    @staticmethod
    def get_file_pointer(
        file: str | bytes | PathLike[str] | BytesIO | BinaryIO,
    ) -> BytesIO | BinaryIO:
        """Get file pointer from various file types.

        Args:
            file: File object (bytes, path, BytesIO, or BinaryIO)

        Returns:
            File-like object (BytesIO or BinaryIO)

        Raises:
            TypeError: If the file type is not supported
        """
        if isinstance(file, bytes):
            return BytesIO(file)

        if isinstance(file, str | PathLike):
            with Path(file).open('rb') as f:
                return BytesIO(f.read())

        if isinstance(file, BytesIO | BinaryIO | BufferedReader | BufferedRandom):
            return file

        raise TypeError(f'Unsupported type {type(file)}')
