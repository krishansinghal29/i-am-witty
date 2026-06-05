from __future__ import annotations

import uuid

from app.application.clock import local_today
from app.application.exceptions import ConflictError, NotFoundError
from app.application.unit_of_work import UnitOfWork
from app.domain.models.daily_plan import DailyPlan
from app.ports.repositories.daily_plan_repository import (
    CreateDailyPlanInput,
    DailyPlanRepository,
)
from app.ports.repositories.task_repository import TaskRepository
from app.ports.repositories.user_repository import UserRepository

PLAN_SIZE = 3


class DailyPlanService:
    def __init__(
        self,
        users: UserRepository,
        plans: DailyPlanRepository,
        tasks: TaskRepository,
        uow: UnitOfWork,
    ) -> None:
        self._users = users
        self._plans = plans
        self._tasks = tasks
        self._uow = uow

    async def get_or_create_today_plan(
        self, app_user_id: uuid.UUID
    ) -> DailyPlan:
        user = await self._users.find_by_id(app_user_id)
        if user is None:
            raise NotFoundError("user_not_found")
        today = local_today(user.timezone)
        plan = await self._plans.get_plan_with_items(app_user_id, today)
        if plan is not None:
            return plan
        catalog = await self._tasks.list_active_catalog()
        chosen = tuple(t.id for t in catalog[:PLAN_SIZE])
        if not chosen:
            raise ConflictError("no_tasks_available")
        async with self._uow.transaction():
            plan = await self._plans.create_plan_with_items(
                CreateDailyPlanInput(
                    app_user_id=app_user_id,
                    plan_date=today,
                    timezone=user.timezone,
                    task_ids=chosen,
                )
            )
        return plan
