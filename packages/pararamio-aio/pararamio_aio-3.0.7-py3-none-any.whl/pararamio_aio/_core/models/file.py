"""Core File model without lazy loading."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Unpack

from pararamio_aio._core.api_schemas.responses import FileResponse
from pararamio_aio._core.utils.helpers import parse_iso_datetime

from .base import ClientT, CoreBaseModel

if TYPE_CHECKING:
    from datetime import datetime

    from pararamio_aio._core._types import FormatterT

__all__ = ('CoreFile',)


# Attribute formatters for File
FILE_ATTR_FORMATTERS: FormatterT = {
    'time_created': parse_iso_datetime,
}


class CoreFile(CoreBaseModel[FileResponse]):
    """Core File model with common functionality."""

    _data: FileResponse
    # File attributes
    guid: str
    name: str
    filename: str
    size: int
    mime_type: str
    origin: tuple[int, int] | None
    url: str | None
    path: str | None
    chat_id: int | None
    post_no: int | None
    user_id: int | None
    time_created: datetime | None

    _attr_formatters: ClassVar[FormatterT] = FILE_ATTR_FORMATTERS

    def __init__(
        self,
        client: ClientT,  # noqa: ARG002
        **kwargs: Unpack[FileResponse],
    ) -> None:
        """Initialize the file model with data.

        Args:
            client: Client instance (Pararamio or AsyncPararamio)
            **kwargs: File data
        """
        # Ensure backward compatibility for 'name' -> 'filename'
        if 'name' in kwargs and 'filename' not in kwargs:
            kwargs['filename'] = kwargs['name']
        self._data = kwargs

    def __getattr__(self, name: str) -> object:
        """Get attribute from data dict.

        Args:
            name: Attribute name

        Returns:
            Attribute value

        Raises:
            AttributeError: If attribute not found
        """
        try:
            return self._data.get(name)
        except KeyError as e:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'"
            ) from e

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CoreFile):
            return id(other) == id(self)
        return self.guid == other.guid
