from __future__ import annotations

from app.domain.models.task_type import TaskType
from app.ports.task_runtime_engine import TaskRuntimeEngine


class TaskRuntimeEngineResolver:
    """Selects the runtime engine for a task by its ``runtime_engine_key``.

    A task type names its engine (e.g. ``voice_prompt_v1``, ``roleplay_v1``)
    via ``runtime_engine_key``; this resolver maps that key to the concrete
    engine instance built at composition time. Keeping selection here means the
    services stay engine-agnostic and adding a new engine is one registry entry.
    """

    def __init__(self, engines: dict[str, TaskRuntimeEngine]) -> None:
        self._engines = dict(engines)

    def for_task_type(self, task_type: TaskType) -> TaskRuntimeEngine:
        key = task_type.runtime_engine_key
        if not key:
            raise ValueError(
                f"task type {task_type.id} has no runtime_engine_key"
            )
        try:
            return self._engines[key]
        except KeyError as exc:
            raise ValueError(f"Unsupported runtime engine: {key}") from exc

    def supports_turns(self, task_type: TaskType) -> bool:
        """Whether the task type is conversational (multi-turn)."""
        return bool((task_type.metadata or {}).get("supports_turns"))
