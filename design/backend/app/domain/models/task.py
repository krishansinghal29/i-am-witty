from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum


class TaskAccessTier(str, Enum):
    free = "free"
    premium = "premium"


class TaskStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    future = "future"


@dataclass(frozen=True)
class Task:
    id: uuid.UUID
    slug: str
    title: str
    description: str | None
    task_type_id: str
    duration_seconds: int | None
    thumbnail_key: str
    image_key: str | None
    content: dict = field(default_factory=dict)
    runtime_config: dict = field(default_factory=dict)
    access_tier: TaskAccessTier = TaskAccessTier.free
    status: TaskStatus = TaskStatus.active
    sort_order: int = 0
    metadata: dict = field(default_factory=dict)

    @property
    def requires_premium(self) -> bool:
        return self.access_tier is TaskAccessTier.premium
