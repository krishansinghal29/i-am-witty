"""Protocols (contracts) for every swappable component. [P1]

Split by execution model:
- Deterministic core (sync): OutcomeRule, Modifier, MoveRegistry, StateEngine,
  TestTrigger, BeatPolicy, TerminalChecker.
- LLM-facing (async): LLMClient, Classifier, BriefAuthor, Actor, Director.
"""
from __future__ import annotations

from typing import Any, AsyncIterator, Optional, Protocol, Sequence, runtime_checkable

from roleplay_sim.domain.config import MoveMeta, PersonaConfig, SceneConfig
from roleplay_sim.domain.enums import (
    ActionType,
    Beat,
    Consequence,
    MoveType,
    SessionStatus,
)
from roleplay_sim.domain.models import (
    ActorTurn,
    BehavioralBrief,
    Classification,
    Dials,
    DirectorStep,
    GameState,
    ModContext,
    OutcomeResult,
    PlayerTurn,
    StateUpdate,
)

Message = dict[str, str]   # {"role": ..., "content": ...}


# ---------------------------------------------------------------------------
# LLM
# ---------------------------------------------------------------------------
@runtime_checkable
class LLMClient(Protocol):
    """Vendor-agnostic LLM access. One client, three roles (classify/author/act)."""

    async def complete(
        self, messages: Sequence[Message], *, model: str | None = None,
        temperature: float = 0.7, max_tokens: int = 400,
    ) -> str: ...

    async def complete_structured(
        self, messages: Sequence[Message], *, schema: dict[str, Any],
        model: str | None = None, temperature: float = 0.2, max_tokens: int = 800,
    ) -> dict[str, Any]: ...

    def stream(
        self, messages: Sequence[Message], *, model: str | None = None,
        temperature: float = 0.9, max_tokens: int = 300,
    ) -> AsyncIterator[str]: ...


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------
@runtime_checkable
class Classifier(Protocol):
    async def classify(
        self, turn: PlayerTurn, state: GameState, history: "TurnHistory",
    ) -> Classification: ...


# ---------------------------------------------------------------------------
# Engine (deterministic)
# ---------------------------------------------------------------------------
@runtime_checkable
class OutcomeRule(Protocol):
    """One per MoveType/ActionType. Reads state to resolve the move.

    Prerequisites that used to be sequencing gates live HERE: e.g. a close rule
    reads Readiness and returns a penalty + CLOSE_REJECTED rather than being
    blocked by an external gate.
    """
    def resolve(self, move: Any, state: GameState, persona: PersonaConfig) -> OutcomeResult: ...


@runtime_checkable
class Modifier(Protocol):
    """Adjusts a base OutcomeResult using context a single rule shouldn't own
    (repetition history, the turn's frame/register, blueprint scaling)."""
    def apply(
        self, move: Any, base: OutcomeResult, state: GameState, persona: PersonaConfig,
        ctx: "ModContext",
    ) -> OutcomeResult: ...


@runtime_checkable
class MoveRegistry(Protocol):
    def meta(self, move_type: MoveType | ActionType) -> MoveMeta: ...
    def rule(self, move_type: MoveType | ActionType) -> OutcomeRule: ...


@runtime_checkable
class StateEngine(Protocol):
    registry: MoveRegistry
    modifiers: Sequence[Modifier]

    def apply(
        self, cls: Classification, state: GameState, persona: PersonaConfig,
    ) -> StateUpdate: ...


# ---------------------------------------------------------------------------
# Director sub-components
# ---------------------------------------------------------------------------
@runtime_checkable
class TestTrigger(Protocol):
    def maybe_test(self, state: GameState, persona: PersonaConfig) -> Optional[str]: ...


@runtime_checkable
class BeatPolicy(Protocol):
    def select(
        self, state: GameState, consequences: list[Consequence], persona: PersonaConfig,
    ) -> tuple[Beat, Optional[Beat], Dials]: ...


@runtime_checkable
class BriefAuthor(Protocol):
    async def author(
        self, state: GameState, beat: Beat, dials: Dials,
        consequences: list[Consequence], history: "TurnHistory", persona: PersonaConfig,
    ) -> tuple[str, str]: ...   # (note, recap)


@runtime_checkable
class Director(Protocol):
    async def step(
        self, cls: Classification, state: GameState, persona: PersonaConfig,
        history: "TurnHistory",
    ) -> DirectorStep: ...


# ---------------------------------------------------------------------------
# Actor & terminal
# ---------------------------------------------------------------------------
@runtime_checkable
class Actor(Protocol):
    async def render(
        self, brief: BehavioralBrief, persona: PersonaConfig, scene: SceneConfig,
        history: "TurnHistory",
    ) -> ActorTurn: ...


@runtime_checkable
class TerminalChecker(Protocol):
    def status(self, state: GameState, last: list[Consequence]) -> SessionStatus: ...


# ---------------------------------------------------------------------------
# History (concrete-but-minimal contract; implementation in orchestrator)
# ---------------------------------------------------------------------------
@runtime_checkable
class TurnHistory(Protocol):
    def window(self, n: int) -> list[tuple[PlayerTurn, ActorTurn]]: ...
    def append(self, player: PlayerTurn, actor: ActorTurn) -> None: ...
