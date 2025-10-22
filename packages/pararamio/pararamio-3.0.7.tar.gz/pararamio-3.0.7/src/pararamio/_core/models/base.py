"""Base model class for all models."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Generic,
    Protocol,
    Self,
    TypeVar,
    cast,
)

if TYPE_CHECKING:
    from pararamio._core._types import FormatterT

__all__ = ('ClientT', 'CoreBaseModel', 'SerializationMixin')


class DictProtocol(Protocol):
    """Protocol for dict-like objects."""

    def __getitem__(self, key: str) -> Any: ...
    def __setitem__(self, key: str, value: Any) -> None: ...
    def get(self, key: str, default: Any = None) -> Any: ...


DataT = TypeVar('DataT', bound=Mapping[str, Any])
ClientT = TypeVar('ClientT')


class CoreBaseModel(Generic[DataT]):
    """Base class for all core models with shared data management."""

    _data: DataT
    _attr_formatters: ClassVar[FormatterT]

    def __repr__(self) -> str:
        """String representation of the model."""
        model_name = self.__class__.__name__
        id_value = getattr(self, 'id', None)
        return f'<{model_name}(id={id_value})>'


class AttrFormatterMixin(Generic[DataT]):
    """Mixin class that provides attribute formatting methods."""

    _data: DataT  # Type annotation for the data attribute
    _attr_formatters: ClassVar[FormatterT]

    def _get_formatted_attr(self, key: str) -> Any:
        if formatter := self._attr_formatters.get(key, None):
            return formatter(self._data, key)
        return self._data[key]


class SerializationMixin(Generic[ClientT, DataT]):
    """Mixin class that provides serialization and deserialization methods."""

    _data: DataT  # Type annotation for the data attribute

    def __init__(self, client: ClientT, **kwargs: Any) -> None:
        """Initialize with a client.

        Args:
            client: Client instance (Pararamio or AsyncPararamio)
            **kwargs: Model data passed to parent classes
        """

    @classmethod
    def from_dict(
        cls,
        client: ClientT,
        data: DataT,
    ) -> Self:
        """Create model instance from dict data.

        Args:
            client: Client instance
            data: Raw API response data

        Returns:
            Model instance
        """
        return cls(client, **data)

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary.

        Returns:
            Model data as dict
        """
        result = {}
        for key, value in cast('dict[str, Any]', self._data).items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            else:
                result[key] = value
        return result
