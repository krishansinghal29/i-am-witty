import json
import random
import os
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from agents.exercise_generator import ExerciseGenerator
from agents.image_generator import ImageGenerator
from helpers.avatar_utils import get_random_avatar_url
from helpers.location_service import get_location_from_request_headers
from helpers.logger import logger
from helpers.unified_evaluation_helpers import (
    validate_unified_evaluation_request,
    extract_unified_evaluation_params,
    run_evaluation_process,
    parse_llm_response,
    build_response_body,
)

router = APIRouter()

EXERCISE_META_PATH = os.path.join(os.path.dirname(__file__), "..", "constants", "exercise_meta.json")

_SUPPORTED_EXERCISES = {
    "yesAnd", "misinterpretation", "loveHate", "ifByXYouMeanY",
    "questionAnswerTease", "vibing", "pushPull",
}


def _load_exercise_meta() -> dict:
    try:
        if os.path.exists(EXERCISE_META_PATH):
            with open(EXERCISE_META_PATH) as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load exercise_meta.json: {e}")
    return {}


@router.post("/generate_question_v2")
async def generate_question_v2(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

    exercise = body.get("exercise")
    if not exercise or exercise not in _SUPPORTED_EXERCISES:
        return JSONResponse({"error": f"Invalid exercise type: {exercise}"}, status_code=400)

    location_context = get_location_from_request_headers(request.headers)

    try:
        if exercise == "pushPull":
            generator = ImageGenerator()
            question = generator.process()
        else:
            generator = ExerciseGenerator(exercise)
            question = generator.process(location_context=location_context)
    except json.JSONDecodeError as e:
        logger.error(f"Error generating question: {str(e)}")
        return JSONResponse({"error": "Error generating question"}, status_code=500)

    try:
        question_data = json.loads(question) if isinstance(question, str) else question
        avatar_url = get_random_avatar_url()
        if avatar_url:
            question_data["avatar_image_url"] = avatar_url
        question = json.dumps(question_data)
    except Exception as e:
        logger.warning(f"Could not inject avatar URL: {str(e)}")

    return JSONResponse(json.loads(question))


@router.post("/unified_evaluation")
async def unified_evaluation(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

    is_valid, error_msg, _ = validate_unified_evaluation_request(body)
    if not is_valid:
        return JSONResponse({"error": error_msg}, status_code=400)

    params = extract_unified_evaluation_params(body)

    eval_result = run_evaluation_process(
        exercise=params["exercise"],
        question=params["question"],
        response=params["response"],
        model_name=params.get("model_name"),
    )

    if not eval_result.get("success"):
        return JSONResponse({"error": eval_result.get("error", "Evaluation failed")}, status_code=500)

    evaluation_data = parse_llm_response(eval_result["result"], "evaluation")
    return JSONResponse(build_response_body(evaluation_data))


@router.get("/exercise_meta")
async def get_exercise_meta():
    meta = _load_exercise_meta()
    if not meta:
        return JSONResponse({"exercises": []})
    exercises = [{"id": k, **v} for k, v in meta.items()]
    return JSONResponse({"exercises": exercises})


@router.post("/get_recommended_exercise")
async def get_recommended_exercise(request: Request):
    meta = _load_exercise_meta()

    active_exercises = [
        key for key, val in meta.items()
        if isinstance(val, dict) and val.get("status") == "ACTIVE"
    ] if meta else list(_SUPPORTED_EXERCISES)

    if not active_exercises:
        active_exercises = list(_SUPPORTED_EXERCISES)

    recommended = random.choice(active_exercises)
    return JSONResponse({
        "success": True,
        "recommendedExercise": recommended,
        "reason": "Randomly selected from active exercises.",
    })
