"""Async Redis-based cache implementation with TTL support."""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

from pararamio_aio._core.utils.logging_config import LoggerManager, get_logger
from pararamio_aio._core.utils.performance import monitor_async_performance

from pararamio_aio.protocols.cache import AsyncCacheStatsProtocol

if TYPE_CHECKING:
    import redis.asyncio as aioredis

try:
    import redis.asyncio as aioredis
except ImportError:
    aioredis = None  # type: ignore[assignment]

log = logging.getLogger(__name__)
cache_logger = get_logger(LoggerManager.CACHE)


@dataclass
class AsyncCacheStats:
    """Async cache statistics data."""

    hits: int = 0
    misses: int = 0
    evictions: int = 0
    expirations: int = 0
    size: int = 0
    memory_bytes: int = 0
    start_time: datetime = field(default_factory=datetime.now)

    @property
    def hit_rate(self) -> float:
        """Calculate hit rate percentage."""
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0

    async def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': self.hit_rate,
            'evictions': self.evictions,
            'expirations': self.expirations,
            'size': self.size,
            'memory_bytes': self.memory_bytes,
            'uptime_seconds': (datetime.now(UTC) - self.start_time).total_seconds(),
        }

    async def reset(self) -> None:
        """Reset all counters."""
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.expirations = 0
        self.start_time = datetime.now(UTC)


