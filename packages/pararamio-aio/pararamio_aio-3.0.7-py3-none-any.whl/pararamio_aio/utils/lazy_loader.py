"""Lazy loading utilities for async operations."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Awaitable, Callable, Sequence

__all__ = ['async_lazy_loader']

ItemT = TypeVar('ItemT')
ClsT = TypeVar('ClsT')


async def async_lazy_loader(
    cls: ClsT,
    items: Sequence[int],
    load_fn: Callable[[ClsT, Sequence[int]], Awaitable[list[ItemT]]],
    per_load: int = 50,
) -> AsyncIterator[ItemT]:
    """
    An async generator function that loads items lazily in batches from a provided sequence of IDs.

    Parameters:
    cls (Any): The class or instance context used by the load function.
    items (Sequence[int]): The collection of item IDs to be loaded.
    load_fn (Callable[[Any, Sequence[int]], Awaitable[List]]): The async function responsible
        for loading a batch of items. It must accept the class or instance (cls) and a subset
        of IDs, and return a list of loaded items.
    per_load (int): The number of items to load in each batch. Default is 50.

    Returns:
    AsyncIterator: An async iterator yielding loaded items in batches.
    """
    load_counter = 0
    loaded_items: list[ItemT] = []
    counter = 0

    async def load_items() -> list[ItemT]:
        return await load_fn(
            cls, items[(per_load * load_counter) : (per_load * load_counter) + per_load]
        )

    for _ in items:
        if not loaded_items:
            loaded_items = await load_items()
        if counter >= per_load:
            counter = 0
            load_counter += 1
            loaded_items = await load_items()
        yield loaded_items[counter]
        counter += 1
