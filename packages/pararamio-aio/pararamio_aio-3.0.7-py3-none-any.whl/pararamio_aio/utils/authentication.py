"""Async authentication utilities."""

from __future__ import annotations

import asyncio
from io import BytesIO
from typing import Any, cast

import httpx

# Import from core
from pararamio_aio._core import (
    AUTH_INIT_URL,
    AUTH_LOGIN_URL,
    AUTH_NEXT_URL,
    AUTH_TOTP_URL,
    XSRF_HEADER_NAME,
    AuthenticationFlow,
    InvalidCredentialsError,
    PararamioAuthenticationError,
    PararamioHTTPRequestError,
    PararamioSecondFactorAuthenticationError,
    RateLimitError,
    RateLimitHandler,
    TwoFactorFailedError,
    build_url,
    generate_otp,
    prepare_headers,
)
from pararamio_aio._core.utils.logging_config import (
    LoggerManager,
    get_logger,
)

__all__ = (
    'async_authenticate',
    'async_do_second_step',
    'async_do_second_step_with_code',
    'get_async_xsrf_token',
)

# Get component-specific loggers
auth_logger = get_logger(LoggerManager.AUTH)
rate_limit_logger = get_logger(LoggerManager.RATE_LIMIT)
session_logger = get_logger(LoggerManager.SESSION)


async def get_async_xsrf_token(client: httpx.AsyncClient) -> str:
    """Get XSRF token from /auth/init endpoint.

    Args:
        client: httpx client

    Returns:
        XSRF token string

    Raises:
        PararamioAuthenticationError: If failed to get token
    """
    auth_logger.debug('Requesting XSRF token from %s', AUTH_INIT_URL)
    url = build_url(AUTH_INIT_URL)
    response = await client.get(url)
    if response.status_code == 200:
        xsrf_token = response.headers.get('X-Xsrftoken')
        if xsrf_token:
            auth_logger.debug(
                'XSRF token obtained: %s...', xsrf_token[:8] if len(xsrf_token) > 8 else '***'
            )
            return cast('str', xsrf_token)

    auth_logger.error('Failed to get XSRF token, status: %d', response.status_code)
    raise PararamioAuthenticationError('Failed to get XSRF token')


async def _make_auth_request(
    client: httpx.AsyncClient,
    url: str,
    method: str = 'GET',
    data: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    rate_limit_handler: RateLimitHandler | None = None,
    wait_auth_limit: bool = False,
) -> tuple[bool, dict[str, Any]]:
    """Make authentication request with error handling.

    Returns:
        Tuple of (success, response_data)
    """
    full_url = build_url(url)
    auth_logger.debug('Async auth request: %s %s', method, full_url)

    try:
        if method == 'POST' and data:
            response = await client.post(full_url, json=data, headers=headers)
        else:  # GET
            response = await client.get(full_url, headers=headers)

        if response.status_code == 429 and rate_limit_handler:
            # Handle rate limiting
            retry_after = rate_limit_handler.handle_rate_limit(dict(response.headers))
            if wait_auth_limit:
                rate_limit_logger.warning(
                    'Rate limit hit, waiting %d seconds before retry', retry_after
                )
                await asyncio.sleep(retry_after)
                rate_limit_logger.debug('Rate limit wait completed, retrying')
                # Retry the request after waiting
                return await _make_auth_request(
                    client, url, method, data, headers, rate_limit_handler, wait_auth_limit
                )
            rate_limit_logger.error(
                'Rate limit exceeded, would need to wait %d seconds', retry_after
            )
            raise RateLimitError(
                f'Rate limit exceeded. Retry after {retry_after} seconds',
                retry_after=retry_after,
            )

        return await _handle_auth_response(response, full_url)

    except httpx.HTTPError as e:
        raise PararamioAuthenticationError(f'Request failed: {e}') from e


async def _handle_auth_response(
    response: httpx.Response,
    full_url: str,
) -> tuple[bool, dict[str, Any]]:
    """Handle authentication response with common logic."""
    if response.status_code == 200:
        return True, response.json()
    if response.status_code < 500:
        return False, response.json()
    raise PararamioHTTPRequestError(
        full_url,
        response.status_code,
        f'HTTP {response.status_code}',
        list(response.headers.items()),
        BytesIO(response.text.encode('utf-8')),
    )


