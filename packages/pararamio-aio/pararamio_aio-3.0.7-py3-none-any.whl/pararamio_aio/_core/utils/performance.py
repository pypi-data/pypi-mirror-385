"""Performance monitoring utilities and decorators."""

from __future__ import annotations

import contextlib
import functools
import logging
import time
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar, cast

from pararamio_aio._core.utils.logging_config import LoggerManager, get_logger

# Get component-specific loggers
cache_logger = get_logger(LoggerManager.CACHE)
http_logger = get_logger(LoggerManager.HTTP_CLIENT)
lazy_logger = get_logger(LoggerManager.LAZY_LOADING)
batch_logger = get_logger(LoggerManager.BATCH_LOGIC)

T = TypeVar('T')


def _log_operation_start(
    logger: Any, operation: str, log_args: bool, args: tuple[Any, ...]
) -> None:
    """Log the start of an operation."""
    if log_args and args:
        # Try to extract key from first arg if it looks like a self.method(key, ...) call
        if len(args) > 1 and hasattr(args[0], '__class__'):
            # Skip 'self' argument
            key_arg = args[1] if len(args) > 1 else None
            if key_arg:
                logger.debug('%s START: key=%s', operation, key_arg)
        else:
            logger.debug('%s START: args=%s', operation, args[:2])  # Limit args logging
    else:
        logger.debug('%s START', operation)


def _log_operation_result(
    logger: Any,
    operation: str,
    result: Any,
    elapsed_ms: float,
    log_result: bool,
) -> None:
    """Log the result of an operation."""
    # Determine if it was a hit or miss for cache operations
    if 'cache' in operation.lower():
        if result is None:
            logger.debug('%s MISS: elapsed=%.2fms', operation, elapsed_ms)
        else:
            # Try to get size if result has __len__
            try:
                size = len(result) if hasattr(result, '__len__') else 0
                if size > 0:
                    logger.debug('%s HIT: size=%d, elapsed=%.2fms', operation, size, elapsed_ms)
                else:
                    logger.debug('%s HIT: elapsed=%.2fms', operation, elapsed_ms)
            except Exception:
                logger.debug('%s HIT: elapsed=%.2fms', operation, elapsed_ms)
    else:
        # For non-cache operations
        if log_result and result is not None:
            logger.debug(
                '%s COMPLETE: result=%s, elapsed=%.2fms',
                operation,
                str(result)[:100],  # Limit result logging
                elapsed_ms,
            )
        else:
            logger.debug('%s COMPLETE: elapsed=%.2fms', operation, elapsed_ms)


