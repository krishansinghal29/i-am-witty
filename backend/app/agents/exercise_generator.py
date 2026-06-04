"""
Generic exercise question generator.

Each exercise owns an ExerciseSpec. This agent uses the spec's system
prompt, generator prompt factory, response schema, and optional technique
picker without knowing the exercise-specific details.
"""

import json

from llm.factory import create_llm_client
from prompts import get_exercise_spec


# ── Generic generator agent ──────────────────────────────────────

class ExerciseGenerator:
    """
    Generic question generator for any exercise type.

    Usage:
        generator = ExerciseGenerator("ifByXYouMeanY")
        result = generator.process()
    """

    def __init__(self, exercise_key: str, model_name: str = None, llm_client=None):
        self.exercise_key = exercise_key
        self.spec = get_exercise_spec(exercise_key)
        self.llm = llm_client or create_llm_client(model_name)
        self.response_schema = self.spec.generator_response_schema

    def _build_messages(self, prompt: str) -> list[dict]:
        return [
            {"role": "system", "content": self.spec.generator_system},
            {"role": "user", "content": prompt},
        ]

    def process(self) -> str:
        prompt = self.spec.generator_prompt()

        result = self.llm.get_response(
            self._build_messages(prompt), response_schema=self.response_schema
        )
        response_array = result.model_dump()["messages"]

        output: dict = {"question": response_array}

        technique = self.spec.technique_picker() if self.spec.technique_picker else None
        if technique:
            output["technique"] = technique

        return json.dumps(output)
