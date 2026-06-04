"""Exercise prompt configuration package."""

from prompts.registry import (
    get_exercise_spec,
    get_supported_exercise_keys,
)

__all__ = [
    "get_exercise_spec",
    "get_supported_exercise_keys",
]
