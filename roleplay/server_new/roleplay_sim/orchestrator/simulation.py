"""Simulation: top-level turn loop. Owns the single source of truth (GameState). [P2]"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from roleplay_sim.domain.config import SessionConfig
from roleplay_sim.domain.enums import SessionStatus
from roleplay_sim.domain.interfaces import Actor, Classifier, Director, TerminalChecker
from roleplay_sim.domain.models import ActorTurn, PlayerTurn
from roleplay_sim.orchestrator.history import TurnHistoryImpl


@dataclass
class Simulation:
    """Drives one practice session.

    submit(): classify -> director.step (engine + brief) -> actor.render
              -> append history -> terminal check.
    The Actor never receives `state`; only the Director's brief.
    """
    cfg: SessionConfig
    classifier: Classifier
    director: Director
    actor: Actor
    terminal: TerminalChecker
    history: TurnHistoryImpl = field(default_factory=TurnHistoryImpl)
    events: list[dict[str, Any]] = field(default_factory=list)
    status: SessionStatus = SessionStatus.ONGOING

    def __post_init__(self) -> None:
        self.state = self.cfg.initial_state

    async def submit(self, turn: PlayerTurn) -> tuple[ActorTurn, SessionStatus]:
        self.state.flags.turn_count += 1
        cls = await self.classifier.classify(turn, self.state, self.history)
        step = await self.director.step(cls, self.state, self.cfg.persona, self.history)
        self.state = step.state
        actor_turn = await self.actor.render(
            step.brief, self.cfg.persona, self.cfg.scene, self.history
        )
        self.history.append(turn, actor_turn)
        self.events.extend(step.events)
        # Carry the running recap forward so the next turn's Actor stays grounded.
        if step.brief.recap:
            self.history.recap = step.brief.recap
        self.status = self.terminal.status(self.state, step.consequences)
        return actor_turn, self.status
