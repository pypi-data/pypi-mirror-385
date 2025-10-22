"""Cookie managers for synchronous Pararamio client."""

from __future__ import annotations

import json
import logging
import os
import threading
import time
import uuid
from abc import ABC, abstractmethod
from collections.abc import Callable
from http.cookiejar import Cookie, CookieJar
from pathlib import Path
from typing import Any, TypeVar

from pararamio._core import CookieManagerBaseMixin
from pararamio._core.exceptions.base import PararamioException

T = TypeVar('T')

log = logging.getLogger(__name__)


class CookieManager(ABC):
    """Abstract cookie manager with versioning and locking support."""

    @abstractmethod
    def load_cookies(self) -> bool:
        """Load cookies from storage."""

    @abstractmethod
    def save_cookies(self) -> None:
        """Save cookies to storage."""

    @abstractmethod
    def add_cookie(self, cookie: Cookie) -> None:
        """Add or update a cookie."""

    @abstractmethod
    def get_cookie(self, domain: str, path: str, name: str) -> Cookie | None:
        """Get a specific cookie."""

    @abstractmethod
    def get_all_cookies(self) -> list[Cookie]:
        """Get all cookies."""

    @abstractmethod
    def clear_cookies(self) -> None:
        """Clear all cookies."""

    @abstractmethod
    def update_from_jar(self, cookie_jar: CookieJar) -> None:
        """Update cookies from a CookieJar."""

    @abstractmethod
    def acquire_auth_lock(self, timeout: float = 30.0) -> bool:
        """Acquire lock for the authentication process."""

    @abstractmethod
    def release_auth_lock(self) -> None:
        """Release authentication lock."""

    @abstractmethod
    def check_version(self) -> bool:
        """Check if our version matches the storage version."""

    @abstractmethod
    def refresh_if_needed(self) -> bool:
        """Reload cookies if the version changed."""

    @abstractmethod
    def handle_auth_error(self, retry_callback: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """Handle authentication error with version check and retry."""

    def populate_jar(self, cookie_jar: CookieJar) -> None:
        """Populate a CookieJar with our cookies.

        This is a convenience method that can be implemented by subclasses
        that use CookieManagerBaseMixin.
        """
        # Default implementation - subclasses can override
        for cookie in self.get_all_cookies():
            cookie_jar.set_cookie(cookie)


class FileCookieManager(CookieManagerBaseMixin, CookieManager):
    """File-based cookie manager implementation."""

    def __init__(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.lock_path = Path(f'{file_path}.lock')
        self.version_path = Path(f'{file_path}.version')
        self._cookies: dict[str, Cookie] = {}
        self._version: int = 0
        self._lock = threading.Lock()
        self._lock_fd: int | None = None

        # Automatically load cookies if the file exists
        if self.file_path.exists():
            try:
                self.load_cookies()
            except (OSError, ValueError):
                # Log error but don't fail initialization
                log.exception(
                    'Failed to load cookies from %s during initialization', self.file_path
                )

    @property
    def version(self) -> int:
        """Get current version."""
        return self._version

    def load_cookies(self) -> bool:
        """Load cookies from a file."""
        with self._lock:
            if not self.file_path.exists():
                return False

            try:
                with self.file_path.open(encoding='utf-8') as f:
                    data = json.load(f)

                self._load_cookies_from_dict(data)

            except (OSError, json.JSONDecodeError) as e:
                log.warning('Failed to load cookies from %s: %s', self.file_path, e)
                return False
            return True

    def save_cookies(self) -> None:
        """Save cookies to a file."""
        with self._lock:
            data = self._prepare_cookies_data()

            # Ensure directory exists
            self.file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write to a temporary file first
            temp_path = Path(f'{self.file_path}.tmp')
            try:
                with temp_path.open('w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                # Atomic rename
                temp_path.rename(self.file_path)
            except (OSError, TypeError, ValueError):
                log.exception('Failed to save cookies to %s', self.file_path)
                if temp_path.exists():
                    temp_path.unlink()
                raise

    def add_cookie(self, cookie: Cookie) -> None:
        """Add or update a cookie."""
        with self._lock:
            key = self.make_key(cookie)
            self._cookies[key] = cookie
            self._version = self._increment_version()

    def get_cookie(self, domain: str, path: str, name: str) -> Cookie | None:
        """Get a specific cookie."""
        with self._lock:
            key = f'{domain}:{path}:{name}'
            return self._cookies.get(key)

    def get_all_cookies(self) -> list[Cookie]:
        """Get all cookies."""
        with self._lock:
            return list(self._cookies.values())

    def clear_cookies(self) -> None:
        """Clear all cookies."""
        with self._lock:
            self._cookies.clear()
            self._version = self._increment_version()

    def update_from_jar(self, cookie_jar: CookieJar) -> None:
        """Update cookies from a CookieJar."""
        with self._lock:
            for cookie in cookie_jar:
                key = self.make_key(cookie)
                self._cookies[key] = cookie
            self._version = self._increment_version()

    def acquire_auth_lock(self, timeout: float = 30.0) -> bool:
        """Acquire file lock with timeout."""
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                # Try to create a lock file exclusively
                self._lock_fd = os.open(
                    str(self.lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644
                )
            except FileExistsError:
                # Lock exists, check if it's stale
                if self._is_lock_stale():
                    self._remove_stale_lock()
                    continue
                time.sleep(0.1)
                continue
            # Write PID for debugging
            os.write(self._lock_fd, str(os.getpid()).encode())
            return True

        return False

    def release_auth_lock(self) -> None:
        """Release file lock."""
        if self._lock_fd is not None:
            try:
                os.close(self._lock_fd)
                self.lock_path.unlink(missing_ok=True)
            except OSError as e:
                log.warning('Failed to release lock: %s', e)
            finally:
                self._lock_fd = None

    def check_version(self) -> bool:
        """Check if our version matches the file version."""
        current_version = self._get_file_version()
        return current_version == self._version

    def refresh_if_needed(self) -> bool:
        """Reload cookies if the version changed."""
        if not self.check_version():
            log.info('Cookie version mismatch, reloading...')
            return self.load_cookies()
        return True

    def handle_auth_error(self, retry_callback: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """Handle authentication error with version check and retry.

        Args:
            retry_callback: Function to call for retry
            *args, **kwargs: Arguments to pass to retry_callback

        Returns:
            Result of retry_callback if successful

        Raises:
            Original exception if all retries fail
        """
        log.info('Authentication error occurred, checking cookie version...')

        # First, check if our cookies are outdated
        if not self.check_version():
            log.info('Cookie version outdated, reloading...')
            if self.load_cookies():
                log.info('Cookies reloaded, retrying with updated cookies...')
                try:
                    return retry_callback(*args, **kwargs)
                except Exception as e:  # pylint: disable=broad-exception-caught
                    log.warning('Retry with updated cookies failed: %s', e)
            else:
                log.warning('Failed to reload cookies')

        # If still failing, acquire lock and re-authenticate
        log.info('Attempting re-authentication...')
        if self.acquire_auth_lock(timeout=30.0):
            try:
                # Clear existing cookies
                self.clear_cookies()
                self.save_cookies()

                # Call retry which should trigger re-authentication
                result = retry_callback(*args, **kwargs)

                # Save new cookies after successful auth
                self.save_cookies()
                return result

            finally:
                self.release_auth_lock()
        msg = 'Failed to acquire authentication lock for re-authentication'
        raise PararamioException(msg)

    def _increment_version(self) -> int:
        """Increment version and save to file."""
        return self._increment_file_version()

    def _is_lock_stale(self, max_age: float = 300.0) -> bool:
        """Check if the lock file is stale (older than max_age seconds)."""
        try:
            stat = self.lock_path.stat()
        except FileNotFoundError:
            return False
        age = time.time() - stat.st_mtime
        return age > max_age

    def _remove_stale_lock(self) -> None:
        """Remove stale lock file."""
        try:
            self.lock_path.unlink()
            log.info('Removed stale lock file: %s', self.lock_path)
        except FileNotFoundError:
            pass


class RedisCookieManager(CookieManagerBaseMixin, CookieManager):
    """Redis-based cookie manager implementation."""

    def __init__(self, redis_client: Any, key_prefix: str = 'pararamio:cookies') -> None:
        self.redis = redis_client
        self.key_prefix = key_prefix
        self.data_key = f'{key_prefix}:data'
        self.lock_key = f'{key_prefix}:lock'
        self.version_key = f'{key_prefix}:version'
        self._cookies: dict[str, Cookie] = {}
        self._version: int = 0
        self._lock = threading.Lock()
        self._lock_token: str | None = None

    @property
    def version(self) -> int:
        """Get current version."""
        return self._version

    def load_cookies(self) -> bool:
        """Load cookies from Redis."""
        with self._lock:
            try:
                data = self.redis.get(self.data_key)
                return self._load_cookies_from_json(data)
            except (json.JSONDecodeError, KeyError, TypeError, AttributeError) as e:
                log.warning('Failed to load cookies from Redis: %s', e)
                return False

    def save_cookies(self) -> None:
        """Save cookies to Redis."""
        with self._lock:
            data = self._prepare_cookies_data()

            try:
                self.redis.set(self.data_key, json.dumps(data))
            except (OSError, TypeError, ValueError, AttributeError):
                log.exception('Failed to save cookies to Redis')
                raise

    def add_cookie(self, cookie: Cookie) -> None:
        """Add or update a cookie."""
        with self._lock:
            key = self.make_key(cookie)
            self._cookies[key] = cookie
            self._version = self._increment_version()

    def get_cookie(self, domain: str, path: str, name: str) -> Cookie | None:
        """Get a specific cookie."""
        with self._lock:
            key = f'{domain}:{path}:{name}'
            return self._cookies.get(key)

    def get_all_cookies(self) -> list[Cookie]:
        """Get all cookies."""
        with self._lock:
            return list(self._cookies.values())

    def clear_cookies(self) -> None:
        """Clear all cookies."""
        with self._lock:
            self._cookies.clear()
            self._version = self._increment_version()

    def update_from_jar(self, cookie_jar: CookieJar) -> None:
        """Update cookies from a CookieJar."""
        with self._lock:
            for cookie in cookie_jar:
                key = self.make_key(cookie)
                self._cookies[key] = cookie
            self._version = self._increment_version()

    def acquire_auth_lock(self, timeout: float = 30.0) -> bool:
        """Acquire distributed lock using Redis."""
        self._lock_token = str(uuid.uuid4())

        start_time = time.time()
        while time.time() - start_time < timeout:
            # Try to set lock with expiration
            if self.redis.set(self.lock_key, self._lock_token, nx=True, ex=300):
                return True
            time.sleep(0.1)

        return False

    def release_auth_lock(self) -> None:
        """Release distributed lock."""
        if self._lock_token:
            # Use Lua script for atomic check-and-delete
            lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
            """
            try:
                self.redis.eval(lua_script, 1, self.lock_key, self._lock_token)
            except (AttributeError, KeyError) as e:
                log.warning('Failed to release Redis lock: %s', e)
            finally:
                self._lock_token = None

    def check_version(self) -> bool:
        """Check if our version matches the Redis version."""
        try:
            version = self.redis.get(self.version_key)
        except (ValueError, AttributeError, TypeError, KeyError):
            return True
        current_version = int(version) if version else 0
        return current_version == self._version

    def refresh_if_needed(self) -> bool:
        """Reload cookies if the version changed."""
        if not self.check_version():
            log.info('Cookie version mismatch, reloading...')
            return self.load_cookies()
        return True

    def handle_auth_error(self, retry_callback: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """Handle authentication error with version check and retry."""
        log.info('Authentication error occurred (Redis), checking cookie version...')

        # First, check if our cookies are outdated
        if not self.check_version():
            log.info('Cookie version outdated, reloading from Redis...')
            if self.load_cookies():
                log.info('Cookies reloaded, retrying with updated cookies...')
                try:
                    return retry_callback(*args, **kwargs)
                except Exception as e:  # pylint: disable=broad-exception-caught
                    log.warning('Retry with updated cookies failed: %s', e)
            else:
                log.warning('Failed to reload cookies from Redis')

        # If still failing, acquire distributed lock and re-authenticate
        log.info('Attempting re-authentication with distributed lock...')
        if self.acquire_auth_lock(timeout=30.0):
            try:
                # Clear existing cookies
                self.clear_cookies()
                self.save_cookies()

                # Call retry which should trigger re-authentication
                result = retry_callback(*args, **kwargs)

                # Save new cookies after successful auth
                self.save_cookies()
                return result

            finally:
                self.release_auth_lock()
        else:
            msg = 'Failed to acquire distributed lock for re-authentication'
            raise PararamioException(msg)

    def _increment_version(self) -> int:
        """Atomically increment version in Redis."""
        try:
            self._version = self.redis.incr(self.version_key)
        except (AttributeError, TypeError):
            log.exception('Failed to increment version in Redis')
            return self._version
        return self._version


class InMemoryCookieManager(CookieManagerBaseMixin, CookieManager):
    """In-memory cookie manager implementation (no persistence)."""

    def __init__(self) -> None:
        self._cookies: dict[str, Cookie] = {}
        self._version: int = 0
        self._lock = threading.Lock()

    @property
    def version(self) -> int:
        """Get current version."""
        return self._version

    def load_cookies(self) -> bool:
        """No-op for in-memory manager."""
        # Cookies are already in memory
        return bool(self._cookies)

    def save_cookies(self) -> None:
        """No-op for in-memory manager."""
        # Cookies are already in memory, nothing to save

    def add_cookie(self, cookie: Cookie) -> None:
        """Add or update a cookie."""
        with self._lock:
            key = self.make_key(cookie)
            self._cookies[key] = cookie
            self._version += 1

    def get_cookie(self, domain: str, path: str, name: str) -> Cookie | None:
        """Get a specific cookie."""
        with self._lock:
            key = f'{domain}:{path}:{name}'
            return self._cookies.get(key)

    def get_all_cookies(self) -> list[Cookie]:
        """Get all cookies."""
        with self._lock:
            return list(self._cookies.values())

    def clear_cookies(self) -> None:
        """Clear all cookies."""
        with self._lock:
            self._cookies.clear()
            self._version += 1

    def update_from_jar(self, cookie_jar: CookieJar) -> None:
        """Update cookies from a CookieJar."""
        with self._lock:
            for cookie in cookie_jar:
                key = self.make_key(cookie)
                self._cookies[key] = cookie
            self._version += 1

    def acquire_auth_lock(self, timeout: float = 30.0) -> bool:  # noqa: ARG002
        """Always returns True for in-memory manager."""
        return True

    def release_auth_lock(self) -> None:
        """No-op for in-memory manager."""

    def check_version(self) -> bool:
        """Always returns True for in-memory manager."""
        return True

    def refresh_if_needed(self) -> bool:
        """No-op for in-memory manager."""
        return True

    def handle_auth_error(self, retry_callback: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """Handle authentication error by retrying."""
        log.info('Authentication error occurred (in-memory), retrying...')

        # For in-memory, just clear cookies and retry
        self.clear_cookies()

        try:
            return retry_callback(*args, **kwargs)
        except (AttributeError, TypeError):
            log.exception('Retry failed')
            raise


__all__ = [
    'CookieManager',
    'FileCookieManager',
    'InMemoryCookieManager',
    'RedisCookieManager',
]
