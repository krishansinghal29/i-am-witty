from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date, datetime
from typing import Protocol


@dataclass(frozen=True)
class DailyUsage:
    free_tasks_completed: int
    free_task_limit: int
    paywall_shown_at: datetime | None


class UsageRepository(Protocol):
    async def get_daily_usage(
        self, app_user_id: uuid.UUID, usage_date: date
    ) -> DailyUsage | None: ...

    async def increment_daily_usage(
        self,
        app_user_id: uuid.UUID,
        usage_date: date,
        timezone: str,
        free_task_limit: int,
    ) -> DailyUsage:
        """Bump the free-task counter for the day, creating the row if absent."""
        ...

    async def mark_paywall_shown(
        self, app_user_id: uuid.UUID, usage_date: date
    ) -> None: ...
