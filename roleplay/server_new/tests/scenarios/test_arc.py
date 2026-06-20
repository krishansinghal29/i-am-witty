"""Deterministic interaction-arc scenarios. [P5 / M2]

Drives the real engine + director (stub brief author) through scripted turns and
asserts the emotional arc behaves sensibly end-to-end.
"""
from __future__ import annotations

import asyncio

from roleplay_sim.domain.enums import (
    Beat,
    MoveType,
    Quality,
    Register,
    Supplication,
    ValuePosture,
)
from roleplay_sim.domain.models import Classification, Frame, GameState, Move
from roleplay_sim.factory import build_director, build_state_engine
from roleplay_sim.orchestrator.history import TurnHistoryImpl
from roleplay_sim.testing import StubBriefAuthor, default_persona

P = default_persona()


def _cls(register, *moves, frame=None):
    return Classification(register=register, moves=list(moves), frame=frame or Frame())


def test_good_arc_builds_attraction_and_premise():
    eng = build_state_engine()
    st = GameState.fresh()
    a0, c0 = st.emotional.attraction, st.emotional.comfort
    script = [
        _cls(Register.PLOTLINE, Move(MoveType.OPEN_PUSH_PULL, Quality.GOOD),
             frame=Frame(value_posture=ValuePosture.HIGH)),
        _cls(Register.BASELINE, Move(MoveType.RAPPORT, Quality.GOOD)),
        _cls(Register.PLOTLINE, Move(MoveType.COLD_READ, Quality.GOOD)),
        _cls(Register.BASELINE, Move(MoveType.STORY_SHOW, Quality.GOOD)),
        _cls(Register.PLOTLINE, Move(MoveType.PUSH_PULL, Quality.GOOD)),
    ]
    for c in script:
        st = eng.apply(c, st, P).new_state
        st.flags.turn_count += 1
    assert st.emotional.attraction > a0 + 8
    assert st.emotional.comfort > c0
    assert st.flags.premise_set is True


def test_qualify_succeeds_once_attracted():
    eng = build_state_engine()
    st = GameState.fresh()
    st.emotional.attraction = 45.0   # already warmed up
    u = eng.apply(_cls(Register.PLOTLINE, Move(MoveType.QUALIFY_LEAD, Quality.GOOD)), st, P)
    assert u.new_state.flags.qualified is True


def test_supplication_spiral_tanks_value():
    eng = build_state_engine()
    st = GameState.fresh()
    st.emotional.perceived_value = 50.0
    pv0 = st.emotional.perceived_value
    for _ in range(3):
        st = eng.apply(
            _cls(Register.BASELINE, Move(MoveType.SUPPLICATE),
                 frame=Frame(supplication=Supplication.STRONG)),
            st, P,
        ).new_state
    assert st.emotional.perceived_value < pv0 - 10
    assert st.emotional.neediness > 10
    assert st.flags.supplication_count >= 3


def test_director_routes_shit_test():
    director = build_director(StubBriefAuthor())
    st = GameState.fresh()
    st.emotional.perceived_value = 60.0
    st.emotional.attraction = 20.0
    st.flags.turn_count = 2  # even -> cadence fires
    step = asyncio.run(
        director.step(_cls(Register.BASELINE), st, P, TurnHistoryImpl())
    )
    assert step.brief.beat is Beat.SHIT_TEST
    assert step.state.flags.pending_test is not None
