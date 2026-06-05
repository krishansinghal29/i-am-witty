from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date

from app.application.clock import local_today, week_start
from app.application.exceptions import NotFoundError
from app.ports.repositories.progress_repository import (
    DayActivity,
    ProgressRepository,
    ProgressSummary,
)
from app.ports.repositories.user_repository import UserRepository


@dataclass(frozen=True)
class WeekView:
    week_start: date
    days: list[DayActivity]


class ProgressService:
    def __init__(
        self, users: UserRepository, progress: ProgressRepository
    ) -> None:
        self._users = users
        self._progress = progress

    async def get_progress(self, app_user_id: uuid.UUID) -> ProgressSummary:
        s = await self._progress.get_summary(app_user_id)
        if s is None:
            return ProgressSummary(
                completed_task_count=0,
                current_streak_count=0,
                longest_streak_count=0,
                last_activity_date=None,
                last_qualified_streak_date=None,
            )
        return s

    async def get_week(
        self, app_user_id: uuid.UUID, reference: date | None = None
    ) -> WeekView:
        user = await self._users.find_by_id(app_user_id)
        if user is None:
            raise NotFoundError("user_not_found")
        today = reference or local_today(user.timezone)
        ws = week_start(today)
        days = await self._progress.get_week_activity(app_user_id, ws)
        return WeekView(week_start=ws, days=days)
