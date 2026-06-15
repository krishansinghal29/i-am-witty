"""Roleplay character generator.

Two stages, mirroring the exercise generators (Python builds a payload ->
LLM renders it):

  Phase 1  build_character()  -> CharacterSheet    (pure Python, deterministic)
  Phase 2  render_character() -> RenderedCharacter (one LLM call: persona + appearance)

Each attribute is produced with the strategy that fits its value space:

  NUM      random number in a range            (age, height)
  ENUM     pick from a curated list, weighted   (eye colour, relationship, looking_for)
  SCALE    sample a 1-5 point on a bipolar axis (Big Five, directness)
  SEED     (subject, adjective) the LLM renders (fashion, niche interest, dealbreaker)
  DERIVE   computed from another attribute      (introversion <- extraversion)

Every dimension is sampled independently for maximum variety; the LLM render
step is what ties them into a believable, coherent person. The only links kept
are DERIVE (a single source of truth, e.g. introversion from extraversion, so
contradictions can't occur) and the scenario's setting (conditioned on the
relationship so the scene stays plausible) — neither reduces variety.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass

from app.infrastructure.runtime.prompts.output_schemas import RenderedCharacter
from app.infrastructure.runtime.prompts.push_pull import APPEARANCE_SEED_CATEGORIES
from app.infrastructure.runtime.prompts.word_lists import word_list
from app.ports.integrations.llm_provider import LlmProvider

# The generator favours variety, matching the engine's generation temperature.
_GENERATION_TEMPERATURE = 1.0

# ── Trait model ──────────────────────────────────────────────────

# Big Five factors (emotional_stability = reverse of neuroticism; higher = calmer).
BIG_FIVE = (
    "openness",
    "conscientiousness",
    "extraversion",
    "agreeableness",
    "emotional_stability",
)

# 1-5 level -> human phrase. We translate scales into words HERE, before the
# LLM ever sees them, because models render "fairly reserved" far better than "E=2".
DESCRIPTORS = {
    "openness":            ["very routine-bound", "prefers the familiar", "fairly open", "curious", "endlessly curious"],
    "conscientiousness":   ["very spontaneous", "easygoing", "balanced", "organised", "highly disciplined"],
    "extraversion":        ["very reserved", "fairly reserved", "an ambivert", "outgoing", "very outgoing"],
    "agreeableness":       ["prickly and guarded", "reserved", "politely warm", "warm", "very warm and generous"],
    "emotional_stability": ["highly strung", "sensitive", "even-keeled", "calm", "unflappable"],
    "confidence":          ["timid", "a little unsure of herself", "quietly self-assured", "confident", "very self-assured"],
    "directness":          ["very indirect", "drops hints", "balanced", "fairly direct", "blunt"],
    "sincerity":           ["relentlessly teasing", "playful", "balanced", "sincere", "earnest"],
    "flirtatiousness":     ["not flirtatious at all", "guarded", "subtly warm", "flirtatious", "openly flirtatious"],
}

# ── Curated value pools (independent ENUM / NUM) ─────────────────

AGE_RANGE = (19, 38)
HEIGHT_RANGE = (150, 170)

BUILDS = ["petite", "slim", "athletic", "tall and lean", "curvy", "average build"]
HAIR_COLORS = [
    "jet black", "dark brown", "chestnut", "auburn", "copper red",
    "honey blonde", "platinum blonde", "ash brown", "dyed pastel", "streaked with colour",
]
HAIR_STYLES = [
    "a pixie cut", "a sharp bob", "shoulder-length and loose", "long waves",
    "tight curls", "a high ponytail", "box braids", "an undercut", "messy and tied up",
]
EYE_COLORS = ["brown", "dark brown", "hazel", "green", "grey", "blue"]
# Mostly None on purpose — most people have no single distinguishing feature.
FEATURES_SPARSE = [None, None, None, None, "glasses", "a small tattoo", "freckles", "a nose ring", "dimples"]

HUMOR_TYPES = ["dry", "sarcastic", "goofy", "witty", "deadpan", "none"]
HUMOR_WEIGHTS = [3, 3, 3, 3, 2, 1]  # "none" is rarer

LOOKING_FOR = ["something casual", "something serious", "not sure, open to where it goes"]

# One flat hobby pool — pick a few, no bucketing.
HOBBIES = [
    "reading", "poetry", "museums", "secondhand bookshops", "tea ceremonies", "crosswords",
    "weightlifting", "hiking", "group fitness classes", "meal prep", "trail running", "rock climbing",
    "painting", "live gigs", "thrifting", "film photography", "journaling", "ceramics",
    "running", "wine tasting", "podcasts", "travel", "pilates", "cooking", "gaming", "baking",
    "houseplants", "knitting", "dancing", "brunch", "music festivals", "karaoke",
    "volunteering", "yoga", "gardening", "book clubs", "documentaries",
]

RELATIONSHIP_TO_USER = [
    "a stranger",
    "a dating-app match",
    "a friend of a friend",
    "a coworker",
    "a classmate",
    "someone you're reconnecting with",
]
# Setting is conditioned on the relationship so the scene stays plausible.
SETTINGS_BY_RELATIONSHIP = {
    "a stranger": ["a coffee shop", "a bookstore", "a quiet bar", "a train platform"],
    "a dating-app match": ["a first-date wine bar", "a coffee shop", "a walk in the park"],
    "a friend of a friend": ["a house party", "a mutual friend's barbecue", "a birthday dinner"],
    "a coworker": ["the office kitchen", "after-work drinks", "a work offsite"],
    "a classmate": ["the back of a lecture hall", "a study group", "a campus café"],
    "someone you're reconnecting with": ["a reunion", "a chance run-in on the street", "a café you both used to go to"],
}
WHO_INITIATED = [
    "she struck up the conversation",
    "you struck up the conversation",
    "it started mutually",
]
GROUP = ["one-on-one", "in a small group"]

# ── Sheet structures ─────────────────────────────────────────────


@dataclass
class Hair:
    color: str
    style: str


@dataclass
class Physical:
    height_cm: int
    build: str
    hair: Hair
    eyes: str
    features: str | None
    fashion: list[tuple[str, str]]  # SEED pairs the LLM renders


@dataclass
class CharacterSheet:
    big_five: dict[str, int]
    confidence: int
    age: int
    derived: dict[str, int]
    physical: Physical
    interests: dict  # hobbies: list[str], quirk: (subject, adjective)
    communication: dict  # humor: str, directness/sincerity/flirtatiousness: int
    values: dict  # looking_for: str, dealbreaker: (subject, adjective)
    scenario: dict


# ── Strategy primitives ──────────────────────────────────────────


def _num(rng: random.Random, lo: int, hi: int) -> int:
    return rng.randint(lo, hi)


def _pick(rng: random.Random, options, weights=None):
    return rng.choices(list(options), weights=weights, k=1)[0]


def _level(rng: random.Random) -> int:
    """Sample a 1-5 trait level uniformly (independent — maximum variety)."""
    return rng.randint(1, 5)


def _fashion_seeds(rng: random.Random, count: int) -> list[tuple[str, str]]:
    """SEEDS: `count` distinct clothing subjects, each with a random adjective
    (the push-pull strategy — the LLM renders each into a concrete worn detail)."""
    cats = list(APPEARANCE_SEED_CATEGORIES)
    weights = [c["weight"] for c in cats]
    seeds: list[tuple[str, str]] = []
    for _ in range(min(count, len(cats))):
        idx = rng.choices(range(len(cats)), weights=weights, k=1)[0]
        subject = cats.pop(idx)["name"]
        weights.pop(idx)
        seeds.append((subject, _pick(rng, word_list("adjectives"))))
    return seeds


# ── Phase 1: build the sheet (pure Python) ───────────────────────


def build_character(rng_seed: int | None = None) -> CharacterSheet:
    rng = random.Random(rng_seed)

    # CORE — every trait sampled independently.
    big_five = {trait: _level(rng) for trait in BIG_FIVE}
    confidence = _level(rng)
    age = _num(rng, *AGE_RANGE)

    # DERIVE — implied traits, so contradictions can't occur.
    derived = {
        "introversion": 6 - big_five["extraversion"],
        "warmth": big_five["agreeableness"],
        "curiosity": big_five["openness"],
        "talkativeness": big_five["extraversion"],
        "social_life": big_five["extraversion"],
        "adventurousness": big_five["openness"],
    }

    # SURFACE — physical.
    physical = Physical(
        height_cm=_num(rng, *HEIGHT_RANGE),
        build=_pick(rng, BUILDS),
        hair=Hair(color=_pick(rng, HAIR_COLORS), style=_pick(rng, HAIR_STYLES)),
        eyes=_pick(rng, EYE_COLORS),
        features=_pick(rng, FEATURES_SPARSE),
        fashion=_fashion_seeds(rng, _num(rng, 2, 3)),
    )

    # SURFACE — interests (flat pool) + a SEED niche interest.
    interests = {
        "hobbies": rng.sample(HOBBIES, _num(rng, 2, 3)),
        "quirk": ("niche interest", _pick(rng, word_list("adjectives"))),
    }

    # SURFACE — communication.
    communication = {
        "humor": _pick(rng, HUMOR_TYPES, HUMOR_WEIGHTS),
        "directness": _level(rng),
        "sincerity": _level(rng),
        "flirtatiousness": _level(rng),
    }

    # VALUES — what she wants + a SEED dealbreaker.
    values = {
        "looking_for": _pick(rng, LOOKING_FOR),
        "dealbreaker": ("a trait she can't stand in people", _pick(rng, word_list("adjectives"))),
    }

    # SCENARIO — relationship drives the rest of the scene.
    relationship = _pick(rng, RELATIONSHIP_TO_USER)
    scenario = {
        "relationship_to_user": relationship,
        "setting": _pick(rng, SETTINGS_BY_RELATIONSHIP[relationship]),
        "who_initiated": _pick(rng, WHO_INITIATED),
        "group": _pick(rng, GROUP),
    }

    return CharacterSheet(
        big_five=big_five,
        confidence=confidence,
        age=age,
        derived=derived,
        physical=physical,
        interests=interests,
        communication=communication,
        values=values,
        scenario=scenario,
    )


# ── Phase 2: render the sheet (one LLM call) ─────────────────────


def _descriptor(trait: str, level: int) -> str:
    return DESCRIPTORS[trait][level - 1]


def to_render_payload(sheet: CharacterSheet) -> dict:
    """Shape the sheet for the LLM: facts literal, scales -> words, seeds raw."""
    bf = sheet.big_five
    facts = {
        "age": sheet.age,
        "height_cm": sheet.physical.height_cm,
        "build": sheet.physical.build,
        "hair": {"color": sheet.physical.hair.color, "style": sheet.physical.hair.style},
        "eyes": sheet.physical.eyes,
    }
    if sheet.physical.features:
        facts["distinguishing_feature"] = sheet.physical.features

    return {
        "facts": facts,
        "personality": {
            "curiosity": _descriptor("openness", bf["openness"]),
            "discipline": _descriptor("conscientiousness", bf["conscientiousness"]),
            "outgoingness": _descriptor("extraversion", bf["extraversion"]),
            "warmth": _descriptor("agreeableness", bf["agreeableness"]),
            "temperament": _descriptor("emotional_stability", bf["emotional_stability"]),
            "confidence": _descriptor("confidence", sheet.confidence),
        },
        "communication": {
            "humor": sheet.communication["humor"],
            "directness": _descriptor("directness", sheet.communication["directness"]),
            "sincerity": _descriptor("sincerity", sheet.communication["sincerity"]),
            "flirtatiousness": _descriptor("flirtatiousness", sheet.communication["flirtatiousness"]),
        },
        "interests": sheet.interests["hobbies"],
        "looking_for": sheet.values["looking_for"],
        "render_these": {
            "fashion": [list(pair) for pair in sheet.physical.fashion],
            "niche_interest": list(sheet.interests["quirk"]),
            "dealbreaker": list(sheet.values["dealbreaker"]),
        },
        "scenario": sheet.scenario,
    }


GENERATOR_SYSTEM = """You are given a structured character sheet describing a woman for a conversation-practice roleplay. Turn it into a believable, specific person, inferring a coherent overall identity (background, profession, the kind of person she is) that ties the traits together naturally.