def monitor_performance(
    operation: str,
    logger: Any | None = None,
    log_args: bool = True,
    log_result: bool = False,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Monitor performance of a synchronous function.

    Args:
        operation: Name of the operation being monitored.
        logger: Logger to use (defaults to cache_logger).
        log_args: Whether to log function arguments.
        log_result: Whether to log function result.

    Returns:
        Decorated function with performance monitoring.
    """
    if logger is None:
        logger = cache_logger

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Check if logging is enabled to avoid measurement overhead
            if not logger.isEnabledFor(logging.DEBUG):
                return func(*args, **kwargs)

            start_time = time.perf_counter()
            _log_operation_start(logger, operation, log_args, args)

            try:
                result = func(*args, **kwargs)
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                _log_operation_result(logger, operation, result, elapsed_ms, log_result)
                return result

            except Exception as e:
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                logger.error('%s ERROR: %s, elapsed=%.2fms', operation, str(e), elapsed_ms)
                raise

        return cast('Callable[..., T]', wrapper)

    return decorator


def monitor_async_performance(
    operation: str,
    logger: Any | None = None,
    log_args: bool = True,
    log_result: bool = False,
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """Monitor performance of an asynchronous function.

    Args:
        operation: Name of the operation being monitored.
        logger: Logger to use (defaults to cache_logger).
        log_args: Whether to log function arguments.
        log_result: Whether to log function result.

    Returns:
        Decorated async function with performance monitoring.
    """
    if logger is None:
        logger = cache_logger

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            # Check if logging is enabled to avoid measurement overhead
            if not logger.isEnabledFor(logging.DEBUG):
                return await func(*args, **kwargs)

            start_time = time.perf_counter()
            _log_operation_start(logger, operation, log_args, args)

            try:
                result = await func(*args, **kwargs)
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                _log_operation_result(logger, operation, result, elapsed_ms, log_result)
                return result

            except Exception as e:
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                logger.error('%s ERROR: %s, elapsed=%.2fms', operation, str(e), elapsed_ms)
                raise

        return cast('Callable[..., Awaitable[T]]', wrapper)

    return decorator


def monitor_batch_operation(
    operation: str,
    batch_size_extractor: Callable[..., int] | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Monitor performance of batch operations.

    Args:
        operation: Name of the batch operation.
        batch_size_extractor: Function to extract batch size from arguments.

    Returns:
        Decorated function with batch operation monitoring.
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Check if logging is enabled to avoid measurement overhead
            if not batch_logger.isEnabledFor(logging.DEBUG):
                return func(*args, **kwargs)

            start_time = time.perf_counter()

            # Extract batch size if possible
            batch_size = 0
            if batch_size_extractor:
                with contextlib.suppress(Exception):
                    batch_size = batch_size_extractor(*args, **kwargs)

            if batch_size > 0:
                batch_logger.debug('%s START: batch_size=%d', operation, batch_size)
            else:
                batch_logger.debug('%s START', operation)

            try:
                result = func(*args, **kwargs)
                elapsed_ms = (time.perf_counter() - start_time) * 1000

                if batch_size > 0:
                    batch_logger.info(
                        '%s COMPLETE: batch_size=%d, elapsed=%.2fms (%.2fms/item)',
                        operation,
                        batch_size,
                        elapsed_ms,
                        elapsed_ms / batch_size if batch_size > 0 else 0,
                    )
                else:
                    batch_logger.info('%s COMPLETE: elapsed=%.2fms', operation, elapsed_ms)

                return result

            except Exception as e:
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                batch_logger.error('%s ERROR: %s, elapsed=%.2fms', operation, str(e), elapsed_ms)
                raise

        return cast('Callable[..., T]', wrapper)

    return decorator


def monitor_http_request(
    method: str | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Monitor performance of HTTP requests.

    Args:
        method: HTTP method (GET, POST, etc.). If None, will try to extract from args.

    Returns:
        Decorated function with HTTP request monitoring.
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Check if logging is enabled to avoid measurement overhead
            if not http_logger.isEnabledFor(logging.DEBUG):
                return func(*args, **kwargs)

            start_time = time.perf_counter()

            # Try to extract URL and method from args
            url = kwargs.get('url', args[1] if len(args) > 1 else 'unknown')
            http_method = method or kwargs.get('method', 'GET')

            http_logger.debug('HTTP %s %s START', http_method, url)

            try:
                result = func(*args, **kwargs)
                elapsed_ms = (time.perf_counter() - start_time) * 1000

                # Try to get status code from result if it's a response object
                status_code = None
                if hasattr(result, 'status_code'):
                    status_code = result.status_code
                elif hasattr(result, 'status'):
                    status_code = result.status

                if status_code:
                    http_logger.info(
                        'HTTP %s %s: status=%d, elapsed=%.2fms',
                        http_method,
                        url,
                        status_code,
                        elapsed_ms,
                    )
                else:
                    http_logger.info('HTTP %s %s: elapsed=%.2fms', http_method, url, elapsed_ms)

                return result

            except Exception as e:
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                http_logger.error(
                    'HTTP %s %s ERROR: %s, elapsed=%.2fms', http_method, url, str(e), elapsed_ms
                )
                raise

        return cast('Callable[..., T]', wrapper)

    return decorator


# Export all decorators
__all__ = [
    'monitor_async_performance',
    'monitor_batch_operation',
    'monitor_http_request',
    'monitor_performance',
]
