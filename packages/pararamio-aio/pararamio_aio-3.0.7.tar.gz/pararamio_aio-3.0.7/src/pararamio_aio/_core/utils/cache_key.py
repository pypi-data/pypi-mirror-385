"""Cache key generation utilities shared between sync and async implementations."""

from __future__ import annotations

import hashlib
import json
from typing import Any, TypeVar

__all__ = [
    'deserialize_from_cache',
    'generate_cache_key',
    'serialize_for_cache',
]

T = TypeVar('T')


def generate_cache_key(
    namespace: str,
    method: str,
    *args: Any,
    **kwargs: Any,
) -> str:
    """Generate a deterministic cache key.

    Args:
        namespace: Cache namespace (e.g., 'user', 'post', 'chat').
        method: Method name (e.g., 'get', 'list', 'search').
        *args: Positional arguments to include in key.
        **kwargs: Keyword arguments to include in key.

    Returns:
        A deterministic cache key string.
    """
    # Build key components
    key_parts = [namespace, method]

    # Add positional arguments
    key_parts.extend(str(arg) for arg in args if arg is not None)

    # Add sorted keyword arguments for deterministic ordering
    for k, v in sorted(kwargs.items()):
        if v is not None:
            key_parts.append(f'{k}={v}')

    # Join parts
    key_string = ':'.join(key_parts)

    # For long keys, append hash to keep reasonable length
    if len(key_string) > 100:
        key_hash = hashlib.md5(key_string.encode()).hexdigest()[:8]
        key_string = f'{key_string[:92]}:{key_hash}'

    return key_string


def serialize_for_cache(obj: Any) -> str:
    """Serialize an object for caching using safe JSON serialization.

    Args:
        obj: Object to serialize.

    Returns:
        JSON string representation.

    Raises:
        TypeError: If object cannot be serialized safely.
    """

    def safe_serializer(item: Any) -> Any:
        """Convert objects to JSON-serializable format."""
        # Handle common types that JSON doesn't support natively
        if hasattr(item, 'isoformat'):  # datetime objects
            return item.isoformat()
        if isinstance(item, (set, frozenset)):
            return list(item)
        if isinstance(item, bytes):
            return item.decode('utf-8', errors='replace')
        # For other objects, convert to string
        return str(item)

    try:
        return json.dumps(obj, default=safe_serializer, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        raise TypeError(f'Object cannot be safely serialized: {e}') from None


def deserialize_from_cache(data: str, expected_type: type[T] | None = None) -> Any:
    """Deserialize an object from cache using safe JSON deserialization.

    Args:
        data: JSON string data.
        expected_type: Optional expected type for validation.

    Returns:
        Deserialized object.

    Raises:
        ValueError: If deserialization fails or type mismatch.
    """
    try:
        obj = json.loads(data)

        # Validate type if specified
        if expected_type and not isinstance(obj, expected_type):
            raise ValueError(f'Expected {expected_type}, got {type(obj)}')

        return obj
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise ValueError(f'Failed to deserialize cache data: {e}') from None
