"""BriefAuthor (LLM): writes the Actor's note + running recap. [P6]

Translates the deterministic outcome (beat, dials, consequences) into natural
language for the Actor — never numbers. Co-located prompt.
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from roleplay_sim.domain.config import PersonaConfig
from roleplay_sim.domain.enums import Beat, Consequence
from roleplay_sim.domain.glossary import DIAL_DOC, beat_line
from roleplay_sim.domain.interfaces import LLMClient
from roleplay_sim.llm.tracing import llm_stage
from roleplay_sim.domain.models import Dials, GameState


class BriefOut(BaseModel):
    note: str
    recap: str


_SYSTEM = (
    "You direct an actress playing a woman being approached. Given her required beat, "
    "performance dials, and what just happened, write: (1) note — ONE in-character line "
    "telling her how to play this beat (no numbers, no meta, no quotes of dialogue), and "
    "(2) recap — a 2-3 sentence running summary of the interaction so far. Output JSON.\n\n"
    "The beat (with its intent in parens) is what she must do this turn. The dials are her "
    "current performance levels (each low/med/high); their meaning:\n" + DIAL_DOC
)


def _transcript(history: Any, n: int = 4) -> str:
    try:
        win = history.window(n)
    except Exception:
        return ""
    lines = []
    for player, her in win:
        lines.append(f"HIM: {player.text}")
        lines.append(f"HER: {her.text}")
    return "\n".join(lines)


class LLMBriefAuthor:
    def __init__(self, client: LLMClient) -> None:
        self.client = client

    async def author(self, state: GameState, beat: Beat, dials: Dials,
                     consequences: list[Consequence], history: Any,
                     persona: PersonaConfig) -> tuple[str, str]:
        prior_recap = getattr(history, "recap", "") or "(none yet)"
        cons = ", ".join(c.value for c in consequences) or "nothing notable"
        user = (
            f"Woman: {persona.archetype}; mood: {persona.mood_tonight}.\n"
            f"Beat: {beat_line(beat)}\n"
            f"Dials: warmth={dials.warmth.value}, investment={dials.investment.value}, "
            f"testiness={dials.testiness.value}, openness={dials.openness.value}, "
            f"receptiveness={dials.receptiveness.value}\n"
            f"What just happened: {cons}\n"
            f"Prior recap: {prior_recap}\n"
            f"Recent transcript:\n{_transcript(history)}\n"
        )
        model = getattr(self.client, "model_for_author", lambda: None)()
        with llm_stage("author"):
            out = await self.client.complete_structured(
                [{"role": "system", "content": _SYSTEM}, {"role": "user", "content": user}],
                schema=BriefOut, model=model,
            )
        note = out.note.strip()
        recap = out.recap.strip() or prior_recap
        return note, recap
