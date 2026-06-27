from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date
from typing import Protocol

from app.domain.models.daily_plan import DailyPlan


@dataclass(frozen=True)
class CreateDailyPlanInput:
    app_user_id: uuid.UUID
    plan_date: date
    timezone: str
    task_ids: tuple[uuid.UUID, ...]


@dataclass(frozen=True)
class MarkPlanItemCurrentInput:
    app_user_id: uuid.UUID
    plan_item_id: uuid.UUID
    current_attempt_id: uuid.UUID | None = None


@dataclass(frozen=True)
class MarkPlanItemCompletedInput:
    app_user_id: uuid.UUID
    plan_item_id: uuid.UUID
    attempt_id: uuid.UUID


class DailyPlanRepository(Protocol):
    async def get_plan_with_items(
        self, app_user_id: uuid.UUID, plan_date: date
    ) -> DailyPlan | None: ...

    async def get_latest_plan_before(
        self, app_user_id: uuid.UUID, before_date: date
    ) -> DailyPlan | None:
        """The user's most recent plan (with items) dated before ``before_date``.

        Used for the daily-plan carry-over rule: re-serve an exercise the user
        was assigned but never finished. Robust to skipped days — returns the
        last plan that exists, not strictly the previous calendar day.
        """
        ...

    async def create_plan_with_items(
        self, input: CreateDailyPlanInput
    ) -> DailyPlan: ...

    async def mark_item_current(self, input: MarkPlanItemCurrentInput) -> None: ...

    async def mark_item_completed(self, input: MarkPlanItemCompletedInput) -> None: ...
