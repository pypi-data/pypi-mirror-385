"""Cache helper utilities for async operations."""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from datetime import timedelta
from typing import TypeVar

# Import shared utilities from core
from pararamio_aio._core.utils.cache_key import (
    deserialize_from_cache,
    generate_cache_key,
    serialize_for_cache,
)

from pararamio_aio.protocols.cache import AsyncCacheProtocol

log = logging.getLogger('pararamio_aio.cache.helpers')

T = TypeVar('T')


async def cache_or_fetch(
    cache: AsyncCacheProtocol | None,
    key: str,
    fetch_func: Callable[[], Awaitable[T]],
    ttl: timedelta | None = None,
) -> T:
    """Async cache-or-fetch pattern helper.

    Tries to get value from cache first. If not found or cache is None,
    executes the async fetch function and stores the result in cache if available.

    Args:
        cache: Optional cache instance.
        key: Cache key.
        fetch_func: Async function to call if cache miss.
        ttl: Optional TTL for cached value.

    Returns:
        The cached or fetched value.
    """
    # Try cache first if available
    if cache is not None:
        try:
            cached = await cache.get(key)
            if cached is not None:
                log.debug('Cache hit for key: %s', key)
                return cached  # type: ignore[no-any-return]
        except Exception as e:
            log.warning('Cache get failed for key %s: %s', key, e)

    # Fetch from source
    log.debug('Cache miss for key: %s, fetching from source', key)
    result = await fetch_func()

    # Store in cache if available
    if cache is not None and result is not None:
        try:
            await cache.set(key, result, ttl=ttl)
            log.debug('Cached result for key: %s', key)
        except Exception as e:
            log.warning('Cache set failed for key %s: %s', key, e)

    return result


async def invalidate_pattern(
    cache: AsyncCacheProtocol | None,
    pattern: str,
) -> int:
    """Invalidate cache entries matching a pattern.

    Args:
        cache: Optional cache instance.
        pattern: Key pattern/prefix to invalidate.

    Returns:
        Number of keys invalidated.
    """
    if cache is None:
        return 0

    try:
        count = await cache.clear(prefix=pattern)
        log.debug('Invalidated %s cache entries with pattern: %s', count, pattern)
        return count
    except Exception as e:
        log.warning('Cache invalidation failed for pattern %s: %s', pattern, e)
        return 0


# Re-export from core for backward compatibility
__all__ = [
    'cache_or_fetch',
    'deserialize_from_cache',
    'generate_cache_key',
    'invalidate_pattern',
    'serialize_for_cache',
]
