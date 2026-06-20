"""OutcomeRules for evaluation (getting her to qualify herself). [P3b]

The ex-"sequencing gate" lives here: qualifying works only once attraction is
high enough. Too early and she feels interviewed (engagement drops). Subtler
methods (lead/have-value) have lower attraction thresholds than a direct ask.
"""
from __future__ import annotations

from roleplay_sim.domain.config import PersonaConfig
from roleplay_sim.domain.enums import Consequence
from roleplay_sim.domain.models import GameState, Move, OutcomeResult
from roleplay_sim.engine.rules._common import outcome, scale


class _QualifyRule:
    threshold = 30.0

    def resolve(self, move: Move, state: GameState, persona: PersonaConfig) -> OutcomeResult:
        if state.emotional.attraction >= self.threshold:
            em = scale(move.quality, attraction=4.0, comfort=3.0, perceived_value=2.0)
            return outcome(em, flags={"qualified": True},
                           consequences=[Consequence.SHE_QUALIFIES], notes="she qualifies")
        return outcome({"engagement": -3.0, "comfort": -1.0},
                       consequences=[Consequence.FEELS_INTERVIEWED],
                       notes=f"qualify too early (attr<{self.threshold:.0f})")


class QualifyAskRule(_QualifyRule):
    threshold = 40.0      # overt, riskiest


class QualifyTeaseRule(_QualifyRule):
    threshold = 25.0


class QualifyLeadRule(_QualifyRule):
    threshold = 18.0


class QualifyHaveValueRule(_QualifyRule):
    threshold = 15.0      # subtlest; works earliest
