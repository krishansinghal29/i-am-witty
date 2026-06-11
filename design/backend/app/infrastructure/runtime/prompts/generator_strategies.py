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


def _as_options(value: str | Sequence[str], name: str) -> list[str]:
    if isinstance(value, str):
        options = [line.strip() for line in value.splitlines() if line.strip()]
    else:
        options = [str(item).strip() for item in value if str(item).strip()]

    if not options:
        raise ValueError(f"{name} must include at least one option")
    return options


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
    prompt_styles: str | Sequence[str],
    contexts: str | Sequence[str],
    topic_suggestions: str | Sequence[str],
    creativity_boosters: str | Sequence[str],
    spark_lists: Sequence[str] = _DEFAULT_SPARK_LISTS,
    spark_count: int = 1,
) -> GeneratorPromptFactory:
    styles = _as_options(prompt_styles, "prompt_styles")
    context_options = _as_options(contexts, "contexts")
    topics = _as_options(topic_suggestions, "topic_suggestions")
    boosters = _as_options(creativity_boosters, "creativity_boosters")
    spark_sources = list(spark_lists)
    if not spark_sources:
        raise ValueError("creative generator requires at least one spark list")
    if spark_count < 1:
        raise ValueError("spark_count must be at least 1")

    def build() -> str:
        instruction = " ".join(
            [
                random.choice(styles),
                random.choice(context_options),
                random.choice(topics),
                random.choice(boosters),
            ]
        )
        spark_words = [
            random.choice(word_list(random.choice(spark_sources)))
            for _ in range(spark_count)
        ]
        return instruction + _spark_clause(spark_words)

    return build


def archetype_generator_prompt(
    *,
    archetypes: Sequence[dict[str, str]],
    constraint: str,
) -> GeneratorPromptFactory:
    if not archetypes:
        raise ValueError("archetype generator must include at least one archetype")

    def build() -> str:
        archetype = random.choice(list(archetypes))
        archetype_type = archetype.get("type", "")
        instruction = archetype.get("instruction", "")
        return (
            f"Generate a specific '{archetype_type}' statement. "
            f"Instruction: {instruction} {constraint}"
        )

    return build


def verb_seed_generator_prompt() -> str:
    verb = random.choice(word_list("verbs"))
    pronoun = random.choice(["I", "you", "we"])
    return (
        f'Generate a sentence using the verb "{verb}" and the pronoun "{pronoun}".'
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
