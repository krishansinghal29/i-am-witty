"""OutcomeRules for narrative moves. [P3b]

Show-don't-tell stories build value+comfort and seed the narrative; bragging
("tell") backfires; social proof is the strongest, lowest-neediness value lever.
"""
from __future__ import annotations

from roleplay_sim.domain.config import PersonaConfig
from roleplay_sim.domain.models import GameState, Move, OutcomeResult
from roleplay_sim.engine.rules._common import outcome, scale


class StoryShowRule:
    def resolve(self, move: Move, state: GameState, persona: PersonaConfig) -> OutcomeResult:
        em = scale(move.quality, attraction=3.0, comfort=3.0, perceived_value=3.0)
        return outcome(em, flags={"narrative_seeded": True}, notes="story (show)")


class StoryTellRule:
    def resolve(self, move, state, persona):
        # Bragging / fact-listing: reads needy regardless of "quality".
        return outcome({"perceived_value": -2.0, "neediness": 2.0, "engagement": -2.0},
                       notes="story (tell/brag)")


class SelfDisclosureRule:
    def resolve(self, move, state, persona):
        em = scale(move.quality, comfort=3.0, attraction=1.0)
        return outcome(em, notes="self_disclosure")


class PreframeRule:
    def resolve(self, move, state, persona):
        em = scale(move.quality, perceived_value=2.0, comfort=1.0)
        return outcome(em, notes="preframe")


class ReframeRule:
    def resolve(self, move, state, persona):
        em = scale(move.quality, perceived_value=2.0, comfort=1.0)
        return outcome(em, notes="reframe")


class SocialProofRule:
    def resolve(self, move, state, persona):
        em = scale(move.quality, perceived_value=6.0, attraction=3.0, comfort=2.0)
        return outcome(em, notes="social_proof")
