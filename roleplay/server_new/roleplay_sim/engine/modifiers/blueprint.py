"""BlueprintModifier: scale a move's effect by HER archetype weights. [P4]

The same move lands differently per woman. A Princess amplifies cocky/challenge
and punishes supplication harder; a good-girl down-weights arrogance. Weights are
authored per persona (P7); absent a weight, the move is unscaled.
"""
from __future__ import annotations

from roleplay_sim.domain.config import PersonaConfig
from roleplay_sim.domain.models import GameState, ModContext, OutcomeResult


class BlueprintModifier:
    def apply(self, move, base: OutcomeResult, state: GameState,
              persona: PersonaConfig, ctx: ModContext) -> OutcomeResult:
        mt = getattr(move, "type", None)
        w = persona.blueprint.archetype_weights.get(mt, 1.0)
        if w == 1.0:
            return base
        for k, v in list(base.delta.emotional.items()):
            base.delta.emotional[k] = round(v * w, 3)
        base.notes += f" |bp x{w:.2f}"
        return base
