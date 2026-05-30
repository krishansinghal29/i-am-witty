import random
from pathlib import Path
from typing import Any, Optional

_VERBS: Optional[list[str]] = None
_ADJECTIVES: Optional[list[str]] = None
_ADVERBS: Optional[list[str]] = None


def _get_verbs() -> list[str]:
    global _VERBS
    if _VERBS is None:
        path = Path(__file__).parent.parent / "data" / "verbs.txt"
        _VERBS = path.read_text().splitlines()
    return _VERBS


def _get_adjectives() -> list[str]:
    global _ADJECTIVES
    if _ADJECTIVES is None:
        path = Path(__file__).parent.parent / "data" / "adjectives.txt"
        _ADJECTIVES = path.read_text().splitlines()
    return _ADJECTIVES


def _get_adverbs() -> list[str]:
    global _ADVERBS
    if _ADVERBS is None:
        path = Path(__file__).parent.parent / "data" / "adverbs.txt"
        _ADVERBS = path.read_text().splitlines()
    return _ADVERBS

from prompts.if_by_x import PROMPT_CONFIG as IF_BY_X_PROMPT
from prompts.love_hate import PROMPT_CONFIG as LOVE_HATE_PROMPT
from prompts.misinterpretation import PROMPT_CONFIG as MISINTERPRETATION_PROMPT
from prompts.push_pull import PROMPT_CONFIG as PUSH_PULL_PROMPT
from prompts.question_answer_tease import PROMPT_CONFIG as QUESTION_ANSWER_TEASE_PROMPT
from prompts.vibing import PROMPT_CONFIG as VIBING_PROMPT
from prompts.yes_and import PROMPT_CONFIG as YES_AND_PROMPT

_EXERCISE_PROMPT_CONFIGS: dict[str, dict[str, Any]] = {
    YES_AND_PROMPT["exercise_key"]: YES_AND_PROMPT,
    MISINTERPRETATION_PROMPT["exercise_key"]: MISINTERPRETATION_PROMPT,
    LOVE_HATE_PROMPT["exercise_key"]: LOVE_HATE_PROMPT,
    IF_BY_X_PROMPT["exercise_key"]: IF_BY_X_PROMPT,
    QUESTION_ANSWER_TEASE_PROMPT["exercise_key"]: QUESTION_ANSWER_TEASE_PROMPT,
    VIBING_PROMPT["exercise_key"]: VIBING_PROMPT,
    PUSH_PULL_PROMPT["exercise_key"]: PUSH_PULL_PROMPT,
}


def _get_exercise_prompt_config(exercise_key: str) -> dict[str, Any]:
    config = _EXERCISE_PROMPT_CONFIGS.get(exercise_key)
    if config is None:
        raise ValueError(f"Unsupported exercise key: {exercise_key}")
    return config


def get_exercise_prompt(exercise_key: str, prompt_type: str) -> str:
    config = _get_exercise_prompt_config(exercise_key)
    prompt_text = config.get("system_prompts", {}).get(prompt_type)
    if not prompt_text:
        raise ValueError(
            f"Prompt type '{prompt_type}' not configured for exercise '{exercise_key}'"
        )
    return prompt_text



def get_sprint_question_label(exercise_key: str) -> str:
    config = _get_exercise_prompt_config(exercise_key)
    return config.get("sprint_question_label", "Question/Scenario")


