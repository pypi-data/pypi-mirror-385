"""Async client for Pararamio API."""
# pylint: disable=too-many-lines

from __future__ import annotations

import asyncio
import datetime
import logging
import os
from collections.abc import AsyncGenerator, AsyncIterator, Callable, Iterable, Sequence
from datetime import timedelta
from http.cookies import SimpleCookie
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING, Any, BinaryIO, TypedDict, TypeVar, cast, overload

import httpx
from pararamio_aio._core import (
    POSTS_LIMIT,
    XSRF_HEADER_NAME,
    PararamioAuthenticationError,
    PararamioHTTPRequestError,
    PararamioValidationError,
)
from pararamio_aio._core._types import GroupSyncResponseT
from pararamio_aio._core.api_schemas.responses import (
    SessionItem,
    SessionsResponse,
)
from pararamio_aio._core.api_schemas.responses.file import DeleteFileResponse, FileResponse
from pararamio_aio._core.api_schemas.responses.user import ChatTagsResponse
from pararamio_aio._core.constants.endpoints import PRIVATE_MESSAGE_URL
from pararamio_aio._core.models.post import CorePost
from pararamio_aio._core.utils import process_cookie_for_storage

from .cache.helpers import generate_cache_key
from .cookie_manager import AsyncCookieManager, AsyncInMemoryCookieManager
from .file_operations import delete_file, download_file, upload_file
from .models import Chat, File, Group, Post, Team, User
from .protocols.cache import AsyncCacheProtocol
from .utils import (
    async_authenticate,
    async_do_second_step_with_code,
    async_lazy_loader,
    get_async_xsrf_token,
)

if TYPE_CHECKING:
    from .models.user import UserSearchResult

ProfileTypeT = dict[str, Any]


class ChatCreationData(TypedDict, total=False):
    """TypedDict for chat creation data based on API documentation."""

    # Required fields
    title: str
    description: str
    users: list[int]
    groups: list[int]

    # Optional fields from API documentation
    organization_id: int | None
    posts_live_time: str | None  # timedelta-sec format
    two_step_required: bool
    history_mode: str  # 'all' | 'since_join'
    org_visible: bool
    allow_api: bool  # default=True, but deprecated
    read_only: bool
    mode_read_only: bool  # Additional read-only mode parameter not in docs


__all__ = ('AsyncPararamio', 'ChatCreationData')
log = logging.getLogger('pararamio_aio.client')

# TypeVar for response models
T = TypeVar('T')


def _create_simple_cookie(cookie: Any) -> tuple[SimpleCookie, str]:  # pylint: disable=too-many-branches
    """Create SimpleCookie from a cookie object.

    Returns:
        Tuple of (SimpleCookie, URL string for the cookie domain)
    """
    # Create proper URL for the cookie domain
    domain = cookie.domain
    # Remove leading dot for URL creation
    url_domain = domain[1:] if domain.startswith('.') else domain
    if not url_domain.startswith('http'):
        url_domain = f'https://{url_domain}'
    # Create URL string with a path
    url = f'{url_domain}{cookie.path}'
    # Create SimpleCookie with all attributes preserved
    simple_cookie = SimpleCookie()
    # Remove quotes from cookie value if present
    cookie_value = cookie.value
    if cookie_value.startswith('"') and cookie_value.endswith('"'):
        cookie_value = cookie_value[1:-1]
    simple_cookie[cookie.name] = cookie_value
    # Set all cookie attributes
    if cookie.domain:
        simple_cookie[cookie.name]['domain'] = cookie.domain
    if cookie.path:
        simple_cookie[cookie.name]['path'] = cookie.path
    if cookie.secure:
        simple_cookie[cookie.name]['secure'] = True
    if cookie.expires is not None:
        # Convert expires timestamp to formatted string
        expires_dt = datetime.datetime.fromtimestamp(cookie.expires, tz=datetime.UTC)
        simple_cookie[cookie.name]['expires'] = expires_dt.strftime('%a, %d %b %Y %H:%M:%S GMT')
    return simple_cookie, url


