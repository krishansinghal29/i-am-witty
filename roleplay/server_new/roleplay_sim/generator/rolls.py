"""Combinatorial rolls — the meta-strategy core. Pure, seeded, no LLM, no I/O
beyond reading the committed word lists once at import.

Every session rolls one woman from a few independent dimensions instead of being
authored. Three layers:

- BEHAVIORAL: a handful of `axes` (tags) -> a deterministic `Blueprint` (the
  numbers the engine reads). Tags are the single source of truth; the same tags
  are handed to the synthesizer so the prose and the numbers can never drift.
- IDENTITY: split OBSERVABLE (what the eye sees — reaches the first impression)
  vs LATENT (name/age/job/home/hobbies — surface only in dialogue).
- VOICE PALETTE: a small set of seed words (from the curated psycholinguistic
  lists) that flavor her imagery, chosen to match her disposition.

Passing a fixed seed makes a whole session reproducible.
"""
from __future__ import annotations

import json
import os
import random
from dataclasses import dataclass, field
from pathlib import Path

from roleplay_sim.domain.config import Blueprint
from roleplay_sim.domain.enums import Ladder, MoveType

_DATA = Path(__file__).resolve().parent / "data"


def _lines(name: str) -> list[str]:
    text = (_DATA / name).read_text(encoding="utf-8")
    return [ln.strip() for ln in text.splitlines() if ln.strip()]


# --- curated lists ----------------------------------------------------------
NAMES = _lines("names.txt")
PROFESSIONS = _lines("professions.txt")
STATES = _lines("states.txt")
HOBBIES = _lines("hobbies.txt")
SETTINGS = _lines("settings.txt")
BODY_SHAPES = _lines("body_shapes.txt")
SPARK_WORDS = _lines("spark_words.txt")
GARMENTS: dict[str, list[str]] = json.loads((_DATA / "garments.json").read_text(encoding="utf-8"))
STYLES = list(GARMENTS.keys())

# Psycholinguistic seed lists for the voice palette (see data/README provenance).
VIVID = _lines("vivid_words.txt")          # highly picturable
EMOTIVE = _lines("emotive_words.txt")      # high-arousal / charged
ADJ_COMMON = _lines("adjectives_common.txt")
ADV_COMMON = _lines("adverbs_common.txt")

NUM_HOBBIES = 3
PALETTE_SIZE = int(os.environ.get("ROLEPLAY_PALETTE_SIZE", "6"))

# Apparent-age bands: (min, max, observable hint). Exact age stays latent.
AGE_TIERS: list[tuple[int, int, str]] = [
    (18, 22, "looks like she's in her early twenties"),
    (23, 26, "looks like she's in her mid-twenties"),
    (27, 30, "looks like she's in her late twenties"),
    (31, 36, "looks like she's in her early-to-mid thirties"),
]

# Optional spotlight details — roll a count, then sample that many (bounded).
TOGGLE_POOL = [
    "her shoes", "her hairstyle",
    "an accessory she's wearing (bag, jewellery, watch, or sunglasses)",
    "her makeup or how put-together she looks", "her nails",
    "the colour or pattern of her outfit", "something she's holding or carrying",
    "what she's doing right now", "a small detail of the surroundings",
]
TOGGLE_COUNT_WEIGHTS: dict[int, int] = {0: 15, 1: 45, 2: 30, 3: 10}

DISTINCTIVE_FEATURES = [
    "a small tattoo", "a tiny nose stud", "glasses", "a streak of coloured hair",
    "light freckles", "a dimple when she smiles", "a beauty spot",
]
DISTINCTIVE_FEATURE_PROB = 0.15

# --- scene pools (small, inline) --------------------------------------------
TIMES_OF_DAY = ["late morning", "midday", "afternoon", "early evening", "evening", "late night"]
PRESENT_COMPANY = [
    "", "", "alone", "a friend", "two friends", "a small group of friends",
    "a couple of coworkers", "her sister",
]
APPROACH_CONTEXTS = [
    "cold approach", "cold approach", "you caught her eye a moment ago",
    "you ended up next to her in a queue", "she's waiting on something",
]
GOALS = ["open", "number", "number", "instant_date"]
DIFFICULTIES = ["beginner", "intermediate", "intermediate", "advanced"]


