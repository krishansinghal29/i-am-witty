"""Reusable generator prompt strategies."""

from __future__ import annotations

import random
from collections.abc import Sequence
from typing import Any

from app.infrastructure.runtime.prompts.spec import GeneratorPromptFactory
from app.infrastructure.runtime.prompts.word_lists import word_list

# Appended to every word-list seed (verb / adjective / verb+adverb / vibe /
# appearance) so an obscure seed word never leaks an unfamiliar term into the
# generated content the learner has to read.
SEED_SIMPLER_LANGUAGE_NOTE = (
    " If the seed word is uncommon or one many people wouldn't immediately "
    "understand, use a simpler, everyday word with the same meaning so the "
    "result stays easy to understand."
)

# Word lists a creative generator draws its spark word(s) from. They are large
# (8k+ verbs, 17k+ adjectives), so the spark is genuinely different every call —
# that diversity is the content entropy the creative generator otherwise lacks,
# the thing that stops it collapsing onto its in-context examples.
_DEFAULT_SPARK_LISTS: tuple[str, ...] = ("verbs", "adjectives")

# The whole user message for a creative generator: a neutral "go" instruction.
# All the substance (role, rules, examples, format) lives in the system prompt,
# and the spark word appended below supplies the per-call variety — so the user
# turn needs nothing more than this.
_DEFAULT_CREATIVE_ASK = (
    "Generate one new output for this exercise now, strictly following the "
    "system instructions above."
)


def _spark_clause(words: Sequence[str]) -> str:
    """Frame random spark word(s) as loose inspiration — never a constraint.

    The words guarantee a different nudge every call (the entropy the creative
    generator otherwise lacks), while the framing keeps the model free to follow
    the system prompt or invent a different direction entirely.
    """
    quoted = " and ".join(f'"{word}"' for word in words)
    if len(words) == 1:
        lead, evokes, label, pronoun, obscure = (
            "here is a random spark word",
            "whatever it evokes",
            "word",
            "it",
            "if it is obscure",
        )
    else:
        lead, evokes, label, pronoun, obscure = (
            "here are random spark words",
            "whatever they evoke",
            "words",
            "them",
            "if they are obscure",
        )
    return (
        f" For fresh inspiration only, {lead}: {quoted}. Let {evokes} nudge you "
        f"toward an unexpected angle. You do NOT have to use the {label}, reference "
        f"{pronoun}, or stay literal — {obscure}, just use the vibe. Always follow "
        "the system prompt's rules and format above; if a more creative direction "
        "comes to mind, take it."
    )


def creative_generator_prompt(
    *,
    ask: str = _DEFAULT_CREATIVE_ASK,
    spark_lists: Sequence[str] = _DEFAULT_SPARK_LISTS,
    spark_count: int = 1,
) -> GeneratorPromptFactory:
    if not ask.strip():
        raise ValueError("creative generator ask must be non-empty")
    spark_sources = list(spark_lists)
    if not spark_sources:
        raise ValueError("creative generator requires at least one spark list")
    if spark_count < 1:
        raise ValueError("spark_count must be at least 1")

    def build() -> str:
        spark_words = [
            random.choice(word_list(random.choice(spark_sources)))
            for _ in range(spark_count)
        ]
        return ask + _spark_clause(spark_words)

    return build


def archetype_generator_prompt(
    *,
    archetypes: Sequence[dict[str, str]],
    constraint: str,
    spark_lists: Sequence[str] = _DEFAULT_SPARK_LISTS,
    spark_count: int = 1,
) -> GeneratorPromptFactory:
    if not archetypes:
        raise ValueError("archetype generator must include at least one archetype")
    spark_sources = list(spark_lists)
    if not spark_sources:
        raise ValueError("archetype generator requires at least one spark list")
    if spark_count < 1:
        raise ValueError("spark_count must be at least 1")

    def build() -> str:
        archetype = random.choice(list(archetypes))
        archetype_type = archetype.get("type", "")
        instruction = archetype.get("instruction", "")
        # The archetype fixes the frame; the spark gives a fresh angle within it,
        # the same entropy the creative generator gets (only 6 archetypes alone
        # would collapse onto a handful of stock accusations).
        spark_words = [
            random.choice(word_list(random.choice(spark_sources)))
            for _ in range(spark_count)
        ]
        return (
            f"Generate a specific '{archetype_type}' statement. "
            f"Instruction: {instruction} {constraint}"
            + _spark_clause(spark_words)
        )

    return build


