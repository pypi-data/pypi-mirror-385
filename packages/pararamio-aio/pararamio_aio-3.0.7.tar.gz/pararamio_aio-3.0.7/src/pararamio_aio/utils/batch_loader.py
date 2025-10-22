"""Async batch loading utilities."""

from __future__ import annotations

import asyncio
from asyncio import Task
from collections.abc import Callable, Coroutine
from typing import Any, TypeVar

from pararamio_aio._core.utils import combine_ranges

T = TypeVar('T')


async def batch_load_by_ranges(
    numbers: list[int],
    loader_func: Callable[[int, int], Coroutine[Any, Any, list[T]]],
    max_gap: int = 50,
) -> dict[int, T]:
    """Load items by batching numbers into ranges and executing loaders in parallel.

    Args:
        numbers: List of numbers to load items for
        loader_func: Async function that takes start and end parameters and returns a list of items.
                    The function should handle the range loading logic.
        max_gap: Maximum gap between numbers to still consider them in the same range

    Returns:
        Dictionary mapping numbers to their corresponding loaded items

    Example:
        async def load_posts(start: int, end: int) -> list[Post]:
            # Load posts from API for range [start, end]
            return await api.get_posts(start, end)

        posts = await batch_load_by_ranges([1, 2, 3, 100, 101, 102],
            load_posts,
            max_gap=50)
        # Results in 2 API calls: one for [1, 3] and one for [100, 102]
    """
    if not numbers:
        return {}

    # Group numbers into ranges
    ranges = combine_ranges(numbers, max_gap=max_gap)

    # Create tasks for each range
    tasks: list[tuple[int, int, Task[list[T]]]] = []
    for start, end in ranges:
        task = asyncio.create_task(loader_func(start, end))
        tasks.append((start, end, task))

    # Wait for all tasks to complete
    results: dict[int, T] = {}

    for _start, _end, task in tasks:
        items = await task
        # Map items back to their numbers
        # Assumes items are returned in order and correspond to the range
        for item in items:
            # The loader function should return items that have a way to identify
            # which number they correspond to. This is a simplified mapping.
            # In practice, the items should have an identifier that can be matched.
            if hasattr(item, 'post_no'):
                # For Post objects
                number = item.post_no
                if number in numbers:
                    results[number] = item
            elif hasattr(item, 'id'):
                # For objects with id
                number = item.id
                if number in numbers:
                    results[number] = item

    return results


async def batch_load_with_extractor(
    numbers: list[int],
    loader_func: Callable[[int, int], Coroutine[Any, Any, list[T]]],
    extractor: Callable[[T], int],
    max_gap: int = 50,
) -> dict[int, T]:
    """Load items by ranges with custom number extractor.

    Args:
        numbers: List of numbers to load items for
        loader_func: Async function that takes start and end parameters and returns a list of items
        extractor: Function to extract the number from each loaded item
        max_gap: Maximum gap between numbers to consider them in same range

    Returns:
        Dictionary mapping numbers to their corresponding loaded items

    Example:
        posts = await batch_load_with_extractor([1, 2, 3, 100, 101],
            load_posts_func,
            lambda post: post.post_no,
            max_gap=50)
    """
    if not numbers:
        return {}

    # Group numbers into ranges
    ranges = combine_ranges(numbers, max_gap=max_gap)

    # Create tasks for each range
    tasks = []
    for start, end in ranges:
        task = asyncio.create_task(loader_func(start, end))
        tasks.append(task)

    # Wait for all tasks to complete and collect results
    all_items = []
    for task in tasks:
        items = await task
        all_items.extend(items)

    # Map items to their numbers using the extractor
    results = {}
    for item in all_items:
        number = extractor(item)
        if number in numbers:
            results[number] = item

    return results


async def parallel_range_executor(
    numbers: list[int],
    executor_func: Callable[[int, int], Coroutine[Any, Any, T]],
    max_gap: int = 50,
) -> list[T]:
    """Execute async function for each range in parallel.

    Args:
        numbers: List of numbers to group into ranges
        executor_func: Async function to execute for each range with start and end parameters
        max_gap: Maximum gap between numbers for grouping

    Returns:
        List of results from all executor calls

    Example:
        results = await parallel_range_executor([1, 2, 3, 100, 101],
            process_range_func,
            max_gap=50)
    """
    if not numbers:
        return []

    # Group numbers into ranges
    ranges = combine_ranges(numbers, max_gap=max_gap)

    # Create and execute tasks in parallel
    tasks = [executor_func(start, end) for start, end in ranges]
    return await asyncio.gather(*tasks)


__all__ = [
    'batch_load_by_ranges',
    'batch_load_with_extractor',
    'parallel_range_executor',
]
