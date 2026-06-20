"""Core dataclasses: classification, hidden state, outcomes, and the actor brief. [P1]

Conventions:
- Emotional variables are floats on a 0–100 scale.
- Ladder levels are floats on a 0–10 scale.
- `StateDelta` is sparse and additive; the engine aggregates then clamps.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from roleplay_sim.domain.enums import (
    ActionType,
    Beat,
    Consequence,
    Ladder,
    LMH,
    MoveType,
    Quality,
    Register,
    Supplication,
    ValuePosture,
)

# ---------------------------------------------------------------------------
# Classifier output
# ---------------------------------------------------------------------------


@dataclass
class Move:
    """One verbal move within a turn (a turn may contain several)."""
    type: MoveType
    quality: Quality = Quality.MEDIOCRE
    intensity: LMH = LMH.MED
    softener: bool = False
    target: str = "none"            # looks | personality | situation | group | self | none
    ladder: Optional[Ladder] = None         # set for verbal-escalation moves
    target_level: Optional[int] = None      # 0–10 rung this move reaches (verbal ladder)


@dataclass
class ActionMove:
    """A non-verbal/logistical action accompanying a turn."""
    type: ActionType
    ladder: Ladder
    target_level: int               # 0–10
    intended_step: int = 1          # -1 | 0 | +1 | +2 (2-forward-1-back intent)


@dataclass
class Frame:
    """The cross-cutting value/posture quality, classified on every turn."""
    value_posture: ValuePosture = ValuePosture.NEUTRAL
    supplication: Supplication = Supplication.NONE
    reaction_seeking: bool = False
    congruence: bool = True


@dataclass
class ShitTestResponse:
    outcome: str                    # passed | partial | failed
    method: str = "unreactive"      # misinterpret | agree_exaggerate | unreactive | defensive | supplicated


@dataclass
class PlayerTurn:
    text: str
    action: Optional[ActionMove] = None


@dataclass
class ActorTurn:
    text: str
    action: Optional[str] = None    # her diegetic *[action]*, e.g. "checks phone" / "walks off"


@dataclass
class Classification:
    """The structured tagging of a single player turn (Classifier output).

    No `timing` and no `sequencing_violation` — both are derived downstream:
    timing falls out of the ladder gap; ex-gates live inside each OutcomeRule.
    """
    register: Register = Register.BASELINE
    moves: list[Move] = field(default_factory=list)
    frame: Frame = field(default_factory=Frame)
    action: Optional[ActionMove] = None
    shit_test_response: Optional[ShitTestResponse] = None


# ---------------------------------------------------------------------------
# Hidden state
# ---------------------------------------------------------------------------


@dataclass
class EmotionalState:
    """Continuous hidden variables (0–100)."""
    attraction: float = 8.0
    comfort: float = 12.0
    perceived_value: float = 30.0
    engagement: float = 55.0
    neediness: float = 0.0
    arousal: float = 0.0
    mood: float = 50.0


@dataclass
class LadderState:
    """Per-ladder permission tracking (levels 0–10)."""
    ceiling: float = 0.0            # her current granted level
    reached: float = 0.0            # highest level actually accepted (re-escalation is cheap)
    locked: Optional[int] = None    # a rung hard-closed by over-reach (point-of-no-return)


@dataclass
class GameFlags:
    premise_set: bool = False
    qualified: bool = False
    narrative_seeded: bool = False
    venue: str = "meet"
    turn_count: int = 0
    consecutive_baseline: int = 0
    consecutive_plotline: int = 0
    supplication_count: int = 0
    move_usage: dict[MoveType, int] = field(default_factory=dict)  # rolling-window counts
    pending_test: Optional[str] = None                            # theme of a scheduled shit test


@dataclass
class GameState:
    emotional: EmotionalState = field(default_factory=EmotionalState)
    ladders: dict[Ladder, LadderState] = field(default_factory=dict)
    flags: GameFlags = field(default_factory=GameFlags)

    @staticmethod
    def fresh() -> "GameState":
        return GameState(
            emotional=EmotionalState(),
            ladders={lad: LadderState() for lad in Ladder},
            flags=GameFlags(),
        )


# ---------------------------------------------------------------------------
# Outcome of resolving moves
# ---------------------------------------------------------------------------


@dataclass
class StateDelta:
    """Sparse, additive changes. Aggregated across moves, then clamped."""
    emotional: dict[str, float] = field(default_factory=dict)      # {"attraction": +6, ...}
    ladder_ceiling: dict[Ladder, float] = field(default_factory=dict)
    ladder_reached: dict[Ladder, float] = field(default_factory=dict)
    lock: dict[Ladder, int] = field(default_factory=dict)
    flags: dict[str, Any] = field(default_factory=dict)

    def merged(self, other: "StateDelta") -> "StateDelta":
        out = StateDelta(
            emotional=dict(self.emotional),
            ladder_ceiling=dict(self.ladder_ceiling),
            ladder_reached=dict(self.ladder_reached),
            lock=dict(self.lock),
            flags=dict(self.flags),
        )
        for k, v in other.emotional.items():
            out.emotional[k] = out.emotional.get(k, 0.0) + v
        for k, v in other.ladder_ceiling.items():
            out.ladder_ceiling[k] = out.ladder_ceiling.get(k, 0.0) + v
        for k, v in other.ladder_reached.items():
            out.ladder_reached[k] = max(out.ladder_reached.get(k, 0.0), v)
        out.lock.update(other.lock)
        out.flags.update(other.flags)
        return out


@dataclass
class OutcomeResult:
    delta: StateDelta = field(default_factory=StateDelta)
    consequences: list[Consequence] = field(default_factory=list)
    success: Optional[bool] = None      # for actions/closes: accepted / rejected
    notes: str = ""


@dataclass
class ModContext:
    """Turn-level context handed to per-move Modifiers (frame is a turn property)."""
    frame: "Frame"
    register: Register


# ---------------------------------------------------------------------------
# Director output → Actor input
# ---------------------------------------------------------------------------


@dataclass
class Dials:
    warmth: LMH = LMH.LOW
    investment: LMH = LMH.LOW
    testiness: LMH = LMH.MED
    openness: LMH = LMH.LOW
    receptiveness: LMH = LMH.LOW


@dataclass
class BehavioralBrief:
    beat: Beat = Beat.NEUTRAL_ENGAGE
    dials: Dials = field(default_factory=Dials)
    note: str = ""
    recap: str = ""
    secondary_beat: Optional[Beat] = None


@dataclass
class StateUpdate:
    new_state: GameState
    consequences: list[Consequence] = field(default_factory=list)
    events: list[dict[str, Any]] = field(default_factory=list)  # structured log for the deferred scorecard


@dataclass
class DirectorStep:
    """Director.step result: new state + the brief + what happened (for terminal/log)."""
    state: GameState
    brief: BehavioralBrief
    consequences: list[Consequence] = field(default_factory=list)
    events: list[dict[str, Any]] = field(default_factory=list)
