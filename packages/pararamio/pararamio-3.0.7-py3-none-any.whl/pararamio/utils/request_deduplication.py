"""Request deduplication utilities to avoid duplicate API calls."""

from __future__ import annotations

import logging
import threading
from collections.abc import Callable
from typing import Any, TypeVar

from pararamio._core.utils.deduplication import generate_deduplication_key

__all__ = ['RequestDeduplicator', 'generate_deduplication_key']

T = TypeVar('T')
log = logging.getLogger('pararamio.request_dedup')


class RequestDeduplicator:
    """Deduplicates identical in-flight requests to avoid unnecessary API calls.

    When multiple requests are made for the same resource simultaneously,
    only the first request is executed. Subsequent requests wait for the
    first request to complete and receive the same result.

    Thread-safe for concurrent requests.

    Examples:
        >>> dedup = RequestDeduplicator()
        >>> # Two simultaneous requests for the same user
        >>> def load_user(user_id):
        ...     return api.get_user(user_id)
        >>> # Only one API call is made, both get the same result
        >>> result1 = dedup.deduplicate('user:123', lambda: load_user(123))
        >>> result2 = dedup.deduplicate('user:123', lambda: load_user(123))
    """

    def __init__(self) -> None:
        """Initialize request deduplicator."""
        self._pending: dict[str, Any] = {}
        self._lock = threading.Lock()
        self._events: dict[str, threading.Event] = {}
        self._results: dict[str, Any] = {}

    def deduplicate(self, key: str, request_fn: Callable[[], T]) -> T:
        """Execute request with deduplication.

        If the same key is already in-flight, waits for that request to complete
        and returns its result instead of making a new request.

        Args:
            key: Unique key identifying the request (e.g., 'user:123', 'chat:456')
            request_fn: Function to execute if no duplicate request is in flight

        Returns:
            Result from the request function

        Example:
            >>> dedup = RequestDeduplicator()
            >>> result = dedup.deduplicate('user:123', lambda: client.get_user(123))
        """
        with self._lock:
            # Check if request is already in flight
            if key in self._pending:
                log.debug('Duplicate request detected: %s, waiting for completion', key)
                event = self._events[key]

        # If duplicate, wait for original request to complete
        if key in self._pending:
            event.wait()
            result = self._results.pop(key, None)
            log.debug('Duplicate request completed: %s', key)
            return result  # type: ignore[no-any-return]

        # Mark request as in-flight
        with self._lock:
            self._pending[key] = True
            event = threading.Event()
            self._events[key] = event

        try:
            # Execute the request
            log.debug('Executing request: %s', key)
            result = request_fn()

            # Store result for waiting requests
            with self._lock:
                self._results[key] = result

            # Notify waiting requests
            event.set()

            return result
        finally:
            # Cleanup
            with self._lock:
                self._pending.pop(key, None)
                self._events.pop(key, None)

    def generate_key(self, method: str, *args: Any, **kwargs: Any) -> str:
        """Generate a deduplication key from method name and arguments.

        Args:
            method: Method name (e.g., 'get_user', 'get_chat')
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Unique key string

        Example:
            >>> dedup = RequestDeduplicator()
            >>> key = dedup.generate_key('get_user', 123)
            >>> # Result: 'get_user:123:hash_of_kwargs'
        """
        return generate_deduplication_key(method, *args, **kwargs)

    def clear(self) -> None:
        """Clear all pending requests and cached results.

        Useful for testing or when you want to force fresh requests.
        """
        with self._lock:
            self._pending.clear()
            self._events.clear()
            self._results.clear()
        log.debug('Request deduplicator cleared')
