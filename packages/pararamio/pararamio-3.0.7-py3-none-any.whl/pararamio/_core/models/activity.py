"""Core Activity model without lazy loading."""

from __future__ import annotations

import datetime as dt
from enum import Enum
from typing import TYPE_CHECKING, Any, ClassVar, Unpack

from pararamio._core.api_schemas.responses import ActivityResponse
from pararamio._core.utils.helpers import parse_iso_datetime

from .base import CoreBaseModel

if TYPE_CHECKING:
    from collections.abc import Callable

    from pararamio._core._types import FormatterT

__all__ = ('Activity', 'ActivityAction', 'CoreActivity')


# Attribute formatters for Activity
ACTIVITY_ATTR_FORMATTERS: FormatterT = {
    'datetime': parse_iso_datetime,
}


class ActivityAction(Enum):
    """Activity action types."""

    ONLINE = 'online'
    OFFLINE = 'offline'
    AWAY = 'away'
    READ = 'thread-read'
    POST = 'thread-post'
    CALL = 'calling'
    CALL_END = 'endcall'


class Activity:
    """User activity record."""

    action: ActivityAction
    time: dt.datetime

    def __init__(self, action: ActivityAction, time: dt.datetime) -> None:
        """Initialize activity.

        Args:
            action: Activity action type
            time: Activity timestamp
        """
        self.action = action
        self.time = time

    def __str__(self) -> str:
        """String representation."""
        return f'Activity({self.time}, {self.action.value})'

    def __repr__(self) -> str:
        """Detailed representation."""
        return f'<Activity(action={self.action}, time={self.time})>'

    def __eq__(self, other: object) -> bool:
        """Check equality."""
        if not isinstance(other, Activity):
            return False
        return self.action == other.action and self.time == other.time

    @classmethod
    def from_api_data(cls, data: dict[str, str]) -> Activity:
        """Create Activity from API response data.

        Args:
            data: API response data

        Returns:
            Activity instance

        Raises:
            ValueError: If the time format is invalid
        """
        time = parse_iso_datetime(data, 'datetime')
        if time is None:
            raise ValueError('Invalid time format')

        return cls(
            action=ActivityAction(data['action']),
            time=time,
        )


class CoreActivity(CoreBaseModel[ActivityResponse]):
    """Core Activity model with common functionality."""

    _data: ActivityResponse
    # Activity attributes
    action: str
    datetime: dt.datetime

    _attr_formatters: ClassVar[FormatterT] = ACTIVITY_ATTR_FORMATTERS

    def __init__(self, client: Any, **kwargs: Unpack[ActivityResponse]) -> None:  # noqa: ARG002
        """Initialize the activity model with data.

        Args:
            client: Client instance (Pararamio or AsyncPararamio)
            **kwargs: Activity data
        """
        self._data = kwargs

    def __str__(self) -> str:
        return self.action

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CoreActivity):
            return id(other) == id(self)
        return self.action == other.action and self.datetime == other.datetime

    @staticmethod
    def filter_activities_by_date_range(
        data: list[dict[str, Any]],
        start: dt.datetime,
        end: dt.datetime,
        activity_factory: Callable[[dict[str, Any]], Any],
    ) -> tuple[list[Any], bool]:
        """Filter activities by date range and create activity objects.

        Args:
            data: List of raw activity data from API
            start: Start datetime for filtering
            end: End datetime for filtering
            activity_factory: Factory function to create activity instances

        Returns:
            Tuple of (the filtered activities list, is_last_page flag)
        """
        results = []
        is_last_page = False

        for activity_data in data:
            activity = activity_factory(activity_data)

            # Skip activities after end date
            if hasattr(activity, 'time'):
                activity_time = activity.time
            elif hasattr(activity, 'datetime'):
                activity_time = activity.datetime
            else:
                continue

            if activity_time > end:
                continue

            # Stop processing if we've reached activities before start date
            if activity_time < start:
                is_last_page = True
                break

            results.append(activity)

        return results, is_last_page
