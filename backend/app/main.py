import json
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from agents.exercise_generator import ExerciseGenerator
from helpers.avatar_utils import get_random_avatar_url
from helpers.logger import logger
from helpers.openai_tts import text_to_speech_multi_role
from helpers.sprint_evaluation_helpers import create_sprint_agent, validate_sprint_request

app = FastAPI(title="i-am-witty backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

_SUPPORTED_EXERCISES = {
    "yesAnd", "misinterpretation", "loveHate", "ifByXYouMeanY",
    "questionAnswerTease", "vibing", "pushPull",
}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/generate_sprint_question")
async def generate_sprint_question(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

    exercise = body.get("exercise")
    if not exercise or exercise not in _SUPPORTED_EXERCISES:
        return JSONResponse({"error": f"Invalid exercise type: {exercise}"}, status_code=400)

    try:
        generator = ExerciseGenerator(exercise)
        question_json = generator.process()
    except json.JSONDecodeError as e:
        logger.error(f"Error generating sprint question: {str(e)}")
        return JSONResponse({"error": "Error generating question"}, status_code=500)

    try:
        question_data = json.loads(question_json) if isinstance(question_json, str) else question_json
    except (json.JSONDecodeError, TypeError):
        question_data = question_json

    question_array = question_data.get("question", question_data) if isinstance(question_data, dict) else question_data

    audio_result = None
    if isinstance(question_array, list):
        try:
            audio_result = text_to_speech_multi_role(question_array)
        except Exception as e:
            logger.error(f"TTS generation failed (non-fatal): {str(e)}")

    response_data = {
        "question": question_array,
        "audio_base64": audio_result.get("audio_content_base64") if audio_result else None,
        "content_type": audio_result.get("audio_content_type") if audio_result else None,
        "speech_text": audio_result.get("speech_text") if audio_result else None,
    }

    try:
        avatar_url = get_random_avatar_url()
        if avatar_url:
            response_data["avatar_image_url"] = avatar_url
    except Exception as e:
        logger.warning(f"Could not inject avatar URL: {str(e)}")

    return JSONResponse(response_data)


@app.post("/analyze_sprint_response")
async def analyze_sprint_response(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

    if "uid" not in body:
        body = {**body, "uid": "anonymous"}

    is_valid, error_msg = validate_sprint_request(body)
    if not is_valid:
        return JSONResponse({"error": error_msg}, status_code=400)

    transcription = body.get("transcription", "")
    audio_base64 = body["audio_base64"]
    duration_seconds = float(body.get("duration_seconds", 0))
    word_count = int(body.get("word_count", 0))
    question_data = body["question_data"]
    exercise_type = body["exercise_type"]

    logger.info(f"Analysing sprint response for exercise {exercise_type}")

    try:
        agent = create_sprint_agent(exercise_type)
        raw_result = agent.process(
            transcription=transcription,
            audio_base64=audio_base64,
            duration_seconds=duration_seconds,
            word_count=word_count,
            question_data=question_data,
            exercise_type=exercise_type,
        )
        result = json.loads(raw_result)
        result["success"] = True
        return JSONResponse(result)
    except Exception as e:
        logger.error(f"Error in analyze_sprint_response: {str(e)}")
        return JSONResponse({"error": f"Analysis failed: {str(e)}"}, status_code=500)