def verb_seed_generator_prompt() -> str:
    verb = random.choice(word_list("verbs"))
    pronoun = random.choice(["I", "you", "we"])
    return (
        f'Generate a sentence using the verb "{verb}" and the pronoun "{pronoun}".'
        + SEED_SIMPLER_LANGUAGE_NOTE
    )


# Three de-archaicized lists, rotated so the seed varies the SHAPE of the line
# (an action, a quality, or a concrete object) rather than always handing the
# generator a verb. That shape variety is what keeps relatable everyday lines
# from collapsing onto one mould. Person-description lists (vibe / appearance)
# are deliberately excluded: this drill wants ordinary lines, not lines about
# how someone looks. All three are common/concrete-filtered, so the seed never
# leaks an archaic word the way the raw verb list did ("electioneer", "docket").
_RELATABLE_SEED_LISTS: tuple[tuple[str, str], ...] = (
    ("verbs_common", "verb"),
    ("adjectives_common", "adjective"),
    ("nouns_concrete", "noun"),
)


def relatable_seed_generator_prompt() -> str:
    """Seed an ordinary, relatable line for the (sexual) misinterpretation drill.

    One random word drawn from a rotated common-POS list, plus a pronoun. The
    word is framed as loose inspiration — not a hard constraint — so the
    generator always prioritises a believable line over wedging the seed in.
    """
    list_name, pos = random.choice(_RELATABLE_SEED_LISTS)
    word = random.choice(word_list(list_name))
    pronoun = random.choice(["I", "you", "we"])
    return (
        f'Seed word ({pos}): "{word}". Pronoun to use: "{pronoun}". Let the seed '
        "word loosely inspire the line — use it naturally if it fits, otherwise "
        "just borrow its everyday vibe; never force it."
        + SEED_SIMPLER_LANGUAGE_NOTE
    )


def _weighted_category_pick(categories: Sequence[dict[str, Any]]) -> str:
    if not categories:
        raise ValueError("weighted seed generator categories cannot be empty")
    weights = [category["weight"] for category in categories]
    return random.choices(list(categories), weights=weights, k=1)[0]["name"]


def weighted_seed_generator_prompt(
    *,
    appearance_categories: Sequence[dict[str, Any]],
    vibe_categories: Sequence[dict[str, Any]],
) -> GeneratorPromptFactory:
    def build() -> str:
        seed_type = random.choices(
            ["verb", "adjective", "verb_adverb", "vibe", "appearance"],
            weights=[1, 1, 1, 1, 2],
            k=1,
        )[0]

        if seed_type == "verb":
            verb = random.choice(word_list("verbs"))
            seed_line = f'Seed type: verb. Value: "{verb}"'
        elif seed_type == "adjective":
            adjective = random.choice(word_list("adjectives"))
            seed_line = f'Seed type: adjective. Value: "{adjective}"'
        elif seed_type == "verb_adverb":
            verb = random.choice(word_list("verbs"))
            adverb = random.choice(word_list("adverbs"))
            seed_line = f'Seed type: verb+adverb. Verb: "{verb}", Adverb: "{adverb}"'
        elif seed_type == "vibe":
            subject = _weighted_category_pick(vibe_categories)
            adjective = random.choice(word_list("adjectives"))
            seed_line = f'Seed type: vibe. Subject: "{subject}", Adjective: "{adjective}"'
        else:
            subject = _weighted_category_pick(appearance_categories)
            adjective = random.choice(word_list("adjectives"))
            seed_line = f'Seed type: appearance. Subject: "{subject}", Adjective: "{adjective}"'

        return seed_line + SEED_SIMPLER_LANGUAGE_NOTE

    return build


