"""Cache configuration management."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any


@dataclass
class CacheConfig:
    """Configuration for cache instances.

    This class provides a centralized way to configure cache behavior,
    including size limits, memory constraints, TTL patterns, and cleanup intervals.

    Args:
        max_size: Maximum number of entries in cache.
        max_memory_mb: Maximum memory usage in megabytes.
        default_ttl: Default time-to-live for entries.
        cleanup_interval: Interval for background cleanup of expired entries.
        ttl_patterns: Pattern-based TTL configuration mapping patterns to timedelta.
        enabled: Whether caching is enabled.
    """

    max_size: int = 10000
    max_memory_mb: int = 100
    default_ttl: timedelta = field(default_factory=lambda: timedelta(minutes=5))
    cleanup_interval: timedelta = field(default_factory=lambda: timedelta(minutes=1))
    enabled: bool = True

    ttl_patterns: dict[str, timedelta] = field(
        default_factory=lambda: {
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
    )

    @classmethod
    def disabled(cls) -> CacheConfig:
        """Create a configuration with caching disabled.

        Returns:
            CacheConfig with enabled=False.
        """
        return cls(enabled=False)

    @classmethod
    def minimal(cls) -> CacheConfig:
        """Create a minimal configuration for testing or low-memory environments.

        Returns:
            CacheConfig with reduced limits.
        """
        return cls(
            max_size=100,
            max_memory_mb=10,
            default_ttl=timedelta(minutes=1),
            cleanup_interval=timedelta(minutes=5),
        )

    @classmethod
    def aggressive(cls) -> CacheConfig:
        """Create an aggressive caching configuration.

        Returns:
            CacheConfig with increased limits and longer TTLs.
        """
        return cls(
            max_size=50000,
            max_memory_mb=500,
            default_ttl=timedelta(minutes=30),
            cleanup_interval=timedelta(minutes=5),
            ttl_patterns={
                'post.*': timedelta(hours=2),
                'chat.*.post.*': timedelta(hours=2),
                'user.*': timedelta(minutes=30),
                'group.*': timedelta(minutes=30),
                'team.*': timedelta(minutes=15),
                'team.*.members': timedelta(minutes=5),
                'poll.*': timedelta(minutes=5),
                'activity.*': timedelta(minutes=5),
                'search.*': timedelta(minutes=5),
                '*': timedelta(minutes=15),
            },
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary.

        Returns:
            Dictionary representation of configuration.
        """
        return {
            'max_size': self.max_size,
            'max_memory_mb': self.max_memory_mb,
            'default_ttl': self.default_ttl.total_seconds(),
            'cleanup_interval': self.cleanup_interval.total_seconds(),
            'enabled': self.enabled,
            'ttl_patterns': {
                pattern: ttl.total_seconds() for pattern, ttl in self.ttl_patterns.items()
            },
        }

    def with_ttl_pattern(self, pattern: str, ttl: timedelta) -> CacheConfig:
        """Create a new configuration with an additional TTL pattern.

        Args:
            pattern: Pattern to match against cache keys.
            ttl: Time-to-live for matching keys.

        Returns:
            New CacheConfig with updated TTL patterns.
        """
        new_patterns = self.ttl_patterns.copy()
        new_patterns[pattern] = ttl
        return CacheConfig(
            max_size=self.max_size,
            max_memory_mb=self.max_memory_mb,
            default_ttl=self.default_ttl,
            cleanup_interval=self.cleanup_interval,
            enabled=self.enabled,
            ttl_patterns=new_patterns,
        )
