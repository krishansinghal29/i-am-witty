"""RepetitionModifier: diminishing / negative returns for overused moves. [P4]

A cold-read or tease lands the first time; by the third it's a crutch — creepy or
try-hard. Reads flags.move_usage (counts from PRIOR turns, since the engine
increments after the rule runs) and scales the move's positive emotional gains.
Only "spike"/gimmick moves decay; comfort staples (rapport, questions) don't.
"""
from __future__ import annotations

from roleplay_sim.domain.config import PersonaConfig
from roleplay_sim.domain.enums import MoveType
from roleplay_sim.domain.models import GameState, ModContext, OutcomeResult

NOVELTY_MOVES: set[MoveType] = {
    MoveType.TEASE, MoveType.PUSH_PULL, MoveType.COLD_READ, MoveType.DISQUALIFY,
    MoveType.EXAGGERATION, MoveType.COCKY_FRAME, MoveType.MISINTERPRET,
    MoveType.OPEN_OPINION, MoveType.OPEN_LOOP,
}
DECAY_PER_USE = 0.35
MIN_FACTOR = -0.5     # heavy overuse actively backfires


class RepetitionModifier:
    def apply(self, move, base: OutcomeResult, state: GameState,
              persona: PersonaConfig, ctx: ModContext) -> OutcomeResult:
        mt = getattr(move, "type", None)
        if mt not in NOVELTY_MOVES:
            return base
        prior = state.flags.move_usage.get(mt, 0)
        if prior <= 0:
            return base
        factor = max(MIN_FACTOR, 1.0 - DECAY_PER_USE * prior)
        for k, v in list(base.delta.emotional.items()):
            if v > 0:  # only the intended gains decay; existing penalties stay
                base.delta.emotional[k] = round(v * factor, 3)
        base.notes += f" |rep x{prior} f={factor:.2f}"
        return base
