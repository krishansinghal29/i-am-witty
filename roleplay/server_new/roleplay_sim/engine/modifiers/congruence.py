"""CongruenceModifier: damp gains when the turn reads incongruent. [P4]

If the move doesn't fit what came before (or his established persona), she senses
something off: the technique's positive effect is halved and a little comfort is
lost.
"""
from __future__ import annotations

from roleplay_sim.domain.config import PersonaConfig
from roleplay_sim.domain.models import GameState, ModContext, OutcomeResult

DAMP = 0.5


class CongruenceModifier:
    def apply(self, move, base: OutcomeResult, state: GameState,
              persona: PersonaConfig, ctx: ModContext) -> OutcomeResult:
        if ctx.frame.congruence:
            return base
        for k, v in list(base.delta.emotional.items()):
            if v > 0:
                base.delta.emotional[k] = round(v * DAMP, 3)
        base.delta.emotional["comfort"] = base.delta.emotional.get("comfort", 0.0) - 1.0
        base.notes += " |incongruent"
        return base
