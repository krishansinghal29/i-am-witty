"""OutcomeRules for opener moves. [P3b]

The opener's job is to start the conversation (engagement) and, depending on
type, plant a little premise/attraction. Per the course, the opener is overrated
— so effects are modest; what follows matters more.
"""
from __future__ import annotations

from roleplay_sim.domain.config import PersonaConfig
from roleplay_sim.domain.models import GameState, Move, OutcomeResult
from roleplay_sim.engine.rules._common import outcome, scale


class _OpenerRule:
    """Base: every opener buys some engagement; subclasses add flavour."""
    base_engagement = 3.0

    def extra(self, move: Move, state: GameState) -> dict[str, float]:
        return {}

    def flags(self, move: Move, state: GameState) -> dict:
        return {}

    def resolve(self, move: Move, state: GameState, persona: PersonaConfig) -> OutcomeResult:
        em = {"engagement": self.base_engagement}
        em.update(scale(move.quality, **self.extra(move, state)))
        return outcome(em, flags=self.flags(move, state), notes=f"opener:{move.type.value}")


class DirectOpenRule(_OpenerRule):
    # Clear intent: small attraction if confident, but shows cards early.
    def extra(self, move, state):
        return {"attraction": 3.0, "perceived_value": -2.0}

    def flags(self, move, state):
        return {"premise_set": True}


class PushPullOpenRule(_OpenerRule):
    def extra(self, move, state):
        return {"attraction": 5.0, "perceived_value": 3.0}

    def flags(self, move, state):
        return {"premise_set": True}


class ObservationalOpenRule(_OpenerRule):
    # A spontaneous tease — emotionally relevant, good for attraction.
    def extra(self, move, state):
        return {"attraction": 4.0, "engagement": 2.0}


class SituationalOpenRule(_OpenerRule):
    # Safe, low risk; mostly just engagement.
    base_engagement = 4.0


class IndirectOpenRule(_OpenerRule):
    base_engagement = 4.0


class NonverbalOpenRule(_OpenerRule):
    base_engagement = 2.0

    def extra(self, move, state):
        return {"perceived_value": 2.0}


class OpinionOpenRule(_OpenerRule):
    # Engaging hook; risks becoming a directionless crutch (repetition modifier bites).
    base_engagement = 4.0

    def extra(self, move, state):
        return {"engagement": 2.0}
