"""
Unified evaluator agent.

Single-file implementation for exercise evaluation with multimodal
analysis (audio + optional image + text prompt).
"""

import json
from typing import Optional

from agents.schemas import EvaluationResult
from agents.sprint_multimodal_agent import SprintMultimodalAgent
from prompts import get_exercise_spec
from helpers.logger import logger
from helpers.question_format_converter import convert_question_to_string


class SprintEvaluator(SprintMultimodalAgent):
    """
    Generic multimodal evaluator for any supported exercise type.

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
            response_schema=EvaluationResult,
        )

    def _format_question(self, question_data) -> str:
        """
        Convert structured question data into a readable string for the prompt.

        Handles both:
          - Plain string questions
          - v2 array format: [{role: "She", content: "..."}, ...]

        Image parts (role == "Image") are filtered out; image bytes are
        sent separately as multimodal content.
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

    def _extract_image_base64(self, question_data) -> Optional[str]:
        """
        Extract image base64 data from the structured question array.

        Used by pushPull exercises where the question includes an image
        with role "Image" and content as a base64 data URI.
        """
        if not isinstance(question_data, list):
            return None
        for item in question_data:
            if isinstance(item, dict) and item.get("role") == "Image":
                return item.get("content")
        return None

    def process(
        self,
        transcription: str,
        audio_base64: str,
        duration_seconds: float,
        word_count: int,
        question_data,
        exercise_type: str,
        previous_response: Optional[dict] = None,
        technique_name: Optional[str] = None,
    ) -> str:
        """
        Evaluate a user's spoken response using multimodal Gemini.
        """
        question_text = self._format_question(question_data)
        image_b64 = self._extract_image_base64(question_data)

        prompt_parts = [
            f"**Exercise Type:** {exercise_type}",
            *(
                [f"**Assigned Technique:** {technique_name}"]
                if technique_name else []
            ),
            f"**{self.question_label}:** {question_text}",
            f"**User's Spoken Response (transcript):** {transcription if transcription and transcription.strip() else '(No transcript available - analyze audio only)'}",
            "",
            "**Recording Info:**",
            f"- Word Count: {word_count}",
            f"- Duration: {duration_seconds:.1f} seconds",
            "",
            "An audio recording of the user's spoken response is attached.",
            "Evaluate the content quality using the exercise criteria in the system instructions.",
            "Use the exact 4-part HTML structure for feedback: What Landed, The Trap, Level Up, Mindset Shift.",
        ]

        prompt_text = "\n".join(prompt_parts)

        try:
            raw_result = self.process_multimodal(
                text_prompt=prompt_text,
                audio_base64=audio_base64,
                image_base64=image_b64,
            )
            return self._post_process(raw_result)
        except Exception as e:
            logger.error(f"Error in SprintEvaluator({self.exercise_key}): {e}")
            return self._fallback_response()

    def _post_process(self, raw_json: str) -> str:
        """Parse the raw Gemini response and return it for the frontend."""
        parsed = json.loads(raw_json)
        return json.dumps(parsed)

    @staticmethod
    def _fallback_response() -> str:
        """Return a safe fallback JSON when the LLM call fails."""
        return json.dumps({
            "feedback": (
                "<b>✅ What Landed</b><br>You submitted a response, which gives us something to work with."
                "<br><br><b>⚠️ The Trap</b><br>We couldn't analyse this attempt reliably, so there isn't specific coaching yet."
                "<br><br><b>🚀 Level Up</b><br>Try again with a clearer recording and a complete spoken answer."
                "<br><br><b>🧠 Mindset Shift</b><br>A clean retry gives better coaching than guessing from incomplete input."
            ),
            "sample_answer": "Please try again with a clearer recording.",
        })
