"""FrameModifier: turn-level value/posture effects. [P4]

This is a turn hook (not a per-move Modifier) because frame is a property of the
whole turn. Supplication and reaction-seeking bleed value and add neediness; a
congruent high-value posture lifts value/attraction.
"""
from __future__ import annotations

from roleplay_sim.domain.config import PersonaConfig
from roleplay_sim.domain.enums import Consequence, Supplication, ValuePosture
from roleplay_sim.domain.models import Classification, GameState, OutcomeResult, StateDelta


def frame_hook(cls: Classification, state: GameState, persona: PersonaConfig) -> OutcomeResult | None:
    f = cls.frame
    d = StateDelta()
    cons: list[Consequence] = []

    if f.supplication is Supplication.MILD:
        d.emotional.update({"perceived_value": -2.0, "neediness": 2.0, "attraction": -1.0})
        d.flags["supplication_count"] = state.flags.supplication_count + 1
        cons.append(Consequence.COOLS)
    elif f.supplication is Supplication.STRONG:
        d.emotional.update({"perceived_value": -5.0, "neediness": 5.0,
                            "attraction": -3.0, "comfort": -2.0})
        d.flags["supplication_count"] = state.flags.supplication_count + 1
        cons.append(Consequence.COOLS)

    if f.value_posture is ValuePosture.HIGH and f.congruence:
        d.emotional["perceived_value"] = d.emotional.get("perceived_value", 0.0) + 3.0
        d.emotional["attraction"] = d.emotional.get("attraction", 0.0) + 2.0
    elif f.value_posture is ValuePosture.LOW:
        d.emotional["perceived_value"] = d.emotional.get("perceived_value", 0.0) - 2.0

    if f.reaction_seeking:
        d.emotional["perceived_value"] = d.emotional.get("perceived_value", 0.0) - 2.0
        d.emotional["neediness"] = d.emotional.get("neediness", 0.0) + 2.0

    if not d.emotional and not d.flags:
        return None
    return OutcomeResult(delta=d, consequences=cons, notes="frame")
