"""Ladder subsystem tests: gap resolution, ceiling growth, lockout. [P3]

The headline test is the timing crux: the *same* action is premature early and
accepted late, purely from where the ceiling sits.
"""
from __future__ import annotations

from roleplay_sim.domain.enums import Consequence, Ladder
from roleplay_sim.domain.models import GameState
from roleplay_sim.engine.ladders import resolve_escalation
from roleplay_sim.testing import default_persona

KISS = 5  # physical ladder rung


def _state() -> GameState:
    return GameState.fresh()


def test_kiss_is_premature_early():
    st = _state()  # ceiling_phys = 0
    out = resolve_escalation(st, Ladder.PHYSICAL, KISS, intended_step=+1, persona=default_persona())
    assert out.success is False
    assert out.consequence is Consequence.LOCKED_OUT  # gap 5 > lock severity
    assert out.delta.emotional["comfort"] < 0


def test_kiss_is_accepted_late():
    st = _state()
    st.ladders[Ladder.PHYSICAL].ceiling = 5.0   # built up over the interaction
    st.ladders[Ladder.PHYSICAL].reached = 4.0
    out = resolve_escalation(st, Ladder.PHYSICAL, KISS, intended_step=+1, persona=default_persona())
    assert out.success is True
    assert out.consequence is Consequence.ESCALATION_ACCEPTED
    assert out.delta.ladder_reached[Ladder.PHYSICAL] == 5.0
    assert out.delta.emotional["arousal"] > 0


def test_re_escalation_is_cheap():
    st = _state()
    st.ladders[Ladder.PHYSICAL].ceiling = 5.0
    st.ladders[Ladder.PHYSICAL].reached = 5.0
    out = resolve_escalation(st, Ladder.PHYSICAL, KISS, intended_step=+1, persona=default_persona())
    assert out.success is True
    assert out.consequence is Consequence.RE_ESCALATION


def test_step_back_builds_comfort():
    st = _state()
    st.ladders[Ladder.PHYSICAL].ceiling = 4.0
    st.ladders[Ladder.PHYSICAL].reached = 4.0
    out = resolve_escalation(st, Ladder.PHYSICAL, 2, intended_step=-1, persona=default_persona())
    assert out.success is True
    assert out.consequence is Consequence.RE_ESCALATION
    assert out.delta.emotional["comfort"] > 0


def test_logistical_pull_too_early_locks():
    st = _state()
    out = resolve_escalation(st, Ladder.LOGISTICAL, 7, intended_step=+1, persona=default_persona())
    assert out.consequence is Consequence.LOCKED_OUT
    assert Ladder.LOGISTICAL in out.delta.lock
