from __future__ import annotations

from dataclasses import dataclass, field

# Task type id for pre-recorded audio lessons. Lessons are consumption, not
# practice: they are surfaced through their own endpoint/tab, kept out of the
# practice catalog and the daily plan, and are non-metered (see `metered`
# in their type metadata).
LESSON_TASK_TYPE_ID = "lesson"


@dataclass(frozen=True)
class TaskType:
    id: str
    display_name: str
    description: str | None
    ui_schema_key: str
    runtime_engine_key: str | None
    default_duration_seconds: int | None
    is_active: bool = True
    sort_order: int = 0
    metadata: dict = field(default_factory=dict)
