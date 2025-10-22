"""Common HTTP client utilities for sync and async implementations."""

from __future__ import annotations

import time
from typing import Any, ClassVar
from urllib.parse import urljoin

from pararamio_aio._core.constants import BASE_API_URL, VERSION, XSRF_HEADER_NAME

__all__ = (
    'HTTPClientConfig',
    'RateLimitHandler',
    'build_url',
    'prepare_headers',
    'should_retry_request',
)


class HTTPClientConfig:
    """Common HTTP client configuration."""

    DEFAULT_HEADERS: ClassVar[dict[str, str]] = {
        'Content-type': 'application/json',
        'Accept': 'application/json',
        'User-agent': f'pararamio lib version {VERSION}',
    }

    # Retry configuration
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0  # seconds
    RETRY_BACKOFF = 2.0  # exponential backoff multiplier

    # Rate limit configuration
    RATE_LIMIT_RETRY_AFTER_DEFAULT = 60  # seconds
    RATE_LIMIT_MAX_RETRIES = 3

    # Status codes that trigger retry
    RETRY_STATUS_CODES: ClassVar[set[int]] = {429, 502, 503, 504}

    # Status codes that are considered successful
    SUCCESS_STATUS_CODES: ClassVar[set[int]] = {200, 201, 204}


class RateLimitHandler:
    """Handle rate limiting (429) responses."""

    last_rate_limit_time: float | None = None
    retry_after: int | None = None

    def __init__(self) -> None:
        self.last_rate_limit_time = None
        self.retry_after = None

    def handle_rate_limit(self, headers: dict[str, str]) -> int:
        """Handle rate limit response and return retry delay.

        Args:
            headers: Response headers

        Returns:
            Seconds to wait before retry
        """
        self.last_rate_limit_time = time.time()

        # Check for Retry-After header
        retry_after = headers.get('Retry-After')
        if retry_after:
            try:
                # Try to parse as integer (seconds)
                self.retry_after = int(retry_after)
            except ValueError:
                # Might be a date, use default
                self.retry_after = HTTPClientConfig.RATE_LIMIT_RETRY_AFTER_DEFAULT
        else:
            self.retry_after = HTTPClientConfig.RATE_LIMIT_RETRY_AFTER_DEFAULT

        return self.retry_after

    def should_wait(self) -> tuple[bool, int]:
        """Check if we should wait due to rate limiting.

        Returns:
            Tuple of (should_wait, seconds_to_wait)
        """
        if self.last_rate_limit_time and self.retry_after:
            elapsed = time.time() - self.last_rate_limit_time
            remaining = self.retry_after - elapsed

            if remaining > 0:
                return True, int(remaining)

        return False, 0

    def clear(self) -> None:
        """Clear rate limit state."""
        self.last_rate_limit_time = None
        self.retry_after = None


def prepare_headers(
    custom_headers: dict[str, str] | None = None,
    xsrf_token: str | None = None,
) -> dict[str, str]:
    """Prepare request headers.

    Args:
        custom_headers: Custom headers to add
        xsrf_token: XSRF token to include

    Returns:
        Combined headers dict
    """
    headers = HTTPClientConfig.DEFAULT_HEADERS.copy()

    if xsrf_token:
        headers[XSRF_HEADER_NAME] = xsrf_token

    if custom_headers:
        headers.update(custom_headers)

    return headers


def build_url(endpoint: str, base_url: str | None = None) -> str:
    """Build full URL from endpoint.

    Args:
        endpoint: API endpoint path
        base_url: Base URL (defaults to BASE_API_URL)

    Returns:
        Full URL
    """
    if endpoint.startswith('http'):
        return endpoint

    base = base_url or BASE_API_URL
    return urljoin(base, endpoint)


def should_retry_request(
    status_code: int,
    attempt: int,
    error: Exception | None = None,
) -> tuple[bool, float]:
    """Determine if request should be retried.

    Args:
        status_code: HTTP status code
        attempt: Current attempt number (1-based)
        error: Optional exception that occurred

    Returns:
        Tuple of (should_retry, delay_seconds)
    """
    if attempt >= HTTPClientConfig.MAX_RETRIES:
        return False, 0

    # Check if status code is retryable
    if status_code in HTTPClientConfig.RETRY_STATUS_CODES:
        # Special handling for rate limit
        if status_code == 429:
            # Rate limit delay is handled separately
            return True, 0

        # Calculate exponential backoff
        delay = HTTPClientConfig.RETRY_DELAY * (HTTPClientConfig.RETRY_BACKOFF ** (attempt - 1))
        return True, delay

    # Check for network errors
    if error and isinstance(error, ConnectionError | TimeoutError):
        delay = HTTPClientConfig.RETRY_DELAY * (HTTPClientConfig.RETRY_BACKOFF ** (attempt - 1))
        return True, delay

    return False, 0


class RequestResult:
    """Result of an HTTP request."""

    def __init__(
        self,
        success: bool,
        status_code: int,
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        error: str | None = None,
    ):
        self.success = success
        self.status_code = status_code
        self.data = data or {}
        self.headers = headers or {}
        self.error = error

    def is_rate_limited(self) -> bool:
        """Check if response indicates rate limiting."""
        return self.status_code == 429

    def is_success(self) -> bool:
        """Check if response is successful."""
        return self.status_code in HTTPClientConfig.SUCCESS_STATUS_CODES
