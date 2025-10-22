"""Retry logic and error handling for API calls."""
from __future__ import annotations

import time
from typing import Any, Callable, TypeVar

from builtins import TimeoutError as BuiltinTimeoutError

from vigil_ai.config import get_config

T = TypeVar("T")


def with_retry(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to add retry logic to API calls.

    Args:
        func: Function to wrap with retry logic

    Returns:
        Wrapped function with retries

    Examples:
        >>> @with_retry
        ... def call_api():
        ...     return api.request()
    """

    def wrapper(*args: Any, **kwargs: Any) -> T:
        config = get_config()
        attempts = config.retry_attempts
        delay = config.retry_delay

        last_error = None

        for attempt in range(attempts):
            try:
                return func(*args, **kwargs)

            except Exception as e:
                last_error = e

                # Check if we should retry
                if not should_retry(e):
                    raise

                # Last attempt - don't wait
                if attempt >= attempts - 1:
                    break

                # Wait before retry with exponential backoff
                wait_time = delay * (2 ** attempt)
                time.sleep(wait_time)

        # All retries failed
        raise last_error  # type: ignore

    return wrapper


def should_retry(error: Exception) -> bool:
    """Determine if an error should trigger a retry.

    Args:
        error: Exception that occurred

    Returns:
        True if should retry

    Examples:
        >>> should_retry(TimeoutError())
        True
        >>> should_retry(ValueError())
        False
    """
    # Retry on network/API errors
    error_types_to_retry = (
        TimeoutError,
        ConnectionError,
    )

    if isinstance(error, error_types_to_retry):
        return True

    # Retry on specific API errors (rate limiting, server errors)
    error_msg = str(error).lower()
    retry_messages = [
        "rate limit",
        "timeout",
        "503",
        "502",
        "500",
        "connection",
    ]

    return any(msg in error_msg for msg in retry_messages)


class APIError(Exception):
    """Deprecated compatibility shim for legacy imports."""


class RateLimitError(APIError):
    """Deprecated compatibility shim for legacy imports."""


class AuthenticationError(APIError):
    """Deprecated compatibility shim for legacy imports."""


TimeoutError = BuiltinTimeoutError
