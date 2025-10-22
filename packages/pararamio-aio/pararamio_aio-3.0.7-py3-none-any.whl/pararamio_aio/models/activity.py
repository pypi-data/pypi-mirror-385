"""Async Activity model with async-specific methods."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from datetime import datetime
from typing import Any

from pararamio_aio._core.api_schemas.responses import UserActivityResponse
from pararamio_aio._core.models import Activity as CoreActivity
from pararamio_aio._core.models import ActivityAction
from pararamio_aio._core.models import CoreActivity as BaseActivity

__all__ = ('Activity', 'ActivityAction')


class Activity(CoreActivity):
    """Async Activity model with async get_activity method."""

    @classmethod
    async def get_activity(
        cls,
        page_loader: Callable[..., Coroutine[Any, Any, UserActivityResponse]],
        start: datetime,
        end: datetime,
        actions: list[ActivityAction] | None = None,
    ) -> list[Activity]:
        """Get user activity within date range (async version).

        Args:
            page_loader: Async function to load activity pages
            start: Start datetime
            end: End datetime
            actions: Optional list of actions to filter

        Returns:
            List of Activity objects sorted by time
        """
        results = []
        actions_to_check: list[ActivityAction | None] = [None]

        if actions:
            actions_to_check = actions  # type: ignore[assignment]

        for action in actions_to_check:
            page = 1
            is_last_page = False

            while not is_last_page:
                # Call async page loader
                response = await page_loader(action, page=page)
                # UserActivityResponse can have either 'data' or 'activities' field
                data = response.get('data', response.get('activities', []))

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
