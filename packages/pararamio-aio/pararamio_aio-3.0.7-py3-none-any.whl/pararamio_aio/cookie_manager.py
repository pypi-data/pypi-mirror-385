"""Async cookie managers for the Pararamio client."""

from __future__ import annotations

import asyncio
import functools
import json
import logging
import os
import time
import uuid
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from http.cookiejar import Cookie, CookieJar
from pathlib import Path
from typing import Any, TypeVar

from pararamio_aio._core import CookieManagerBaseMixin
from pararamio_aio._core.exceptions.base import PararamioException

T = TypeVar('T')

log = logging.getLogger(__name__)


class AsyncCookieManager(ABC):
    """Abstract async cookie manager."""

    @abstractmethod
    async def load_cookies(self) -> bool:
        """Load cookies from storage asynchronously."""

    @abstractmethod
    async def save_cookies(self) -> None:
        """Save cookies to storage asynchronously."""

    @abstractmethod
    async def acquire_auth_lock(self, timeout: float = 30.0) -> bool:
        """Acquire lock for the authentication process asynchronously."""

    @abstractmethod
    async def release_auth_lock(self) -> None:
        """Release authentication lock asynchronously."""

    @abstractmethod
    async def handle_auth_error(
        self, retry_callback: Callable[..., Awaitable[T]], *args: Any, **kwargs: Any
    ) -> T:
        """Handle authentication error with version check and retry asynchronously."""

    @abstractmethod
    def add_cookie(self, cookie: Cookie) -> None:
        """Add or update a cookie."""

    @abstractmethod
    def get_all_cookies(self) -> list[Cookie]:
        """Get all cookies."""


