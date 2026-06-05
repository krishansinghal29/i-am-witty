from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.daily_plan import (
    DailyPlan,
    DailyPlanItem,
    DailyPlanItemStatus,
    DailyPlanStatus,
)
from app.infrastructure.db.orm.plans import DailyPlan as OrmDailyPlan
from app.infrastructure.db.orm.plans import DailyPlanItem as OrmDailyPlanItem
from app.infrastructure.db.orm.plans import (
    DailyPlanItemStatus as OrmItemStatus,
)
from app.ports.repositories.daily_plan_repository import (
    CreateDailyPlanInput,
    MarkPlanItemCompletedInput,
    MarkPlanItemCurrentInput,
)


class PgDailyPlanRepository:
    """Async SQLAlchemy implementation of the daily plan repository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_plan_with_items(
        self, app_user_id: uuid.UUID, plan_date: date
    ) -> DailyPlan | None:
        stmt = select(OrmDailyPlan).where(
            OrmDailyPlan.app_user_id == app_user_id,
            OrmDailyPlan.plan_date == plan_date,
        )
        plan = (await self._session.execute(stmt)).scalar_one_or_none()
        if plan is None:
            return None
        items = await self._load_items(plan.id)
        return self._to_domain(plan, items)

    async def create_plan_with_items(self, input: CreateDailyPlanInput) -> DailyPlan:
        plan = OrmDailyPlan(
            app_user_id=input.app_user_id,
            plan_date=input.plan_date,
            timezone=input.timezone,
        )
        self._session.add(plan)
        await self._session.flush()

        for index, task_id in enumerate(input.task_ids):
            self._session.add(
                OrmDailyPlanItem(
                    daily_plan_id=plan.id,
                    task_id=task_id,
                    position=index + 1,
                    status=OrmItemStatus.upcoming,
                )
            )
        await self._session.flush()

        items = await self._load_items(plan.id)
        return self._to_domain(plan, items)

    async def mark_item_current(self, input: MarkPlanItemCurrentInput) -> None:
        stmt = select(OrmDailyPlanItem).where(
            OrmDailyPlanItem.id == input.plan_item_id,
            OrmDailyPlanItem.daily_plan_id.in_(self._user_plan_ids(input.app_user_id)),
        )
        item = (await self._session.execute(stmt)).scalar_one_or_none()
        if item is None:
            return
        item.status = OrmItemStatus.current
        item.started_at = datetime.now(timezone.utc)
        item.current_attempt_id = input.current_attempt_id
        await self._session.flush()

    async def mark_item_completed(self, input: MarkPlanItemCompletedInput) -> None:
        stmt = select(OrmDailyPlanItem).where(
            OrmDailyPlanItem.id == input.plan_item_id,
            OrmDailyPlanItem.daily_plan_id.in_(self._user_plan_ids(input.app_user_id)),
        )
        item = (await self._session.execute(stmt)).scalar_one_or_none()
        if item is None:
            return
        item.status = OrmItemStatus.completed
        item.completed_at = datetime.now(timezone.utc)
        item.current_attempt_id = input.attempt_id
        await self._session.flush()

    @staticmethod
    def _user_plan_ids(app_user_id: uuid.UUID) -> Select[tuple[uuid.UUID]]:
        return select(OrmDailyPlan.id).where(OrmDailyPlan.app_user_id == app_user_id)

    async def _load_items(self, plan_id: uuid.UUID) -> list[OrmDailyPlanItem]:
        stmt = (
            select(OrmDailyPlanItem)
            .where(OrmDailyPlanItem.daily_plan_id == plan_id)
            .order_by(OrmDailyPlanItem.position)
        )
        return list((await self._session.execute(stmt)).scalars().all())

    @classmethod
    def _to_domain(
        cls, plan: OrmDailyPlan, items: list[OrmDailyPlanItem]
    ) -> DailyPlan:
        return DailyPlan(
            id=plan.id,
            app_user_id=plan.app_user_id,
            plan_date=plan.plan_date,
            timezone=plan.timezone,
            status=DailyPlanStatus(plan.status.value),
            items=tuple(cls._item_to_domain(item) for item in items),
        )

    @staticmethod
    def _item_to_domain(item: OrmDailyPlanItem) -> DailyPlanItem:
        return DailyPlanItem(
            id=item.id,
            daily_plan_id=item.daily_plan_id,
            task_id=item.task_id,
            position=item.position,
            status=DailyPlanItemStatus(item.status.value),
            current_attempt_id=item.current_attempt_id,
            started_at=item.started_at,
            completed_at=item.completed_at,
            missed_at=item.missed_at,
        )
