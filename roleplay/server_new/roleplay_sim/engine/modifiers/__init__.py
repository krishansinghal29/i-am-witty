"""Cross-cutting modifiers applied around every outcome rule. [P4]

Two kinds:
- per-move Modifiers (run inside the move loop): repetition, congruence, blueprint
- turn-level hooks (run once per turn): frame, fractionation
"""
from __future__ import annotations

from roleplay_sim.engine.modifiers.blueprint import BlueprintModifier
from roleplay_sim.engine.modifiers.congruence import CongruenceModifier
from roleplay_sim.engine.modifiers.fractionation import fractionation_hook
from roleplay_sim.engine.modifiers.frame import frame_hook
from roleplay_sim.engine.modifiers.repetition import RepetitionModifier


def default_modifiers() -> list:
    """Per-move modifier chain (order: novelty -> congruence -> blueprint scaling)."""
    return [RepetitionModifier(), CongruenceModifier(), BlueprintModifier()]


def default_turn_hooks() -> list:
    """Turn-level hooks merged after all moves are processed."""
    return [frame_hook, fractionation_hook]
