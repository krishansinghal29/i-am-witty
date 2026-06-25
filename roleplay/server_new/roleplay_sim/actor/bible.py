"""Character-Bible assembly + band-keyed few-shot selection. [P6/P7]

Composes the Actor's static prompt layer from the persona, and picks the few-shot
examples matching the current beat's band so the model anchors both voice and the
right warmth level.
"""
from __future__ import annotations

import random

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
    "interested you actually are (bored = short/closed; into it = longer, teasing back).\n"
    "RHYTHM: He drives the conversation, not you — most of your lines are plain, "
    "lightly-guarded reactions, NOT questions volleyed back. Probing, teasing, and testing "
    "are seasoning, not your default: only a minority of lines challenge him; the rest just "
    "react. When he asks you a direct question, actually respond to it — answer briefly, or "
    "deflect with something of substance — never just fire back another question. Don't end "
    "most replies with a question, and don't reuse the same deflection turn after turn."
)


def about_you(persona: PersonaConfig) -> str:
    """Concrete facts about her own life, so she has material to draw on beyond the
    scene in front of her. Reachable conversational fodder — not an info-dump."""
    ident = persona.identity or {}
    facts = []
    if ident.get("occupation"):
        facts.append(f"work: {ident['occupation']}")
    if ident.get("hometown"):
        facts.append(f"from: {ident['hometown']}")
    hobbies = ident.get("hobbies") or []
    if hobbies:
        facts.append(f"into: {', '.join(hobbies)}")
    if not facts:
        return ""
    return (
        "ABOUT YOU (your own life — you're a whole person, not just a feature of this "
        "scene). Don't volunteer these as a list or info-dump, but let them surface "
        "naturally as the talk warms, and lean on your own world rather than looping the "
        "same detail of the setting: " + "; ".join(facts) + "."
    )


def character_system(persona: PersonaConfig) -> str:
    if persona.bible:
        base = persona.bible
    else:
        ident = persona.identity
        name = ident.get("name", "she")
        age = ident.get("age", "")
        occ = ident.get("occupation", "")
        base = (
            f"You are {name}, {age}, {occ}. Archetype: {persona.archetype}. "
            f"Speaking style: {persona.speaking_style}. Tonight you are {persona.mood_tonight}. "
            f"You are drawn to: {', '.join(persona.attracts)}. "
            f"You are turned off by: {', '.join(persona.repels)}."
        )
    return "\n\n".join(p for p in (base, about_you(persona), HARD_RULES) if p)


def select_fewshot(persona: PersonaConfig, beat: Beat, k: int = 3,
                   rng: random.Random | None = None) -> list[str]:
    """Sample (not slice) k lines from the beat's band, so successive turns don't
    anchor on the same few examples — fights few-shot mode collapse."""
    band = BAND.get(beat, "neutral")
    pool = list(persona.fewshot.get(band, []))
    if len(pool) <= k:
        return pool
    return (rng or random).sample(pool, k)
