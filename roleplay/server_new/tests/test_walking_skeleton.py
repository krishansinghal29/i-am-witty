"""End-to-end stubbed turn loop smoke test. [P2]"""
from __future__ import annotations

import asyncio

from roleplay_sim.domain.enums import ActionType, Ladder, SessionStatus
from roleplay_sim.domain.models import ActionMove, PlayerTurn
from roleplay_sim.testing import build_stub_simulation


def test_single_turn_round_trips():
    sim = build_stub_simulation()
    actor_turn, status = asyncio.run(sim.submit(PlayerTurn(text="hey, you look like trouble")))
    assert actor_turn.text
    assert status is SessionStatus.ONGOING
    assert len(sim.history) == 1
    assert sim.state.flags.turn_count == 1


def test_turn_with_action_round_trips():
    sim = build_stub_simulation()
    turn = PlayerTurn(
        text="mind if I join?",
        action=ActionMove(type=ActionType.SIT_DOWN, ladder=Ladder.PHYSICAL, target_level=1),
    )
    actor_turn, status = asyncio.run(sim.submit(turn))
    assert actor_turn.text
    assert status is SessionStatus.ONGOING


def test_engagement_drain_ends_session():
    sim = build_stub_simulation()
    sim.state.emotional.engagement = 2.0  # close to the floor
    last_status = SessionStatus.ONGOING
    for _ in range(5):
        _, last_status = asyncio.run(sim.submit(PlayerTurn(text="so... nice weather")))
        if last_status is not SessionStatus.ONGOING:
            break
    assert last_status is SessionStatus.LEFT
