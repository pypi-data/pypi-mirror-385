"""Cookie management base mixin shared between sync and async implementations."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from http.cookiejar import Cookie, CookieJar
from typing import Any

log = logging.getLogger(__name__)


class CookieManagerBaseMixin:
    """Mixin with common cookie management functionality."""

    # These attributes are expected to be defined by classes using this mixin
    _cookies: dict[str, Cookie]
    _version: int

    @staticmethod
    def make_key(cookie: Cookie) -> str:
        """Make a unique key for cookie."""
        return f'{cookie.domain}:{cookie.path}:{cookie.name}'

    @staticmethod
    def cookie_to_dict(cookie: Cookie) -> dict[str, Any]:
        """Convert Cookie object to dictionary."""
        return {
            'name': cookie.name,
            'value': cookie.value,
            'domain': cookie.domain,
            'path': cookie.path,
            'secure': cookie.secure,
            'expires': cookie.expires,
            'discard': cookie.discard,
            'comment': cookie.comment,
            'comment_url': cookie.comment_url,
            'rfc2109': cookie.rfc2109,
            'port': cookie.port,
            'port_specified': cookie.port_specified,
            'domain_specified': cookie.domain_specified,
            'domain_initial_dot': cookie.domain_initial_dot,
            'path_specified': cookie.path_specified,
            'version': cookie.version,
        }

    @staticmethod
    def dict_to_cookie(data: dict[str, Any]) -> Cookie | None:
        """Convert dictionary to a Cookie object."""
        try:
            return Cookie(
                version=data.get('version', 0),
                name=data['name'],
                value=data['value'],
                port=data.get('port'),
                port_specified=data.get('port_specified', False),
                domain=data['domain'],
                domain_specified=data.get('domain_specified', True),
                domain_initial_dot=data.get('domain_initial_dot', False),
                path=data['path'],
                path_specified=data.get('path_specified', True),
                secure=data.get('secure', False),
                expires=data.get('expires'),
                discard=data.get('discard', False),
                comment=data.get('comment'),
                comment_url=data.get('comment_url'),
                rest={},
                rfc2109=data.get('rfc2109', False),
            )
        except (KeyError, TypeError):
            log.exception('Failed to create cookie from dict')
            return None

    def populate_jar(self, cookie_jar: CookieJar) -> None:
        """Populate a CookieJar with our cookies."""
        cookies = getattr(self, '_cookies', {})
        # Check if we need thread safety
        lock = getattr(self, '_lock', None)
        if lock is not None:
            with lock:
                for cookie in cookies.values():
                    cookie_jar.set_cookie(cookie)
        else:
            for cookie in cookies.values():
                cookie_jar.set_cookie(cookie)

    def has_cookies(self) -> bool:
        """Check if manager has any cookies."""
        return bool(getattr(self, '_cookies', {}))

    def _get_file_version(self) -> int:
        """Get current version from the file."""
        version_path = getattr(self, 'version_path', None)
        if not version_path or not version_path.exists():
            return 0

        try:
            with version_path.open(encoding='utf-8') as f:
                return int(f.read().strip())
        except (OSError, ValueError):
            return 0

    def _load_cookies_from_json(self, data: str | None) -> bool:
        """Load cookies from JSON data.

        Args:
            data: JSON string containing cookie's data

        Returns:
            True if loaded successfully, False otherwise
        """
        if not data:
            return False

        parsed_data = json.loads(data)
        return self._load_cookies_from_dict(parsed_data)

    def _load_cookies_from_dict(self, data: dict[str, Any]) -> bool:
        """Load cookies from dictionary data.

        Args:
            data: Dictionary containing cookie's data

        Returns:
            True if loaded successfully
        """
        self._version = data.get('version', 0)
        cookies_data = data.get('cookies', [])

        self._cookies.clear()
        for cookie_dict in cookies_data:
            cookie = self.dict_to_cookie(cookie_dict)
            if cookie:
                key = self.make_key(cookie)
                self._cookies[key] = cookie

        return True

    def _prepare_cookies_data(self) -> dict[str, Any]:
        """Prepare cookie's data for saving.

        Returns:
            Dictionary with a version, cookies, and timestamp
        """
        cookies = getattr(self, '_cookies', {})
        version = getattr(self, '_version', 0)

        cookies_data = [
            self.cookie_to_dict(cookie)
            for cookie in cookies.values()
            if not cookie.discard  # Only save persistent cookies
        ]

        return {
            'version': version,
            'cookies': cookies_data,
            'saved_at': datetime.now(UTC).isoformat(),
        }

    def _increment_file_version(self) -> int:
        """Increment version and save to file."""
        version_path = getattr(self, 'version_path', None)
        if not version_path:
            return 0

        self._version = self._get_file_version() + 1

        try:
            version_path.parent.mkdir(parents=True, exist_ok=True)
            with version_path.open('w', encoding='utf-8') as f:
                f.write(str(self._version))
        except OSError:
            log.exception('Failed to save version')

        return self._version
