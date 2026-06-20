"""Hardening: anti-sycophancy, golden arcs, terminal edges, tuning load. [P8]"""
from __future__ import annotations

from roleplay_sim.config.tuning import TUNING
from roleplay_sim.director.beat_policy import BeatPolicyImpl
from roleplay_sim.domain.enums import (
    Beat,
    Consequence,
    MoveType,
    Quality,
    Register,
    SessionStatus,
    Supplication,
)
from roleplay_sim.domain.models import Classification, Frame, GameState, Move
from roleplay_sim.factory import build_state_engine
from roleplay_sim.orchestrator.terminal import TerminalCheckerImpl
from roleplay_sim.testing import default_persona

P = default_persona()
BEATS = BeatPolicyImpl()


def _cls(register, *moves, frame=None):
    return Classification(register=register, moves=list(moves), frame=frame or Frame())


def _run(state, script):
    """Apply a script; return (final_state, beats_seen)."""
    eng = build_state_engine()
    beats = []
    for c in script:
        upd = eng.apply(c, state, P)
        state = upd.new_state
        state.flags.turn_count += 1
        beat, _, _ = BEATS.select(state, upd.consequences, P)
        beats.append(beat)
    return state, beats


def test_tuning_loads_from_yaml():
    assert TUNING.accrual_rate == 0.30
    assert TUNING.base_engagement_drain == 1.0


def test_anti_sycophancy_bad_player_never_warms():
    st = GameState.fresh()
    st.emotional.perceived_value = 40.0
    bad = [
        _cls(Register.BASELINE, Move(MoveType.SUPPLICATE),
             frame=Frame(supplication=Supplication.STRONG)),
        _cls(Register.BASELINE, Move(MoveType.INTERVIEW_QS)),
        _cls(Register.BASELINE, Move(MoveType.SEEK_VALIDATION),
             frame=Frame(supplication=Supplication.MILD, reaction_seeking=True)),
        _cls(Register.BASELINE, Move(MoveType.OVER_EXPLAIN)),
        _cls(Register.BASELINE, Move(MoveType.SUPPLICATE),
             frame=Frame(supplication=Supplication.STRONG)),
    ]
    final, beats = _run(st, bad)
    assert final.emotional.attraction <= 12.0           # never really warmed
    assert final.emotional.perceived_value < 40.0        # value bled out
    assert final.emotional.neediness > 10.0
    assert Beat.WARM_OPEN not in beats                    # she does not melt
    assert final.emotional.engagement < 55.0


def test_good_arc_shape_warms_and_qualifies():
    st = GameState.fresh()
    good = [
        _cls(Register.PLOTLINE, Move(MoveType.OPEN_PUSH_PULL, Quality.GOOD)),
        _cls(Register.BASELINE, Move(MoveType.RAPPORT, Quality.GOOD)),
        _cls(Register.PLOTLINE, Move(MoveType.COLD_READ, Quality.GOOD)),
        _cls(Register.BASELINE, Move(MoveType.STORY_SHOW, Quality.GOOD)),
        _cls(Register.PLOTLINE, Move(MoveType.DISQUALIFY, Quality.GOOD)),
        _cls(Register.BASELINE, Move(MoveType.SOCIAL_PROOF, Quality.GOOD)),
        _cls(Register.PLOTLINE, Move(MoveType.PUSH_PULL, Quality.GOOD)),
    ]
    final, _ = _run(st, good)
    assert final.emotional.attraction > 25.0
    assert final.emotional.comfort > 20.0
    assert final.flags.premise_set is True
    # once attracted, qualifying lands
    upd = build_state_engine().apply(
        _cls(Register.PLOTLINE, Move(MoveType.QUALIFY_LEAD, Quality.GOOD)), final, P
    )
    assert Consequence.SHE_QUALIFIES in upd.consequences


def test_terminal_won_on_close():
    st = GameState.fresh()
    st.emotional.attraction = 75.0
    st.emotional.comfort = 65.0
    st.flags.premise_set = True
    st.flags.qualified = True
    upd = build_state_engine().apply(
        _cls(Register.PLOTLINE, Move(MoveType.CLOSE_NUMBER)), st, P
    )
    assert Consequence.CLOSE_ACCEPTED in upd.consequences
    assert TerminalCheckerImpl().status(upd.new_state, upd.consequences) is SessionStatus.WON


def test_terminal_left_on_engagement_floor():
    st = GameState.fresh()
    st.emotional.engagement = 0.5
    assert TerminalCheckerImpl().status(st, []) is SessionStatus.LEFT


def test_terminal_locked_out():
    st = GameState.fresh()
    st.emotional.engagement = 10.0
    assert (
        TerminalCheckerImpl().status(st, [Consequence.LOCKED_OUT])
        is SessionStatus.LOCKED_OUT
    )
