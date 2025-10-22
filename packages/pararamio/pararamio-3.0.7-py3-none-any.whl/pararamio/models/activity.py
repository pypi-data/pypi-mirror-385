"""Sync Activity model with sync-specific methods."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from pararamio._core.api_schemas import UserActivityResponse
from pararamio._core.models import Activity as CoreActivity
from pararamio._core.models import ActivityAction
from pararamio._core.models import CoreActivity as BaseActivity

__all__ = ('Activity', 'ActivityAction')


class Activity(CoreActivity):
    """Sync Activity model with get_activity method."""

    @classmethod
    def get_activity(
        cls,
        page_loader: Callable[..., UserActivityResponse],
        start: datetime,
        end: datetime,
        actions: list[ActivityAction] | None = None,
    ) -> list[Activity]:
        """Get user activity within date range (sync version).

        Args:
            page_loader: Function to load activity pages
            start: Start datetime
            end: End datetime
            actions: Optional list of actions to filter

        Returns:
            List of Activity objects sorted by time
        """
        results = []
        actions_: list[ActivityAction | None] = [None]
        if actions:
            actions_ = actions  # type: ignore[assignment]
        for action in actions_:
            page = 1
            is_last_page = False
            while not is_last_page:
                data = page_loader(action, page=page).get('data', [])
                if not data:
                    break

                # Use the common filtering logic from CoreActivity
                filtered_activities, should_stop = BaseActivity.filter_activities_by_date_range(
                    data, start, end, cls.from_api_data
                )
                results.extend(filtered_activities)

                if should_stop:
                    is_last_page = True
                    break

                page += 1
        return sorted(results, key=lambda x: x.time)
