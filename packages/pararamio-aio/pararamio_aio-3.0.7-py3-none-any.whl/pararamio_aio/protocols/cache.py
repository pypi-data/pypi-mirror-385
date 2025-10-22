"""Cache protocol definitions for asynchronous cache backends."""

# Re-export from core to maintain backward compatibility
from pararamio_aio._core.protocols import AsyncCacheProtocol, AsyncCacheStatsProtocol

__all__ = ('AsyncCacheProtocol', 'AsyncCacheStatsProtocol')
