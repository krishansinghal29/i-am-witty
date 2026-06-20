"""Persona loader + blueprint wiring tests. [P7]"""
from __future__ import annotations

from roleplay_sim.actor.bible import character_system, select_fewshot
from roleplay_sim.domain.enums import Beat, Ladder, MoveType
from roleplay_sim.domain.models import GameState, ModContext, Move, OutcomeResult, StateDelta, Frame
from roleplay_sim.domain.enums import Register
from roleplay_sim.engine.modifiers.blueprint import BlueprintModifier
from roleplay_sim.personas.loader import load_persona


def test_load_princess():
    p = load_persona("princess")
    assert p.archetype == "princess"
    assert p.blueprint.value_comfort_ratio == 0.75
    assert p.blueprint.archetype_weights[MoveType.COCKY_FRAME] == 1.4
    assert p.blueprint.archetype_weights[MoveType.SUPPLICATE] == 1.6
    assert p.blueprint.ladder_growth[Ladder.LOGISTICAL] == 0.85
    assert "Sofia" in p.bible
    assert p.fewshot["testing"]


def test_blueprint_modifier_uses_princess_weights():
    p = load_persona("princess")
    ctx = ModContext(frame=Frame(), register=Register.PLOTLINE)
    base = OutcomeResult(delta=StateDelta(emotional={"perceived_value": 6.0}))
    res = BlueprintModifier().apply(Move(type=MoveType.COCKY_FRAME), base, GameState.fresh(), p, ctx)
    assert res.delta.emotional["perceived_value"] == 8.4   # 6.0 * 1.4, rounded


def test_actor_uses_bible_and_band_fewshot():
    p = load_persona("princess")
    assert "never break character" in character_system(p).lower()
    lines = select_fewshot(p, Beat.SHIT_TEST)
    assert lines and any("sit" in ln.lower() or "bold" in ln.lower() for ln in lines)
