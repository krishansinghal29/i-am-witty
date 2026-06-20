"""Character-Bible assembly + band-keyed few-shot selection. [P6/P7]

Composes the Actor's static prompt layer from the persona, and picks the few-shot
examples matching the current beat's band so the model anchors both voice and the
right warmth level.
"""
from __future__ import annotations

from roleplay_sim.domain.config import PersonaConfig
from roleplay_sim.domain.enums import Beat

# Beat -> few-shot band.
BAND: dict[Beat, str] = {
    Beat.LEAVE: "cold",
    Beat.COOL_OFF: "cold",
    Beat.POLITE_BRUSHOFF: "cold",
    Beat.NEUTRAL_ENGAGE: "neutral",
    Beat.CURIOUS: "neutral",
    Beat.FLAKE_SIGNAL: "neutral",
    Beat.SHIT_TEST: "testing",
    Beat.BRAKES: "testing",
    Beat.QUALIFY_SELF: "qualifying",
    Beat.WARM_OPEN: "warm",
    Beat.BANTER: "warm",
    Beat.COMPLY: "warm",
    Beat.ESCALATE_BACK: "warm",
}

HARD_RULES = (
    "HARD RULES: Never break character. Never coach or hint at what he should say. "
    "Never state your feelings or any rating/number. Show everything through what you "
    "say and do. You owe him nothing — interest is earned. Match your effort to how "
    "interested you actually are (bored = short/closed; into it = longer, teasing back)."
)


def character_system(persona: PersonaConfig) -> str:
    if persona.bible:
        return f"{persona.bible}\n\n{HARD_RULES}"
    ident = persona.identity
    name = ident.get("name", "she")
    age = ident.get("age", "")
    occ = ident.get("occupation", "")
    return (
        f"You are {name}, {age}, {occ}. Archetype: {persona.archetype}. "
        f"Speaking style: {persona.speaking_style}. Tonight you are {persona.mood_tonight}. "
        f"You are drawn to: {', '.join(persona.attracts)}. "
        f"You are turned off by: {', '.join(persona.repels)}.\n\n{HARD_RULES}"
    )


def select_fewshot(persona: PersonaConfig, beat: Beat, k: int = 3) -> list[str]:
    band = BAND.get(beat, "neutral")
    return list(persona.fewshot.get(band, [])[:k])
