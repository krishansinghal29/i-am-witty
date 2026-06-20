"""OutcomeRules for attraction techniques. [P3b]

These are the plotline spikes. Most are comfort-gated: a sharp tease or a
sexual line with no comfort underneath reads mean/creepy and backfires.
SEXUALIZE / MISINTERPRET ride the verbal escalation ladder (shared timing logic).
"""
from __future__ import annotations

from roleplay_sim.domain.config import PersonaConfig
from roleplay_sim.domain.enums import Consequence, LMH, Ladder
from roleplay_sim.domain.models import GameState, Move, OutcomeResult, StateDelta
from roleplay_sim.engine.ladders import resolve_escalation
from roleplay_sim.engine.rules._common import outcome, scale

COMFORT_FLOOR = 15.0   # below this, hard/edgy moves can sting


class TeaseRule:
    def resolve(self, move: Move, state: GameState, persona: PersonaConfig) -> OutcomeResult:
        e = state.emotional
        if e.comfort < COMFORT_FLOOR and move.intensity is LMH.HIGH and not move.softener:
            return outcome({"comfort": -3.0, "attraction": -2.0},
                           consequences=[Consequence.COOLS], notes="harsh tease, low comfort")
        em = scale(move.quality, attraction=5.0, perceived_value=3.0, engagement=2.0)
        cons = [Consequence.WARMS] if e.attraction > 20 else []
        return outcome(em, consequences=cons, notes="tease")


class PushPullRule:
    def resolve(self, move, state, persona):
        em = scale(move.quality, attraction=6.0, perceived_value=3.0, engagement=2.0)
        return outcome(em, notes="push_pull")


class ColdReadRule:
    def resolve(self, move, state, persona):
        # Repetition modifier punishes overuse (fortune-teller / creepy).
        em = scale(move.quality, attraction=4.0, comfort=2.0, perceived_value=2.0, engagement=2.0)
        return outcome(em, notes="cold_read")


class DisqualifyRule:
    def resolve(self, move, state, persona):
        e = state.emotional
        if e.comfort < COMFORT_FLOOR and move.intensity is LMH.HIGH:
            return outcome({"comfort": -3.0}, consequences=[Consequence.COOLS],
                           notes="disqualify too early/harsh")
        em = scale(move.quality, attraction=5.0, perceived_value=4.0, engagement=2.0)
        return outcome(em, notes="disqualify (selective)")


class CockyFrameRule:
    def resolve(self, move, state, persona):
        # BlueprintModifier rescales for archetype (a good-girl reads arrogance down).
        em = scale(move.quality, perceived_value=6.0, attraction=4.0)
        return outcome(em, notes="cocky_frame")


class OpenLoopRule:
    def resolve(self, move, state, persona):
        em = scale(move.quality, engagement=4.0, attraction=1.0)
        return outcome(em, notes="open_loop (curiosity)")


class ExaggerationRule:
    def resolve(self, move, state, persona):
        em = scale(move.quality, attraction=3.0, engagement=2.0)
        return outcome(em, notes="exaggeration")


class _VerbalLadderRule:
    """Sexual verbal moves resolved through the verbal escalation ladder."""
    default_level = 5
    base_attraction = 2.0

    def resolve(self, move: Move, state: GameState, persona: PersonaConfig) -> OutcomeResult:
        level = move.target_level if move.target_level is not None else self.default_level
        out = resolve_escalation(state, Ladder.VERBAL, level, intended_step=+1, persona=persona)
        delta: StateDelta = out.delta
        if out.success:
            delta.emotional["attraction"] = delta.emotional.get("attraction", 0.0) + self.base_attraction
        return OutcomeResult(delta=delta, consequences=[out.consequence], success=out.success,
                             notes=f"verbal_escalation:{move.type.value} L{level}")


class MisinterpretRule(_VerbalLadderRule):
    default_level = 4
    base_attraction = 2.0

    def resolve(self, move, state, persona):
        res = super().resolve(move, state, persona)
        res.delta.flags["premise_set"] = True
        return res


class SexualizeRule(_VerbalLadderRule):
    default_level = 6
    base_attraction = 3.0
