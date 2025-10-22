"""Request deduplication utilities shared between sync and async implementations."""

from __future__ import annotations

import hashlib
from typing import Any

__all__ = ['generate_deduplication_key']


def generate_deduplication_key(method: str, *args: Any, **kwargs: Any) -> str:
    """Generate a deduplication key from method name and arguments.

    Args:
        method: Method name (e.g., 'get_user', 'get_chat')
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Unique key string

    Example:
        >>> key = generate_deduplication_key('get_user', 123)
        >>> # Result: 'get_user:123:hash_of_kwargs'
    """
    # Create base key from method and positional args
    parts = [method] + [str(arg) for arg in args]

    # Add sorted kwargs to ensure consistent ordering
    if kwargs:
        kwargs_str = ','.join(f'{k}={v}' for k, v in sorted(kwargs.items()))
        kwargs_hash = hashlib.md5(kwargs_str.encode()).hexdigest()[:8]
        parts.append(kwargs_hash)

    return ':'.join(parts)
