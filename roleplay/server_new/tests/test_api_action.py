"""API action-channel wiring: dropdown value -> ActionMove. [P10]"""
from __future__ import annotations

from roleplay_sim.api.routes import _build_action
from roleplay_sim.api.schemas import ChatStreamIn
from roleplay_sim.domain.enums import ActionType, Ladder


def test_schema_accepts_optional_action():
    assert ChatStreamIn(session_id="s", message="hi").action is None
    assert ChatStreamIn(session_id="s", message="hi", action="kiss_attempt").action == "kiss_attempt"


def test_build_action_maps_to_ladder():
    a = _build_action("sit_down")
    assert a is not None
    assert a.type is ActionType.SIT_DOWN
    assert a.ladder is Ladder.PHYSICAL
    assert a.target_level == 1
    assert a.intended_step == 1


def test_step_back_is_deescalation():
    a = _build_action("step_back")
    assert a.intended_step == -1


def test_pull_is_logistical():
    a = _build_action("pull")
    assert a.ladder is Ladder.LOGISTICAL
    assert a.target_level == 7


def test_invalid_or_empty_action_is_none():
    assert _build_action("") is None
    assert _build_action(None) is None
    assert _build_action("not_a_real_action") is None
