"""Exercise prompt configuration package."""

from prompts.exercise_prompts.registry import (
    build_generator_prompt,
    get_exercise_prompt,
    get_message_key,
    get_sprint_question_label,
)

__all__ = [
    "build_generator_prompt",
    "get_exercise_prompt",
    "get_message_key",
    "get_sprint_question_label",
]

