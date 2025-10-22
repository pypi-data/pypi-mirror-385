"""Cache helper utilities for sync operations."""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import timedelta
from typing import TypeVar

# Import shared utilities from core
from pararamio._core.utils.cache_key import (
    deserialize_from_cache,
    generate_cache_key,
    serialize_for_cache,
)

from pararamio.protocols.cache import CacheProtocol

log = logging.getLogger('pararamio.cache.helpers')

T = TypeVar('T')


def cache_or_fetch(
    cache: CacheProtocol | None,
    key: str,
    fetch_func: Callable[[], T],
    ttl: timedelta | None = None,
) -> T:
    """Cache-or-fetch pattern helper.

    Tries to get value from cache first. If not found or cache is None,
    executes the fetch function and stores result in cache if available.

    Args:
        cache: Optional cache instance.
        key: Cache key.
        fetch_func: Function to call if cache miss.
        ttl: Optional TTL for cached value.

    Returns:
        The cached or fetched value.
    """
    # Try cache first if available
    if cache is not None:
        try:
            cached = cache.get(key)
            if cached is not None:
                log.debug('Cache hit for key: %s', key)
                return cached  # type: ignore[no-any-return]
        except Exception as e:
            log.warning('Cache get failed for key %s: %s', key, e)

    # Fetch from source
    log.debug('Cache miss for key: %s, fetching from source', key)
    result = fetch_func()

    # Store in cache if available
    if cache is not None and result is not None:
        try:
            cache.set(key, result, ttl=ttl)
            log.debug('Cached result for key: %s', key)
        except Exception as e:
            log.warning('Cache set failed for key %s: %s', key, e)

    return result


def invalidate_pattern(
    cache: CacheProtocol | None,
    pattern: str,
) -> int:
    """Invalidate cache entries matching a pattern.

    Args:
        cache: Optional cache instance.
        pattern: Key pattern/prefix to invalidate.

    Returns:
        Number of keys invalidated.
    """
    if cache is None:
        return 0

    try:
        count = cache.clear(prefix=pattern)
        log.debug('Invalidated %s cache entries with pattern: %s', count, pattern)
        return count
    except Exception as e:
        log.warning('Cache invalidation failed for pattern %s: %s', pattern, e)
        return 0


# Re-export from core for backward compatibility
__all__ = [
    'cache_or_fetch',
    'deserialize_from_cache',
    'generate_cache_key',
    'invalidate_pattern',
    'serialize_for_cache',
]
