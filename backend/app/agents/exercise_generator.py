"""
Generic exercise question generator.

Replaces the per-exercise generator files (if_by_x_generator_v2.py,
love_hate_generator_v2.py, etc.) with a single parameterised class.

Each exercise defines its generator response schema in prompt config
(via `generator.response_roles`), and this class builds the Pydantic
model dynamically at init time.
"""

import json
from typing import Literal

from pydantic import BaseModel

from agents.base_agent import BaseAgent
from prompts import build_generator_prompt, get_exercise_prompt
from prompts.registry import _get_exercise_prompt_config, get_technique_for_exercise


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

    # Wrap in an object — OpenAI structured output requires type: "object" at root
    ResponseModel = type(
        f"{exercise_key}_GeneratorResponse",
        (BaseModel,),
        {"__annotations__": {"messages": list[MessageModel]}},
    )

    return ResponseModel


# ── Generic generator agent ──────────────────────────────────────

class ExerciseGenerator(BaseAgent):
    """
    Generic question generator for any exercise type.

    Usage:
        generator = ExerciseGenerator("ifByXYouMeanY")
        result = generator.process()
    """

    def __init__(self, exercise_key: str):
        self.exercise_key = exercise_key
        system_message = get_exercise_prompt(exercise_key, "generator")
        self.response_schema = _build_response_schema(exercise_key)
        super().__init__(system_message, agent_type=f"{exercise_key}_generator")

    def process(self) -> str:
        prompt = build_generator_prompt(self.exercise_key)
        llm_messages = self.generate_llm_history(prompt)

        result = self.llm.get_response(
            llm_messages, response_schema=self.response_schema
        )
        response_array = result.model_dump()["messages"]

        # Limit to the expected number of turns (one per response_role)
        config = _get_exercise_prompt_config(self.exercise_key)
        expected_count = len(config.get("generator", {}).get("response_roles", []))
        if expected_count > 0:
            response_array = response_array[:expected_count]

        output: dict = {"question": response_array}

        technique = get_technique_for_exercise(self.exercise_key)
        if technique:
            output["technique"] = technique

        return json.dumps(output)