Produce exactly two fields:
- persona: who she is — her personality, background, interests, what she's looking for, and the scenario (where this is happening and your relationship to her) woven into a natural, flowing description. Write her as a real, particular person, not a list of traits.
- appearance: how she looks right now — her physical features and what she's wearing.

How to use the sheet:
- "facts" are fixed. Honor every value exactly (age, height, hair, eyes, build).
- "personality" and "communication" describe how she comes across. Express them through specifics and behavior — do NOT restate the labels.
- "interests", "looking_for", and "scenario" are context to weave in naturally.
- "render_these" are SEEDS, not finished details. Each is a [subject, adjective] pair. Invent ONE concrete, specific detail for each and work it in — never output the raw pair.
    - fashion: each pair is one clothing or accessory item and its character. Turn it into a specific worn detail.
    - niche_interest: a particular hobby or obsession flavored by the adjective.
    - dealbreaker: a kind of person or behavior she can't stand.
    - The adjectives are reference seeds for inspiration, not words to reuse. If one is obscure, archaic, technical, or just complex, do NOT use it literally — render the plain, everyday quality or mood it evokes instead.

Keep both fields concise — a short paragraph each. Write in plain, everyday language; concrete and specific, never generic."""


async def render_character(
    sheet: CharacterSheet,
    llm: LlmProvider,
    *,
    model: str | None = None,
    temperature: float = _GENERATION_TEMPERATURE,
) -> RenderedCharacter:
    return await llm.complete_structured(
        messages=[
            {"role": "system", "content": GENERATOR_SYSTEM},
            {"role": "user", "content": json.dumps(to_render_payload(sheet), indent=2)},
        ],
        response_model=RenderedCharacter,
        temperature=temperature,
        model=model,
    )


async def generate_character(
    llm: LlmProvider,
    *,
    rng_seed: int | None = None,
    model: str | None = None,
    temperature: float = _GENERATION_TEMPERATURE,
) -> RenderedCharacter:
    """Build a sheet and render it into persona + appearance."""
    sheet = build_character(rng_seed)
    return await render_character(sheet, llm, model=model, temperature=temperature)