class AsyncFileCookieManager(CookieManagerBaseMixin, AsyncCookieManager):
    """Async file-based cookie manager."""

    def __init__(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.lock_path = Path(f'{file_path}.lock')
        self.version_path = Path(f'{file_path}.version')
        self._cookies: dict[str, Cookie] = {}
        self._version: int = 0
        self._lock = asyncio.Lock()
        self._lock_fd: int | None = None

        # Automatically load cookies synchronously if a file exists
        if self.file_path.exists():
            try:
                # Use synchronous file reading for initialization
                with self.file_path.open(encoding='utf-8') as f:
                    data = json.load(f)
                self._load_cookies_from_dict(data)
                # Try to load the version
                if self.version_path.exists():
                    with self.version_path.open(encoding='utf-8') as f:
                        self._version = int(f.read().strip())
            except (OSError, ValueError):
                # Log error but don't fail initialization
                log.exception(
                    'Failed to load cookies from %s during initialization', self.file_path
                )

    @property
    def version(self) -> int:
        """Get current version."""
        return self._version

    async def load_cookies(self) -> bool:
        """Load cookies from a file asynchronously."""
        async with self._lock:
            if not self.file_path.exists():
                return False

            try:
                loop = asyncio.get_event_loop()
                read_func = functools.partial(self.file_path.read_text, encoding='utf-8')
                content = await loop.run_in_executor(None, read_func)
                data = json.loads(content)

                self._load_cookies_from_dict(data)

            except (OSError, json.JSONDecodeError) as e:
                log.warning('Failed to load cookies from %s: %s', self.file_path, e)
                return False
            return True

    async def save_cookies(self) -> None:
        """Save cookies to file asynchronously."""
        async with self._lock:
            data = self._prepare_cookies_data()

            # Ensure directory exists
            self.file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write to a temp file first
            temp_path = Path(f'{self.file_path}.tmp')
            try:
                loop = asyncio.get_event_loop()
                content = json.dumps(data, indent=2)
                # Use functools.partial to bind the arguments
                write_func = functools.partial(temp_path.write_text, content, encoding='utf-8')
                await loop.run_in_executor(None, write_func)
                # Atomic rename
                await loop.run_in_executor(None, temp_path.rename, self.file_path)
            except (OSError, TypeError, ValueError):
                log.exception('Failed to save cookies to %s', self.file_path)
                if temp_path.exists():
                    temp_path.unlink()
                raise

    def add_cookie(self, cookie: Cookie) -> None:
        """Add or update a cookie."""
        key = self.make_key(cookie)
        self._cookies[key] = cookie
        self._version = self._increment_version()

    def get_cookie(self, domain: str, path: str, name: str) -> Cookie | None:
        """Get a specific cookie."""
        key = f'{domain}:{path}:{name}'
        return self._cookies.get(key)

    def get_all_cookies(self) -> list[Cookie]:
        """Get all cookies."""
        return list(self._cookies.values())

    def clear_cookies(self) -> None:
        """Clear all cookies."""
        self._cookies.clear()
        self._version = self._increment_version()

    def update_from_jar(self, cookie_jar: CookieJar) -> None:
        """Update cookies from a CookieJar."""
        for cookie in cookie_jar:
            key = self.make_key(cookie)
            self._cookies[key] = cookie
        self._version = self._increment_version()

    async def acquire_auth_lock(self, timeout: float = 30.0) -> bool:
        """Acquire file lock asynchronously."""
        start_time = time.time()
        loop = asyncio.get_event_loop()

        while time.time() - start_time < timeout:
            try:
                # Try to create a lock file exclusively
                self._lock_fd = await loop.run_in_executor(
                    None, os.open, str(self.lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644
                )
            except FileExistsError:
                # Lock exists, check if it's stale
                if await self._is_lock_stale():
                    await self._remove_stale_lock()
                    continue
                await asyncio.sleep(0.1)
                continue
            # Write PID for debugging
            await loop.run_in_executor(None, os.write, self._lock_fd, str(os.getpid()).encode())
            return True

        return False

    async def release_auth_lock(self) -> None:
        """Release file lock asynchronously."""
        if self._lock_fd is not None:
            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, os.close, self._lock_fd)
                self.lock_path.unlink(missing_ok=True)
            except OSError as e:
                log.warning('Failed to release lock: %s', e)
            finally:
                self._lock_fd = None

    def check_version(self) -> bool:
        """Check if our version matches the file version."""
        current_version = self._get_file_version()
        return current_version == self._version

    def refresh_if_needed(self) -> bool:
        """Reload cookies if the version changed."""
        # This needs to be async but is called from sync context
        # For now, return False to indicate async operation needed
        return not self.check_version()

    async def refresh_if_needed_async(self) -> bool:
        """Reload cookies if the version changed (async version)."""
        if not self.check_version():
            log.info('Cookie version mismatch, reloading...')
            return await self.load_cookies()
        return True

    async def handle_auth_error(
        self, retry_callback: Callable[..., Awaitable[T]], *args: Any, **kwargs: Any
    ) -> T:
        """Handle authentication error with version check and retry asynchronously."""
        log.info('Authentication error occurred (async), checking cookie version...')

        # First, check if our cookies are outdated
        if not self.check_version():
            log.info('Cookie version outdated, reloading...')
            if await self.load_cookies():
                log.info('Cookies reloaded, retrying with updated cookies...')
                try:
                    return await retry_callback(*args, **kwargs)
                except Exception as e:  # pylint: disable=broad-exception-caught
                    log.warning('Retry with updated cookies failed: %s', e)
            else:
                log.warning('Failed to reload cookies')

        # If still failing, acquire lock and re-authenticate
        log.info('Attempting re-authentication...')
        if await self.acquire_auth_lock(timeout=30.0):
            try:
                # Clear existing cookies
                self.clear_cookies()
                await self.save_cookies()

                # Call retry which should trigger re-authentication
                result = await retry_callback(*args, **kwargs)

                # Save new cookies after successful auth
                await self.save_cookies()
                return result

            finally:
                await self.release_auth_lock()
        msg = 'Failed to acquire authentication lock for re-authentication'
        raise PararamioException(msg)

    def _increment_version(self) -> int:
        """Increment version and save to file."""
        return self._increment_file_version()

    async def _is_lock_stale(self, max_age: float = 300.0) -> bool:
        """Check if the lock file is stale (older than max_age seconds)."""
        try:
            stat = self.lock_path.stat()
        except FileNotFoundError:
            return False
        age = time.time() - stat.st_mtime
        return age > max_age

    async def _remove_stale_lock(self) -> None:
        """Remove a stale lock file."""
        try:
            self.lock_path.unlink()
            log.info('Removed a stale lock file: %s', self.lock_path)
        except FileNotFoundError:
            pass


class AsyncRedisCookieManager(CookieManagerBaseMixin, AsyncCookieManager):
    """Async Redis-based cookie manager."""

    def __init__(self, redis_client: Any, key_prefix: str = 'pararamio:cookies') -> None:
        self.redis = redis_client
        self.key_prefix = key_prefix
        self.data_key = f'{key_prefix}:data'
        self.lock_key = f'{key_prefix}:lock'
        self.version_key = f'{key_prefix}:version'
        self._cookies: dict[str, Cookie] = {}
        self._version: int = 0
        self._lock = asyncio.Lock()
        self._lock_token: str | None = None

    @property
    def version(self) -> int:
        """Get current version."""
        return self._version

    async def load_cookies(self) -> bool:
        """Load cookies from Redis asynchronously."""
        async with self._lock:
            # Assuming redis_client is async
            try:
                data = await self.redis.get(self.data_key)
                return self._load_cookies_from_json(data)
            except (json.JSONDecodeError, KeyError, TypeError, AttributeError) as e:
                log.warning('Failed to load cookies from Redis: %s', e)
                return False

    async def save_cookies(self) -> None:
        """Save cookies to Redis asynchronously."""
        async with self._lock:
            data = self._prepare_cookies_data()

            try:
                await self.redis.set(self.data_key, json.dumps(data))
            except (OSError, TypeError, ValueError, AttributeError):
                log.exception('Failed to save cookies to Redis')
                raise

    def add_cookie(self, cookie: Cookie) -> None:
        """Add or update a cookie."""
        key = self.make_key(cookie)
        self._cookies[key] = cookie
        self._version = self._increment_version()

    def get_cookie(self, domain: str, path: str, name: str) -> Cookie | None:
        """Get a specific cookie."""
        key = f'{domain}:{path}:{name}'
        return self._cookies.get(key)

    def get_all_cookies(self) -> list[Cookie]:
        """Get all cookies."""
        return list(self._cookies.values())

    def clear_cookies(self) -> None:
        """Clear all cookies."""
        self._cookies.clear()
        self._version = self._increment_version()

    def update_from_jar(self, cookie_jar: CookieJar) -> None:
        """Update cookies from a CookieJar."""
        for cookie in cookie_jar:
            key = self.make_key(cookie)
            self._cookies[key] = cookie
        self._version = self._increment_version()

    def check_version(self) -> bool:
        """Check if our version matches the Redis version."""
        try:
            loop = asyncio.get_event_loop()
            future = asyncio.ensure_future(self.redis.get(self.version_key))
            version = loop.run_until_complete(future)
        except (ValueError, AttributeError, RuntimeError):
            return True
        current_version = int(version) if version else 0
        return current_version == self._version

    async def check_version_async(self) -> bool:
        """Check if our version matches Redis version (async version)."""
        try:
            version = await self.redis.get(self.version_key)
        except (ValueError, AttributeError):
            return True
        current_version = int(version) if version else 0
        return current_version == self._version

    def refresh_if_needed(self) -> bool:
        """Reload cookies if the version changed."""
        # This needs to be async
        return not self.check_version()

    async def refresh_if_needed_async(self) -> bool:
        """Reload cookies if the version changed (async version)."""
        if not await self.check_version_async():
            log.info('Cookie version mismatch, reloading...')
            return await self.load_cookies()
        return True

    def _increment_version(self) -> int:
        """Atomically increment version in Redis."""
        # This is sync but needs to use async redis
        # For now just increment locally
        self._version += 1
        return self._version

    async def _increment_version_async(self) -> int:
        """Atomically increment version in Redis."""
        try:
            self._version = await self.redis.incr(self.version_key)
        except (AttributeError, TypeError):
            log.exception('Failed to increment version in Redis')
            return self._version
        return self._version

    async def acquire_auth_lock(self, timeout: float = 30.0) -> bool:
        """Acquire distributed lock asynchronously."""
        self._lock_token = str(uuid.uuid4())

        start_time = time.time()
        while time.time() - start_time < timeout:
            # Try to set lock with expiration
            if await self.redis.set(self.lock_key, self._lock_token, nx=True, ex=300):
                return True
            await asyncio.sleep(0.1)

        return False

    async def release_auth_lock(self) -> None:
        """Release distributed lock asynchronously."""
        if self._lock_token:
            lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
            """
            try:
                await self.redis.eval(lua_script, 1, self.lock_key, self._lock_token)
            except (AttributeError, KeyError) as e:
                log.warning('Failed to release Redis lock: %s', e)
            finally:
                self._lock_token = None

    async def handle_auth_error(
        self, retry_callback: Callable[..., Awaitable[T]], *args: Any, **kwargs: Any
    ) -> T:
        """Handle authentication error with version check and retry asynchronously."""
        log.info('Authentication error occurred (async Redis), checking cookie version...')

        # First, check if our cookies are outdated
        if not await self.check_version_async():
            log.info('Cookie version outdated, reloading from Redis...')
            if await self.load_cookies():
                log.info('Cookies reloaded, retrying with updated cookies...')
                try:
                    return await retry_callback(*args, **kwargs)
                except Exception as e:  # pylint: disable=broad-exception-caught
                    log.warning('Retry with updated cookies failed: %s', e)
            else:
                log.warning('Failed to reload cookies from Redis')

        # If still failing, acquire distributed lock and re-authenticate
        log.info('Attempting re-authentication with distributed lock...')
        if await self.acquire_auth_lock(timeout=30.0):
            try:
                # Clear existing cookies
                self.clear_cookies()
                await self.save_cookies()

                # Call retry which should trigger re-authentication
                result = await retry_callback(*args, **kwargs)

                # Save new cookies after successful auth
                await self.save_cookies()
                return result

            finally:
                await self.release_auth_lock()
        msg = 'Failed to acquire distributed lock for re-authentication'
        raise PararamioException(msg)


class AsyncInMemoryCookieManager(CookieManagerBaseMixin, AsyncCookieManager):
    """Async in-memory cookie manager."""

    def __init__(self) -> None:
        self._cookies: dict[str, Cookie] = {}
        self._version: int = 0
        self._lock = asyncio.Lock()

    @property
    def version(self) -> int:
        """Get current version."""
        return self._version

    async def load_cookies(self) -> bool:
        """No-op for in-memory manager."""
        async with self._lock:
            return bool(self._cookies)

    async def save_cookies(self) -> None:
        """No-op for in-memory manager."""

    def add_cookie(self, cookie: Cookie) -> None:
        """Add or update a cookie."""
        key = self.make_key(cookie)
        self._cookies[key] = cookie
        self._version += 1

    def get_cookie(self, domain: str, path: str, name: str) -> Cookie | None:
        """Get a specific cookie."""
        key = f'{domain}:{path}:{name}'
        return self._cookies.get(key)

    def get_all_cookies(self) -> list[Cookie]:
        """Get all cookies."""
        return list(self._cookies.values())

    def clear_cookies(self) -> None:
        """Clear all cookies."""
        self._cookies.clear()
        self._version += 1

    def update_from_jar(self, cookie_jar: CookieJar) -> None:
        """Update cookies from a CookieJar."""
        for cookie in cookie_jar:
            key = self.make_key(cookie)
            self._cookies[key] = cookie
        self._version += 1

    def populate_jar(self, cookie_jar: CookieJar) -> None:
        """Populate a CookieJar with stored cookies (synchronous version for async manager)."""
        # Since this is called synchronously, we can't use the async lock
        # Just iterate over cookies without locking
        for cookie in self._cookies.values():
            cookie_jar.set_cookie(cookie)

    # noinspection PyMethodMayBeStatic
    def check_version(self) -> bool:
        """Always returns True for in-memory manager."""
        return True

    # noinspection PyMethodMayBeStatic
    def refresh_if_needed(self) -> bool:
        """No-op for in-memory manager."""
        return True

    async def acquire_auth_lock(self, timeout: float = 30.0) -> bool:  # noqa: ARG002
        """Always returns True for in-memory manager."""
        return True

    async def release_auth_lock(self) -> None:
        """No-op for in-memory manager."""

    async def handle_auth_error(
        self, retry_callback: Callable[..., Awaitable[T]], *args: Any, **kwargs: Any
    ) -> T:
        """Handle authentication error by retrying."""
        log.info('Authentication error occurred (async in-memory), retrying...')

        # For in-memory, just clear cookies and retry
        async with self._lock:
            self.clear_cookies()

        try:
            return await retry_callback(*args, **kwargs)
        except (AttributeError, TypeError):
            log.exception('Retry failed')
            raise


__all__ = [
    'AsyncCookieManager',
    'AsyncFileCookieManager',
    'AsyncInMemoryCookieManager',
    'AsyncRedisCookieManager',
]
