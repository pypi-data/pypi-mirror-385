"""Base classes for async models."""

from __future__ import annotations

import contextlib
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Generic, TypeVar

# Imports from core
from pararamio_aio._core.models.base import AttrFormatterMixin, SerializationMixin

from pararamio_aio.exceptions import PararamModelNotLoadedError

if TYPE_CHECKING:
    from pararamio_aio.client import AsyncPararamio

__all__ = ('AsyncClientMixin', 'SerializationMixin')

DataT = TypeVar('DataT', bound=Mapping[str, Any])


class AsyncClientMixin(Generic[DataT], AttrFormatterMixin[DataT]):
    """Mixin for async models with reference to AsyncPararamio client."""

    _client: AsyncPararamio
    _data: DataT
    _is_loaded: bool

    def __init__(self, client: AsyncPararamio, **kwargs: Any) -> None:  # noqa: ARG002
        """Initialize with AsyncPararamio client.

        Args:
            client: AsyncPararamio client instance
            **kwargs: Model data passed to parent classes
        """
        self._client = client
        self._is_loaded = False

    @property
    def client(self) -> AsyncPararamio:
        """Get the AsyncPararamio client instance."""
        return self._client

    @property
    def is_loaded(self) -> bool:
        """Check if model data has been loaded.

        Override in subclasses to check for required fields.
        """
        return self._is_loaded

    def _set_loaded(self) -> None:
        """Set model data as loaded."""
        self._is_loaded = True

    def __getattr__(self, key: str) -> Any:
        """Get attribute from _data with load check for async models.

        This is called only when attribute is not found in the instance.
        For async, we don't do lazy loading - we raise an error if data is not loaded.
        """
        if key.startswith('_'):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{key}'")

        with contextlib.suppress(KeyError):
            return self._get_formatted_attr(key)
        if not self.is_loaded:
            msg = (
                f'{self.__class__.__name__} data has not been loaded. '
                'Use load() to fetch data first.'
            )
            raise PararamModelNotLoadedError(msg)

        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{key}'")
