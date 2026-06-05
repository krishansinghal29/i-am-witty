from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum


class DailyPlanStatus(str, Enum):
    active = "active"
    completed = "completed"
    expired = "expired"


class DailyPlanItemStatus(str, Enum):
    upcoming = "upcoming"
    current = "current"
    completed = "completed"
    missed = "missed"
    skipped = "skipped"


@dataclass(frozen=True)
class DailyPlanItem:
    id: uuid.UUID
    daily_plan_id: uuid.UUID
    task_id: uuid.UUID
    position: int
    status: DailyPlanItemStatus
    current_attempt_id: uuid.UUID | None
    started_at: datetime | None
    completed_at: datetime | None
    missed_at: datetime | None


@dataclass(frozen=True)
class DailyPlan:
    id: uuid.UUID
    app_user_id: uuid.UUID
    plan_date: date
    timezone: str
    status: DailyPlanStatus
    items: tuple[DailyPlanItem, ...] = ()

    @property
    def next_up(self) -> DailyPlanItem | None:
        """The single task the user should do next, or None if none remain.

        Returns the `current` item if one exists, otherwise the first
        `upcoming` item. This mirrors the "exactly one next-up task" rule
        (functional req §4); the DB enforces at most one `current` item per
        plan via a partial unique index, so the first `current` match is the
        only one. Items are assumed ordered by `position`.
        """
        for item in self.items:
            if item.status is DailyPlanItemStatus.current:
                return item
        for item in self.items:
            if item.status is DailyPlanItemStatus.upcoming:
                return item
        return None
