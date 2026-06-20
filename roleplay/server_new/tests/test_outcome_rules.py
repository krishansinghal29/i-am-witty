"""Per-move OutcomeRule tests. [P3b]"""
from __future__ import annotations

from roleplay_sim.domain.enums import Consequence, LMH, Quality
from roleplay_sim.domain.models import GameState, Move
from roleplay_sim.domain.enums import MoveType
from roleplay_sim.engine.registry import build_registry
from roleplay_sim.testing import default_persona

REG = build_registry()
P = default_persona()


def _run(state, move_type, **mv):
    move = Move(type=move_type, **mv)
    return REG.rule(move_type).resolve(move, state, P)


def test_good_tease_raises_attraction():
    st = GameState.fresh()
    st.emotional.comfort = 30.0
    res = _run(st, MoveType.TEASE, quality=Quality.GOOD, intensity=LMH.MED)
    assert res.delta.emotional["attraction"] > 0


def test_harsh_tease_low_comfort_backfires():
    st = GameState.fresh()  # comfort 12 < floor
    res = _run(st, MoveType.TEASE, quality=Quality.GOOD, intensity=LMH.HIGH, softener=False)
    assert res.delta.emotional["attraction"] < 0
    assert Consequence.COOLS in res.consequences


def test_botched_move_flips_to_penalty():
    st = GameState.fresh()
    st.emotional.comfort = 40.0
    res = _run(st, MoveType.PUSH_PULL, quality=Quality.BOTCHED)
    assert res.delta.emotional["attraction"] < 0


def test_qualify_gated_on_attraction():
    early = GameState.fresh()                # attraction 8
    late = GameState.fresh()
    late.emotional.attraction = 50.0
    r_early = _run(early, MoveType.QUALIFY_ASK, quality=Quality.GOOD)
    r_late = _run(late, MoveType.QUALIFY_ASK, quality=Quality.GOOD)
    assert Consequence.FEELS_INTERVIEWED in r_early.consequences
    assert Consequence.SHE_QUALIFIES in r_late.consequences
    assert r_late.delta.flags.get("qualified") is True


def test_premise_subtle_sets_flag():
    st = GameState.fresh()
    res = _run(st, MoveType.PREMISE_SUBTLE, quality=Quality.GOOD)
    assert res.delta.flags.get("premise_set") is True
    assert Consequence.PREMISE_SET in res.consequences


def test_close_rejected_when_cold():
    st = GameState.fresh()  # low attraction/comfort, no premise
    res = _run(st, MoveType.CLOSE_NUMBER)
    assert res.success is False
    assert Consequence.CLOSE_REJECTED in res.consequences


def test_close_accepted_when_ready():
    st = GameState.fresh()
    st.emotional.attraction = 70.0
    st.emotional.comfort = 60.0
    st.flags.premise_set = True
    st.flags.qualified = True
    res = _run(st, MoveType.CLOSE_NUMBER)
    assert res.success is True
    assert Consequence.CLOSE_ACCEPTED in res.consequences


def test_supplicate_tanks_value():
    st = GameState.fresh()
    res = _run(st, MoveType.SUPPLICATE)
    assert res.delta.emotional["perceived_value"] < 0
    assert res.delta.emotional["neediness"] > 0
    assert res.delta.flags["supplication_count"] == 1


def test_social_proof_strong_value():
    st = GameState.fresh()
    res = _run(st, MoveType.SOCIAL_PROOF, quality=Quality.GOOD)
    assert res.delta.emotional["perceived_value"] >= 5.0
