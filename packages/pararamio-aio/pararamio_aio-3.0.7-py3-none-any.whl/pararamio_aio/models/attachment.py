"""Async Attachment model."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from io import BufferedRandom, BufferedReader, BytesIO
from os import PathLike
from pathlib import Path
from typing import BinaryIO

from pararamio_aio._core.models.attachment import CoreAttachment

__all__ = ('Attachment',)


@dataclass
class Attachment:
    """File attachment representation.

    This is a utility class for handling file attachments before upload.
    It can handle various file input types and provides helpers for
    filename and content type detection.
    """

    file: str | bytes | PathLike[str] | BytesIO | BinaryIO
    filename: str | None = None
    content_type: str | None = None

    @property
    def guess_filename(self) -> str:
        """Guess filename from the file object.

        Returns:
            Guessed filename or 'unknown'
        """
        return CoreAttachment.guess_filename_from_file(self.file, self.filename)

    @property
    def guess_content_type(self) -> str:
        """Guess content type from file.

        Returns:
            MIME type string
        """
        return CoreAttachment.guess_content_type_from_file(self.file, self.content_type)

    async def _get_fp(self) -> BytesIO | BinaryIO:
        """Get file pointer asynchronously (internal method).

        This method handles async file reading for path-based files.

        Returns:
            File-like object (BytesIO or BinaryIO)

        Raises:
            TypeError: If a file type is not supported
        """
        if isinstance(self.file, bytes):
            return BytesIO(self.file)

        if isinstance(self.file, str | PathLike):
            # Read file synchronously in executor to avoid blocking
            loop = asyncio.get_event_loop()
            file_path = str(self.file)  # Convert to string for open()

            def read_file_sync() -> bytes:
                with Path(file_path).open('rb') as f:
                    return f.read()

            content = await loop.run_in_executor(None, read_file_sync)
            return BytesIO(content)

        if isinstance(self.file, BytesIO | BinaryIO | BufferedReader | BufferedRandom):
            return self.file

        raise TypeError(f'Unsupported type {type(self.file)}')

    @property
    def fp(self) -> BytesIO | BinaryIO:
        """Get file pointer.

        Note: This is a sync property. For async file reading,
        use _get_fp() method instead (internal).

        Returns:
            File-like object

        Raises:
            TypeError: If a file type is not supported
        """
        return CoreAttachment.get_file_pointer(self.file)

    def __str__(self) -> str:
        """String representation."""
        return f'Attachment({self.guess_filename})'

    @staticmethod
    def get_file_pointer(
        file: str | bytes | PathLike[str] | BytesIO | BinaryIO,
    ) -> BytesIO | BinaryIO:
        """Get file pointer from various file types."""
        return CoreAttachment.get_file_pointer(file)

    @staticmethod
    def guess_content_type_from_file(
        file: str | bytes | PathLike[str] | BytesIO | BinaryIO | BufferedReader,
        content_type: str | None = None,
    ) -> str:
        """Guess content type from a file object."""
        return CoreAttachment.guess_content_type_from_file(file, content_type)

    @staticmethod
    def guess_filename_from_file(
        file: str | bytes | PathLike[str] | BytesIO | BinaryIO, filename: str | None = None
    ) -> str:
        """Guess filename from a file object."""
        return CoreAttachment.guess_filename_from_file(file, filename)
