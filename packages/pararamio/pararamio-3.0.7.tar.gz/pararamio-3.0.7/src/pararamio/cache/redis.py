"""Redis-based cache implementation with TTL support."""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

import redis
from pararamio._core.utils.logging_config import LoggerManager, get_logger
from pararamio._core.utils.performance import monitor_performance

from pararamio.protocols.cache import CacheStatsProtocol

log = logging.getLogger(__name__)
cache_logger = get_logger(LoggerManager.CACHE)


@dataclass
class CacheStats:
    """Cache statistics data."""

    hits: int = 0
    misses: int = 0
    evictions: int = 0
    expirations: int = 0
    size: int = 0
    memory_bytes: int = 0
    start_time: datetime = field(default_factory=datetime.now)

    @property
    def hit_rate(self) -> float:
        """Calculate hit rate percentage."""
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0

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
            'uptime_seconds': (datetime.now(UTC) - self.start_time).total_seconds(),
        }

    def reset(self) -> None:
        """Reset all counters."""
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.expirations = 0
        self.start_time = datetime.now(UTC)


class RedisCache:
    """Redis cache implementation with TTL support.

    This implementation provides:
    - Redis-based distributed caching
    - Pattern-based TTL configuration
    - Automatic serialization/deserialization using safe JSON
    - Prefix-based key namespacing
    - Comprehensive statistics collection

    Args:
        redis_client: Existing Redis client instance.
        host: Redis server host (used if redis_client is None).
        port: Redis server port (used if redis_client is None).
        db: Redis database number (used if redis_client is None).
        prefix: Prefix for all cache keys to avoid collisions.
        ttl_patterns: Pattern-based TTL configuration mapping patterns to timedelta.
    """

    def __init__(
        self,
        redis_client: redis.Redis | None = None,
        host: str = 'localhost',
        port: int = 6379,
        db: int = 0,
        prefix: str = 'pararamio:',
        ttl_patterns: dict[str, timedelta] | None = None,
    ):
        """Initialize Redis cache."""
        self.redis = redis_client or redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=False,
        )
        self.prefix = prefix
        self._stats = CacheStats()  # In-memory statistics

        cache_logger.info(
            'Redis cache initialized: host=%s, port=%d, db=%d, prefix=%s',
            host if not redis_client else 'provided-client',
            port,
            db,
            prefix,
        )

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
        return timedelta(minutes=5)  # Default fallback

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

    @monitor_performance('Redis GET', cache_logger)
    def get(self, key: str) -> Any | None:
        """Get value from Redis.

        Args:
            key: Cache key to retrieve.

        Returns:
            Cached value or None if not found.
        """
        full_key = f'{self.prefix}{key}'
        try:
            data = self.redis.get(full_key)

            if data is None:
                self._stats.misses += 1
                return None

            self._stats.hits += 1
            if isinstance(data, bytes):
                return json.loads(data.decode('utf-8'))
            return json.loads(str(data))
        except (redis.RedisError, json.JSONDecodeError, UnicodeDecodeError) as e:
            log.warning('Redis get error for %s: %s', key, e)
            self._stats.misses += 1
            return None

    @monitor_performance('Redis SET', cache_logger, log_result=True)
    def set(self, key: str, value: Any, ttl: timedelta | None = None) -> bool:
        """Set value in Redis with TTL.

        Args:
            key: Cache key to set.
            value: Value to cache.
            ttl: Time-to-live for the cached value. If None, uses pattern-based TTL.

        Returns:
            True if value was cached successfully, False otherwise.
        """
        full_key = f'{self.prefix}{key}'

        if ttl is None:
            ttl = self.get_ttl_for_key(key)

        try:
            data = json.dumps(value, default=str, ensure_ascii=False).encode('utf-8')
            self.redis.setex(full_key, int(ttl.total_seconds()), data)
            cache_logger.debug(
                'Redis SET: key=%s, size=%d bytes, ttl=%ds',
                key,
                len(data),
                int(ttl.total_seconds()),
            )
            return True
        except (redis.RedisError, json.JSONDecodeError, TypeError) as e:
            log.warning('Redis set error for %s: %s', key, e)
            return False

    @monitor_performance('Redis DELETE', cache_logger, log_result=True)
    def delete(self, key: str) -> bool:
        """Delete key from Redis.

        Args:
            key: Cache key to delete.

        Returns:
            True if key was deleted, False if key didn't exist.
        """
        full_key = f'{self.prefix}{key}'
        try:
            result = bool(self.redis.delete(full_key))
            if result:
                cache_logger.debug('Redis DELETE: key=%s deleted', key)
            else:
                cache_logger.debug('Redis DELETE: key=%s not found', key)
            return result
        except redis.RedisError as e:
            log.warning('Redis delete error for %s: %s', key, e)
            return False

    @monitor_performance('Redis CLEAR', cache_logger, log_result=True)
    def clear(self, prefix: str | None = None) -> int:
        """Clear keys by prefix.

        Args:
            prefix: Optional key prefix to clear. If None, clears all keys with cache prefix.

        Returns:
            Number of keys cleared.
        """
        pattern = f'{self.prefix}{prefix}*' if prefix else f'{self.prefix}*'

        try:
            # Use SCAN to avoid blocking on large datasets
            keys = []
            cursor = 0
            while True:
                result = self.redis.scan(cursor, match=pattern, count=100)
                if isinstance(result, (list, tuple)) and len(result) >= 2:
                    cursor, batch = int(result[0]), result[1]
                    keys.extend(batch)
                    if cursor == 0:
                        break
                else:
                    break

            if keys:
                deleted_count = self.redis.delete(*keys)
                cache_logger.info(
                    'Redis CLEAR: pattern=%s, deleted=%d keys',
                    pattern,
                    deleted_count if isinstance(deleted_count, int) else 0,
                )
                return deleted_count if isinstance(deleted_count, int) else 0

            cache_logger.debug('Redis CLEAR: pattern=%s, no keys found', pattern)
            return 0
        except redis.RedisError as e:
            log.warning('Redis clear error for pattern %s: %s', pattern, e)
            return 0

    def exists(self, key: str) -> bool:
        """Check if key exists.

        Args:
            key: Cache key to check.

        Returns:
            True if key exists, False otherwise.
        """
        full_key = f'{self.prefix}{key}'
        try:
            return bool(self.redis.exists(full_key))
        except redis.RedisError as e:
            log.warning('Redis exists error for %s: %s', key, e)
            return False

    @monitor_performance('Redis STATS', cache_logger)
    def get_stats(self) -> CacheStatsProtocol:
        """Get cache statistics.

        Returns:
            A cache statistics object.
        """
        try:
            # Update size from Redis
            # Count keys with our prefix
            cursor = 0
            count = 0
            pattern = f'{self.prefix}*'
            while True:
                result = self.redis.scan(cursor, match=pattern, count=100)
                if isinstance(result, (list, tuple)) and len(result) >= 2:
                    cursor, keys = int(result[0]), result[1]
                    count += len(keys)
                    if cursor == 0:
                        break
                else:
                    break
            self._stats.size = count

            # Get memory usage from Redis INFO
            info = self.redis.info('memory')
            if isinstance(info, dict):
                self._stats.memory_bytes = info.get('used_memory', 0)
            else:
                self._stats.memory_bytes = 0

            cache_logger.debug(
                'Redis STATS: size=%d, memory=%d bytes, hit_rate=%.1f%%',
                self._stats.size,
                self._stats.memory_bytes,
                self._stats.hit_rate,
            )
        except redis.RedisError as e:
            log.warning('Redis stats error: %s', e)

        return self._stats
