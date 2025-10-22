from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Any, Generic, Self, TypeVar

from pararamio._core.models.base import AttrFormatterMixin

from pararamio.exceptions import PararamModelNotLoadedError

if TYPE_CHECKING:
    from collections.abc import Mapping

    from pararamio.client import Pararamio

__all__ = ('SyncClientMixin',)


DataT = TypeVar('DataT', bound='Mapping[str, Any]')


class SyncClientMixin(Generic[DataT], AttrFormatterMixin[DataT]):
    """Mixin for sync models with reference to a Pararamio client."""

    _client: Pararamio
    _data: DataT
    _is_loaded: bool

    def __init__(self, client: Pararamio, **kwargs: Any) -> None:  # noqa: ARG002
        """Initialize with the Pararamio client.

        Args:
            client: Pararamio client instance
            **kwargs: Model data passed to parent classes
        """
        self._is_loaded = False
        self._client = client

    @property
    def client(self) -> Pararamio:
        """Get the Pararamio client instance."""
        return self._client

    def _set_loaded(self) -> None:
        """Set model data as loaded."""
        self._is_loaded = True

    @property
    def is_loaded(self) -> bool:
        """Check if model data has been loaded.

        Override in subclasses to check for required fields.
        """
        return self._is_loaded

    def load(self) -> Self:
        raise NotImplementedError

    def __getattr__(self, key: str) -> Any:
        """Get attribute from _data with lazy loading for sync models.

        This is called only when attribute is not found in the instance.
        For sync, we do lazy loading if load_on_key_error is True.
        """
        if key.startswith('_'):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{key}'")

        # Try to get from _data
        with contextlib.suppress(KeyError):
            return self._get_formatted_attr(key)

        # If not found and not loaded
        if not self.is_loaded:
            if self._client.load_on_key_error:
                # Load the object
                self.load()
                # Try again after loading
                with contextlib.suppress(KeyError):
                    return self._get_formatted_attr(key)
            else:
                # Raise PararamModelNotLoadedError if load_on_key_error is False
                msg = (
                    f'{self.__class__.__name__} data has not been loaded. '
                    f'Attribute "{key}" is not available. Use load() to fetch data first.'
                )
                raise PararamModelNotLoadedError(msg)

        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{key}'")
