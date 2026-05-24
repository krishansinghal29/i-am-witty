"""
Generic exercise evaluator agent.

Replaces the per-exercise evaluator files (yes_and_with_past_context_evaluator.py,
love_hate_with_past_context_evaluator.py, etc.) with a single parameterised class.

Note: PushPullEvaluator has unique image-handling logic and few-shot examples,
so it is kept as a separate class (not replaced by this generic).
"""

import json

from agents.base_agent import BaseAgent
from agents.schemas import EvaluationFeedback
from prompts.exercise_prompts import get_exercise_prompt, get_message_key
from helpers.logger import logger


class ExerciseEvaluator(BaseAgent):
    """
    Generic text-based evaluator for any exercise type.

    The only differences between per-exercise evaluators were:
      - EXERCISE_KEY
      - class name / agent_type string

    Usage:
        evaluator = ExerciseEvaluator("yesAnd", model_name=...)
        result = evaluator.process(question, response, recent_exercises)
    """

    def __init__(self, exercise_key: str, model_name: str = None):
        self.exercise_key = exercise_key
        system_message = get_exercise_prompt(exercise_key, "evaluator")

        self.response_schema = EvaluationFeedback
        self.message_key = get_message_key(exercise_key, "evaluator")

        super().__init__(
            system_message,
            model_name=model_name,
            agent_type=f"{exercise_key}_evaluator",
        )

    def process(
        self, question: str, response: str, recent_exercises: list = None
    ) -> str:
        message = {
            self.message_key: question,
            "response": response,
            "recent_exercises": recent_exercises or [],
        }

        llm_messages = self.generate_llm_history(json.dumps(message))

        try:
            result = self.llm.get_response(
                llm_messages, response_schema=self.response_schema
            )
            return result.model_dump_json()
        except Exception as e:
            logger.error(f"Error in ExerciseEvaluator({self.exercise_key}): {e}")
            return json.dumps(
                {
                    "feedback": "I encountered an issue processing your response. Please try again.",
                    "sample_answer": "Let's try a different approach to this exercise.",
                }
            )
