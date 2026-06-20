"""OutcomeRules for anti-patterns. [P3b]

Explicit low-value moves. (Turn-level *posture* supplication is also handled by
the FrameModifier in P4; an explicit SUPPLICATE move stacks on top of it.)
"""
from __future__ import annotations

from roleplay_sim.domain.config import PersonaConfig
from roleplay_sim.domain.enums import Consequence
from roleplay_sim.domain.models import GameState, Move, OutcomeResult
from roleplay_sim.engine.rules._common import outcome


class SupplicateRule:
    def resolve(self, move: Move, state: GameState, persona: PersonaConfig) -> OutcomeResult:
        return outcome(
            {"perceived_value": -5.0, "attraction": -3.0, "neediness": 6.0},
            flags={"supplication_count": state.flags.supplication_count + 1},
            consequences=[Consequence.COOLS], notes="supplicate",
        )


class SeekValidationRule:
    def resolve(self, move, state, persona):
        return outcome({"perceived_value": -3.0, "neediness": 4.0}, notes="seek_validation")


class InterviewQsRule:
    def resolve(self, move, state, persona):
        return outcome({"engagement": -3.0, "comfort": 1.0},
                       consequences=[Consequence.BORED], notes="interview_qs")


class OverExplainRule:
    def resolve(self, move, state, persona):
        return outcome({"perceived_value": -2.0, "engagement": -2.0}, notes="over_explain")


class TryHardRule:
    def resolve(self, move, state, persona):
        return outcome({"perceived_value": -3.0, "attraction": -2.0, "neediness": 3.0},
                       notes="try_hard")
