"""OutcomeRules for closes. [P3b]

Readiness blends attraction & comfort, weighted by HER value-comfort ratio, and
is dampened until premise is set and lifted once she's qualified. The ex-gate is
absorbed: an early close isn't blocked, it's *rejected* (with a neediness cost).
"""
from __future__ import annotations

from roleplay_sim.config.tuning import TUNING
from roleplay_sim.domain.config import PersonaConfig
from roleplay_sim.domain.enums import Consequence
from roleplay_sim.domain.models import GameState, Move, OutcomeResult
from roleplay_sim.engine.rules._common import outcome

FLAKY_FRACTION = TUNING.flaky_fraction   # readiness in [frac*thr, thr) -> a flaky yes


def readiness(state: GameState, persona: PersonaConfig) -> float:
    e = state.emotional
    vcr = persona.blueprint.value_comfort_ratio
    base = vcr * e.attraction + (1.0 - vcr) * e.comfort
    if not state.flags.premise_set:
        base *= 0.5
    if state.flags.qualified:
        base += 8.0
    return base


class _CloseRule:
    flag_key = "closed_number"

    def resolve(self, move: Move, state: GameState, persona: PersonaConfig) -> OutcomeResult:
        r = readiness(state, persona)
        thr = persona.blueprint.close_threshold
        if r >= thr:
            return outcome({"attraction": 5.0}, consequences=[Consequence.CLOSE_ACCEPTED],
                           success=True, notes=f"close accepted (readiness {r:.0f}/{thr:.0f})")
        if r >= FLAKY_FRACTION * thr:
            return outcome({}, consequences=[Consequence.CLOSE_FLAKY], success=True,
                           notes=f"flaky close (readiness {r:.0f}/{thr:.0f})")
        return outcome({"attraction": -4.0, "engagement": -5.0, "neediness": 3.0},
                       consequences=[Consequence.CLOSE_REJECTED], success=False,
                       notes=f"close too early (readiness {r:.0f}/{thr:.0f})")


class CloseNumberRule(_CloseRule):
    flag_key = "closed_number"


class CloseDateRule(_CloseRule):
    flag_key = "closed_date"


class CloseInstantDateRule(_CloseRule):
    flag_key = "closed_instant"