# ---------------------------------------------------------------------------
# Behavioral axes -> Blueprint
# ---------------------------------------------------------------------------
# Each axis is rolled to a tag; tags map deterministically to numbers AND are
# described in words to the synthesizer (single source of truth).
VALUE_ORIENTATIONS = ["comfort_driven", "balanced", "value_driven"]
WARMTHS = ["cold", "cool", "neutral", "warm"]
TESTINESS = ["low", "medium", "high"]
CLOSE_DIFFICULTY = ["easy", "medium", "hard"]
ESCALATION_STYLES = ["leads", "passive", "guarded"]
MOTIVATIONS = ["status", "rapport", "novelty", "humor", "depth", "adventure"]


@dataclass
class Axes:
    value_orientation: str
    warmth: str
    testiness: str
    close_difficulty: str
    escalation_style: str
    motivation: str

    def disposition(self) -> str:
        """One-line natural-language summary handed to the synthesizer."""
        return (
            f"{self.warmth} by default, {self.value_orientation.replace('_', '-')}, "
            f"{self.testiness}-testiness, {self.escalation_style} about escalation, "
            f"drawn most to {self.motivation}; she is "
            f"{self.close_difficulty} to win over."
        )


def _band(rng: random.Random, tag: str, table: dict[str, tuple[float, float]]) -> float:
    lo, hi = table[tag]
    return round(rng.uniform(lo, hi), 2)


def roll_axes(rng: random.Random) -> Axes:
    return Axes(
        value_orientation=rng.choice(VALUE_ORIENTATIONS),
        warmth=rng.choice(WARMTHS),
        testiness=rng.choice(TESTINESS),
        close_difficulty=rng.choice(CLOSE_DIFFICULTY),
        escalation_style=rng.choice(ESCALATION_STYLES),
        motivation=rng.choice(MOTIVATIONS),
    )


def blueprint_from_axes(rng: random.Random, axes: Axes) -> Blueprint:
    """Deterministic-ish (seeded) map from disposition tags to engine numbers."""
    vcr = _band(rng, axes.value_orientation, {
        "comfort_driven": (0.22, 0.38), "balanced": (0.42, 0.6), "value_driven": (0.66, 0.82),
    })
    close = _band(rng, axes.close_difficulty, {
        "easy": (45.0, 52.0), "medium": (52.0, 60.0), "hard": (60.0, 68.0),
    })

    # How hard her attraction moves "pop" scales with testiness + value-orientation.
    test_gain = {"low": 1.0, "medium": 1.2, "high": 1.4}[axes.testiness]
    demand = 1.0 + 0.5 * vcr  # value-driven women punish anti-patterns harder
    comfort_eff = round(1.2 - vcr, 2)  # comfort moves do less for value-driven women

    weights: dict[MoveType, float] = {
        MoveType.COCKY_FRAME: round(test_gain, 2),
        MoveType.DISQUALIFY: round(0.9 * test_gain + 0.2, 2),
        MoveType.PUSH_PULL: round(0.9 * test_gain + 0.2, 2),
        MoveType.TEASE: round(0.85 * test_gain + 0.2, 2),
        MoveType.OPEN_PUSH_PULL: round(0.85 * test_gain + 0.2, 2),
        MoveType.SOCIAL_PROOF: round(0.9 + 0.5 * vcr, 2),
        MoveType.PREMISE_OVERT: round(0.9 + 0.4 * vcr, 2),
        MoveType.RAPPORT: comfort_eff,
        MoveType.GENUINE_QUESTION: comfort_eff,
        MoveType.SUPPLICATE: round(1.2 * demand, 2),
        MoveType.SEEK_VALIDATION: round(1.1 * demand, 2),
        MoveType.TRY_HARD: round(1.1 * demand, 2),
    }

    growth = {
        "leads": {Ladder.PHYSICAL: 1.15, Ladder.LOGISTICAL: 1.1, Ladder.VERBAL: 1.1},
        "passive": {Ladder.PHYSICAL: 1.0, Ladder.LOGISTICAL: 1.0, Ladder.VERBAL: 1.0},
        "guarded": {Ladder.PHYSICAL: 0.9, Ladder.LOGISTICAL: 0.85, Ladder.VERBAL: 1.0},
    }[axes.escalation_style]

    return Blueprint(
        value_comfort_ratio=vcr,
        close_threshold=close,
        escalation_style=axes.escalation_style,
        archetype_weights=weights,
        ladder_growth=dict(growth),
    )


