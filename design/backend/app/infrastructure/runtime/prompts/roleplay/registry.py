"""Registry for roleplay specs."""

from __future__ import annotations

from app.infrastructure.runtime.prompts.roleplay.misinterpretation import SPEC as RP_MISINTERPRETATION
from app.infrastructure.runtime.prompts.roleplay.spec import RoleplaySpec

_ROLEPLAYS: dict[str, RoleplaySpec] = {RP_MISINTERPRETATION.key: RP_MISINTERPRETATION}


def get_roleplay_spec(key: str) -> RoleplaySpec:
    try:
        return _ROLEPLAYS[key]
    except KeyError as exc:
        raise ValueError(f"Unsupported roleplay key: {key}") from exc


def get_supported_roleplay_keys() -> frozenset[str]:
    return frozenset(_ROLEPLAYS)
