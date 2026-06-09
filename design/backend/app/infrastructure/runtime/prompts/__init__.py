"""Exercise prompt configuration package."""

from app.infrastructure.runtime.prompts.registry import (
    get_exercise_spec,
    get_supported_exercise_keys,
)

__all__ = [
    "get_exercise_spec",
    "get_supported_exercise_keys",
]
