"""
Logging configuration for Pararamio library.

This module provides centralized logging configuration with:
- Component-specific loggers
- Environment variable control (PARARAMIO_DEBUG)
- Performance-aware conditional logging
- Sanitization of sensitive data
"""

import logging
import os
import sys
from functools import lru_cache
from typing import Any


class LoggerManager:
    """Manages component-specific loggers with configurable levels."""

    # Component logger names
    HTTP_CLIENT = 'pararamio.http_client'
    LAZY_LOADING = 'pararamio.lazy_loading'
    BATCH_LOGIC = 'pararamio.batch_logic'
    CACHE = 'pararamio.cache'
    AUTH = 'pararamio.auth'
    SESSION = 'pararamio.session'
    API = 'pararamio.api'
    RETRY = 'pararamio.retry'
    RATE_LIMIT = 'pararamio.rate_limit'

    # Log format patterns
    DETAILED_FORMAT = (
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    SIMPLE_FORMAT = '%(name)s - %(levelname)s - %(message)s'
    DEBUG_FORMAT = (
        '%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - '
        '[%(filename)s:%(lineno)d in %(funcName)s()] - %(message)s'
    )

    def __init__(self) -> None:
        """Initialize the logger manager."""
        self._loggers: dict[str, logging.Logger] = {}
        self._configured = False
        self._debug_mode = self._check_debug_mode()
        self._log_level = self._get_log_level()

    @staticmethod
    def _check_debug_mode() -> bool:
        """Check if debug mode is enabled via environment variable."""
        debug_env = os.environ.get('PARARAMIO_DEBUG', '').lower()
        return debug_env in ('1', 'true', 'yes', 'on')

    def _get_log_level(self) -> int:
        """Get the appropriate log level based on environment."""
        if self._debug_mode:
            return logging.DEBUG

        level_env = os.environ.get('PARARAMIO_LOG_LEVEL', 'WARNING').upper()
        return getattr(logging, level_env, logging.WARNING)

    def _get_formatter(self) -> logging.Formatter:
        """Get the appropriate formatter based on debug mode."""
        if self._debug_mode:
            fmt = self.DEBUG_FORMAT
            datefmt = '%Y-%m-%d %H:%M:%S'
        elif self._log_level <= logging.INFO:
            fmt = self.DETAILED_FORMAT
            datefmt = '%Y-%m-%d %H:%M:%S'
        else:
            fmt = self.SIMPLE_FORMAT
            datefmt = None

        return logging.Formatter(fmt, datefmt=datefmt)

    def configure(self, force: bool = False) -> None:
        """
        Configure all loggers with appropriate handlers and levels.

        Args:
            force: Force reconfiguration even if already configured
        """
        if self._configured and not force:
            return

        # Create console handler
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(self._get_formatter())

        # Configure root pararamio logger
        root_logger = logging.getLogger('pararamio')
        root_logger.setLevel(self._log_level)
        root_logger.handlers = []  # Clear existing handlers
        root_logger.addHandler(handler)
        root_logger.propagate = False

        # Configure component loggers with specific levels if needed
        component_levels = self._get_component_levels()
        for component, level in component_levels.items():
            logger = logging.getLogger(component)
            if level is not None:
                logger.setLevel(level)

        self._configured = True

    def _get_component_levels(self) -> dict[str, int | None]:
        """Get component-specific log levels from environment variables."""
        levels = {}

        # Map of component to env variable
        env_map = {
            self.HTTP_CLIENT: 'PARARAMIO_LOG_HTTP',
            self.LAZY_LOADING: 'PARARAMIO_LOG_LAZY',
            self.BATCH_LOGIC: 'PARARAMIO_LOG_BATCH',
            self.CACHE: 'PARARAMIO_LOG_CACHE',
            self.AUTH: 'PARARAMIO_LOG_AUTH',
            self.SESSION: 'PARARAMIO_LOG_SESSION',
            self.API: 'PARARAMIO_LOG_API',
            self.RETRY: 'PARARAMIO_LOG_RETRY',
            self.RATE_LIMIT: 'PARARAMIO_LOG_RATE_LIMIT',
        }

        for component, env_var in env_map.items():
            level_str = os.environ.get(env_var)
            if level_str:
                level = getattr(logging, level_str.upper(), None)
                levels[component] = level
            else:
                levels[component] = None

        return levels

    @lru_cache(maxsize=128)
    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger for the specified component.

        Args:
            name: Logger name (use class constants like HTTP_CLIENT)

        Returns:
            Configured logger instance
        """
        if not self._configured:
            self.configure()

        return logging.getLogger(name)

    def is_debug_enabled(self) -> bool:
        """Check if debug mode is enabled."""
        return self._debug_mode

    def set_level(self, name: str, level: int | str) -> None:
        """
        Set log level for a specific component.

        Args:
            name: Logger name
            level: Log level (int or string like 'DEBUG')
        """
        if isinstance(level, str):
            level = getattr(logging, level.upper(), logging.WARNING)

        logger = self.get_logger(name)
        logger.setLevel(level)


# Singleton instance
_manager = LoggerManager()


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger for the specified component.

    Args:
        name: Logger name (use LoggerManager constants)

    Returns:
        Configured logger instance

    Example:
        >>> from pararamio._core.utils.logging_config import get_logger, LoggerManager
        >>> logger = get_logger(LoggerManager.HTTP_CLIENT)
        >>> logger.debug('Making API request to %s', url)
    """
    return _manager.get_logger(name)


def configure_logging(force: bool = False) -> None:
    """
    Configure the logging system.

    Args:
        force: Force reconfiguration even if already configured
    """
    _manager.configure(force=force)


def is_debug_enabled() -> bool:
    """Check if debug logging is enabled."""
    return _manager.is_debug_enabled()


def set_log_level(component: str, level: int | str) -> None:
    """
    Set log level for a specific component.

    Args:
        component: Component name (use LoggerManager constants)
        level: Log level (int or string)
    """
    _manager.set_level(component, level)


def sanitize_headers(headers: dict[str, str]) -> dict[str, str]:
    """
    Sanitize sensitive headers for logging.

    Args:
        headers: Original headers dictionary

    Returns:
        Sanitized headers with sensitive values masked
    """
    if not headers:
        return {}

    sensitive_keys = {
        'cookie',
        'authorization',
        'x-auth-token',
        'x-api-key',
        'x-csrf-token',
        'x-xsrf-token',
    }

    sanitized = {}
    for key, value in headers.items():
        key_lower = key.lower()
        if any(sensitive in key_lower for sensitive in sensitive_keys):
            # Show first 8 chars for debugging, mask the rest
            if len(value) > 8:
                sanitized[key] = f'{value[:8]}...MASKED'
            else:
                sanitized[key] = '***MASKED***'
        else:
            sanitized[key] = value

    return sanitized


def sanitize_cookies(cookies: Any) -> str:
    """
    Sanitize cookie values for logging.

    Args:
        cookies: Cookie jar or dict

    Returns:
        Sanitized representation
    """
    if not cookies:
        return 'No cookies'

    if hasattr(cookies, '__iter__'):
        count = len(list(cookies))
        return f'<{count} cookies>'
    return '<cookies present>'


def log_performance(logger: logging.Logger, operation: str, duration: float) -> None:
    """
    Log performance metrics if duration exceeds threshold.

    Args:
        logger: Logger instance
        operation: Operation name
        duration: Duration in seconds
    """
    if duration > 1.0:  # Log if operation takes more than 1 second
        logger.warning('%s took %.2f seconds', operation, duration)
    elif duration > 0.5 and logger.isEnabledFor(logging.INFO):
        logger.info('%s took %.2f seconds', operation, duration)
    elif logger.isEnabledFor(logging.DEBUG):
        logger.debug('%s took %.2f seconds', operation, duration)
