"""Registry for exercise prompt specs."""

from __future__ import annotations

from app.infrastructure.runtime.prompts.first_unusual_thing import SPEC as FIRST_UNUSUAL_THING
from app.infrastructure.runtime.prompts.if_by_x import SPEC as IF_BY_X
from app.infrastructure.runtime.prompts.love_hate import SPEC as LOVE_HATE
from app.infrastructure.runtime.prompts.misinterpretation import SPEC as MISINTERPRETATION
from app.infrastructure.runtime.prompts.misinterpretation_techniques import SPEC as MISINTERPRETATION_TECHNIQUES
from app.infrastructure.runtime.prompts.push_pull import SPEC as PUSH_PULL
from app.infrastructure.runtime.prompts.question_answer_tease import SPEC as QUESTION_ANSWER_TEASE
from app.infrastructure.runtime.prompts.sex_with_me import SPEC as SEX_WITH_ME_IS_LIKE
from app.infrastructure.runtime.prompts.sexual_misinterpretation import SPEC as SEXUAL_MISINTERPRETATION
from app.infrastructure.runtime.prompts.shit_test import SPEC as SHIT_TEST
from app.infrastructure.runtime.prompts.spec import ExerciseSpec
from app.infrastructure.runtime.prompts.vibing import SPEC as VIBING
from app.infrastructure.runtime.prompts.yes_and import SPEC as YES_AND

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
        FIRST_UNUSUAL_THING,
        SHIT_TEST,
        SEXUAL_MISINTERPRETATION,
        SEX_WITH_ME_IS_LIKE,
    ]
}


def get_exercise_spec(exercise_key: str) -> ExerciseSpec:
    try:
        return _EXERCISES[exercise_key]
    except KeyError as exc:
        raise ValueError(f"Unsupported exercise key: {exercise_key}") from exc


def get_supported_exercise_keys() -> frozenset[str]:
    return frozenset(_EXERCISES)