def _build_creative_generator_prompt(
    generator_components: dict[str, Any],
) -> str:
    prompt_styles = generator_components.get("prompt_styles", [])
    contexts = generator_components.get("contexts", [])
    topic_suggestions = generator_components.get("topic_suggestions", [])
    creativity_boosters = generator_components.get("creativity_boosters", [])

    if isinstance(prompt_styles, str):
        prompt_styles = [line.strip() for line in prompt_styles.splitlines() if line.strip()]
    if isinstance(contexts, str):
        contexts = [line.strip() for line in contexts.splitlines() if line.strip()]
    if isinstance(topic_suggestions, str):
        topic_suggestions = [line.strip() for line in topic_suggestions.splitlines() if line.strip()]
    if isinstance(creativity_boosters, str):
        creativity_boosters = [line.strip() for line in creativity_boosters.splitlines() if line.strip()]

    if not (prompt_styles and contexts and topic_suggestions and creativity_boosters):
        raise ValueError("Creative generator config is missing required prompt parts")

    base_prompt = random.choice(prompt_styles)
    context = random.choice(contexts)
    topic_suggestion = random.choice(topic_suggestions)
    creativity_booster = random.choice(creativity_boosters)

    return f"{base_prompt} {context} {topic_suggestion} {creativity_booster}"


def _build_archetype_generator_prompt(
    generator_components: dict[str, Any],
) -> str:
    archetypes = generator_components.get("archetypes", [])
    if isinstance(archetypes, str):
        raise ValueError("Archetype generator config must provide list-style archetypes")
    if not archetypes:
        raise ValueError("Archetype generator config is missing archetypes")

    selected_archetype = random.choice(archetypes)
    archetype_type = selected_archetype.get("type", "")
    instruction = selected_archetype.get("instruction", "")
    constraint = str(generator_components.get("constraint", ""))

    base_prompt = f"Generate a specific '{archetype_type}' statement."
    specific_instruction = f"Instruction: {instruction}"

    return f"{base_prompt} {specific_instruction} {constraint}"


def _build_verb_seed_generator_prompt() -> str:
    verb = random.choice(_get_verbs())
    pronoun = random.choice(["I", "you", "we"])
    return f'Generate a sentence using the verb "{verb}" and the pronoun "{pronoun}".'


def _weighted_category_pick(categories: list[dict]) -> str:
    weights = [c["weight"] for c in categories]
    return random.choices(categories, weights=weights, k=1)[0]["name"]


def _build_weighted_seed_generator_prompt(config: dict) -> str:
    generator_config = config.get("generator", {})
    appearance_categories = generator_config.get("appearance_categories", [])
    vibe_categories = generator_config.get("vibe_categories", [])

    # appearance = 1/3, each of the other four = 1/6
    seed_types = ["verb", "adjective", "verb_adverb", "vibe", "appearance"]
    weights = [1, 1, 1, 1, 2]

    seed_type = random.choices(seed_types, weights=weights, k=1)[0]

    if seed_type == "verb":
        verb = random.choice(_get_verbs())
        return f'Seed type: verb. Value: "{verb}"'
    if seed_type == "adjective":
        adj = random.choice(_get_adjectives())
        return f'Seed type: adjective. Value: "{adj}"'
    if seed_type == "verb_adverb":
        verb = random.choice(_get_verbs())
        adverb = random.choice(_get_adverbs())
        return f'Seed type: verb+adverb. Verb: "{verb}", Adverb: "{adverb}"'
    if seed_type == "vibe":
        subject = _weighted_category_pick(vibe_categories)
        adj = random.choice(_get_adjectives())
        return f'Seed type: vibe. Subject: "{subject}", Adjective: "{adj}"'
    # appearance
    subject = _weighted_category_pick(appearance_categories)
    adj = random.choice(_get_adjectives())
    return f'Seed type: appearance. Subject: "{subject}", Adjective: "{adj}"'


def build_generator_prompt(exercise_key: str) -> str:
    config = _get_exercise_prompt_config(exercise_key)
    mode = str(config.get("generator", {}).get("mode", "none"))
    generator_components = config.get("prompt_components", {}).get("generator", {})

    if mode == "creative":
        return _build_creative_generator_prompt(generator_components)
    if mode == "archetype":
        return _build_archetype_generator_prompt(generator_components)
    if mode == "verb_seed":
        return _build_verb_seed_generator_prompt()
    if mode == "weighted_seed":
        return _build_weighted_seed_generator_prompt(config)

    raise ValueError(f"Exercise '{exercise_key}' does not support text prompt generation")