async def async_do_second_step(
    client: httpx.AsyncClient,
    headers: dict[str, str],
    key: str,
    rate_limit_handler: RateLimitHandler,
    wait_auth_limit: bool = False,
) -> tuple[bool, dict[str, str]]:
    """
    Do second step authentication with a TOTP key asynchronously.

    Args:
        client: httpx client
        headers: Headers to send
        key: TOTP key to generate one time code
        rate_limit_handler: Rate limit handler instance
        wait_auth_limit: Wait for rate limit instead of raising exception

    Returns:
        Tuple of (success, response_data)

    Raises:
        PararamioSecondFactorAuthenticationError: If 2FA fails
    """
    auth_logger.debug('Starting async 2FA with TOTP key')
    if not key:
        auth_logger.error('2FA key is empty')
        raise PararamioSecondFactorAuthenticationError('key can not be empty')

    try:
        code = generate_otp(key)
        auth_logger.debug('Generated OTP code from key')
    except Exception as e:
        auth_logger.error('Invalid 2FA key format')
        raise PararamioSecondFactorAuthenticationError('Invalid second step key') from e

    return await async_do_second_step_with_code(
        client, headers, code, rate_limit_handler, wait_auth_limit
    )


async def async_do_second_step_with_code(
    client: httpx.AsyncClient,
    headers: dict[str, str],
    code: str,
    rate_limit_handler: RateLimitHandler,
    wait_auth_limit: bool = False,
) -> tuple[bool, dict[str, str]]:
    """
    Do second step authentication with TOTP code asynchronously.

    Args:
        client: httpx client
        headers: Headers to send
        code: 6 digits code
        rate_limit_handler: Rate limit handler instance
        wait_auth_limit: Wait for rate limit instead of raising exception

    Returns:
        Tuple of (success, response_data)

    Raises:
        PararamioSecondFactorAuthenticationError: If 2FA fails
    """
    auth_logger.debug('Starting async 2FA with code')
    if not code:
        auth_logger.error('2FA code is empty')
        raise PararamioSecondFactorAuthenticationError('code can not be empty')
    if len(code) != 6:
        auth_logger.error('2FA code has invalid length: %d', len(code))
        raise PararamioSecondFactorAuthenticationError('code must be 6 digits len')

    totp_data = AuthenticationFlow.prepare_totp_data(code)
    return await _make_auth_request(
        client,
        AUTH_TOTP_URL,
        'POST',
        totp_data,
        headers,
        rate_limit_handler,
        wait_auth_limit,
    )


async def async_authenticate(
    client: httpx.AsyncClient,
    login: str,
    password: str,
    key: str | None = None,
    wait_auth_limit: bool = False,
    second_step_fn: Any = None,
    second_step_arg: str | None = None,
) -> tuple[bool, str]:
    """Authenticate with Pararamio API asynchronously.

    Follows the unified authentication flow from core.

    Args:
        client: httpx client
        login: User login
        password: User password
        key: Authentication key (for automatic TOTP generation)
        wait_auth_limit: Wait for rate limit instead of raising exception
        second_step_fn: Optional async function for second step authentication
        second_step_arg: Argument for second step function (key or code)

    Returns:
        Tuple of (success, xsrf_token)

    Raises:
        Various authentication exceptions
    """
    rate_limit_handler = RateLimitHandler()

    # Check rate limiting
    await _check_rate_limit(rate_limit_handler, wait_auth_limit)

    try:
        # Step 1: Get XSRF token and login
        xsrf_token, headers = await _perform_login(
            client, login, password, rate_limit_handler, wait_auth_limit
        )

        # Step 2: Handle second step authentication
        await _handle_second_step(
            client,
            headers,
            key,
            second_step_fn,
            second_step_arg,
            rate_limit_handler,
            wait_auth_limit,
        )

        # Step 3: Complete auth flow
        await _complete_auth_flow(client, headers, rate_limit_handler, wait_auth_limit)

        # Clear rate limit on success
        rate_limit_handler.clear()

        return True, xsrf_token

    except RateLimitError:
        # Let rate limit exceptions bubble up
        raise
    except Exception as e:
        if not isinstance(e, InvalidCredentialsError | TwoFactorFailedError):
            raise PararamioAuthenticationError(f'Authentication failed: {e}') from e
        raise


