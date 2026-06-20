"""StateEngine aggregation + clamping tests. [P3]"""
from __future__ import annotations

from roleplay_sim.domain.enums import ActionType, Consequence, Ladder, Register
from roleplay_sim.domain.models import (
    ActionMove,
    Classification,
    GameState,
    ShitTestResponse,
)
from roleplay_sim.engine.registry import build_registry
from roleplay_sim.engine.state_engine import StateEngineImpl
from roleplay_sim.testing import default_persona


def _engine() -> StateEngineImpl:
    return StateEngineImpl(registry=build_registry())


def test_low_action_accepted_and_state_immutable():
    eng = _engine()
    st = GameState.fresh()
    cls = Classification(
        action=ActionMove(type=ActionType.SIT_DOWN, ladder=Ladder.PHYSICAL, target_level=1)
    )
    upd = eng.apply(cls, st, default_persona())
    # caller's state untouched
    assert st.flags.turn_count == 0
    assert upd.new_state is not st
    assert upd.new_state.flags.move_usage.get(ActionType.SIT_DOWN) == 1


def test_premature_kiss_drops_comfort_and_engagement():
    eng = _engine()
    st = GameState.fresh()
    before_c, before_e = st.emotional.comfort, st.emotional.engagement
    cls = Classification(
        action=ActionMove(type=ActionType.KISS_ATTEMPT, ladder=Ladder.PHYSICAL, target_level=5)
    )
    upd = eng.apply(cls, st, default_persona())
    assert upd.new_state.emotional.comfort < before_c
    assert upd.new_state.emotional.engagement < before_e
    assert Consequence.LOCKED_OUT in upd.consequences


def test_passed_shit_test_raises_attraction():
    eng = _engine()
    st = GameState.fresh()
    st.flags.pending_test = "sat down uninvited"
    before = st.emotional.attraction
    cls = Classification(
        register=Register.PLOTLINE,
        shit_test_response=ShitTestResponse(outcome="passed", method="agree_exaggerate"),
    )
    upd = eng.apply(cls, st, default_persona())
    assert upd.new_state.emotional.attraction > before
    assert Consequence.TEST_PASSED in upd.consequences
    assert upd.new_state.flags.pending_test is None


def test_engagement_drains_each_turn():
    eng = _engine()
    st = GameState.fresh()
    st.emotional.engagement = 50.0
    upd = eng.apply(Classification(register=Register.BASELINE), st, default_persona())
    assert upd.new_state.emotional.engagement < 50.0
    assert upd.new_state.flags.consecutive_baseline == 1
