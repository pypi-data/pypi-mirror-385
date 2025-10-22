"""Cache protocol definitions for synchronous cache backends."""

# Re-export from core to maintain backward compatibility
from pararamio._core.protocols import CacheProtocol, CacheStatsProtocol

__all__ = ('CacheProtocol', 'CacheStatsProtocol')