# ---------------------------------------------------------------------------
# Identity (observable vs latent)
# ---------------------------------------------------------------------------
@dataclass
class Observable:
    style: str
    outfit: str
    body_shape: str
    age_hint: str
    toggles: list[str]
    distinctive_feature: str | None
    spark_word: str


@dataclass
class Latent:
    name: str
    age: int
    occupation: str
    hometown: str
    hobbies: list[str]


def roll_identity(rng: random.Random) -> tuple[Observable, Latent]:
    style = rng.choice(STYLES)
    lo, hi, age_hint = rng.choice(AGE_TIERS)
    count = rng.choices(list(TOGGLE_COUNT_WEIGHTS), weights=list(TOGGLE_COUNT_WEIGHTS.values()))[0]
    feature = rng.choice(DISTINCTIVE_FEATURES) if rng.random() < DISTINCTIVE_FEATURE_PROB else None
    observable = Observable(
        style=style,
        outfit=rng.choice(GARMENTS[style]),
        body_shape=rng.choice(BODY_SHAPES),
        age_hint=age_hint,
        toggles=rng.sample(TOGGLE_POOL, count),
        distinctive_feature=feature,
        spark_word=rng.choice(SPARK_WORDS),
    )
    latent = Latent(
        name=rng.choice(NAMES),
        age=rng.randint(lo, hi),
        occupation=rng.choice(PROFESSIONS),
        hometown=rng.choice(STATES),
        hobbies=rng.sample(HOBBIES, NUM_HOBBIES),
    )
    return observable, latent


# ---------------------------------------------------------------------------
# Voice palette
# ---------------------------------------------------------------------------
def roll_voice_palette(rng: random.Random, axes: Axes, size: int = PALETTE_SIZE) -> list[str]:
    """Pick a seed list to match disposition, then sample a small palette.

    High-arousal/dramatic dispositions draw charged words; grounded ones draw
    picturable words; dry ones draw common adjectives/adverbs. Mixed in a touch
    of vivid imagery either way so the palette is never one-note.
    """
    if axes.testiness == "high" or axes.motivation in {"adventure", "depth"}:
        primary = EMOTIVE
    elif axes.warmth in {"cold", "cool"} or axes.motivation == "humor":
        primary = ADJ_COMMON + ADV_COMMON
    else:
        primary = VIVID
    pool = primary + VIVID
    k = min(size, len(pool))
    # de-dup while keeping it seeded
    out: list[str] = []
    seen: set[str] = set()
    while len(out) < k and len(seen) < len(pool):
        w = rng.choice(pool)
        if w not in seen:
            seen.add(w)
            out.append(w)
    return out


# ---------------------------------------------------------------------------
# Scene
# ---------------------------------------------------------------------------
@dataclass
class SceneRoll:
    venue: str
    time_of_day: str
    present_company: str
    approach_context: str
    goal: str
    difficulty: str


def roll_scene(rng: random.Random, *, goal: str | None = None) -> SceneRoll:
    return SceneRoll(
        venue=rng.choice(SETTINGS),
        time_of_day=rng.choice(TIMES_OF_DAY),
        present_company=rng.choice(PRESENT_COMPANY),
        approach_context=rng.choice(APPROACH_CONTEXTS),
        goal=goal or rng.choice(GOALS),
        difficulty=rng.choice(DIFFICULTIES),
    )


# ---------------------------------------------------------------------------
# Top-level roll
# ---------------------------------------------------------------------------
@dataclass
class RolledPersona:
    axes: Axes
    blueprint: Blueprint
    observable: Observable
    latent: Latent
    voice_palette: list[str] = field(default_factory=list)

    @property
    def archetype(self) -> str:
        """Short human label (used by the brief author + logs)."""
        return f"{self.axes.warmth}/{self.axes.value_orientation.replace('_', '-')}/{self.axes.motivation}"


@dataclass
class Rolled:
    persona: RolledPersona
    scene: SceneRoll


def roll(seed: int | None = None, *, goal: str | None = None) -> Rolled:
    """Roll a full session. Same seed -> same persona + scene."""
    rng = random.Random(seed)
    axes = roll_axes(rng)
    blueprint = blueprint_from_axes(rng, axes)
    observable, latent = roll_identity(rng)
    palette = roll_voice_palette(rng, axes)
    scene = roll_scene(rng, goal=goal)
    persona = RolledPersona(
        axes=axes, blueprint=blueprint, observable=observable,
        latent=latent, voice_palette=palette,
    )
    return Rolled(persona=persona, scene=scene)
