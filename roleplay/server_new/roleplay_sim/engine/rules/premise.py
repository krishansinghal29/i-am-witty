"""OutcomeRules for premise moves. [P3b]

Premise establishes the man-to-woman frame. Subtle premise (push-pull / implied)
raises value; overt premise (a plain compliment / stated interest) sets the frame
but reads a touch needy — fine for beginners, weaker for value.
"""
from __future__ import annotations

from roleplay_sim.domain.config import PersonaConfig
from roleplay_sim.domain.enums import Consequence
from roleplay_sim.domain.models import GameState, Move, OutcomeResult
from roleplay_sim.engine.rules._common import outcome, scale


class PremiseSubtleRule:
    def resolve(self, move: Move, state: GameState, persona: PersonaConfig) -> OutcomeResult:
        em = scale(move.quality, attraction=4.0, perceived_value=3.0)
        return outcome(em, flags={"premise_set": True},
                       consequences=[Consequence.PREMISE_SET], notes="premise_subtle")


class PremiseOvertRule:
    def resolve(self, move: Move, state: GameState, persona: PersonaConfig) -> OutcomeResult:
        # Sets premise but shows cards: small value dip, slight neediness.
        return outcome({"perceived_value": -2.0, "neediness": 2.0},
                       flags={"premise_set": True},
                       consequences=[Consequence.PREMISE_SET], notes="premise_overt")
