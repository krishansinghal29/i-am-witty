from __future__ import annotations

import uuid
from datetime import date, datetime
from datetime import timezone as dt_timezone

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.orm.billing import DailyUsageCounter
from app.ports.repositories.usage_repository import DailyUsage


class PgUsageRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_daily_usage(
        self, app_user_id: uuid.UUID, usage_date: date
    ) -> DailyUsage | None:
        row = await self._session.get(DailyUsageCounter, (app_user_id, usage_date))
        if row is None:
            return None
        return self._to_daily_usage(row)

    async def increment_daily_usage(
        self,
        app_user_id: uuid.UUID,
        usage_date: date,
        timezone: str,
        free_task_limit: int,
    ) -> DailyUsage:
        """Bump the free-task counter for the day, creating the row if absent.

        On first write the per-day ``free_task_limit`` snapshot is captured; on
        subsequent writes only the counter is bumped, preserving that snapshot.
        """
        now = datetime.now(dt_timezone.utc)
        stmt = (
            pg_insert(DailyUsageCounter)
            .values(
                app_user_id=app_user_id,
                usage_date=usage_date,
                timezone=timezone,
                free_tasks_completed=1,
                free_task_limit=free_task_limit,
                updated_at=now,
            )
            .on_conflict_do_update(
                index_elements=[
                    DailyUsageCounter.app_user_id,
                    DailyUsageCounter.usage_date,
                ],
                set_={
                    "free_tasks_completed": DailyUsageCounter.free_tasks_completed + 1,
                    "updated_at": now,
                },
            )
            .returning(
                DailyUsageCounter.free_tasks_completed,
                DailyUsageCounter.free_task_limit,
                DailyUsageCounter.paywall_shown_at,
            )
        )
        result = await self._session.execute(stmt)
        free_tasks_completed, limit, paywall_shown_at = result.one()
        return DailyUsage(
            free_tasks_completed=free_tasks_completed,
            free_task_limit=limit,
            paywall_shown_at=paywall_shown_at,
        )

    async def mark_paywall_shown(
        self, app_user_id: uuid.UUID, usage_date: date
    ) -> None:
        row = await self._session.get(DailyUsageCounter, (app_user_id, usage_date))
        if row is None:
            return
        now = datetime.now(dt_timezone.utc)
        row.paywall_shown_at = now
        row.updated_at = now
        await self._session.flush()

    @staticmethod
    def _to_daily_usage(row: DailyUsageCounter) -> DailyUsage:
        return DailyUsage(
            free_tasks_completed=row.free_tasks_completed,
            free_task_limit=row.free_task_limit,
            paywall_shown_at=row.paywall_shown_at,
        )
