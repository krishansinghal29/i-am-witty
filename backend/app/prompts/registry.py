import random
from pathlib import Path
from typing import Any, Optional

_VERBS: Optional[list[str]] = None

def _get_verbs() -> list[str]:
    global _VERBS
    if _VERBS is None:
        path = Path(__file__).parent.parent / "data" / "verbs.txt"
        _VERBS = path.read_text().splitlines()
    return _VERBS

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


def _extract_location(location_context: Optional[dict]) -> str:
    if not location_context:
        return ""

    country = str(location_context.get("country", "")).strip()
    city = str(location_context.get("city", "")).strip()
    region = str(location_context.get("region", "")).strip()

    if city:
        return city
    if region:
        return region
    return country


def _build_creative_generator_prompt(
    generator_components: dict[str, Any],
    location_context: Optional[dict] = None,
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

    location_instruction = ""
    location = _extract_location(location_context)
    location_probability = float(generator_components.get("location_inclusion_probability", 0.4))
    template = str(generator_components.get("location_instruction_template", ""))

    if location and template and random.random() < location_probability:
        location_instruction = template.format(location=location)

    return f"{base_prompt} {context} {topic_suggestion} {creativity_booster}{location_instruction}"


def _build_archetype_generator_prompt(
    generator_components: dict[str, Any],
    location_context: Optional[dict] = None,
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

    location_instruction = ""
    location = _extract_location(location_context)
    location_probability = float(generator_components.get("location_inclusion_probability", 0.4))
    template = str(generator_components.get("location_instruction_template", ""))

    if location and template and random.random() < location_probability:
        location_instruction = template.format(location=location)

    return f"{base_prompt} {specific_instruction} {constraint}{location_instruction}"


def _build_verb_seed_generator_prompt() -> str:
    verb = random.choice(_get_verbs())
    pronoun = random.choice(["I", "you", "we"])
    return f'Generate a sentence using the verb "{verb}" and the pronoun "{pronoun}".'


def build_generator_prompt(exercise_key: str, location_context: Optional[dict] = None) -> str:
    config = _get_exercise_prompt_config(exercise_key)
    mode = str(config.get("generator", {}).get("mode", "none"))
    generator_components = config.get("prompt_components", {}).get("generator", {})

    if mode == "creative":
        return _build_creative_generator_prompt(generator_components, location_context)
    if mode == "archetype":
        return _build_archetype_generator_prompt(generator_components, location_context)
    if mode == "verb_seed":
        return _build_verb_seed_generator_prompt()

    raise ValueError(f"Exercise '{exercise_key}' does not support text prompt generation")

