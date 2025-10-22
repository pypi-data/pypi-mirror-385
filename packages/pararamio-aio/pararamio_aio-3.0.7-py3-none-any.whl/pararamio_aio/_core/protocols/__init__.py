"""Protocol definitions for cache backends."""

from .cache import AsyncCacheProtocol, AsyncCacheStatsProtocol, CacheProtocol, CacheStatsProtocol

__all__ = (
    'AsyncCacheProtocol',
    'AsyncCacheStatsProtocol',
    'CacheProtocol',
    'CacheStatsProtocol',
)
