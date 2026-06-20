"""Blueprint + actor-bible wiring (persona-folder-free since the generator landed).

The persona is no longer loaded from a folder; these tests pin the engine/actor
contract using a small in-code PersonaConfig fixture.
"""
from __future__ import annotations

from roleplay_sim.actor.bible import character_system, select_fewshot
from roleplay_sim.domain.config import Blueprint, PersonaConfig
from roleplay_sim.domain.enums import Beat, Ladder, MoveType, Register
from roleplay_sim.domain.models import (
    Frame,
    GameState,
    ModContext,
    Move,
    OutcomeResult,
    StateDelta,
)
from roleplay_sim.engine.modifiers.blueprint import BlueprintModifier


def _persona() -> PersonaConfig:
    return PersonaConfig(
        identity={"name": "Sofia", "age": 26, "occupation": "designer"},
        archetype="princess",
        blueprint=Blueprint(
            value_comfort_ratio=0.75,
            archetype_weights={MoveType.COCKY_FRAME: 1.4, MoveType.SUPPLICATE: 1.6},
            ladder_growth={Ladder.LOGISTICAL: 0.85},
        ),
        bible="You are Sofia, 26.",
        fewshot={"testing": [
            'She raises an eyebrow. "Bold of you to just sit down."',
            'She looks unimpressed. "Prove it. Why should I care?"',
        ]},
    )


def test_blueprint_modifier_uses_persona_weights():
    p = _persona()
    ctx = ModContext(frame=Frame(), register=Register.PLOTLINE)
    base = OutcomeResult(delta=StateDelta(emotional={"perceived_value": 6.0}))
    res = BlueprintModifier().apply(Move(type=MoveType.COCKY_FRAME), base, GameState.fresh(), p, ctx)
    assert res.delta.emotional["perceived_value"] == 8.4   # 6.0 * 1.4, rounded


def test_actor_uses_bible_and_band_fewshot():
    p = _persona()
    assert "never break character" in character_system(p).lower()
    lines = select_fewshot(p, Beat.SHIT_TEST)
    assert lines and any("bold" in ln.lower() or "prove" in ln.lower() for ln in lines)
