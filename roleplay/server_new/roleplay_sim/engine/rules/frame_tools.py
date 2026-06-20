"""OutcomeRules for frame / pacing tools. [P3b]

Light-touch moves: social pressure, seeding, baby-stepping, and the two
"keep her here" tools (false time constraint, assume the burden) that refill
engagement so she doesn't drift off early.
"""
from __future__ import annotations

from roleplay_sim.domain.config import PersonaConfig
from roleplay_sim.domain.models import GameState, Move, OutcomeResult
from roleplay_sim.engine.rules._common import outcome, scale


class SocialPressureRule:
    def resolve(self, move: Move, state: GameState, persona: PersonaConfig) -> OutcomeResult:
        em = scale(move.quality, perceived_value=2.0, engagement=1.0)
        return outcome(em, notes="social_pressure")


class SeedingRule:
    def resolve(self, move, state, persona):
        em = scale(move.quality, comfort=1.0)
        return outcome(em, notes="seeding")


class BabystepRule:
    def resolve(self, move, state, persona):
        em = scale(move.quality, comfort=2.0)
        return outcome(em, notes="babystep")


class FalseTimeConstraintRule:
    # Reassures she won't be trapped -> she stays engaged.
    def resolve(self, move, state, persona):
        return outcome({"engagement": 3.0, "comfort": 1.0}, notes="false_time_constraint")


class AssumeBurdenRule:
    # Carrying the conversation keeps a hesitant target in the interaction.
    def resolve(self, move, state, persona):
        return outcome({"engagement": 3.0, "comfort": 1.0}, notes="assume_burden")
