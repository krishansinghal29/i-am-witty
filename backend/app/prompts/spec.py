"""Exercise prompt specs and reusable generator prompt strategies."""

from __future__ import annotations

import random
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

GeneratorPromptFactory = Callable[[], str]
TechniquePicker = Callable[[], Optional[dict[str, Any]]]

_WORDS: dict[str, list[str]] = {}


@dataclass(frozen=True)
class ExerciseSpec:
    """Everything the generator and evaluator need for one exercise."""

    key: str
    description: str
    sprint_question_label: str
    response_roles: tuple[str, ...]
    generator_system: str
    generator_user_prompt: GeneratorPromptFactory
    evaluator_system: str
    technique_picker: Optional[TechniquePicker] = None

    def build_generator_prompt(self) -> str:
        return self.generator_user_prompt()

    def pick_technique(self) -> Optional[dict[str, Any]]:
        if self.technique_picker is None:
            return None
        return self.technique_picker()


def _as_options(value: str | Sequence[str], name: str) -> list[str]:
    if isinstance(value, str):
        options = [line.strip() for line in value.splitlines() if line.strip()]
    else:
        options = [str(item).strip() for item in value if str(item).strip()]

    if not options:
        raise ValueError(f"{name} must include at least one option")
    return options


def creative_generator_prompt(
    *,
    prompt_styles: str | Sequence[str],
    contexts: str | Sequence[str],
    topic_suggestions: str | Sequence[str],
    creativity_boosters: str | Sequence[str],
) -> GeneratorPromptFactory:
    styles = _as_options(prompt_styles, "prompt_styles")
    context_options = _as_options(contexts, "contexts")
    topics = _as_options(topic_suggestions, "topic_suggestions")
    boosters = _as_options(creativity_boosters, "creativity_boosters")

    def build() -> str:
        return " ".join(
            [
                random.choice(styles),
                random.choice(context_options),
                random.choice(topics),
                random.choice(boosters),
            ]
        )

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


def _word_list(name: str) -> list[str]:
    words = _WORDS.get(name)
    if words is None:
        path = Path(__file__).parent.parent / "data" / f"{name}.txt"
        words = path.read_text().splitlines()
        _WORDS[name] = words
    return words


def verb_seed_generator_prompt() -> str:
    verb = random.choice(_word_list("verbs"))
    pronoun = random.choice(["I", "you", "we"])
    return f'Generate a sentence using the verb "{verb}" and the pronoun "{pronoun}".'


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
            verb = random.choice(_word_list("verbs"))
            return f'Seed type: verb. Value: "{verb}"'
        if seed_type == "adjective":
            adjective = random.choice(_word_list("adjectives"))
            return f'Seed type: adjective. Value: "{adjective}"'
        if seed_type == "verb_adverb":
            verb = random.choice(_word_list("verbs"))
            adverb = random.choice(_word_list("adverbs"))
            return f'Seed type: verb+adverb. Verb: "{verb}", Adverb: "{adverb}"'
        if seed_type == "vibe":
            subject = _weighted_category_pick(vibe_categories)
            adjective = random.choice(_word_list("adjectives"))
            return f'Seed type: vibe. Subject: "{subject}", Adjective: "{adjective}"'

        subject = _weighted_category_pick(appearance_categories)
        adjective = random.choice(_word_list("adjectives"))
        return f'Seed type: appearance. Subject: "{subject}", Adjective: "{adjective}"'

    return build
