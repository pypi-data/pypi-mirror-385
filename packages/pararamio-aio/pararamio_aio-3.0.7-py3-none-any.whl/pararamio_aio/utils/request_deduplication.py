"""Async request deduplication utilities to avoid duplicate API calls."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from pararamio_aio._core.utils.deduplication import generate_deduplication_key

__all__ = ['AsyncRequestDeduplicator', 'generate_deduplication_key']

T = TypeVar('T')
log = logging.getLogger('pararamio_aio.request_dedup')


class AsyncRequestDeduplicator:
    """Lock-free async request deduplicator.

    Uses asyncio.Task and minimal locking for high-performance deduplication.
    When multiple async requests are made for the same resource simultaneously,
    only the first request is executed. Later requests await the
    first request to complete and receive the same result.

    Performance characteristics:
    - Lock-free task lookup (dict access is atomic in CPython)
    - Minimal lock only for task registration
    - No blocking on different keys
    """

    def __init__(self) -> None:
        """Initialize async request deduplicator."""
        self._pending: dict[str, asyncio.Task[Any]] = {}
        self._lock = asyncio.Lock()  # Only for registration, not for waiting

    async def deduplicate(self, key: str, request_fn: Callable[[], Awaitable[T]]) -> T:
        """Execute async request with deduplication (lock-free).

        If the same key is already in-flight, waits for that request to complete
        and returns its result instead of making a new request.

        Args:
            key: Unique key identifying the request (e.g., 'user:123', 'chat:456')
            request_fn: Async function to execute if no duplicate request is in flight

        Returns:
            Result from the request function
        """
        # Fast path: check if a task exists (lock-free read in CPython GIL)
        if key in self._pending:
            task = self._pending[key]
            log.debug('Duplicate request detected: %s, awaiting completion', key)
            return await task  # type: ignore[no-any-return]

        # Slow path: create a new task with minimal locking
        async with self._lock:
            # Double-check after acquiring lock (another coroutine might have created it)
            if key in self._pending:
                task = self._pending[key]
                log.debug('Duplicate request detected (race): %s, awaiting completion', key)
            else:
                # Create and register a task
                log.debug('Executing async request: %s', key)
                task = asyncio.create_task(self._execute_and_cleanup(key, request_fn))
                self._pending[key] = task

        # Await outside lock
        return await task  # type: ignore[no-any-return]

    async def _execute_and_cleanup(self, key: str, request_fn: Callable[[], Awaitable[T]]) -> T:
        """Execute request and cleanup on completion."""
        try:
            return await request_fn()
        finally:
            # Cleanup: remove from pending (fast operation, no lock needed)
            self._pending.pop(key, None)

    def generate_key(self, method: str, *args: Any, **kwargs: Any) -> str:
        """Generate a deduplication key from method name and arguments.

        Args:
            method: Method name (e.g., 'get_user', 'get_chat')
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Unique key string

        Example:
            >>> dedup = AsyncRequestDeduplicator()
            >>> key = dedup.generate_key('get_user', 123)
            >>> # Result: 'get_user:123:hash_of_kwargs'
        """
        return generate_deduplication_key(method, *args, **kwargs)

    async def clear(self) -> None:
        """Clear all pending requests.

        Useful for testing or when you want to force fresh requests.
        """
        async with self._lock:
            self._pending.clear()
        log.debug('Async request deduplicator cleared')
