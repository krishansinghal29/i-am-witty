from __future__ import annotations

from dataclasses import dataclass, field


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
