"""Exercise prompt configuration package."""

from prompts.registry import (
    get_exercise_prompt,
    get_exercise_spec,
    get_sprint_question_label,
    get_supported_exercise_keys,
    get_technique_for_exercise,
)

__all__ = [
    "get_exercise_prompt",
    "get_exercise_spec",
    "get_sprint_question_label",
    "get_supported_exercise_keys",
    "get_technique_for_exercise",
]
