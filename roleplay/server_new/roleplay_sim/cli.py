"""Tiny REPL driver for the simulation. [P2]

Usage:
    python -m roleplay_sim.cli           # stub simulation (no LLM, no keys)

Type a line as the player; '/quit' to exit. An optional action can be appended
with '::', e.g.  "you're trouble :: sit_down".
"""
from __future__ import annotations

import asyncio

from roleplay_sim.domain.config import SceneConfig, SessionConfig
from roleplay_sim.domain.enums import ActionType, Ladder, SessionStatus
from roleplay_sim.domain.models import ActionMove, GameState, PlayerTurn
from roleplay_sim.personas.loader import load_persona
from roleplay_sim.testing import build_stub_simulation


def _parse(line: str) -> PlayerTurn:
    text, _, act = line.partition("::")
    action = None
    act = act.strip()
    if act:
        try:
            action = ActionMove(type=ActionType(act), ladder=Ladder.PHYSICAL, target_level=2)
        except ValueError:
            print(f"  (unknown action '{act}', ignoring)")
    return PlayerTurn(text=text.strip(), action=action)


async def _run() -> None:
    cfg = SessionConfig(
        persona=load_persona("princess"),
        scene=SceneConfig(venue="rooftop bar", approach_context="cold approach",
                          present_company="two friends", goal="number"),
        initial_state=GameState.fresh(),
    )
    sim = build_stub_simulation(cfg)
    print("roleplay_sim REPL (stub classifier/actor — no LLM). '/quit' to exit.\n")
    while True:
        line = input("you> ").strip()
        if line in {"/quit", "/q", "exit"}:
            break
        turn = _parse(line)
        actor_turn, status = await sim.submit(turn)
        suffix = f"  *[{actor_turn.action}]*" if actor_turn.action else ""
        print(f"her> {actor_turn.text}{suffix}")
        print(f"     (engagement={sim.state.emotional.engagement:.0f}, status={status.value})\n")
        if status is not SessionStatus.ONGOING:
            print(f"--- session ended: {status.value} ---")
            break


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