async def _check_rate_limit(rate_limit_handler: RateLimitHandler, wait_auth_limit: bool) -> None:
    """Check and handle rate limiting."""
    should_wait, wait_seconds = rate_limit_handler.should_wait()
    if should_wait:
        if wait_auth_limit:
            await asyncio.sleep(wait_seconds)
        else:
            raise RateLimitError(
                f'Rate limit exceeded. Retry after {wait_seconds} seconds', retry_after=wait_seconds
            )


async def _perform_login(
    client: httpx.AsyncClient,
    login: str,
    password: str,
    rate_limit_handler: RateLimitHandler,
    wait_auth_limit: bool,
) -> tuple[str, dict[str, str]]:
    """Perform login and handle XSRF retry if needed."""
    xsrf_token = await get_async_xsrf_token(client)
    headers = prepare_headers(xsrf_token=xsrf_token)

    login_data = AuthenticationFlow.prepare_login_data(login, password)

    success, resp = await _make_auth_request(
        client,
        AUTH_LOGIN_URL,
        'POST',
        login_data,
        headers,
        rate_limit_handler,
        wait_auth_limit,
    )

    if not success:
        # Parse error and check if we need new XSRF
        error_type, error_msg = AuthenticationFlow.parse_error_response(resp)

        if AuthenticationFlow.should_retry_with_new_xsrf(error_type, error_msg):
            # Retry with new XSRF token
            xsrf_token = await get_async_xsrf_token(client)
            headers[XSRF_HEADER_NAME] = xsrf_token

            success, _ = await _make_auth_request(
                client,
                AUTH_LOGIN_URL,
                'POST',
                login_data,
                headers,
                rate_limit_handler,
                wait_auth_limit,
            )

            if not success:
                raise InvalidCredentialsError('Login failed after XSRF retry')
        else:
            raise InvalidCredentialsError(f'Login failed: {error_msg}')

    return xsrf_token, headers


async def _handle_second_step(
    client: httpx.AsyncClient,
    headers: dict[str, str],
    key: str | None,
    second_step_fn: Any,
    second_step_arg: str | None,
    rate_limit_handler: RateLimitHandler,
    wait_auth_limit: bool,
) -> None:
    """Handle second step authentication (TOTP or custom)."""
    if second_step_fn is not None and second_step_arg:
        # Use provided second step function
        success, _ = await second_step_fn(
            client, headers, second_step_arg, rate_limit_handler, wait_auth_limit
        )
        if not success:
            raise TwoFactorFailedError('Second factor authentication failed')
    elif key:
        # Use default TOTP with a key
        try:
            code = generate_otp(key)
        except Exception as e:
            raise TwoFactorFailedError('Invalid TOTP key') from e

        totp_data = AuthenticationFlow.prepare_totp_data(code)
        success, _ = await _make_auth_request(
            client,
            AUTH_TOTP_URL,
            'POST',
            totp_data,
            headers,
            rate_limit_handler,
            wait_auth_limit,
        )

        if not success:
            raise TwoFactorFailedError('TOTP authentication failed')


async def _complete_auth_flow(
    client: httpx.AsyncClient,
    headers: dict[str, str],
    rate_limit_handler: RateLimitHandler,
    wait_auth_limit: bool,
) -> None:
    """Complete the authentication flow."""
    success, _ = await _make_auth_request(
        client, AUTH_NEXT_URL, 'GET', {}, headers, rate_limit_handler, wait_auth_limit
    )

    if not success:
        raise PararamioAuthenticationError('Failed to complete auth flow')

    success, _ = await _make_auth_request(
        client, AUTH_INIT_URL, 'GET', {}, headers, rate_limit_handler, wait_auth_limit
    )

    if not success:
        raise PararamioAuthenticationError('Failed to initialize session')
