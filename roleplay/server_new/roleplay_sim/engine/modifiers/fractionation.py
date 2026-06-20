"""FractionationModifier: baseline<->plotline rhythm. [P4]

Turn hook over the register counters (already updated by the engine this turn):
- a long plotline run is exhausting (comfort/engagement down)
- a long baseline run is boring / friend-zone (attraction/engagement down)
- a fresh alternation earns a small comfort+attraction bonus
"""
from __future__ import annotations

from roleplay_sim.domain.config import PersonaConfig
from roleplay_sim.domain.enums import Consequence
from roleplay_sim.domain.models import Classification, GameState, OutcomeResult, StateDelta

RUN_LIMIT = 3


def fractionation_hook(cls: Classification, state: GameState,
                       persona: PersonaConfig) -> OutcomeResult | None:
    flags = state.flags
    d = StateDelta()
    cons: list[Consequence] = []

    if flags.consecutive_plotline >= RUN_LIMIT:
        d.emotional.update({"comfort": -3.0, "engagement": -3.0})
        cons.append(Consequence.COOLS)
    elif flags.consecutive_baseline >= RUN_LIMIT:
        d.emotional.update({"attraction": -3.0, "engagement": -2.0})
        cons.append(Consequence.BORED)
    elif flags.turn_count > 1 and (flags.consecutive_plotline == 1 or flags.consecutive_baseline == 1):
        # just alternated -> fractionation reward
        d.emotional.update({"comfort": 1.0, "attraction": 1.0})

    if not d.emotional:
        return None
    return OutcomeResult(delta=d, consequences=cons, notes="fractionation")
