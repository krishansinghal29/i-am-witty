"""Session / persona / scene configuration dataclasses. [P1]"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional, TYPE_CHECKING

from roleplay_sim.domain.enums import Ladder, MoveType
from roleplay_sim.domain.models import GameState

if TYPE_CHECKING:  # avoid a runtime import cycle with interfaces
    from roleplay_sim.domain.interfaces import OutcomeRule


@dataclass
class Blueprint:
    """The specific woman's calibration: what moves attraction/comfort for HER."""
    value_comfort_ratio: float = 0.5            # 0 = comfort-driven, 1 = value-driven
    close_threshold: float = 55.0               # Readiness needed to accept a close
    escalation_style: str = "passive"           # leads | passive | guarded
    cultural_factors: dict[str, Any] = field(default_factory=dict)
    history_factors: dict[str, Any] = field(default_factory=dict)
    archetype_weights: dict[MoveType, float] = field(default_factory=dict)  # per-move magnitude scaling
    # Per-ladder ceiling growth multiplier (guarded girls grant permission slower).
    ladder_growth: dict[Ladder, float] = field(default_factory=dict)


@dataclass
class PersonaConfig:
    identity: dict[str, Any] = field(default_factory=dict)   # name, age, occupation, backstory
    archetype: str = "princess"
    blueprint: Blueprint = field(default_factory=Blueprint)
    speaking_style: str = ""
    attracts: list[str] = field(default_factory=list)
    repels: list[str] = field(default_factory=list)
    mood_tonight: str = ""
    bible: str = ""                                          # static Actor prompt layer (text)
    fewshot: dict[str, list[str]] = field(default_factory=dict)  # band -> example lines
    # Seed words that flavor her imagery/word-choice (NOT her register). One may be
    # offered to the Actor per turn as loose, ignorable inspiration. [generator]
    voice_palette: list[str] = field(default_factory=list)


@dataclass
class SceneConfig:
    venue: str = "bar"
    approach_context: str = ""
    present_company: str = ""
    time_of_day: str = "evening"
    goal: str = "number"            # open | number | instant_date
    difficulty: str = "intermediate"  # beginner | intermediate | advanced
    # Observable opener: the plain-language first impression he takes in at a glance,
    # synthesized from observable facts only (never the latent backstory). Streamed
    # as the session's opening turn and threaded into the Actor's scene block.
    first_impression: str = ""
    # Observable appearance (what the eye can see), for the Actor's scene context.
    style: str = ""
    body_shape: str = ""
    age_hint: str = ""


@dataclass
class MoveMeta:
    """Static metadata for a move/action type, held by the MoveRegistry."""
    ladder: Optional[Ladder] = None
    default_level: Optional[int] = None
    rule: "OutcomeRule | None" = None


@dataclass
class SessionConfig:
    persona: PersonaConfig
    scene: SceneConfig
    initial_state: GameState = field(default_factory=GameState.fresh)
