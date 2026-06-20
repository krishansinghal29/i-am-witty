"""Deterministic stub Classifier for the walking skeleton + tests. [P2]

No NLU — just enough to drive the loop. Echoes the player's action and tags a
crude register so end-to-end wiring can be exercised without an LLM.
"""
from __future__ import annotations

from roleplay_sim.domain.enums import Register
from roleplay_sim.domain.models import Classification, GameState, PlayerTurn


class StubClassifier:
    async def classify(
        self, turn: PlayerTurn, state: GameState, history: object
    ) -> Classification:
        text = (turn.text or "").lower()
        plotty = any(w in text for w in ("?!", "haha", "tease", "trouble", "kiss"))
        return Classification(
            register=Register.PLOTLINE if plotty else Register.BASELINE,
            moves=[],
            action=turn.action,
        )
