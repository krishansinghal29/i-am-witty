"""
Generic exercise question generator.

Each exercise owns an ExerciseSpec. This agent uses the spec's system
prompt, generator prompt factory, response roles, and optional technique
picker without knowing the exercise-specific details.
"""

import json
from typing import Literal

from pydantic import BaseModel

from agents.base_agent import BaseAgent
from prompts import get_exercise_spec


# ── Dynamic schema factory ────────────────────────────────────────

def _build_response_schema(exercise_key: str, response_roles: tuple[str, ...]):
    """
    Build a Pydantic response schema with role values constrained to the spec.
    """
    if not response_roles:
        raise ValueError(
            f"Exercise '{exercise_key}' must define at least one response role"
        )

    if len(response_roles) == 1:
        RoleLiteral = Literal[response_roles[0]]  # type: ignore[valid-type]
    else:
        RoleLiteral = Literal.__getitem__(response_roles)  # type: ignore[attr-defined]

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
        self.spec = get_exercise_spec(exercise_key)
        self.response_schema = _build_response_schema(
            exercise_key, self.spec.response_roles
        )
        super().__init__(
            self.spec.generator_system,
            agent_type=f"{exercise_key}_generator",
        )

    def process(self) -> str:
        prompt = self.spec.build_generator_prompt()
        llm_messages = self.generate_llm_history(prompt)

        result = self.llm.get_response(
            llm_messages, response_schema=self.response_schema
        )
        response_array = result.model_dump()["messages"]

        # Limit to the expected number of turns (one per response_role)
        expected_count = len(self.spec.response_roles)
        if expected_count > 0:
            response_array = response_array[:expected_count]

        output: dict = {"question": response_array}

        technique = self.spec.pick_technique()
        if technique:
            output["technique"] = technique

        return json.dumps(output)
