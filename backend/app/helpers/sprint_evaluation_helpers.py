"""
Sprint Evaluation Helpers

Utility functions for the analyze_sprint_response endpoint.
Handles agent dispatch, question formatting, and result parsing
for sprint (spoken response) exercises.
"""

from agents.sprint_evaluator import SprintEvaluator
from prompts import get_supported_exercise_keys


_SUPPORTED_SPRINT_EXERCISES = get_supported_exercise_keys()


def create_sprint_agent(exercise_type: str, model_name: str = None) -> SprintEvaluator:
    """
    Create a sprint evaluator for the given exercise type.

    Args:
        exercise_type: Exercise identifier (e.g. "yesAnd", "pushPull").
        model_name: Optional model override.

    Returns:
        Configured SprintEvaluator instance.
    """
    if exercise_type not in _SUPPORTED_SPRINT_EXERCISES:
        raise ValueError(f"Unsupported exercise type: {exercise_type}")
    return SprintEvaluator(exercise_key=exercise_type, model_name=model_name)


def validate_sprint_request(body: dict) -> tuple[bool, str]:
    """
    Validate the request body for analyze_sprint_response.

    Returns:
        Tuple of (is_valid, error_message).
    """
    if not body:
        return False, "Invalid JSON body"

    required_fields = [
        "uid",
        "audio_base64",
        "duration_seconds",
        "word_count",
        "question_data",
        "exercise_type",
    ]
    for field in required_fields:
        if field not in body:
            return False, f"Missing required field: {field}"

    try:
        duration_seconds = float(body["duration_seconds"])
        if duration_seconds < 0:
            return False, "duration_seconds must be >= 0"
    except (TypeError, ValueError):
        return False, "duration_seconds must be a number"

    try:
        word_count = int(body["word_count"])
        if word_count < 0:
            return False, "word_count must be >= 0"
    except (TypeError, ValueError):
        return False, "word_count must be an integer"

    question_data = body["question_data"]
    if not isinstance(question_data, list) or len(question_data) == 0:
        return False, "question_data must be a non-empty array"

    for i, item in enumerate(question_data):
        if not isinstance(item, dict):
            return False, f"question_data[{i}] must be an object"

        role = item.get("role")
        content = item.get("content")
        if not isinstance(role, str) or not role.strip():
            return False, f"question_data[{i}].role must be a non-empty string"
        if not isinstance(content, str) or not content.strip():
            return False, f"question_data[{i}].content must be a non-empty string"

    exercise_type = body.get("exercise_type", "")
    if exercise_type not in _SUPPORTED_SPRINT_EXERCISES:
        return False, f"Unsupported exercise type: {exercise_type}"

    return True, ""
