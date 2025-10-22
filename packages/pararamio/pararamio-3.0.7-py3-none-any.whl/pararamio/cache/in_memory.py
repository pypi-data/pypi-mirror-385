"""Thread-safe in-memory cache implementation with LRU eviction and TTL support."""

from __future__ import annotations

import heapq
import json
import re
import sys
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

from pararamio._core.utils.logging_config import (
    LoggerManager,
    get_logger,
)

from pararamio.protocols.cache import CacheStatsProtocol

if TYPE_CHECKING:
    from .config import CacheConfig

# Get cache-specific logger
cache_logger = get_logger(LoggerManager.CACHE)


def get_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(UTC)


@dataclass
class CacheEntry:
    """Individual cache entry with metadata."""

    key: str
    value: Any
    created_at: datetime = field(default_factory=get_now)
    accessed_at: datetime = field(default_factory=get_now)
    expires_at: datetime | None = None
    access_count: int = 0
    size_bytes: int = 0
    tags: list[str] = field(default_factory=list)

    @property
    def is_expired(self) -> bool:
        """Check if entry has expired."""
        if self.expires_at is None:
            return False
        return get_now() > self.expires_at

    @property
    def ttl_remaining(self) -> timedelta | None:
        """Get remaining TTL."""
        if self.expires_at is None:
            return None
        remaining = self.expires_at - get_now()
        return remaining if remaining.total_seconds() > 0 else timedelta(0)

    def touch(self) -> None:
        """Update access time and count."""
        self.accessed_at = get_now()
        self.access_count += 1


@dataclass
class CacheStats:
    """Cache statistics data."""

    hits: int = 0
    misses: int = 0
    evictions: int = 0
    expirations: int = 0
    size: int = 0
    memory_bytes: int = 0
    start_time: datetime = field(default_factory=get_now)
    total_hit_time_ms: float = 0.0
    total_miss_time_ms: float = 0.0

    @property
    def hit_rate(self) -> float:
        """Calculate hit rate percentage."""
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0

    @property
    def avg_hit_time_ms(self) -> float:
        """Calculate average hit response time in milliseconds."""
        return (self.total_hit_time_ms / self.hits) if self.hits > 0 else 0.0

    @property
    def avg_miss_time_ms(self) -> float:
        """Calculate average miss response time in milliseconds."""
        return (self.total_miss_time_ms / self.misses) if self.misses > 0 else 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': self.hit_rate,
            'evictions': self.evictions,
            'expirations': self.expirations,
            'size': self.size,
            'memory_bytes': self.memory_bytes,
            'uptime_seconds': (get_now() - self.start_time).total_seconds(),
            'avg_hit_time_ms': self.avg_hit_time_ms,
            'avg_miss_time_ms': self.avg_miss_time_ms,
        }

    def reset(self) -> None:
        """Reset all counters."""
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.expirations = 0
        self.total_hit_time_ms = 0.0
        self.total_miss_time_ms = 0.0
        self.start_time = get_now()