# Broad "where" buckets the scene generator expands into a specific ordinary
# place. Kept small and abstract on purpose: domain x adjective (or x speaker)
# explodes combinatorially, so variety comes from the multiplication rather than
# a long hardcoded list of named locations.
SCENE_DOMAINS = [
    "at home",
    "in transit",
    "at work",
    "shopping or at a checkout",
    "eating or drinking out",
    "waiting somewhere",
    "a social gathering",
    "outdoors",
    "on the phone or online",
    "at a service counter",
    "at the gym or recreation",
    "running an errand",
]

# Who delivers an "overheard" line spoken to the user.
SCENE_SPEAKERS = [
    "a friend",
    "a partner",
    "a relative",
    "a coworker",
    "a stranger",
    "someone serving you (a waiter, clerk, or barista)",
]


def scene_seed_generator_prompt(
    *,
    appearance_categories: Sequence[dict[str, Any]],
    vibe_categories: Sequence[dict[str, Any]],
    domains: Sequence[str] = SCENE_DOMAINS,
    speakers: Sequence[str] = SCENE_SPEAKERS,
) -> GeneratorPromptFactory:
    """Seed strategy for mundane base-reality scenes (First Unusual Thing).

    Rolls a weighted seed type. The first five mirror the push-pull seeds (so
    they can be dialed to zero); ``object``/``setting``/``overheard`` add the
    scene-specific axes a single verb seed can't reach — a concrete handle to
    tilt, a place, and a conversational line spoken to the user.
    """
    seed_types = [
        ("verb", 2),
        ("adjective", 1),
        ("verb_adverb", 1),
        ("vibe", 1),
        ("appearance", 1),
        ("object", 3),
        ("setting", 3),
        ("overheard", 2),
    ]
    names = [name for name, _ in seed_types]
    weights = [weight for _, weight in seed_types]

    def build() -> str:
        seed_type = random.choices(names, weights=weights, k=1)[0]

        if seed_type == "verb":
            verb = random.choice(word_list("verbs"))
            seed_line = f'Seed type: verb. Value: "{verb}"'
        elif seed_type == "adjective":
            adjective = random.choice(word_list("adjectives"))
            seed_line = f'Seed type: adjective. Value: "{adjective}"'
        elif seed_type == "verb_adverb":
            verb = random.choice(word_list("verbs"))
            adverb = random.choice(word_list("adverbs"))
            seed_line = f'Seed type: verb+adverb. Verb: "{verb}", Adverb: "{adverb}"'
        elif seed_type == "vibe":
            subject = _weighted_category_pick(vibe_categories)
            adjective = random.choice(word_list("adjectives"))
            seed_line = f'Seed type: vibe. Subject: "{subject}", Adjective: "{adjective}"'
        elif seed_type == "appearance":
            subject = _weighted_category_pick(appearance_categories)
            adjective = random.choice(word_list("adjectives"))
            seed_line = f'Seed type: appearance. Subject: "{subject}", Adjective: "{adjective}"'
        elif seed_type == "object":
            noun = random.choice(word_list("nouns_concrete"))
            seed_line = f'Seed type: object. Value: "{noun}"'
            if random.random() < 0.5:
                adjective = random.choice(word_list("adjectives"))
                seed_line += f', Adjective: "{adjective}"'
        elif seed_type == "setting":
            domain = random.choice(list(domains))
            adjective = random.choice(word_list("adjectives"))
            seed_line = f'Seed type: setting. Domain: "{domain}", Flavor adjective: "{adjective}"'
        else:  # overheard
            domain = random.choice(list(domains))
            speaker = random.choice(list(speakers))
            seed_line = f'Seed type: overheard. Domain: "{domain}", Speaker: "{speaker}"'

        return seed_line + SEED_SIMPLER_LANGUAGE_NOTE

    return build
