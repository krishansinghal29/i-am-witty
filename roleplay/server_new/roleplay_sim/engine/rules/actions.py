"""OutcomeRules for the action channel (physical + logistical escalation). [P3]

All actions resolve through the shared ladder gap logic, so "early vs. late"
behaviour is identical across approach, physical, and logistical moves.
"""
from __future__ import annotations

from roleplay_sim.domain.config import PersonaConfig
from roleplay_sim.domain.models import ActionMove, GameState, OutcomeResult
from roleplay_sim.engine.ladders import resolve_escalation


class EscalationActionRule:
    """Resolves any ActionMove via the ladder (gap = target_level - ceiling)."""

    def resolve(self, move: ActionMove, state: GameState, persona: PersonaConfig) -> OutcomeResult:
        out = resolve_escalation(
            state, move.ladder, move.target_level, move.intended_step, persona
        )
        return OutcomeResult(
            delta=out.delta,
            consequences=[out.consequence],
            success=out.success,
            notes=f"action {move.type.value} L{move.target_level} -> {out.consequence.value}",
        )
