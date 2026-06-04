"""Exercise prompt configuration package."""

from prompts.registry import (
    build_generator_prompt,
    get_exercise_prompt,
    get_exercise_spec,
    get_response_roles,
    get_sprint_question_label,
    get_supported_exercise_keys,
    get_technique_for_exercise,
)

__all__ = [
    "build_generator_prompt",
    "get_exercise_prompt",
    "get_exercise_spec",
    "get_response_roles",
    "get_sprint_question_label",
    "get_supported_exercise_keys",
    "get_technique_for_exercise",
]
