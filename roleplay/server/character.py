"""Character generation for the roleplay.

Each session rolls one woman: a coherent OBSERVABLE scene (where he sees her,
her style/outfit, build, apparent age, plus a bounded handful of optional
spotlight details and a rare distinguishing mark) and a LATENT backstory
(name, exact age, profession, hometown, hobbies) that surfaces only in
conversation.

A synthesizer LLM writes the plain-language first impression from the OBSERVABLE
facts only — it never sees the latent backstory, so it cannot leak it. The
latent facts are dropped raw into the system prompt for the roleplay model to
reveal in dialogue.

Generation strategy (see also design/backend .../data/README.md): grounded
facts come from curated lists; optional details use count-then-sample so the
description never bloats or goes bare; exactly one "spark" word is offered as
loose inspiration the synthesizer may ignore.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path

from server.prompts import SYNTH_SYSTEM, SYSTEM_PROMPT_TEMPLATE

DATA_DIR = Path(__file__).resolve().parent / "data"


def _lines(name: str) -> list[str]:
    text = (DATA_DIR / name).read_text(encoding="utf-8")
    return [line.strip() for line in text.splitlines() if line.strip()]


SETTINGS = _lines("settings.txt")
BODY_SHAPES = _lines("body_shapes.txt")
SPARK_WORDS = _lines("spark_words.txt")
NAMES = _lines("names.txt")
PROFESSIONS = _lines("professions.txt")
STATES = _lines("states.txt")
HOBBIES = _lines("hobbies.txt")
GARMENTS: dict[str, list[str]] = json.loads(
    (DATA_DIR / "garments.json").read_text(encoding="utf-8")
)
ARCHETYPES = list(GARMENTS.keys())

# Apparent-age bands: (min, max, observable hint shown up front). Exact age latent.
AGE_TIERS: list[tuple[int, int, str]] = [
    (18, 22, "looks like she's in her early twenties"),
    (23, 26, "looks like she's in her mid-twenties"),
    (27, 30, "looks like she's in her late twenties"),
]

# Optional spotlight details. Roll a count, then sample that many — keeps the
# description bounded (never a bloated paragraph, never bare). The synthesizer
# invents the actual content for each.
TOGGLE_POOL = [
    "her shoes",
    "her hairstyle",
    "an accessory she's wearing (bag, jewellery, watch, or sunglasses)",
    "her makeup or how put-together she looks",
    "her nails",
    "the colour or pattern of her outfit",
    "something she's holding or carrying",
    "what she's doing right now",
    "a small detail of the surroundings",
]
TOGGLE_COUNT_WEIGHTS: dict[int, int] = {0: 15, 1: 45, 2: 30, 3: 10}

# Rare, memorable distinguishing mark — fires occasionally, pick one when it does.
DISTINCTIVE_FEATURES = [
    "a small tattoo",
    "a tiny nose stud",
    "glasses",
    "a streak of coloured hair",
    "light freckles",
    "a dimple when she smiles",
    "a beauty spot",
]
DISTINCTIVE_FEATURE_PROB = 0.15

NUM_HOBBIES = 3


@dataclass
class Character:
    # observable (may reach the user via the first impression)
    setting: str
    archetype: str
    outfit: str
    body_shape: str
    age_hint: str
    toggles: list[str]
    distinctive_feature: str | None
    spark_word: str
    # latent (system prompt only; revealed in conversation)
    name: str
    age: int
    profession: str
    hometown: str
    hobbies: list[str]


def roll_character() -> Character:
    """Roll one woman from the curated lists + bounded random detail toggles."""
    archetype = random.choice(ARCHETYPES)
    lo, hi, age_hint = random.choice(AGE_TIERS)

    count = random.choices(
        list(TOGGLE_COUNT_WEIGHTS), weights=list(TOGGLE_COUNT_WEIGHTS.values())
    )[0]
    toggles = random.sample(TOGGLE_POOL, count)

    feature = (
        random.choice(DISTINCTIVE_FEATURES)
        if random.random() < DISTINCTIVE_FEATURE_PROB
        else None
    )

    return Character(
        setting=random.choice(SETTINGS),
        archetype=archetype,
        outfit=random.choice(GARMENTS[archetype]),
        body_shape=random.choice(BODY_SHAPES),
        age_hint=age_hint,
        toggles=toggles,
        distinctive_feature=feature,
        spark_word=random.choice(SPARK_WORDS),
        name=random.choice(NAMES),
        age=random.randint(lo, hi),
        profession=random.choice(PROFESSIONS),
        hometown=random.choice(STATES),
        hobbies=random.sample(HOBBIES, NUM_HOBBIES),
    )


def synth_messages(c: Character) -> list[dict[str, str]]:
    """Build the synthesizer call — OBSERVABLE facts only, never the latent ones."""
    lines = [
        f"Setting: {c.setting}",
        f"Overall style: {c.archetype}",
        f"Main outfit: {c.outfit}",
        f"Build: {c.body_shape}",
        f"Apparent age: {c.age_hint}",
    ]
    if c.toggles:
        lines.append(
            "Also work in these details — invent something specific and natural "
            "for each: " + "; ".join(c.toggles) + "."
        )
    if c.distinctive_feature:
        lines.append(f"She has one distinctive feature: {c.distinctive_feature}.")
    lines.append(
        f'Spark word: "{c.spark_word}" — use it ONLY as loose inspiration if it '
        "fits naturally. You do not have to use it; ignore it if it doesn't fit."
    )
    return [
        {"role": "system", "content": SYNTH_SYSTEM},
        {"role": "user", "content": "\n".join(lines)},
    ]


def fallback_first_impression(c: Character) -> str:
    """Deterministic first impression if the synthesizer call is unavailable."""
    bits = [
        f"You spot her at {c.setting}.",
        f"She's {c.body_shape}, wearing {c.outfit}, and {c.age_hint}.",
    ]
    if c.distinctive_feature:
        bits.append(f"You notice {c.distinctive_feature}.")
    return " ".join(bits)


def build_system_prompt(c: Character, first_impression: str) -> str:
    """Assemble the roleplay system prompt: scene + first-impression + latent block."""
    return SYSTEM_PROMPT_TEMPLATE.format(
        name=c.name,
        setting=c.setting,
        first_impression=first_impression.strip(),
        age=c.age,
        hometown=c.hometown,
        profession=c.profession,
        hobbies=", ".join(c.hobbies),
    )
