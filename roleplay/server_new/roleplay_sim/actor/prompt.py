"""Actor prompt assembly (co-located). [P6]

Layers: character bible (system) + scene + turn direction (beat/dials/note) +
recent transcript + band-keyed few-shot + a strict output contract.
The Actor never receives the raw GameState — only the brief.
"""
from __future__ import annotations

from typing import Any

from roleplay_sim.actor.bible import character_system, select_fewshot
from roleplay_sim.domain.config import PersonaConfig, SceneConfig
from roleplay_sim.domain.models import BehavioralBrief


def _transcript(history: Any, n: int = 4) -> str:
    try:
        win = history.window(n)
    except Exception:
        return ""
    out = []
    for player, her in win:
        out.append(f"HIM: {player.text}")
        out.append(f"HER: {her.text}")
    return "\n".join(out)


def build_messages(brief: BehavioralBrief, persona: PersonaConfig, scene: SceneConfig,
                   history: Any) -> list[dict[str, str]]:
    name = persona.identity.get("name", "she")
    d = brief.dials
    fewshot = select_fewshot(persona, brief.beat)
    fewshot_block = ("\nExamples of how you'd sound right now:\n- " + "\n- ".join(fewshot)) if fewshot else ""

    scene_block = (
        f"Setting: {scene.venue}, {scene.time_of_day}. {scene.approach_context}. "
        f"{('Present: ' + scene.present_company) if scene.present_company else ''}"
    )
    direction = (
        f"Beat: {brief.beat.value}"
        + (f" (then {brief.secondary_beat.value})" if brief.secondary_beat else "")
        + f"\nDials: warmth={d.warmth.value}, investment={d.investment.value}, "
        f"testiness={d.testiness.value}, openness={d.openness.value}, "
        f"receptiveness={d.receptiveness.value}"
        + (f"\nDirection: {brief.note}" if brief.note else "")
    )
    recap = f"\nSo far: {brief.recap}" if brief.recap else ""
    transcript = _transcript(history)
    transcript_block = f"\nRecent:\n{transcript}" if transcript else ""

    contract = (
        f"Reply ONLY as {name}: 1-2 casual spoken sentences (a single word is fine when "
        "cold). Optionally ONE action in *[...]* (e.g. *[checks phone]*, *[leans in]*, "
        "*[walks off]*). No narration, no explanation."
    )

    user = f"{scene_block}\n\n{direction}{recap}{transcript_block}\n{fewshot_block}\n\n{contract}"
    return [
        {"role": "system", "content": character_system(persona)},
        {"role": "user", "content": user},
    ]
