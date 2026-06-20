"""OutcomeRules for baseline / comfort moves. [P3b]

These build comfort and lower neediness. On their own they don't raise
attraction — too many in a row stalls the interaction (the FractionationModifier
applies the friend-zone/boredom penalty across turns).
"""
from __future__ import annotations

from roleplay_sim.domain.config import PersonaConfig
from roleplay_sim.domain.models import GameState, Move, OutcomeResult
from roleplay_sim.engine.rules._common import outcome, scale


class GenuineQuestionRule:
    def resolve(self, move: Move, state: GameState, persona: PersonaConfig) -> OutcomeResult:
        em = scale(move.quality, comfort=3.0, neediness=-1.0)
        return outcome(em, notes="genuine_question")


class RapportRule:
    def resolve(self, move, state, persona):
        em = scale(move.quality, comfort=3.0)
        return outcome(em, notes="rapport")


class ActiveListeningRule:
    def resolve(self, move, state, persona):
        em = scale(move.quality, comfort=2.0, neediness=-1.0)
        return outcome(em, notes="active_listening")


class AgreeExaggerateRule:
    # Playful agree-&-exaggerate: light attraction + banter energy.
    def resolve(self, move, state, persona):
        em = scale(move.quality, attraction=2.0, engagement=2.0)
        return outcome(em, notes="agree_exaggerate")
