"""Actor prompt assembly (co-located). [P6]

Layers: character bible (system) + scene (incl. what he sees) + turn direction
(beat/dials/note) + recent transcript + band-keyed few-shot + an optional palette
spark + a strict output contract. The Actor never receives the raw GameState —
only the brief. Output is ONE combined string: spoken words in double quotes, a
short third-person beat outside them.
"""
from __future__ import annotations

import os
import random
from typing import Any

from roleplay_sim.actor.bible import character_system, select_fewshot
from roleplay_sim.domain.config import PersonaConfig, SceneConfig
from roleplay_sim.domain.glossary import DIAL_DOC, beat_line
from roleplay_sim.domain.models import BehavioralBrief

# Probability the Actor is offered one palette seed as loose, ignorable inspiration
# this turn (fights within-conversation mode collapse). Env-overridable.
SPARK_PROB = float(os.environ.get("ROLEPLAY_SPARK_PROB", "0.3"))


def _transcript(history: Any, n: int = 4) -> str:
    try:
        return history.transcript(n)   # owns pairs + the in-flight pending line
    except Exception:
        return ""


def _spark(persona: PersonaConfig, rng: random.Random) -> str:
    """Maybe offer one palette seed as loose imagery inspiration for this turn."""
    if persona.voice_palette and rng.random() < SPARK_PROB:
        word = rng.choice(persona.voice_palette)
        return (
            f"\nLoose inspiration (optional): the word '{word}' — let it color one image "
            "or word choice ONLY if it fits naturally. Never force it; never let it change "
            "how she talks."
        )
    return ""


def build_messages(brief: BehavioralBrief, persona: PersonaConfig, scene: SceneConfig,
                   history: Any, rng: random.Random | None = None) -> list[dict[str, str]]:
    rng = rng or random
    name = persona.identity.get("name", "she")
    d = brief.dials
    fewshot = select_fewshot(persona, brief.beat)
    fewshot_block = ("\nExamples of how you'd sound right now:\n- " + "\n- ".join(fewshot)) if fewshot else ""

    # A compact venue + look tag — NOT the full first impression. Re-injecting the
    # vivid opening snapshot every turn over-weights the scene's props and pulls her
    # into looping the same detail; the snapshot is shown once, at the opening.
    look = ", ".join(p for p in (scene.style, scene.body_shape, scene.age_hint) if p)
    scene_block = (
        f"Setting: {scene.venue}, {scene.time_of_day}. {scene.approach_context}."
        + (f" Present: {scene.present_company}." if scene.present_company else "")
        + (f"\nYou: {look}." if look else "")
    )
    direction = (
        f"Beat (what to do this turn): {beat_line(brief.beat, brief.secondary_beat)}"
        + f"\nDials (low/med/high) — warmth={d.warmth.value}, investment={d.investment.value}, "
        f"testiness={d.testiness.value}, openness={d.openness.value}, "
        f"receptiveness={d.receptiveness.value}\n"
        + DIAL_DOC
        + (f"\nDirection: {brief.note}" if brief.note else "")
    )
    recap = f"\nSo far: {brief.recap}" if brief.recap else ""
    transcript = _transcript(history)
    transcript_block = f"\nRecent:\n{transcript}" if transcript else ""
    spark = _spark(persona, rng)

    contract = (
        f"Reply ONLY as {name}, in ONE short turn (1-2 sentences; a single quoted word is "
        "fine when she's cold). Put her spoken words in double quotes and write any action "
        "or expression as a short plain phrase outside the quotes, in third person — e.g. "
        'She glances up, unimpressed. "That\'s a bold opener." '
        "Do not narrate his actions or her private thoughts, and do not reuse phrasings "
        "from earlier in this conversation. No markdown, asterisks, or bracketed stage directions."
    )

    user = f"{scene_block}\n\n{direction}{recap}{transcript_block}\n{fewshot_block}{spark}\n\n{contract}"
    return [
        {"role": "system", "content": character_system(persona)},
        {"role": "user", "content": user},
    ]
