from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date
from typing import Protocol


@dataclass(frozen=True)
class ProgressSummary:
    completed_task_count: int
    current_streak_count: int
    longest_streak_count: int
    last_activity_date: date | None
    last_qualified_streak_date: date | None


@dataclass(frozen=True)
class DayActivity:
    activity_date: date
    timezone: str
    completed_task_count: int
    had_missed_plan_items: bool = False
    streak_qualified: bool = False
    streak_protected: bool = False


class ProgressRepository(Protocol):
    async def get_summary(self, app_user_id: uuid.UUID) -> ProgressSummary | None: ...

    async def update_after_completion(
        self, app_user_id: uuid.UUID, summary: ProgressSummary
    ) -> ProgressSummary: ...

    async def get_week_activity(
        self, app_user_id: uuid.UUID, week_start: date
    ) -> list[DayActivity]: ...

    async def record_day_activity(
        self, app_user_id: uuid.UUID, activity: DayActivity
    ) -> None: ...