class InMemoryCache:
    """Thread-safe in-memory cache with LRU eviction and TTL support.

    This implementation provides:
    - Thread-safe operations using RLock
    - LRU (Least Recently Used) eviction policy
    - TTL (Time-To-Live) support with automatic expiration
    - Memory usage tracking and limits
    - Comprehensive statistics collection
    - Efficient O(1) get/set operations (amortized)

    Args:
        max_size: Maximum number of entries in cache.
        max_memory_mb: Maximum memory usage in megabytes.
        default_ttl: Default time-to-live for entries.
        cleanup_interval: Interval for background cleanup of expired entries.
    """

    def __init__(
        self,
        max_size: int = 10000,
        max_memory_mb: int = 100,
        default_ttl: timedelta | None = None,
        cleanup_interval: timedelta = timedelta(minutes=1),
        ttl_patterns: dict[str, timedelta] | None = None,
        config: CacheConfig | None = None,
    ):
        """Initialize the in-memory cache.

        Args:
            max_size: Maximum number of entries in cache.
            max_memory_mb: Maximum memory usage in megabytes.
            default_ttl: Default time-to-live for entries.
            cleanup_interval: Interval for background cleanup of expired entries.
            ttl_patterns: Pattern-based TTL configuration mapping patterns to timedelta.
            config: Optional CacheConfig to override all other parameters.
        """
        # Use config if provided, otherwise use individual parameters
        if config:
            max_size = config.max_size
            max_memory_mb = config.max_memory_mb
            default_ttl = config.default_ttl
            cleanup_interval = config.cleanup_interval
            ttl_patterns = config.ttl_patterns

        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        self._max_size = max_size
        self._max_memory_bytes = max_memory_mb * 1024 * 1024
        self._current_memory = 0
        self._default_ttl = default_ttl or timedelta(minutes=5)
        self._stats = CacheStats()
        self._cleanup_interval = cleanup_interval
        self._expiry_heap: list[tuple[datetime, str]] = []
        self._cleanup_timer: threading.Timer | None = None
        self._tag_index: dict[str, set[str]] = {}  # Maps tags to sets of keys

        # TTL pattern configuration with defaults
        self._ttl_patterns = ttl_patterns or {
            'post.*': timedelta(minutes=30),  # Individual posts
            'chat.*.post.*': timedelta(minutes=30),  # Posts in chat context
            'user.*': timedelta(minutes=10),  # User data
            'group.*': timedelta(minutes=10),  # Group data
            'team.*': timedelta(minutes=5),  # Team data (changes more often)
            'team.*.members': timedelta(minutes=2),  # Team members list
            'poll.*': timedelta(minutes=2),  # Polls (dynamic)
            'activity.*': timedelta(minutes=2),  # User activity
            'search.*': timedelta(minutes=1),  # Search results
            '*': timedelta(minutes=5),  # Default fallback
        }

        self._start_cleanup_timer()

    def get(self, key: str) -> Any | None:
        """Get value from cache.

        Thread-safe operation that:
        1. Checks if key exists
        2. Validates entry is not expired
        3. Updates LRU order and access stats
        4. Returns cached value

        Args:
            key: Cache key to retrieve.

        Returns:
            Cached value or None if not found/expired.
        """
        start_time = time.perf_counter()

        with self._lock:
            entry = self._cache.get(key)

            if entry is None:
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                self._stats.misses += 1
                self._stats.total_miss_time_ms += elapsed_ms
                cache_logger.debug(
                    'Cache MISS: key=%s (not found), elapsed=%.2fms', key, elapsed_ms
                )
                return None

            # Check expiration
            if entry.is_expired:
                self._expire_entry(key)
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                self._stats.misses += 1
                self._stats.total_miss_time_ms += elapsed_ms
                cache_logger.debug('Cache MISS: key=%s (expired), elapsed=%.2fms', key, elapsed_ms)
                return None

            # Update LRU order
            self._cache.move_to_end(key)
            entry.touch()

            elapsed_ms = (time.perf_counter() - start_time) * 1000
            self._stats.hits += 1
            self._stats.total_hit_time_ms += elapsed_ms

            cache_logger.debug(
                'Cache HIT: key=%s, size=%d bytes, elapsed=%.2fms',
                key,
                entry.size_bytes,
                elapsed_ms,
            )

            return entry.value

    def get_ttl_for_key(self, key: str) -> timedelta:
        """Get TTL for a given key based on configured patterns.

        Args:
            key: Cache key to determine TTL for.

        Returns:
            TTL duration for the key based on pattern matching.
        """
        for pattern, ttl in self._ttl_patterns.items():
            if self._matches_pattern(pattern, key):
                return ttl
        return self._default_ttl

    def _matches_pattern(self, pattern: str, key: str) -> bool:
        """Check if key matches pattern.

        Args:
            pattern: Pattern to match against (supports * wildcard).
            key: Key to check.

        Returns:
            True if key matches pattern, False otherwise.
        """
        # Convert pattern to regex
        regex_pattern = pattern.replace('.', r'\.').replace('*', r'[^.]*')
        return re.match(f'^{regex_pattern}$', key) is not None

    def set(
        self,
        key: str,
        value: Any,
        ttl: timedelta | None = None,
        tags: list[str] | None = None,
    ) -> bool:
        """Set value in cache with optional TTL and tags.

        Thread-safe operation that:
        1. Calculates entry size
        2. Evicts entries if necessary to stay within limits
        3. Creates and stores cache entry
        4. Updates expiry tracking

        Args:
            key: Cache key to set.
            value: Value to cache.
            ttl: Time-to-live for the cached value. If None, uses pattern-based TTL.
            tags: Optional list of tags to associate with this cache entry.

        Returns:
            True if value was cached successfully, False otherwise.
        """
        start_time = time.perf_counter()

        with self._lock:
            # Calculate size
            size = self._calculate_size(value)

            # Check memory limit
            if size > self._max_memory_bytes:
                cache_logger.warning(
                    'Cache SET rejected: key=%s, size=%d bytes exceeds max=%d MB',
                    key,
                    size,
                    self._max_memory_bytes // (1024 * 1024),
                )
                return False

            # Evict if necessary
            evicted_count = 0
            while (
                self._current_memory + size > self._max_memory_bytes
                or len(self._cache) >= self._max_size
            ):
                if not self._evict_lru():
                    cache_logger.warning(
                        'Cache SET failed: unable to evict enough space for key=%s', key
                    )
                    return False
                evicted_count += 1

            if evicted_count > 0:
                cache_logger.debug('Evicted %d entries to make room for key=%s', evicted_count, key)

            # Calculate expiration using pattern-based TTL if not explicitly provided
            if ttl is None:
                ttl = self.get_ttl_for_key(key)
            expires_at = get_now() + ttl if ttl else None

            # Create entry
            entry = CacheEntry(
                key=key,
                value=value,
                expires_at=expires_at,
                size_bytes=size,
                tags=tags or [],
            )

            # Update cache
            is_update = key in self._cache
            if is_update:
                old_entry = self._cache[key]
                self._current_memory -= old_entry.size_bytes
                # Remove old tags from index
                self._remove_from_tag_index(key, old_entry.tags)

            self._cache[key] = entry
            self._cache.move_to_end(key)
            self._current_memory += size
            self._stats.size = len(self._cache)
            self._stats.memory_bytes = self._current_memory

            # Track expiry
            if expires_at:
                heapq.heappush(self._expiry_heap, (expires_at, key))

            # Add tags to index
            if tags:
                self._add_to_tag_index(key, tags)

            elapsed_ms = (time.perf_counter() - start_time) * 1000

            cache_logger.debug(
                'Cache %s: key=%s, size=%d bytes, ttl=%s, elapsed=%.2fms',
                'UPDATE' if is_update else 'SET',
                key,
                size,
                str(ttl.total_seconds()) + 's' if ttl else 'none',
                elapsed_ms,
            )

            return True

    def delete(self, key: str) -> bool:
        """Delete single key from cache.

        Args:
            key: Cache key to delete.

        Returns:
            True if key was deleted, False if key didn't exist.
        """
        with self._lock:
            if key not in self._cache:
                cache_logger.debug('Cache DELETE miss: key=%s not found', key)
                return False

            entry = self._cache[key]
            del self._cache[key]
            self._current_memory -= entry.size_bytes
            # Remove from tag index
            if entry.tags:
                self._remove_from_tag_index(key, entry.tags)
            self._stats.size = len(self._cache)
            self._stats.memory_bytes = self._current_memory

            cache_logger.debug('Cache DELETE: key=%s, freed %d bytes', key, entry.size_bytes)
            return True

    def clear(self, prefix: str | None = None) -> int:
        """Clear cache or keys with prefix.

        Args:
            prefix: Optional key prefix to clear. If None, clears entire cache.

        Returns:
            Number of keys cleared.
        """
        with self._lock:
            if prefix is None:
                # Clear entire cache
                count = len(self._cache)
                memory_freed = self._current_memory
                self._cache.clear()
                self._current_memory = 0

                if count > 0:
                    cache_logger.info(
                        'Cache CLEAR: removed %d entries, freed %.2f MB',
                        count,
                        memory_freed / (1024 * 1024),
                    )
                self._expiry_heap.clear()
                self._stats.size = 0
                self._stats.memory_bytes = 0
                return count

            # Clear keys with prefix
            keys_to_delete = [k for k in self._cache if k.startswith(prefix)]
            for key in keys_to_delete:
                entry = self._cache[key]
                del self._cache[key]
                self._current_memory -= entry.size_bytes
                # Remove from tag index
                if entry.tags:
                    self._remove_from_tag_index(key, entry.tags)

            self._stats.size = len(self._cache)
            self._stats.memory_bytes = self._current_memory
            return len(keys_to_delete)

    def exists(self, key: str) -> bool:
        """Check if key exists in cache.

        Args:
            key: Cache key to check.

        Returns:
            True if key exists and is not expired, False otherwise.
        """
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return False

            # Check expiration
            if entry.is_expired:
                self._expire_entry(key)
                return False

            return True

    def get_stats(self) -> CacheStatsProtocol:
        """Get cache statistics.

        Returns:
            A cache statistics object.
        """
        with self._lock:
            # Update current size and memory
            self._stats.size = len(self._cache)
            self._stats.memory_bytes = self._current_memory
            return self._stats

    def _evict_lru(self) -> bool:
        """Evict least recently used entry.

        Returns:
            True if an entry was evicted, False if cache is empty.
        """
        if not self._cache:
            return False

        # Get the oldest key (first in OrderedDict)
        key = next(iter(self._cache))
        entry = self._cache[key]

        # Remove from cache
        del self._cache[key]
        self._current_memory -= entry.size_bytes
        # Remove from tag index
        if entry.tags:
            self._remove_from_tag_index(key, entry.tags)
        self._stats.evictions += 1
        self._stats.size = len(self._cache)
        self._stats.memory_bytes = self._current_memory

        return True

    def _expire_entry(self, key: str) -> None:
        """Remove expired entry.

        Args:
            key: Cache key to expire.
        """
        if key in self._cache:
            entry = self._cache[key]
            del self._cache[key]
            self._current_memory -= entry.size_bytes
            # Remove from tag index
            if entry.tags:
                self._remove_from_tag_index(key, entry.tags)
            self._stats.expirations += 1
            self._stats.size = len(self._cache)
            self._stats.memory_bytes = self._current_memory

    def _calculate_size(self, obj: Any) -> int:
        """Calculate object size in bytes.

        Args:
            obj: Object to measure.

        Returns:
            Size in bytes.
        """
        try:
            # Try JSON serialization for size estimation
            json_str = json.dumps(obj, default=str, ensure_ascii=False)
            return len(json_str.encode('utf-8'))
        except (TypeError, ValueError):
            # Fallback to sys.getsizeof
            return sys.getsizeof(obj)

    def _cleanup_expired(self) -> None:
        """Background task to clean up expired entries."""
        with self._lock:
            now = get_now()
            # Process expired entries from heap
            while self._expiry_heap and self._expiry_heap[0][0] <= now:
                _expires_at, key = heapq.heappop(self._expiry_heap)
                # Check if key still exists and is expired
                entry = self._cache.get(key)
                if entry and entry.is_expired:
                    self._expire_entry(key)

        # Schedule next cleanup
        self._start_cleanup_timer()

    def _start_cleanup_timer(self) -> None:
        """Start the cleanup timer."""
        if self._cleanup_timer:
            self._cleanup_timer.cancel()

        self._cleanup_timer = threading.Timer(
            self._cleanup_interval.total_seconds(),
            self._cleanup_expired,
        )
        self._cleanup_timer.daemon = True
        self._cleanup_timer.start()

    def __del__(self) -> None:
        """Cleanup on deletion."""
        if hasattr(self, '_cleanup_timer') and self._cleanup_timer:
            self._cleanup_timer.cancel()

    def _add_to_tag_index(self, key: str, tags: list[str]) -> None:
        """Add key to tag index.

        Args:
            key: Cache key.
            tags: List of tags to associate with the key.
        """
        for tag in tags:
            if tag not in self._tag_index:
                self._tag_index[tag] = set()
            self._tag_index[tag].add(key)

    def _remove_from_tag_index(self, key: str, tags: list[str]) -> None:
        """Remove key from tag index.

        Args:
            key: Cache key.
            tags: List of tags to remove association from.
        """
        for tag in tags:
            if tag in self._tag_index:
                self._tag_index[tag].discard(key)
                if not self._tag_index[tag]:
                    del self._tag_index[tag]

    def invalidate_tags(self, tags: list[str]) -> int:
        """Invalidate all cache entries with given tags.

        Args:
            tags: List of tags to invalidate.

        Returns:
            Number of keys invalidated.
        """
        with self._lock:
            keys_to_delete = set()
            for tag in tags:
                if tag in self._tag_index:
                    keys_to_delete.update(self._tag_index[tag])

            deleted_count = 0
            memory_freed = 0
            for key in keys_to_delete:
                if key in self._cache:
                    entry = self._cache[key]
                    # Skip expired entries - they're already logically deleted
                    if entry.is_expired:
                        # Clean up expired entry
                        self._expire_entry(key)
                        continue

                    del self._cache[key]
                    self._current_memory -= entry.size_bytes
                    memory_freed += entry.size_bytes
                    self._remove_from_tag_index(key, entry.tags)
                    deleted_count += 1

            self._stats.size = len(self._cache)
            self._stats.memory_bytes = self._current_memory

            if deleted_count > 0:
                cache_logger.info(
                    'Cache tag invalidation: tags=%s, invalidated %d entries, freed %.2f MB',
                    tags,
                    deleted_count,
                    memory_freed / (1024 * 1024),
                )

            return deleted_count

    def get_tags(self, key: str) -> list[str]:
        """Get tags associated with a cache key.

        Args:
            key: Cache key to get tags for.

        Returns:
            List of tags associated with the key, empty list if key not found.
        """
        with self._lock:
            entry = self._cache.get(key)
            if entry:
                return entry.tags.copy()
            return []

    @classmethod
    def from_config(cls, config: CacheConfig) -> InMemoryCache:
        """Create cache from configuration.

        Args:
            config: Cache configuration.

        Returns:
            Configured InMemoryCache instance.
        """
        return cls(config=config)
