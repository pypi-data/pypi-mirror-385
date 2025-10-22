"""Universal lazy loading utilities for posts iteration."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LazyLoadingConfig:
    """Configuration for lazy loading with cache-first approach.

    Attributes:
        start_post_no: Starting post number (1-based)
        end_post_no: Ending post number (inclusive)
        per_request: Number of posts to load per batch
        cache_key_template: Template for cache keys, e.g. "chat.{chat_id}.post.{post_no}"
        chat_id: Chat ID for cache key generation
    """

    start_post_no: int
    end_post_no: int
    per_request: int
    cache_key_template: str
    chat_id: int


@dataclass
class LazyLoadBatch:
    """Represents a batch of posts to load.

    Attributes:
        start: Starting post number
        end: Ending post number (inclusive)
        retry_count: Number of retry attempts for this batch
    """

    start: int
    end: int
    retry_count: int = 0


def generate_cache_key(template: str, chat_id: int, post_no: int) -> str:
    """Generate a cache key for a specific post.

    Args:
        template: Cache key template with placeholders
        chat_id: Chat ID
        post_no: Post number

    Returns:
        Formatted cache key
    """
    return template.format(chat_id=chat_id, post_no=post_no)


def get_retry_delay(attempt: int) -> float:
    """Calculate retry delay with exponential backoff.

    Args:
        attempt: Attempt number (0-based)

    Returns:
        Delay in seconds: 0.5s, 1s, 2s for attempts 0, 1, 2
    """
    return float(0.5 * (2**attempt))
