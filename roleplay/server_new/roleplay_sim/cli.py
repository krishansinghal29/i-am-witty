"""Tiny REPL driver for the simulation. [P2]

Usage:
    python -m roleplay_sim.cli           # stub simulation (no LLM, no keys)

Type a line as the player; '/quit' to exit. An optional action can be appended
with '::', e.g.  "you're trouble :: sit_down".
"""
from __future__ import annotations

import asyncio

from roleplay_sim.domain.enums import ActionType, Ladder, SessionStatus
from roleplay_sim.domain.models import ActionMove, PlayerTurn
from roleplay_sim.generator.session import offline_session
from roleplay_sim.orchestrator.conversation_log import build_recorder_from_env
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
    cfg = offline_session()      # rolled persona + scene, no LLM (stub actor below)
    recorder = build_recorder_from_env("cli", cfg.persona, cfg.scene, cfg.initial_state)
    sim = build_stub_simulation(cfg, recorder=recorder)
    print("roleplay_sim REPL (stub classifier/actor — no LLM). '/quit' to exit.\n")
    print(f"[{cfg.persona.identity['name']}, {cfg.persona.archetype}]")
    print(f"{cfg.scene.first_impression}\n")
    if recorder is not None:
        print(f"(logging to {recorder.out_dir} as {recorder.slug}.*.json)\n")
    while True:
        line = input("you> ").strip()
        if line in {"/quit", "/q", "exit"}:
            break
        turn = _parse(line)
        actor_turn, status = await sim.submit(turn)
        print(f"her> {actor_turn.text}")
        print(f"     (engagement={sim.state.emotional.engagement:.0f}, status={status.value})\n")
        if status is not SessionStatus.ONGOING:
            print(f"--- session ended: {status.value} ---")
            break


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
