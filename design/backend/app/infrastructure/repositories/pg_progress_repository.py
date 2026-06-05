from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.orm.plans import UserDayActivity
from app.infrastructure.db.orm.users import UserProgressSummary
from app.ports.repositories.progress_repository import DayActivity, ProgressSummary


class PgProgressRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_summary(self, app_user_id: uuid.UUID) -> ProgressSummary | None:
        row = await self._session.get(UserProgressSummary, app_user_id)
        if row is None:
            return None
        return self._to_summary(row)

    async def update_after_completion(
        self, app_user_id: uuid.UUID, summary: ProgressSummary
    ) -> ProgressSummary:
        row = await self._session.get(UserProgressSummary, app_user_id)
        if row is None:
            row = UserProgressSummary(app_user_id=app_user_id)
            self._session.add(row)
        row.completed_task_count = summary.completed_task_count
        row.current_streak_count = summary.current_streak_count
        row.longest_streak_count = summary.longest_streak_count
        row.last_activity_date = summary.last_activity_date
        row.last_qualified_streak_date = summary.last_qualified_streak_date
        row.updated_at = datetime.now(timezone.utc)
        await self._session.flush()
        await self._session.refresh(row)
        return self._to_summary(row)

    async def get_week_activity(
        self, app_user_id: uuid.UUID, week_start: date
    ) -> list[DayActivity]:
        week_end = week_start + timedelta(days=6)
        stmt = (
            select(UserDayActivity)
            .where(
                UserDayActivity.app_user_id == app_user_id,
                UserDayActivity.activity_date >= week_start,
                UserDayActivity.activity_date <= week_end,
            )
            .order_by(UserDayActivity.activity_date)
        )
        result = await self._session.execute(stmt)
        return [self._to_day_activity(row) for row in result.scalars().all()]

    async def record_day_activity(
        self, app_user_id: uuid.UUID, activity: DayActivity
    ) -> None:
        row = await self._session.get(
            UserDayActivity, (app_user_id, activity.activity_date)
        )
        if row is None:
            row = UserDayActivity(
                app_user_id=app_user_id, activity_date=activity.activity_date
            )
            self._session.add(row)
        row.timezone = activity.timezone
        row.completed_task_count = activity.completed_task_count
        row.had_missed_plan_items = activity.had_missed_plan_items
        row.streak_qualified = activity.streak_qualified
        row.streak_protected = activity.streak_protected
        row.updated_at = datetime.now(timezone.utc)
        await self._session.flush()

    @staticmethod
    def _to_summary(row: UserProgressSummary) -> ProgressSummary:
        return ProgressSummary(
            completed_task_count=row.completed_task_count,
            current_streak_count=row.current_streak_count,
            longest_streak_count=row.longest_streak_count,
            last_activity_date=row.last_activity_date,
            last_qualified_streak_date=row.last_qualified_streak_date,
        )

    @staticmethod
    def _to_day_activity(row: UserDayActivity) -> DayActivity:
        return DayActivity(
            activity_date=row.activity_date,
            timezone=row.timezone,
            completed_task_count=row.completed_task_count,
            had_missed_plan_items=row.had_missed_plan_items,
            streak_qualified=row.streak_qualified,
            streak_protected=row.streak_protected,
        )
