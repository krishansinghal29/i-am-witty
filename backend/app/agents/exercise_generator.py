"""
Generic exercise question generator.

Replaces the per-exercise generator files (if_by_x_generator_v2.py,
love_hate_generator_v2.py, etc.) with a single parameterised class.

Each exercise defines its generator response schema in prompt config
(via `generator.response_roles`), and this class builds the Pydantic
model dynamically at init time.
"""

import json
from typing import Literal, Optional

from pydantic import BaseModel, RootModel

from agents.base_agent import BaseAgent
from prompts.exercise_prompts import build_generator_prompt, get_exercise_prompt
from prompts.exercise_prompts.registry import _get_exercise_prompt_config


# ── Dynamic schema factory ────────────────────────────────────────

def _build_response_schema(exercise_key: str):
    """
    Build a Pydantic response schema from the exercise prompt config.

    The config's `generator.response_roles` is a list like:
        [{"role": "She"}]  or  [{"role": "You"}, {"role": "She"}]

    This creates a Pydantic RootModel[list[_Message]] where _Message
    has a `role` field constrained to the listed role literals.
    """
    config = _get_exercise_prompt_config(exercise_key)
    roles_config = config.get("generator", {}).get("response_roles", [])

    if not roles_config:
        raise ValueError(
            f"Exercise '{exercise_key}' generator config must define "
            f"'response_roles' (e.g. [{{'role': 'She'}}])"
        )

    # Collect all role strings
    role_literals = tuple(r["role"] for r in roles_config)

    # Create the Literal type for roles
    if len(role_literals) == 1:
        RoleLiteral = Literal[role_literals[0]]  # type: ignore[valid-type]
    else:
        RoleLiteral = Literal[role_literals]  # type: ignore[valid-type]

    # Create the message model dynamically
    MessageModel = type(
        f"_{exercise_key}_Message",
        (BaseModel,),
        {
            "__annotations__": {"role": RoleLiteral, "content": str},
        },
    )

    # Create the root model (list of messages)
    ResponseModel = type(
        f"{exercise_key}_GeneratorResponse",
        (RootModel,),
        {"__annotations__": {"root": list[MessageModel]}},
    )

    return ResponseModel


# ── Generic generator agent ──────────────────────────────────────

class ExerciseGenerator(BaseAgent):
    """
    Generic question generator for any exercise type.

    Usage:
        generator = ExerciseGenerator("ifByXYouMeanY")
        result = generator.process(location_context=...)
    """

    def __init__(self, exercise_key: str):
        self.exercise_key = exercise_key
        system_message = get_exercise_prompt(exercise_key, "generator")
        self.response_schema = _build_response_schema(exercise_key)
        super().__init__(system_message, agent_type=f"{exercise_key}_generator")

    def process(self, location_context: Optional[dict] = None) -> str:
        prompt = build_generator_prompt(self.exercise_key, location_context)
        llm_messages = self.generate_llm_history(prompt)

        result = self.llm.get_response(
            llm_messages, response_schema=self.response_schema
        )
        response_array = result.model_dump()

        # Limit to the expected number of turns (one per response_role)
        config = _get_exercise_prompt_config(self.exercise_key)
        expected_count = len(config.get("generator", {}).get("response_roles", []))
        if expected_count > 0:
            response_array = response_array[:expected_count]

        return json.dumps({"question": response_array})
