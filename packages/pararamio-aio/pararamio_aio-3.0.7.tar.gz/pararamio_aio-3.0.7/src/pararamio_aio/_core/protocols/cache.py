"""Shared cache protocol definitions for both sync and async implementations."""

from __future__ import annotations

from datetime import timedelta
from typing import Any, Protocol


class CacheStatsProtocol(Protocol):
    """Protocol for cache statistics (synchronous)."""

    @property
    def hits(self) -> int:
        """Number of cache hits."""
        ...

    @property
    def misses(self) -> int:
        """Number of cache misses."""
        ...

    @property
    def evictions(self) -> int:
        """Number of evicted entries."""
        ...

    @property
    def expirations(self) -> int:
        """Number of expired entries."""
        ...

    @property
    def size(self) -> int:
        """Number of entries in cache."""
        ...

    @property
    def memory_bytes(self) -> int:
        """Memory usage in bytes."""
        ...

    @property
    def hit_rate(self) -> float:
        """Cache hit rate percentage (0-100)."""
        ...

    def to_dict(self) -> dict[str, Any]:
        """Convert statistics to dictionary format."""
        ...

    def reset(self) -> None:
        """Reset all statistics counters."""
        ...


class AsyncCacheStatsProtocol(Protocol):
    """Protocol for async cache statistics."""

    @property
    def hits(self) -> int:
        """Number of cache hits."""
        ...

    @property
    def misses(self) -> int:
        """Number of cache misses."""
        ...

    @property
    def evictions(self) -> int:
        """Number of evicted entries."""
        ...

    @property
    def expirations(self) -> int:
        """Number of expired entries."""
        ...

    @property
    def size(self) -> int:
        """Number of entries in cache."""
        ...

    @property
    def memory_bytes(self) -> int:
        """Memory usage in bytes."""
        ...

    @property
    def hit_rate(self) -> float:
        """Cache hit rate percentage (0-100)."""
        ...

    async def to_dict(self) -> dict[str, Any]:
        """Convert statistics to dictionary format."""
        ...

    async def reset(self) -> None:
        """Reset all statistics counters."""
        ...


class CacheProtocol(Protocol):
    """Protocol defining synchronous cache backend interface."""

    def get_ttl_for_key(self, key: str) -> timedelta:
        """Get TTL for a given key based on configured patterns.

        Args:
            key: Cache key to determine TTL for.

        Returns:
            timedelta: TTL duration for the key based on pattern matching.
        """
        ...

    def get(self, key: str) -> Any | None:
        """Get value from cache.

        Args:
            key: Cache key to retrieve.

        Returns:
            Cached value or None if not found/expired.
        """
        ...

    def set(
        self,
        key: str,
        value: Any,
        ttl: timedelta | None = None,
        tags: list[str] | None = None,
    ) -> bool:
        """Set value in cache with optional TTL and tags.

        Args:
            key: Cache key to set.
            value: Value to cache.
            ttl: Time-to-live for the cached value.
            tags: Optional list of tags to associate with this key.

        Returns:
            True if value was cached successfully, False otherwise.
        """
        ...

    def delete(self, key: str) -> bool:
        """Delete single key from cache.

        Args:
            key: Cache key to delete.

        Returns:
            True if key was deleted, False if key didn't exist.
        """
        ...

    def clear(self, prefix: str | None = None) -> int:
        """Clear cache or keys with prefix.

        Args:
            prefix: Optional key prefix to clear. If None, clears entire cache.

        Returns:
            Number of keys cleared.
        """
        ...

    def exists(self, key: str) -> bool:
        """Check if key exists in cache.

        Args:
            key: Cache key to check.

        Returns:
            True if key exists and is not expired, False otherwise.
        """
        ...

    def get_stats(self) -> CacheStatsProtocol:
        """Get cache statistics.

        Returns:
            Cache statistics object implementing CacheStatsProtocol.
        """
        ...

    def invalidate_tags(self, tags: list[str]) -> int:
        """Invalidate all cache entries with given tags.

        Args:
            tags: List of tags to invalidate.

        Returns:
            Number of keys invalidated.
        """
        ...

    def get_tags(self, key: str) -> list[str]:
        """Get tags associated with a cache key.

        Args:
            key: Cache key to get tags for.

        Returns:
            List of tags associated with the key, empty list if key not found.
        """
        ...


class AsyncCacheProtocol(Protocol):
    """Protocol defining asynchronous cache backend interface."""

    def get_ttl_for_key(self, key: str) -> timedelta:
        """Get TTL for a given key based on configured patterns.

        Args:
            key: Cache key to determine TTL for.

        Returns:
            timedelta: TTL duration for the key based on pattern matching.
        """
        ...

    async def get(self, key: str) -> Any | None:
        """Get value from cache.

        Args:
            key: Cache key to retrieve.

        Returns:
            Cached value or None if not found/expired.
        """
        ...

    async def set(
        self,
        key: str,
        value: Any,
        ttl: timedelta | None = None,
        tags: list[str] | None = None,
    ) -> bool:
        """Set value in cache with optional TTL and tags.

        Args:
            key: Cache key to set.
            value: Value to cache.
            ttl: Time-to-live for the cached value.
            tags: Optional list of tags to associate with this key.

        Returns:
            True if value was cached successfully, False otherwise.
        """
        ...

    async def delete(self, key: str) -> bool:
        """Delete single key from cache.

        Args:
            key: Cache key to delete.

        Returns:
            True if key was deleted, False if key didn't exist.
        """
        ...

    async def clear(self, prefix: str | None = None) -> int:
        """Clear cache or keys with prefix.

        Args:
            prefix: Optional key prefix to clear. If None, clears entire cache.

        Returns:
            Number of keys cleared.
        """
        ...

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache.

        Args:
            key: Cache key to check.

        Returns:
            True if key exists and is not expired, False otherwise.
        """
        ...

    async def get_stats(self) -> AsyncCacheStatsProtocol:
        """Get cache statistics.

        Returns:
            Cache statistics object implementing AsyncCacheStatsProtocol.
        """
        ...

    async def invalidate_tags(self, tags: list[str]) -> int:
        """Invalidate all cache entries with given tags.

        Args:
            tags: List of tags to invalidate.

        Returns:
            Number of keys invalidated.
        """
        ...

    async def get_tags(self, key: str) -> list[str]:
        """Get tags associated with a cache key.

        Args:
            key: Cache key to get tags for.

        Returns:
            List of tags associated with the key, empty list if key not found.
        """
        ...
