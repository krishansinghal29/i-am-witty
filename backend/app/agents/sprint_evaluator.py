"""
Unified evaluator agent.

Single-file implementation for exercise evaluation using transcript text.
"""

import json
from typing import Optional

from helpers.logger import logger
from llm.factory import create_llm_client
from prompts import get_exercise_spec

EVALUATOR_TEMPERATURE = 1.0


class SprintEvaluator:
    """
    Generic transcript evaluator for any supported exercise type.

    Usage:
        evaluator = SprintEvaluator("yesAnd", model_name=...)
        result = evaluator.process(...)
    """

    def __init__(self, exercise_key: str, model_name: str = None, llm_client=None):
        self.exercise_key = exercise_key
        self.spec = get_exercise_spec(exercise_key)
        self.llm = llm_client or create_llm_client(model_name)
        self.response_schema = self.spec.evaluator_response_schema

    def _build_messages(self, prompt: str) -> list[dict]:
        return [
            {"role": "system", "content": self.spec.evaluator_system},
            {"role": "user", "content": prompt},
        ]

    def process(
        self,
        transcription: str,
        question_data,
        technique_name: Optional[str] = None,
    ) -> str:
        """
        Evaluate a user's response using its transcript.
        """
        prompt_text = self.spec.evaluator_prompt(
            question_data=question_data,
            transcription=transcription,
            technique_name=technique_name,
        )

        try:
            result = self.llm.get_response(
                self._build_messages(prompt_text),
                response_schema=self.response_schema,
                generation_config={"temperature": EVALUATOR_TEMPERATURE},
            )
            return json.dumps(result.model_dump())
        except Exception as e:
            logger.error(f"Error in SprintEvaluator({self.exercise_key}): {e}")
            return self._fallback_response()

    def _fallback_response(self) -> str:
        """Return the exercise's schema-compatible fallback JSON."""
        return json.dumps(
            self.response_schema.model_validate(
                self.spec.evaluator_fallback()
            ).model_dump()
        )
