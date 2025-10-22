from __future__ import annotations

__all__ = (
    'PararamModelNotLoadedError',
    'PararamMultipleFoundError',
    'PararamNoNextPostError',
    'PararamNoPrevPostError',
    'PararamNotFoundError',
    'PararamioAuthenticationError',
    'PararamioCaptchaAuthenticationError',
    'PararamioException',
    'PararamioHTTPRequestError',
    'PararamioLimitExceededError',
    'PararamioMethodNotAllowedError',
    'PararamioPasswordAuthenticationError',
    'PararamioRequestError',
    'PararamioSecondFactorAuthenticationError',
    'PararamioServerResponseError',
    'PararamioTypeError',
    'PararamioValidationError',
    'PararamioValueError',
    'PararamioXSRFRequestError',
)

import json
from email.message import Message
from json import JSONDecodeError
from typing import IO, Any


class PararamioException(Exception):  # noqa: N818
    pass


class PararamioValidationError(PararamioException):
    pass


class PararamioValueError(PararamioException, ValueError):
    """Exception that is both a PararamioException and a ValueError."""


class PararamioTypeError(PararamioException, TypeError):
    """Exception that is both a PararamioException and a TypeError."""


class PararamModelNotLoadedError(PararamioException):
    """Exception raised when trying to access an attribute that hasn't been loaded yet."""


class PararamNotFoundError(PararamioException):
    """Exception raised when expected item is not found."""

    def __init__(self, message: str = 'Expected item not found'):
        super().__init__(message)


class PararamMultipleFoundError(PararamioException):
    """Exception raised when multiple items found when expecting exactly one."""

    def __init__(self, message: str = 'Multiple items found when expecting one'):
        super().__init__(message)


class PararamioHTTPRequestError(PararamioException):
    """HTTP request error for Pararamio API calls."""

    def __init__(
        self,
        url: str,
        code: int,
        msg: str,
        headers: Message[str, str] | list[tuple[str, str]] | None = None,
        fp: IO[bytes] | None = None,
    ):
        self.url = url
        self.code = code
        self.msg = msg
        self.headers = headers
        self.fp = fp
        self._response: bytes | None = None
        super().__init__(f'HTTP {code} error for {url}: {msg}')

    @property
    def response(self) -> bytes:
        """Get response body as bytes."""
        if not self._response and self.fp is not None:
            self._response = self.fp.read()
        return self._response or b''

    @property
    def message(self) -> str | None:
        """Extract error message from response JSON if available."""
        if self.code in [403, 400]:
            try:
                resp = json.loads(self.response)
                error: str | None = resp.get('error', None)
                message: str | None = resp.get('message', None)
                return error or message
            except JSONDecodeError:
                pass
        return None

    def __str__(self) -> str:
        """String representation prioritizing API error message."""
        msg = self.message
        if msg:
            return msg
        return f'HTTP {self.code}: {self.msg}'


class PararamioRequestError(PararamioException):
    pass


class PararamioServerResponseError(PararamioRequestError):
    response: dict[str, Any]

    def __init__(self, msg: str, response: dict[str, Any]) -> None:
        self.msg = msg
        self.response = response

    def __str__(self) -> str:
        return f'{self.__class__.__name__}, {self.msg or " has been raised"}'


class PararamioLimitExceededError(PararamioRequestError):
    pass


class PararamioMethodNotAllowedError(PararamioException):
    pass


class PararamioAuthenticationError(PararamioException):
    """Base authentication exception."""

    def __init__(self, message: str, error_code: str | None = None, **kwargs: Any) -> None:
        super().__init__(message)
        self.error_code = error_code
        self.retry_after: int | None = kwargs.get('retry_after')


class PararamioXSRFRequestError(PararamioAuthenticationError):
    pass


class PararamioPasswordAuthenticationError(PararamioAuthenticationError):
    pass


class PararamioSecondFactorAuthenticationError(PararamioAuthenticationError):
    pass


class PararamioCaptchaAuthenticationError(PararamioAuthenticationError):
    pass


class PararamNoNextPostError(PararamioException, StopIteration):
    pass


class PararamNoPrevPostError(PararamioException, StopIteration):
    pass
