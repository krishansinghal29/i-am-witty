from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class TaskAttemptSource(str, Enum):
    onboarding = "onboarding"
    daily_plan = "daily_plan"
    practice_library = "practice_library"
    role_play = "role_play"


class TaskAttemptStatus(str, Enum):
    started = "started"
    completed = "completed"
    abandoned = "abandoned"


@dataclass(frozen=True)
class TaskAttempt:
    id: uuid.UUID
    app_user_id: uuid.UUID
    task_id: uuid.UUID
    daily_plan_item_id: uuid.UUID | None
    source: TaskAttemptSource
    status: TaskAttemptStatus
    started_at: datetime
    completed_at: datetime | None
    abandoned_at: datetime | None
    completion_metadata: dict = field(default_factory=dict)
    runtime_state: dict = field(default_factory=dict)
