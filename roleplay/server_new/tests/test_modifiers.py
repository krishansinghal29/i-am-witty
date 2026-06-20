"""Modifier-chain tests: repetition, congruence, blueprint, frame, fractionation. [P4]"""
from __future__ import annotations

from roleplay_sim.domain.enums import MoveType, Quality, Register, Supplication, ValuePosture
from roleplay_sim.domain.models import (
    Classification,
    Frame,
    GameState,
    ModContext,
    Move,
    OutcomeResult,
    StateDelta,
)
from roleplay_sim.engine.modifiers.blueprint import BlueprintModifier
from roleplay_sim.engine.modifiers.congruence import CongruenceModifier
from roleplay_sim.engine.modifiers.fractionation import fractionation_hook
from roleplay_sim.engine.modifiers.frame import frame_hook
from roleplay_sim.engine.modifiers.repetition import RepetitionModifier
from roleplay_sim.factory import build_state_engine
from roleplay_sim.testing import default_persona

P = default_persona()
CTX = ModContext(frame=Frame(), register=Register.PLOTLINE)


def _base(**em) -> OutcomeResult:
    return OutcomeResult(delta=StateDelta(emotional=dict(em)))


def test_repetition_decays_repeated_spike():
    st = GameState.fresh()
    st.flags.move_usage[MoveType.COLD_READ] = 2  # used twice already
    mod = RepetitionModifier()
    res = mod.apply(Move(type=MoveType.COLD_READ), _base(attraction=4.0), st, P, CTX)
    assert res.delta.emotional["attraction"] < 4.0


def test_repetition_ignores_comfort_staples():
    st = GameState.fresh()
    st.flags.move_usage[MoveType.RAPPORT] = 5
    mod = RepetitionModifier()
    res = mod.apply(Move(type=MoveType.RAPPORT), _base(comfort=3.0), st, P, CTX)
    assert res.delta.emotional["comfort"] == 3.0  # not a novelty move


def test_congruence_damps_when_incongruent():
    st = GameState.fresh()
    ctx = ModContext(frame=Frame(congruence=False), register=Register.PLOTLINE)
    res = CongruenceModifier().apply(Move(type=MoveType.TEASE), _base(attraction=4.0), st, P, ctx)
    assert res.delta.emotional["attraction"] == 2.0
    assert res.delta.emotional["comfort"] < 0


def test_blueprint_scales_by_weight():
    st = GameState.fresh()
    persona = default_persona()
    persona.blueprint.archetype_weights = {MoveType.COCKY_FRAME: 1.5}
    res = BlueprintModifier().apply(
        Move(type=MoveType.COCKY_FRAME), _base(perceived_value=6.0), st, persona, CTX
    )
    assert res.delta.emotional["perceived_value"] == 9.0


def test_frame_hook_strong_supplication():
    st = GameState.fresh()
    cls = Classification(frame=Frame(supplication=Supplication.STRONG))
    res = frame_hook(cls, st, P)
    assert res is not None
    assert res.delta.emotional["perceived_value"] < 0
    assert res.delta.emotional["neediness"] > 0
    assert res.delta.flags["supplication_count"] == 1


def test_frame_hook_high_value_posture():
    st = GameState.fresh()
    cls = Classification(frame=Frame(value_posture=ValuePosture.HIGH, congruence=True))
    res = frame_hook(cls, st, P)
    assert res is not None
    assert res.delta.emotional["perceived_value"] > 0


def test_fractionation_baseline_run_is_boring():
    st = GameState.fresh()
    st.flags.consecutive_baseline = 3
    res = fractionation_hook(Classification(register=Register.BASELINE), st, P)
    assert res is not None
    assert res.delta.emotional["attraction"] < 0


def test_repetition_integration_via_engine():
    eng = build_state_engine()
    st = GameState.fresh()
    st.emotional.comfort = 40.0
    st.emotional.attraction = 30.0
    cls = Classification(register=Register.PLOTLINE,
                         moves=[Move(type=MoveType.COLD_READ, quality=Quality.GOOD)])
    u1 = eng.apply(cls, st, P)
    gain1 = u1.new_state.emotional.attraction - st.emotional.attraction
    u2 = eng.apply(cls, u1.new_state, P)
    gain2 = u2.new_state.emotional.attraction - u1.new_state.emotional.attraction
    assert gain2 < gain1   # the repeated cold-read lands weaker
