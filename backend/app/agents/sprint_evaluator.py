"""
Unified sprint evaluator agent.

Single-file implementation for sprint exercise evaluation with multimodal
analysis (audio + optional image + text prompt).
"""

import json
from typing import Optional

from agents.schemas import SprintEvaluationResult
from agents.sprint_multimodal_agent import SprintMultimodalAgent
from prompts import get_exercise_prompt, get_sprint_question_label
from helpers.logger import logger
from helpers.question_format_converter import convert_question_to_string


class SprintEvaluator(SprintMultimodalAgent):
    """
    Generic multimodal sprint evaluator for any supported exercise type.

    Usage:
        evaluator = SprintEvaluator("yesAnd", model_name=...)
        result = evaluator.process(...)
    """

    def __init__(self, exercise_key: str, model_name: str = None):
        self.exercise_key = exercise_key
        system_message = get_exercise_prompt(exercise_key, "sprint")
        self.question_label = get_sprint_question_label(exercise_key)

        super().__init__(
            system_message=system_message,
            model_name=model_name,
            agent_type=f"{exercise_key}_sprint_agent",
            response_schema=SprintEvaluationResult,
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
    ) -> str:
        """
        Evaluate a user's spoken sprint response using multimodal Gemini.
        """
        question_text = self._format_question(question_data)
        image_b64 = self._extract_image_base64(question_data)

        prompt_parts = [
            f"**Exercise Type:** {exercise_type}",
            f"**{self.question_label}:** {question_text}",
            f"**User's Spoken Response (transcript):** {transcription if transcription and transcription.strip() else '(No transcript available - analyze audio only)'}",
            "",
            "**Recording Info:**",
            f"- Word Count: {word_count}",
            f"- Duration: {duration_seconds:.1f} seconds",
            "",
            "An audio recording of the user's spoken response is attached.",
            "Please analyze the AUDIO directly to evaluate vocal delivery:",
            "filler words, pacing, tone, confidence, fluency, and energy level.",
            "Do NOT rely solely on the transcript for voice analysis.",
            "For text_feedback, use the exact 4-part HTML structure from the system instructions:",
            "What Landed, The Trap, Level Up, Mindset Shift.",
            "Keep voice_feedback separate and focused only on vocal delivery.",
        ]

        if previous_response:
            prompt_parts.extend([
                "",
                "=== REFINEMENT MODE ===",
                "This is the user's SECOND attempt. Compare with their first attempt:",
                f'**Previous Response:** "{previous_response.get("transcription", "")}"',
                f"**Previous Scores:** Text: {previous_response.get('text_score', 'N/A')}, "
                f"Voice: {previous_response.get('voice_score', 'N/A')}, "
                f"Overall: {previous_response.get('overall_score', 'N/A')}",
                f"**Previous Text Feedback:** {previous_response.get('text_feedback', 'N/A')}",
                f"**Previous Voice Feedback:** {previous_response.get('voice_feedback', 'N/A')}",
                "",
                "Compare the two attempts in detail. Highlight specific improvements or regressions.",
                "Did they address the feedback from the first attempt?",
            ])

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
        """
        Parse the raw Gemini response and reshape it for the frontend.
        """
        parsed = json.loads(raw_json)

        for key in ("text_score", "voice_score", "overall_score"):
            if key in parsed:
                parsed[key] = max(1, min(10, int(parsed[key])))

        breakdown = {}
        try:
            raw_bd = parsed.pop("filler_words_breakdown", "{}")
            if isinstance(raw_bd, str):
                breakdown = json.loads(raw_bd)
            elif isinstance(raw_bd, dict):
                breakdown = raw_bd
        except json.JSONDecodeError:
            breakdown = {}

        parsed["filler_words_detail"] = {
            "total_count": parsed.pop("filler_words_total_count", 0),
            "breakdown": breakdown,
            "frequency_per_minute": parsed.pop("filler_words_frequency_per_minute", 0),
        }

        rc = parsed.get("refinement_comparison")
        if rc in ("null", "None", ""):
            parsed["refinement_comparison"] = None

        return json.dumps(parsed)

    @staticmethod
    def _fallback_response() -> str:
        """Return a safe fallback JSON when the LLM call fails."""
        return json.dumps({
            "text_score": 5,
            "voice_score": 5,
            "overall_score": 5,
            "text_feedback": (
                "<b>✅ What Landed</b><br>You submitted a response, which gives us something to work with."
                "<br><br><b>⚠️ The Trap</b><br>We couldn't analyse this attempt reliably, so there isn't specific coaching yet."
                "<br><br><b>🚀 Level Up</b><br>Try again with a clearer recording and a complete spoken answer."
                "<br><br><b>🧠 Mindset Shift</b><br>A clean retry gives better coaching than guessing from incomplete input."
            ),
            "voice_feedback": "Voice analysis could not be completed.",
            "sample_answer": "Please try again with a clearer recording.",
            "filler_words_detail": {
                "total_count": 0,
                "breakdown": {},
                "frequency_per_minute": 0,
            },
            "improvement_tips": ["Try speaking clearly and at a moderate pace."],
            "pace_wpm": 0,
            "confidence_level": "medium",
            "refinement_comparison": None,
        })