class AsyncRedisCache:
    """Async Redis cache implementation with TTL support.

    This implementation provides:
    - Redis-based distributed caching with async operations
    - Pattern-based TTL configuration
    - Automatic serialization/deserialization using safe JSON
    - Prefix-based key namespacing
    - Comprehensive statistics collection

    Args:
        redis_client: Existing async Redis client instance.
        url: Redis connection URL (used if redis_client is None).
        prefix: Prefix for all cache keys to avoid collisions.
        ttl_patterns: Pattern-based TTL configuration mapping patterns to timedelta.
    """

    def __init__(
        self,
        redis_client: aioredis.Redis | None = None,
        url: str = 'redis://localhost:6379/0',
        prefix: str = 'pararamio:',
        ttl_patterns: dict[str, timedelta] | None = None,
    ):
        """Initialize async Redis cache."""
        if redis_client is None:
            if aioredis is None:
                raise ImportError(
                    'Async Redis support requires redis-py with async support. '
                    'Install with: pip install "redis[hiredis]"'
                )
            cache_logger.debug('Creating Redis client from URL: %s', url)
            self.redis = aioredis.from_url(url)  # type: ignore[no-untyped-call]
        else:
            cache_logger.debug('Using provided Redis client')
            self.redis = redis_client
        self.prefix = prefix
        self._stats = AsyncCacheStats()  # In-memory statistics

        # TTL pattern configuration with defaults
        self._ttl_patterns = ttl_patterns or {
            'post.*': timedelta(minutes=30),  # Individual posts
            'chat.*.post.*': timedelta(minutes=30),  # Posts in chat context
            'user.*': timedelta(minutes=10),  # User data
            'group.*': timedelta(minutes=10),  # Group data
            'team.*': timedelta(minutes=5),  # Team data (changes more often)
            'team.*.members': timedelta(minutes=2),  # Team members list
            'poll.*': timedelta(minutes=2),  # Polls (dynamic)
            'activity.*': timedelta(minutes=2),  # User activity
            'search.*': timedelta(minutes=1),  # Search results
            '*': timedelta(minutes=5),  # Default fallback
        }

        cache_logger.debug(
            'Async Redis cache initialized with prefix: %s, %d TTL patterns configured',
            self.prefix,
            len(self._ttl_patterns),
        )

    def get_ttl_for_key(self, key: str) -> timedelta:
        """Get TTL for a given key based on configured patterns.

        Args:
            key: Cache key to determine TTL for.

        Returns:
            TTL duration for the key based on pattern matching.
        """
        for pattern, ttl in self._ttl_patterns.items():
            if self._matches_pattern(pattern, key):
                return ttl
        return timedelta(minutes=5)  # Default fallback

    def _matches_pattern(self, pattern: str, key: str) -> bool:
        """Check if key matches pattern.

        Args:
            pattern: Pattern to match against (supports * wildcard).
            key: Key to check.

        Returns:
            True if key matches pattern, False otherwise.
        """
        # Convert pattern to regex
        regex_pattern = pattern.replace('.', r'\.').replace('*', r'[^.]*')
        return re.match(f'^{regex_pattern}$', key) is not None

    @monitor_async_performance('Async Redis GET', cache_logger)
    async def get(self, key: str) -> Any | None:
        """Get value from Redis.

        Args:
            key: Cache key to retrieve.

        Returns:
            Cached value or None if not found.
        """
        full_key = f'{self.prefix}{key}'
        try:
            data = await self.redis.get(full_key)
            if data is None:
                self._stats.misses += 1
                cache_logger.debug('Cache miss for key: %s', key)
                return None

            self._stats.hits += 1
            cache_logger.debug('Cache hit for key: %s', key)
            return json.loads(data.decode('utf-8'))
        except Exception as e:
            log.warning('Redis get error for %s: %s', key, e)
            self._stats.misses += 1
            return None

    @monitor_async_performance('Async Redis SET', cache_logger)
    async def set(self, key: str, value: Any, ttl: timedelta | None = None) -> bool:
        """Set value in Redis with TTL.

        Args:
            key: Cache key to set.
            value: Value to cache.
            ttl: Time-to-live for the cached value. If None, uses pattern-based TTL.

        Returns:
            True if value was cached successfully, False otherwise.
        """
        full_key = f'{self.prefix}{key}'

        if ttl is None:
            ttl = self.get_ttl_for_key(key)

        try:
            data = json.dumps(value, default=str, ensure_ascii=False).encode('utf-8')
            await self.redis.setex(full_key, int(ttl.total_seconds()), data)
            cache_logger.debug('Cached key: %s with TTL: %s', key, ttl)
            return True
        except Exception as e:
            log.warning('Redis set error for %s: %s', key, e)
            return False

    @monitor_async_performance('Async Redis DELETE', cache_logger)
    async def delete(self, key: str) -> bool:
        """Delete key from Redis.

        Args:
            key: Cache key to delete.

        Returns:
            True if key was deleted, False if key didn't exist.
        """
        full_key = f'{self.prefix}{key}'
        try:
            deleted = bool(await self.redis.delete(full_key))
            if deleted:
                cache_logger.debug('Deleted key: %s', key)
            return deleted
        except Exception as e:
            log.warning('Redis delete error for %s: %s', key, e)
            return False

    @monitor_async_performance('Async Redis CLEAR', cache_logger)
    async def clear(self, prefix: str | None = None) -> int:
        """Clear keys by prefix.

        Args:
            prefix: Optional key prefix to clear. If None, clears all keys with cache prefix.

        Returns:
            Number of keys cleared.
        """
        pattern = f'{self.prefix}{prefix}*' if prefix else f'{self.prefix}*'

        try:
            # Use SCAN to avoid blocking on large datasets
            keys = []
            cursor = 0
            while True:
                cursor, batch = await self.redis.scan(cursor, match=pattern, count=100)
                keys.extend(batch)
                if cursor == 0:
                    break

            if keys:
                deleted_count = await self.redis.delete(*keys)
                count = int(deleted_count) if deleted_count is not None else 0
                cache_logger.debug('Cleared %d keys with pattern: %s', count, pattern)
                return count
            return 0
        except Exception as e:
            log.warning('Redis clear error for pattern %s: %s', pattern, e)
            return 0

    async def exists(self, key: str) -> bool:
        """Check if key exists.

        Args:
            key: Cache key to check.

        Returns:
            True if key exists, False otherwise.
        """
        full_key = f'{self.prefix}{key}'
        try:
            return bool(await self.redis.exists(full_key))
        except Exception as e:
            log.warning('Redis exists error for %s: %s', key, e)
            return False

    @monitor_async_performance('Async Redis GET_STATS', cache_logger)
    async def get_stats(self) -> AsyncCacheStatsProtocol:
        """Get cache statistics.

        Returns:
            A cache statistics object.
        """
        try:
            # Update size from Redis
            # Count keys with our prefix
            cursor = 0
            count = 0
            pattern = f'{self.prefix}*'
            while True:
                cursor, keys = await self.redis.scan(cursor, match=pattern, count=100)
                count += len(keys)
                if cursor == 0:
                    break
            self._stats.size = count

            # Get memory usage from Redis INFO
            info = await self.redis.info('memory')
            self._stats.memory_bytes = info.get('used_memory', 0)

            cache_logger.debug(
                'Stats - Size: %d, Hits: %d, Misses: %d, Hit Rate: %.1f%%',
                self._stats.size,
                self._stats.hits,
                self._stats.misses,
                self._stats.hit_rate,
            )
        except Exception as e:
            log.warning('Redis stats error: %s', e)

        return self._stats

    async def close(self) -> None:
        """Close Redis connection."""
        try:
            await self.redis.close()
        except Exception as e:
            log.warning('Error closing Redis connection: %s', e)
