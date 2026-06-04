"""Registry for exercise prompt specs."""

from __future__ import annotations

from prompts.first_unusual_thing import SPEC as FIRST_UNUSUAL_THING
from prompts.heightening import SPEC as HEIGHTENING
from prompts.if_by_x import SPEC as IF_BY_X
from prompts.love_hate import SPEC as LOVE_HATE
from prompts.misinterpretation import SPEC as MISINTERPRETATION
from prompts.misinterpretation_techniques import SPEC as MISINTERPRETATION_TECHNIQUES
from prompts.push_pull import SPEC as PUSH_PULL
from prompts.question_answer_tease import SPEC as QUESTION_ANSWER_TEASE
from prompts.spec import ExerciseSpec
from prompts.vibing import SPEC as VIBING
from prompts.yes_and import SPEC as YES_AND

_EXERCISES: dict[str, ExerciseSpec] = {
    spec.key: spec
    for spec in [
        YES_AND,
        MISINTERPRETATION,
        MISINTERPRETATION_TECHNIQUES,
        LOVE_HATE,
        IF_BY_X,
        QUESTION_ANSWER_TEASE,
        VIBING,
        PUSH_PULL,
        HEIGHTENING,
        FIRST_UNUSUAL_THING,
    ]
}


def get_exercise_spec(exercise_key: str) -> ExerciseSpec:
    try:
        return _EXERCISES[exercise_key]
    except KeyError as exc:
        raise ValueError(f"Unsupported exercise key: {exercise_key}") from exc


def get_supported_exercise_keys() -> frozenset[str]:
    return frozenset(_EXERCISES)
