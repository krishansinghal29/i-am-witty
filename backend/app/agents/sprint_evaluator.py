"""
Unified evaluator agent.

Single-file implementation for exercise evaluation using transcript text.
"""

import json
from typing import Optional

from agents.base_agent import BaseAgent
from agents.schemas import EvaluationResult
from prompts import get_exercise_spec
from helpers.logger import logger
from helpers.question_format_converter import convert_question_to_string

EVALUATOR_TEMPERATURE = 1.0


class SprintEvaluator(BaseAgent):
    """
    Generic transcript evaluator for any supported exercise type.

    Usage:
        evaluator = SprintEvaluator("yesAnd", model_name=...)
        result = evaluator.process(...)
    """

    def __init__(self, exercise_key: str, model_name: str = None):
        self.exercise_key = exercise_key
        self.spec = get_exercise_spec(exercise_key)
        self.question_label = self.spec.sprint_question_label

        super().__init__(
            system_message=self.spec.evaluator_system,
            model_name=model_name,
            agent_type=f"{exercise_key}_evaluator",
        )
        self.response_schema = EvaluationResult

    def _format_question(self, question_data) -> str:
        """
        Convert structured question data into a readable string for the prompt.

        Handles both:
          - Plain string questions
          - v2 array format: [{role: "She", content: "..."}, ...]

        Image parts (role == "Image") are skipped because sprint evaluation
        is transcript-only.
        """
        if isinstance(question_data, list):
            parts = []
            for item in question_data:
                if isinstance(item, dict):
                    role = item.get("role", "")
                    content = item.get("content", "")
                    if role == "Image":
                        continue
                    if role and content:
                        parts.append(f"{role}: {content}")
                    elif content:
                        parts.append(content)
            return "\n".join(parts) if parts else ""
        return convert_question_to_string(question_data)

    def process(
        self,
        transcription: str,
        question_data,
        technique_name: Optional[str] = None,
    ) -> str:
        """
        Evaluate a user's response using its transcript.
        """
        question_text = self._format_question(question_data)
        transcript_text = transcription.strip()

        prompt_parts = [
            f"**Exercise Type:** {self.exercise_key}",
            *(
                [f"**Assigned Technique:** {technique_name}"]
                if technique_name else []
            ),
            f"**{self.question_label}:** {question_text}",
            f"**User's Response Transcript:** {transcript_text}",
            "",
            "Evaluate only the response content available in the transcript.",
            "Do not assess audio quality, vocal delivery, tone, pacing, or confidence.",
            "Use the exact 4-part HTML structure for feedback: What Landed, The Trap, Level Up, Mindset Shift.",
        ]

        prompt_text = "\n".join(prompt_parts)

        try:
            raw_result = self.llm.get_response(
                self.build_messages(prompt_text),
                response_schema=self.response_schema,
                generation_config={"temperature": EVALUATOR_TEMPERATURE},
            )
            if hasattr(raw_result, "model_dump"):
                return json.dumps(raw_result.model_dump())
            return json.dumps(json.loads(raw_result))
        except Exception as e:
            logger.error(f"Error in SprintEvaluator({self.exercise_key}): {e}")
            return self._fallback_response()

    @staticmethod
    def _fallback_response() -> str:
        """Return a safe fallback JSON when the LLM call fails."""
        return json.dumps({
            "feedback": (
                "<b>✅ What Landed</b><br>You submitted a response, which gives us something to work with."
                "<br><br><b>⚠️ The Trap</b><br>We couldn't analyse this attempt reliably, so there isn't specific coaching yet."
                "<br><br><b>🚀 Level Up</b><br>Try again with a complete response transcript."
                "<br><br><b>🧠 Mindset Shift</b><br>A clean retry gives better coaching than guessing from incomplete text."
            ),
            "sample_answer": "Please try again with a complete response transcript.",
        })
