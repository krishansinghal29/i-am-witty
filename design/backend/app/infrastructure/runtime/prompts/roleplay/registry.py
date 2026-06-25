"""Registry for roleplay specs."""

from __future__ import annotations

from app.infrastructure.runtime.prompts.roleplay.first_unusual_thing import SPEC as RP_FIRST_UNUSUAL_THING
from app.infrastructure.runtime.prompts.roleplay.love_hate import SPEC as RP_LOVE_HATE
from app.infrastructure.runtime.prompts.roleplay.misinterpretation import SPEC as RP_MISINTERPRETATION
from app.infrastructure.runtime.prompts.roleplay.push_pull import SPEC as RP_PUSH_PULL
from app.infrastructure.runtime.prompts.roleplay.question_answer_tease import SPEC as RP_QUESTION_ANSWER_TEASE
from app.infrastructure.runtime.prompts.roleplay.sex_with_me import SPEC as RP_SEX_WITH_ME
from app.infrastructure.runtime.prompts.roleplay.sexual_misinterpretation import SPEC as RP_SEXUAL_MISINTERPRETATION
from app.infrastructure.runtime.prompts.roleplay.shit_test import SPEC as RP_SHIT_TEST
from app.infrastructure.runtime.prompts.roleplay.spec import RoleplaySpec
from app.infrastructure.runtime.prompts.roleplay.vibing import SPEC as RP_VIBING
from app.infrastructure.runtime.prompts.roleplay.yes_and import SPEC as RP_YES_AND

_ROLEPLAYS: dict[str, RoleplaySpec] = {
    RP_MISINTERPRETATION.key: RP_MISINTERPRETATION,
    RP_QUESTION_ANSWER_TEASE.key: RP_QUESTION_ANSWER_TEASE,
    RP_PUSH_PULL.key: RP_PUSH_PULL,
    RP_YES_AND.key: RP_YES_AND,
    RP_SHIT_TEST.key: RP_SHIT_TEST,
    RP_SEXUAL_MISINTERPRETATION.key: RP_SEXUAL_MISINTERPRETATION,
    RP_SEX_WITH_ME.key: RP_SEX_WITH_ME,
    RP_LOVE_HATE.key: RP_LOVE_HATE,
    RP_VIBING.key: RP_VIBING,
    RP_FIRST_UNUSUAL_THING.key: RP_FIRST_UNUSUAL_THING,
}


def get_roleplay_spec(key: str) -> RoleplaySpec:
    try:
        return _ROLEPLAYS[key]
    except KeyError as exc:
        raise ValueError(f"Unsupported roleplay key: {key}") from exc


def get_supported_roleplay_keys() -> frozenset[str]:
    return frozenset(_ROLEPLAYS)