class AsyncPararamio:  # pylint: disable=too-many-public-methods
    """Asynchronous Pararamio client class.

    Provides an async client interface for interacting with the Pararamio API with
    support for lazy loading, caching, and async iterators.

    Parameters:
        login: User email address for authentication.
        password: User password for authentication.
        key: TOTP/2FA secret key for two-factor authentication (optional).
        cookie_manager: Async cookie storage manager for session persistence.
            Defaults to AsyncInMemoryCookieManager if not provided.
        cache: Async cache instance implementing AsyncCacheProtocol for response caching.
            Supports AsyncInMemoryCache or custom implementations (optional).
        session: Custom httpx.AsyncClient instance for HTTP requests (optional).
        wait_auth_limit: If True, wait for rate limits to expire instead of raising
            PararamioAuthenticationError. Default: False.
            Rate limits: 3 attempts/minute, 10 attempts/30 minutes.

    Examples:
        Basic usage with context manager:
            >>> async def example():  # pragma: allowlist secret
            ...     async with AsyncPararamio(
            ...         login='user@example.com', password='pass'
            ...     ) as client:
            ...         profile = await client.get_profile()

        With persistent cookies:
            >>> async def example():
            ...     from pararamio_aio import AsyncFileCookieManager
            ...
            ...     cookie_mgr = AsyncFileCookieManager('cookies.txt')
            ...     async with AsyncPararamio(cookie_manager=cookie_mgr) as client:
            ...         profile = await client.get_profile()

        With caching enabled:
            >>> async def example():  # pragma: allowlist secret
            ...     from pararamio_aio import AsyncInMemoryCache
            ...     from datetime import timedelta
            ...
            ...     cache = AsyncInMemoryCache(max_size=1000, default_ttl=timedelta(minutes=5))
            ...     async with AsyncPararamio(
            ...         login='user@example.com', password='pass', cache=cache
            ...     ) as client:
            ...         user = await client.get_user_by_id(123)

        Iterate over chat posts:
            >>> async def example():
            ...     async with AsyncPararamio(...) as client:
            ...         chat = await client.get_chat_by_id(123)
            ...         async for post in chat:
            ...             print(post.text)
    """

    _cookie_manager: AsyncCookieManager
    _cache: AsyncCacheProtocol | None

    def __init__(
        self,
        login: str | None = None,
        password: str | None = None,
        key: str | None = None,
        cookie_manager: AsyncCookieManager | None = None,
        cache: AsyncCacheProtocol | None = None,
        session: httpx.AsyncClient | None = None,
        wait_auth_limit: bool = False,
    ) -> None:
        self._login = login
        self._password = password
        self._key = key
        self._cache = cache
        self._wait_auth_limit = wait_auth_limit
        self._authenticated = False
        self._session = session
        self._cookie_jar = httpx.Cookies()
        self._cookie_manager = (
            cookie_manager if cookie_manager is not None else AsyncInMemoryCookieManager()
        )
        self._headers: dict[str, str] = {}
        self._profile: ProfileTypeT | None = None

    async def _load_cookies_to_session(self) -> None:
        """Load cookies from cookie manager to session."""
        cookies = self._cookie_manager.get_all_cookies()
        if not cookies:
            # Try to load if no cookies yet
            await self._cookie_manager.load_cookies()
            cookies = self._cookie_manager.get_all_cookies()

        if cookies:
            # Add cookies directly to the jar to preserve all attributes
            for cookie in cookies:
                # Skip cookies with empty or None value
                if not cookie.value:
                    continue
                # Add cookie directly to jar to preserve all attributes
                if self._session:
                    self._session.cookies.jar.set_cookie(cookie)

    def _ensure_session(self) -> None:
        """Ensure session is created and open."""
        if self._session is None or self._session.is_closed:
            self._session = httpx.AsyncClient(
                cookies=self._cookie_jar,
                timeout=30.0,
                limits=httpx.Limits(max_connections=30, max_keepalive_connections=10),
            )

    def _check_xsrf_token(self) -> None:
        """Check for XSRF token in cookies and set authentication status."""
        cookies = self._cookie_manager.get_all_cookies()
        for cookie in cookies:
            if cookie.name == '_xsrf' and cookie.value is not None:
                self._headers[XSRF_HEADER_NAME] = cookie.value
                self._authenticated = True
                break

    async def __aenter__(self) -> AsyncPararamio:
        """Async context manager entry."""
        return await self.connect()

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    @property
    def session(self) -> httpx.AsyncClient:
        """Get the httpx client session."""
        if self._session is None:
            raise RuntimeError('Client session not initialized. Use async context manager.')
        return self._session

    async def connect(self) -> AsyncPararamio:
        """Connect and initialize client session.

        This method allows using the client without async context manager.
        You must call close() when done to clean up resources.

        Returns:
            Self for chaining

        Example:
            >>> client = AsyncPararamio(  # pragma: allowlist secret
            ...     login='user@example.com', password='pass'
            ... )
            >>> await client.connect()
            >>> try:
            ...     profile = await client.get_profile()
            ... finally:
            ...     await client.close()
        """
        # Create session with cookie jar
        self._ensure_session()
        # Load cookies from cookie manager to session
        await self._load_cookies_to_session()
        # Check for XSRF token in cookies
        self._check_xsrf_token()
        return self

    async def close(self) -> None:
        """Close the client session and save cookies.

        This method should be called when done with manual session management.
        Automatically called when using async context manager.

        Example:
            >>> client = AsyncPararamio(  # pragma: allowlist secret
            ...     login='user@example.com', password='pass'
            ... )
            >>> await client.connect()
            >>> try:
            ...     profile = await client.get_profile()
            ... finally:
            ...     await client.close()
        """
        # Save cookies if we have a cookie manager
        await self._save_cookies_to_manager()
        # Close session if it exists
        if self._session:
            await self._session.aclose()

    async def _save_cookies_to_manager(self) -> None:
        """Save cookies from httpx cookie jar to cookie manager."""
        if not self._cookie_manager or not self._session:
            return

        # Only save if we have cookies in session
        if self._session.cookies:
            # Don't clear cookies - just update/add new ones
            for cookie in self._session.cookies.jar:
                processed_cookie = process_cookie_for_storage(cookie)
                self._cookie_manager.add_cookie(processed_cookie)

            # Save cookies after updating
            await self._cookie_manager.save_cookies()
        # If session has no cookies, don't save anything to preserve existing cookies

    async def authenticate(
        self,
        login: str | None = None,
        password: str | None = None,
        key: str | None = None,
    ) -> bool:
        """Authenticate with the Pararamio API.

        Args:
            login: Optional login override
            password: Optional password override
            key: Optional key override

        Returns:
            True if authentication successful
        """
        login = login or self._login or ''
        password = password or self._password or ''
        key = key or self._key or ''
        if not key:
            raise PararamioAuthenticationError('key must be set and not empty')

        self._authenticated, xsrf_token = await async_authenticate(
            self.session, login, password, key, self._wait_auth_limit
        )
        if self._authenticated:
            self._headers[XSRF_HEADER_NAME] = xsrf_token
            # Save cookies through cookie manager
            await self._save_cookies_to_manager()

        return self._authenticated

    async def authenticate_with_code(
        self,
        code: str,
        login: str | None = None,
        password: str | None = None,
    ) -> bool:
        """Authenticate with a TOTP code directly.

        Args:
            code: The 6-digit authentication code. Must be set and not empty.
            login: Optional login override
            password: Optional password override

        Returns:
            True if authentication successful

        Raises:
            PararamioAuthenticationError: If the code is not provided or is empty.
        """
        login = login or self._login or ''
        password = password or self._password or ''
        if not code:
            raise PararamioAuthenticationError('code must be set and not empty')

        self._authenticated, xsrf_token = await async_authenticate(
            self.session,
            login,
            password,
            key=None,
            wait_auth_limit=self._wait_auth_limit,
            second_step_fn=async_do_second_step_with_code,
            second_step_arg=code,
        )

        if self._authenticated:
            self._headers[XSRF_HEADER_NAME] = xsrf_token
            # Save cookies through cookie manager
            await self._save_cookies_to_manager()

        return self._authenticated

    async def _ensure_authenticated(self) -> None:
        """Ensure the client is authenticated."""
        if not self._authenticated:
            success = await self.authenticate()
            if not success:
                raise PararamioAuthenticationError('Failed to authenticate')

    async def _api_request_with_retry(self, method: str, url: str, **kwargs: Any) -> dict[str, Any]:  # pylint: disable=too-many-branches
        """Make API request with retry logic for specific error codes."""
        try:
            return await self._api_request(method, url, **kwargs)
        except PararamioHTTPRequestError as e:
            code = e.code
            message = str(e).lower()

            # XSRF token errors should always be retried
            if 'xsrf' in message or 'csrf' in message:
                log.info('XSRF token error, retrying with new token')
                self._headers[XSRF_HEADER_NAME] = ''
                return await self._api_request(method, url, **kwargs)

            # Retry for rate limits (429) and server errors (500-599)
            if code == 429 or 500 <= code < 600:
                log.warning('Retryable error %d, attempting retry', code)
                return await self._api_request(method, url, **kwargs)

            # All other errors (401, 403, 404, etc.) should raise immediately
            raise

    async def _api_request(self, method: str, url: str, **kwargs: Any) -> dict[str, Any]:
        """Make raw API request."""
        await self._ensure_authenticated()
        # Ensure XSRF token is present in headers
        if not self._headers.get(XSRF_HEADER_NAME):
            try:
                xsrf_token = await get_async_xsrf_token(self.session)
                self._headers[XSRF_HEADER_NAME] = xsrf_token
                # Save cookies after getting new XSRF token
                await self._save_cookies_to_manager()
            except (httpx.HTTPError, ValueError) as e:
                log.warning('Failed to get XSRF token: %s', e)

        full_url = f'https://api.pararam.io{url}'
        try:
            response = await self.session.request(method, full_url, headers=self._headers, **kwargs)
        except httpx.HTTPError as e:
            # Wrap httpx errors in our custom exception
            raise PararamioHTTPRequestError(
                full_url,
                500,  # Use 500 for network errors
                f'Network error: {e}',
                [],
                BytesIO(b''),
            ) from e

        if response.status_code != 200:
            # Read response body for error details
            error_body = response.text  # This is a property, won't raise
            # Create a BytesIO object for the error body to match expected interface
            error_fp = BytesIO(
                error_body.encode('utf-8') if error_body else b''
            )  # BytesIO already imported at top of a file

            raise PararamioHTTPRequestError(
                full_url,
                response.status_code,
                f'HTTP {response.status_code}',
                list(response.headers.items()),
                error_fp,
            )
        return cast('dict[str, Any]', response.json())

    @overload
    async def api_get(
        self,
        url: str,
        *,
        cacheable: bool = False,
        cache_key: str | None = None,
        cache_key_fn: Callable[[str], str] | None = None,
        validator: Callable[[Any], str | None] | None = None,
    ) -> dict[str, Any]: ...

    @overload
    async def api_get(
        self,
        url: str,
        *,
        response_model: type[T],
        cacheable: bool = False,
        cache_key: str | None = None,
        cache_key_fn: Callable[[str], str] | None = None,
        validator: Callable[[Any], str | None] | None = None,
    ) -> T: ...

    async def api_get(
        self,
        url: str,
        *,
        response_model: type[T] | None = None,
        cacheable: bool = False,
        cache_key: str | None = None,
        cache_key_fn: Callable[[str], str] | None = None,
        validator: Callable[[Any], str | None] | None = None,
    ) -> T | dict[str, Any]:
        """Make an authenticated GET request with optional caching.

        Args:
            url: API endpoint URL.
            response_model: Optional type to cast the response to.
            cacheable: Whether this request can be cached (default: False).
            cache_key: Explicit cache key to use.
            cache_key_fn: Function to generate a cache key from URL.
            validator: Optional function to validate response. Should return None on success
                      or an error message on failure.

        Returns:
            JSON response as dict or cast to response_model

        Raises:
            PararamioValidationError: If validator returns an error message
        """
        # Determine a cache key if caching is enabled
        key = None
        if self._cache is not None and cacheable:
            if cache_key:
                key = cache_key
            elif cache_key_fn:
                key = cache_key_fn(url)

            # Try to get from cache
            if key:
                cached = await self._cache.get(key)
                if cached is not None:
                    return cached if not response_model else cast('T', cached)

        # Make the API request
        response = await self._api_request_with_retry('GET', url)

        # Validate response
        if validator:
            error = validator(response)
            if error is not None:
                raise PararamioValidationError(str(error))

        # Cache successful response if caching is enabled
        if self._cache is not None and cacheable and key:
            await self._cache.set(key, response)  # TTL will be determined by cache

        if response_model:
            return cast('T', response)

        return response

    async def _process_mutation_response(
        self,
        response: Any,
        *,
        validator: Callable[[Any], str | None] | None = None,
        invalidate_tags: list[str] | None = None,
        response_model: type[T] | None = None,
    ) -> T | dict[str, Any]:
        """Process mutation response with validation and cache invalidation.

        Args:
            response: The response from API request
            validator: Optional function to validate response
            invalidate_tags: List of cache tags to invalidate after successful mutation
            response_model: Optional type to cast the response to

        Returns:
            Validated and optionally cast response

        Raises:
            PararamioValidationError: If validator returns an error message
        """
        if validator:
            error = validator(response)
            if error is not None:
                raise PararamioValidationError(str(error))

        # Invalidate cache tags after successful mutation
        if self._cache is not None and invalidate_tags:
            await self._cache.invalidate_tags(invalidate_tags)

        if response_model:
            return cast('T', response)

        return cast('dict[str, Any]', response)

    @overload
    async def api_post(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        *,
        validator: Callable[[Any], str | None] | None = None,
        invalidate_tags: list[str] | None = None,
    ) -> dict[str, Any]: ...

    @overload
    async def api_post(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        *,
        response_model: type[T],
        validator: Callable[[Any], str | None] | None = None,
        invalidate_tags: list[str] | None = None,
    ) -> T: ...

    async def api_post(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        *,
        response_model: type[T] | None = None,
        validator: Callable[[Any], str | None] | None = None,
        invalidate_tags: list[str] | None = None,
    ) -> T | dict[str, Any]:
        """Make an authenticated POST request.

        Args:
            url: API endpoint URL
            data: Optional data payload
            response_model: Optional type to cast the response to
            validator: Optional function to validate response. Should return None on success
                      or an error message on failure.
            invalidate_tags: List of cache tags to invalidate after successful mutation

        Returns:
            JSON response as dict or cast to response_model

        Raises:
            PararamioValidationError: If validator returns an error message
        """
        response = await self._api_request_with_retry('POST', url, json=data)
        return await self._process_mutation_response(
            response,
            validator=validator,
            invalidate_tags=invalidate_tags,
            response_model=response_model,
        )

    @overload
    async def api_put(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        *,
        validator: Callable[[Any], str | None] | None = None,
        invalidate_tags: list[str] | None = None,
    ) -> dict[str, Any]: ...

    @overload
    async def api_put(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        *,
        response_model: type[T],
        validator: Callable[[Any], str | None] | None = None,
        invalidate_tags: list[str] | None = None,
    ) -> T: ...

    async def api_put(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        *,
        response_model: type[T] | None = None,
        validator: Callable[[Any], str | None] | None = None,
        invalidate_tags: list[str] | None = None,
    ) -> T | dict[str, Any]:
        """Make an authenticated PUT request.

        Args:
            url: API endpoint URL
            data: Optional data payload
            response_model: Optional type to cast the response to
            validator: Optional function to validate response. Should return None on success
                      or an error message on failure.
            invalidate_tags: List of cache tags to invalidate after successful mutation

        Returns:
            JSON response as dict or cast to response_model

        Raises:
            PararamioValidationError: If validator returns an error message
        """
        response = await self._api_request_with_retry('PUT', url, json=data)
        return await self._process_mutation_response(
            response,
            validator=validator,
            invalidate_tags=invalidate_tags,
            response_model=response_model,
        )

    @overload
    async def api_delete(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        *,
        validator: Callable[[Any], str | None] | None = None,
        invalidate_tags: list[str] | None = None,
    ) -> dict[str, Any]: ...

    @overload
    async def api_delete(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        *,
        response_model: type[T],
        validator: Callable[[Any], str | None] | None = None,
        invalidate_tags: list[str] | None = None,
    ) -> T: ...

    async def api_delete(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        *,
        response_model: type[T] | None = None,
        validator: Callable[[Any], str | None] | None = None,
        invalidate_tags: list[str] | None = None,
    ) -> T | dict[str, Any]:
        """Make an authenticated DELETE request.

        Args:
            url: API endpoint URL
            data: Optional data payload
            response_model: Optional type to cast the response to
            validator: Optional function to validate response. Should return None on success
                      or an error message on failure.
            invalidate_tags: List of cache tags to invalidate after successful mutation

        Returns:
            JSON response as dict or cast to response_model

        Raises:
            PararamioValidationError: If validator returns an error message
        """
        response = await self._api_request_with_retry('DELETE', url, json=data)
        return await self._process_mutation_response(
            response,
            validator=validator,
            invalidate_tags=invalidate_tags,
            response_model=response_model,
        )

    async def get_profile(self) -> ProfileTypeT:
        """Get user profile.

        Returns:
            User profile data
        """
        if not self._profile:
            response = await self.api_get('/user/me')
            self._profile = response
        return self._profile

    async def get_cookies(self) -> httpx.Cookies:
        """Get current cookie jar.

        If not authenticated, performs authentication first.

        Returns:
            Current httpx Cookies object
        """
        if not self._authenticated:
            await self.authenticate()
        return self._cookie_jar

    def get_headers(self) -> dict[str, str]:
        """Get current request headers.

        Note: Unlike sync version, this doesn't trigger authentication.
        Use authenticate() explicitly if needed.

        Returns:
            Copy of current headers dict
        """
        return self._headers.copy()

    async def search_users(self, query: str, include_self: bool = False) -> list[UserSearchResult]:
        """Search for users based on the given query string.

        Args:
            query: The search query used to find matching users.
            include_self: Whether to include current user in results. Default is False.

        Returns:
            List of UserSearchResult objects that match the search query.
        """
        return await User.search(self, query, include_self)

    async def get_user_by_id(self, user_id: int) -> User | None:
        """Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User object or None if not found
        """
        # Generate cache key
        cache_key = generate_cache_key('user', 'get', user_id)

        # Check cache first if available
        if self._cache is not None:
            cached = await self._cache.get(cache_key)
            if cached is not None:
                return cast('User | None', cached)

        # Fetch from API
        try:
            users = list(await self.get_users_by_ids([user_id]))
            result = users[0] if users else None
        except (httpx.HTTPError, IndexError, KeyError):
            result = None

        # Cache the result
        if self._cache is not None and result is not None:
            await self._cache.set(cache_key, result, ttl=timedelta(minutes=5))

        return result

    async def get_users_by_ids(
        self,
        ids: Sequence[int],
        load_per_request: int = 100,  # noqa: ARG002
    ) -> Iterable[User]:
        """Get multiple users by IDs.

        Args:
            ids: Sequence of user IDs
            load_per_request: Number of users to load per request (ignored in async)

        Returns:
            Iterable of user objects
        """
        if not ids:
            return iter([])
        if len(ids) > 100:
            raise PararamioValidationError('too many ids, max 100')

        url = '/user/list?ids=' + ','.join(map(str, ids))
        response = await self.api_get(url)
        users = []
        for user_data in response.get('users', []):
            user = User.from_dict(self, user_data)
            users.append(user)
        return users

    async def get_chat_by_id(self, chat_id: int) -> Chat | None:
        """Get a chat by ID.

        Args:
            chat_id: Chat ID

        Returns:
            Chat object or None if not found
        """
        try:
            chats = await self.get_chats_by_ids([chat_id])
            return chats[0] if chats else None
        except (httpx.HTTPError, IndexError, KeyError):
            return None

    async def get_chats_by_ids(self, ids: Sequence[int]) -> list[Chat]:
        """Get multiple chats by IDs.

        Args:
            ids: Sequence of chat IDs

        Returns:
            List of chat objects
        """
        if not ids:
            return []

        # Convert to sorted tuple for a consistent cache key
        ids_tuple = tuple(sorted(ids))

        # Generate a cache key
        cache_key = generate_cache_key('chats', 'get_by_ids', ids=str(ids_tuple))

        # Check cache first if available
        if self._cache is not None:
            cached = await self._cache.get(cache_key)
            if cached is not None:
                return cast('list[Chat]', cached)

        # Fetch from API
        url = f'/core/chat?ids={",".join(map(str, ids))}'
        response = await self.api_get(url)
        chats = []
        for chat_data in response.get('chats', []):
            chat = Chat.from_dict(self, chat_data)
            chats.append(chat)

        # Cache the result
        if self._cache is not None:
            await self._cache.set(cache_key, chats, ttl=timedelta(minutes=5))

        return chats

    async def list_chats(self) -> AsyncIterator[Chat]:
        """List all user chats.

        Returns:
            AsyncIterator of chat objects
        """
        url = '/core/chat/sync'
        chats_per_load = 50
        response = await self.api_get(url)
        ids = response.get('chats', [])
        return async_lazy_loader(self, ids, Chat.load_chats, per_load=chats_per_load)

    async def create_chat(
        self,
        title: str,
        description: str = '',
        users: list[int] | None = None,
        groups: list[int] | None = None,
        organization_id: int | None = None,
        posts_live_time: str | None = None,
        two_step_required: bool | None = None,
        history_mode: str | None = None,
        org_visible: bool | None = None,
        allow_api: bool | None = None,
        read_only: bool | None = None,
    ) -> Chat:
        """Create a new chat.

        Args:
            title: Chat title
            description: Chat description
            users: List of user IDs to add
            groups: List of group IDs to add
            organization_id: Optional team ID
            posts_live_time: Optional posts lifetime in timedelta-sec format
            two_step_required: Optional two-step verification requirement
            history_mode: Optional history mode ('all' or 'since_join')
            org_visible: Optional organization visibility
            allow_api: Optional API access (deprecated)
            read_only: Optional read-only mode

        Returns:
            Created a chat object
        """
        data = ChatCreationData(
            title=title,
            description=description,
            users=users or [],
            groups=groups or [],
        )
        # Add optional parameters if provided
        if organization_id is not None:
            data['organization_id'] = organization_id
        if posts_live_time is not None:
            data['posts_live_time'] = posts_live_time
        if two_step_required is not None:
            data['two_step_required'] = two_step_required
        if history_mode is not None:
            data['history_mode'] = history_mode
        if org_visible is not None:
            data['org_visible'] = org_visible
        if allow_api is not None:
            data['allow_api'] = allow_api
        if read_only is not None:
            data['read_only'] = read_only
        response = await self.api_post('/core/chat', dict(data))
        chat_id = response['chat_id']
        chat = await self.get_chat_by_id(chat_id)
        if not chat:
            raise PararamioValidationError(f'Failed to create chat with ID {chat_id}')
        return chat

    async def search_chats(
        self, query: str, *, chat_type: str = 'all', visibility: str = 'all'
    ) -> list[Chat]:
        """Search for chats.

        Args:
            query: Search string
            chat_type: Filter by type (all, private, group, etc.)
            visibility: Filter by visibility (all, visible, hidden)

        Returns:
            List of Chat objects matching the search criteria
        """
        return await Chat.search(self, query, chat_type=chat_type, visibility=visibility)

    async def get_group_by_id(self, group_id: int) -> Group | None:
        """Get group by ID.

        Args:
            group_id: Group ID

        Returns:
            Group object or None if not found
        """
        try:
            groups = [g async for g in await self.get_groups_by_ids([group_id])]
            return groups[0] if groups else None
        except (httpx.HTTPError, IndexError, KeyError, PararamioHTTPRequestError):
            return None

    async def get_groups_by_ids(
        self,
        ids: Sequence[int],
        load_per_request: int = 100,
    ) -> AsyncIterator[Group]:
        """Get multiple groups by IDs.

        Fetches groups by their IDs using lazy-loading technique which loads
        the data in smaller chunks to avoid high memory consumption.

        Args:
            ids: Sequence of group IDs
            load_per_request: Number of groups to load per request. Defaults to 100.

        Returns:
            AsyncIterator of group objects
        """
        # Convert to int sequence for async_lazy_loader
        int_ids = [int(id_) for id_ in ids]
        return async_lazy_loader(self, int_ids, Group.load_groups, per_load=load_per_request)

    async def get_groups_ids(self) -> list[int]:
        """Get IDs of groups the current user belongs to.

        Returns:
            List of group IDs that the current user is a member of.
        """
        url = '/core/group/ids'
        response = await self.api_get(url)
        return cast('list[int]', response.get('group_ids', []))

    async def sync_groups(self, ids: list[int], sync_time: str) -> GroupSyncResponseT:
        """Synchronize groups with server.

        Args:
            ids: Current group IDs
            sync_time: Last synchronization time in UTC ISO datetime format

        Returns:
            Dict containing 'new', 'groups', and 'removed' group IDs
        """
        url = '/core/group/ids'
        data = {'ids': ids, 'sync_time': sync_time}
        response = await self.api_post(url, data)
        return {
            'new': response.get('new', []),
            'groups': response.get('groups', []),
            'removed': response.get('removed', []),
        }

    async def search_posts_lazy(
        self,
        query: str,
        *,
        order_type: str = 'time',
        chat_ids: list[int] | None = None,
        max_results: int | None = None,
        per_page: int = POSTS_LIMIT,
    ) -> AsyncGenerator[Post]:
        """Search for posts with lazy loading pagination (async generator).

        Args:
            query: A search query
            order_type: Order type ('time' or 'relevance')
            chat_ids: Optional list of chat IDs to filter by
            max_results: Maximum total results to fetch (None = unlimited)
            per_page: Number of posts to fetch per page

        Yields:
            Post objects one at a time

        Example:
            >>> async def example():
            ...     async for post in client.search_posts_lazy('hello', max_results=100):
            ...         print(post.text)
        """
        async for post in Chat.search_posts_lazy(
            self,
            query,
            order_type=order_type,
            chat_ids=chat_ids,
            max_results=max_results,
            per_page=per_page,
        ):
            yield post

    async def search_posts(
        self,
        query: str,
        order_type: str = 'time',
        page: int = 1,
        chat_ids: list[int] | None = None,
        limit: int | None = None,
    ) -> tuple[int, AsyncIterator[Post]]:
        """Search for posts.

        search_posts searches for posts based on a given query and various optional parameters.

        Arguments:
        - query: The search term used to find posts.
        - order_type: Specifies the order of the search results. Default is 'time'.
        - page: The page number of the search results to retrieve. Default is 1.
        - chat_ids: Optional list of chat IDs to search within. If None, search in all chats.
        - limit: The maximum number of posts to return. If None, use the default limit.

        Returns:
        - A tuple containing the total number of posts matching
          the search query and an async iterator of Post objects.

        Note: This endpoint is not in the official documentation but works in practice.
        """
        # Fetch from API
        return await Chat.search_posts(
            self, query, order_type=order_type, page=page, chat_ids=chat_ids, limit=limit
        )

    async def _load_posts_from_data(self, posts_data: list[dict[str, Any]]) -> list[Post]:
        """Create Post objects from search results - creates minimal Post objects (lazy loading)."""
        posts = []
        created_chats = {}

        for post_data in posts_data:
            # API returns thread_id in search results
            thread_id = post_data.get('thread_id')
            post_no = post_data.get('post_no')

            if thread_id and post_no:
                # Create Chat if not exists
                if thread_id not in created_chats:
                    created_chats[thread_id] = Chat(self, id=thread_id)

                # Create a Post object with minimal data (post_no only)
                # Full data will be loaded on demand via lazy loading
                post = Post(created_chats[thread_id], post_no=post_no)
                posts.append(post)

        return posts

    async def get_post(self, chat_id: int, post_no: int) -> Post | None:
        """Get a specific post by chat ID and post-number.

        Args:
            chat_id: Chat ID
            post_no: Post number

        Returns:
            Post object or None if not found
        """
        try:
            return await Chat(self, chat_id=chat_id).get_post(post_no)
        except (httpx.HTTPError, IndexError, KeyError, PararamioHTTPRequestError):
            return None

    async def _upload_file(
        self,
        file: BinaryIO | BytesIO,
        chat_id: int,
        *,
        filename: str | None = None,
        type_: str | None = None,
        organization_id: int | None = None,
        reply_no: int | None = None,
        quote_range: str | None = None,
    ) -> FileResponse:
        """
        Internal method for uploading a file to a specified chat or organization.

        Args:
            file: A binary stream of the file to be uploaded.
            chat_id: The ID of the chat where the file will be uploaded.
            filename: An optional parameter that specifies the name of the file.
            type_: An optional parameter that specifies the type of file being uploaded.
                   If not provided, it will be inferred from the filename.
            organization_id: An optional parameter that specifies the ID of the organization
                             if the file is an organization avatar.
            reply_no: An optional parameter that specifies the reply number
                      associated with the file.
            quote_range: An optional parameter that specifies the range
                         of quotes associated with the file.

        Returns:
            FileResponse with the response from the upload_file function.

        Raises:
            PararamioValidationError: If filename is not set when type is None,
            or if organization_id is not set when type is organization_avatar,
            or if chat_id is not set when type is chat_avatar.
        """
        await self._ensure_authenticated()

        fields, content_type = CorePost.prepare_file_upload_fields(
            file=file,
            chat_id=chat_id,
            filename=filename,
            type_=type_,
            organization_id=organization_id,
            reply_no=reply_no,
            quote_range=quote_range,
        )
        # Convert FileUploadFields to a list of tuples for upload_file
        fields_list: list[tuple[str, str | int | None]] = [
            (k, cast('str | int | None', v)) for k, v in fields.items()
        ]
        result = await upload_file(
            self.session,
            fp=file,
            fields=fields_list,
            filename=filename,
            content_type=content_type,
            headers=self._headers,
        )
        return cast('FileResponse', result)

    async def upload_file(
        self,
        file: str | BytesIO | BinaryIO | os.PathLike[str],
        chat_id: int,
        *,
        filename: str | None = None,
        content_type: str | None = None,
        reply_no: int | None = None,
        quote_range: str | None = None,
    ) -> File:
        """
        Upload a file to a specified chat.

        Args:
            file: The file to be uploaded. It can be a file path,
                  a BytesIO object, or an os.PathLike object.
            chat_id: The ID of the chat where the file should be uploaded.
            filename: The name of the file.
                      If not specified and the file is a path, the basename of the file
                      path will be used.
            content_type: The MIME type of the file.
            reply_no: The reply number in the chat to which this file is in response.
            quote_range: The range of messages being quoted.

        Returns:
            File: An instance of the File class representing the uploaded file.
        """
        if isinstance(file, str | os.PathLike):
            filename = filename or Path(file).name
            # Read file synchronously in executor to avoid blocking
            loop = asyncio.get_event_loop()

            def read_file_sync() -> bytes:
                with Path(file).open('rb') as f:
                    return f.read()

            content = await loop.run_in_executor(None, read_file_sync)
            bio = BytesIO(content)
            res = await self._upload_file(
                bio,
                chat_id,
                filename=filename,
                type_=content_type,
                reply_no=reply_no,
                quote_range=quote_range,
            )
        else:
            res = await self._upload_file(
                file,
                chat_id,
                filename=filename,
                type_=content_type,
                reply_no=reply_no,
                quote_range=quote_range,
            )
        # res is FileResponse from _upload_file, pass it directly to File constructor
        return File(self, **res)

    async def delete_file(self, guid: str) -> DeleteFileResponse:
        """
        Delete a file identified by the provided GUID.

        Args:
            guid: The globally unique identifier of the file to be deleted.

        Returns:
            DeleteFileResponse: The result of the deletion operation.
        """
        return await delete_file(self.session, guid, headers=self._headers)

    async def download_file(self, guid: str, filename: str) -> BytesIO:
        """
        Download and return a file as a BytesIO object given its unique identifier and filename.

        Args:
            guid: The unique identifier of the file to be downloaded.
            filename: The name of the file to be downloaded.

        Returns:
            BytesIO: A BytesIO object containing the downloaded file content.
        """
        return await download_file(self.session, guid, filename, headers=self._headers)

    async def post_private_message_by_user_email(self, email: str, text: str) -> Post:
        """Post a private message to a user identified by their email address.

        Args:
            email: The email address of the user to whom the message will be sent.
            text: The content of the message to be posted.

        Returns:
            A Post object representing the posted message.
        """
        url = PRIVATE_MESSAGE_URL
        resp = await self.api_post(url, data={'text': text, 'user_email': email})
        # Get the created post
        post = await self.get_post(resp['chat_id'], resp['post_no'])
        if post is None:
            raise ValueError(
                f'Failed to retrieve created post {resp["post_no"]} from chat {resp["chat_id"]}'
            )
        return post

    async def post_private_message_by_user_id(self, user_id: int, text: str) -> Post:
        """Send a private message to a specific user.

        Args:
            user_id: The ID of the user to whom the message will be sent.
            text: The content of the message to be sent.

        Returns:
            The Post object containing information about the message sent.
        """
        url = PRIVATE_MESSAGE_URL
        resp = await self.api_post(url, data={'text': text, 'user_id': user_id})
        # Get the created post
        post = await self.get_post(resp['chat_id'], resp['post_no'])
        if post is None:
            raise ValueError(
                f'Failed to retrieve created post {resp["post_no"]} from chat {resp["chat_id"]}'
            )
        return post

    async def post_private_message_by_user_unique_name(self, unique_name: str, text: str) -> Post:
        """Post a private message to a user identified by their unique name.

        Args:
            unique_name: The unique name of the user to whom the private message is to be sent.
            text: The content of the private message.

        Returns:
            An instance of the Post class representing the posted message.
        """
        url = PRIVATE_MESSAGE_URL
        resp = await self.api_post(url, data={'text': text, 'user_unique_name': unique_name})
        # Get the created post
        post = await self.get_post(resp['chat_id'], resp['post_no'])
        if post is None:
            raise ValueError(
                f'Failed to retrieve created post {resp["post_no"]} from chat {resp["chat_id"]}'
            )
        return post

    async def mark_all_messages_as_read(self, org_id: int | None = None) -> bool:
        """Mark all messages as read for the organization or everywhere if org_id is None.

        Args:
            org_id: The ID of the organization. This parameter is optional.

        Returns:
            True if the operation was successful, False otherwise.
        """
        url = '/msg/lastread/all'
        data = {}
        if org_id is not None:
            data['org_id'] = org_id
        response = await self.api_post(url, data=data)
        return cast('bool', response.get('result', None) == 'OK')

    async def get_my_team_ids(self) -> list[int]:
        """Get IDs of teams the current user belongs to from the user profile.

        Returns:
            List of team IDs (organizations) that the current user is a member of.
        """
        profile = await self.get_profile()
        return cast('list[int]', profile.get('organizations', []))

    async def get_chat_tags(self) -> dict[str, list[int]]:
        """Get chat tags for the current user.

        Returns:
            Dictionary mapping tag names to lists of chat IDs.
        """
        response = await self.api_get('/user/chat/tags', response_model=ChatTagsResponse)
        tags_dict: dict[str, list[int]] = {}
        for tag_data in response.get('chats_tags', []):
            tags_dict[tag_data['tag']] = tag_data['chat_ids']
        return tags_dict

    async def get_teams_by_ids(self, ids: Sequence[int]) -> list[Team]:
        """Get teams (organizations) by their IDs.

        Args:
            ids: Sequence of team IDs to fetch.

        Returns:
            List of Team objects.
        """
        if not ids:
            return []
        teams = []
        # API supports max 50 IDs per request
        for i in range(0, len(ids), 50):
            chunk_ids = ids[i : i + 50]
            url = f'/core/org?ids={",".join(map(str, chunk_ids))}'
            response = await self.api_get(url)
            for team_data in response.get('orgs', []):
                team = Team(self, **team_data)
                teams.append(team)
        return teams

    async def get_my_teams(self) -> list[Team]:
        """Get all teams (organizations) that the current user belongs to.

        This is a convenience method that combines get_my_team_ids() and get_teams_by_ids().

        Returns:
            List of Team objects that the current user is a member of.
        """
        team_ids = await self.get_my_team_ids()
        return await self.get_teams_by_ids(team_ids)

    async def get_sessions(self) -> list[SessionItem]:
        """Get all active sessions for the current user.

        Returns:
            List of session objects with details about each session including
            - Session ID
            - Browser and OS information
            - IP address and location
            - Login method used
            - Whether it's the current session
        """
        response = await self.api_get('/auth/session', response_model=SessionsResponse)
        return response.get('data', [])
