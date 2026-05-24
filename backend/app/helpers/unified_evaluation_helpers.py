import json
import time
from helpers.logger import logger
from helpers.question_format_converter import convert_question_to_string
from agents.exercise_evaluator import ExerciseEvaluator
from agents.push_pull_evaluator import PushPullEvaluator


def validate_unified_evaluation_request(body: dict) -> tuple[bool, str, dict]:
    if not body:
        return False, "Invalid JSON body", {}
    for field in ["exercise", "question", "response"]:
        if field not in body:
            return False, f"Missing field: {field}", {}
    return True, "", body


def extract_unified_evaluation_params(body: dict) -> dict:
    return {
        "exercise": body["exercise"],
        "question": body["question"],
        "response": body["response"],
        "model_name": body.get("model_name"),
    }


def get_evaluator_class(exercise: str):
    if exercise == "pushPull":
        return PushPullEvaluator
    _SUPPORTED = {"yesAnd", "vibing", "questionAnswerTease", "loveHate", "misinterpretation", "ifByXYouMeanY"}
    if exercise in _SUPPORTED:
        return lambda model_name=None: ExerciseEvaluator(exercise, model_name=model_name)
    return None


def prepare_context_exercises(recent_exercises: list) -> list:
    return [
        {
            "exerciseKey": ex.get("exerciseKey"),
            "promptGiven": ex.get("promptGiven"),
            "userAnswer": ex.get("userAnswer"),
            "feedback": ex.get("feedback"),
        }
        for ex in recent_exercises
    ]


def parse_llm_response(response_data, response_type: str) -> dict:
    if isinstance(response_data, str):
        try:
            return json.loads(response_data)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse {response_type} as JSON: {response_data}")
            if response_type == "evaluation":
                return {"feedback": str(response_data), "sample_answer": ""}
            return {"success": False, "error": f"Invalid {response_type} data format"}
    return response_data


def run_evaluation_process(exercise: str, question, response: str, model_name: str) -> dict:
    try:
        question_str = convert_question_to_string(question)
        evaluator_class = get_evaluator_class(exercise)
        if not evaluator_class:
            return {"success": False, "error": f"Unsupported exercise type: {exercise}"}

        evaluator = evaluator_class(model_name=model_name)

        if exercise == "pushPull":
            result = evaluator.process(question, response)
        else:
            result = evaluator.process(question_str, response, [])

        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Error in evaluation: {str(e)}")
        return {"success": False, "error": str(e)}


def build_response_body(evaluation_data: dict) -> dict:
    return {
        "success": True,
        "evaluation": {
            "feedback": evaluation_data.get("feedback", ""),
            "sample_answer": evaluation_data.get("sample_answer", ""),
        },
    }
