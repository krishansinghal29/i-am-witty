# Backend Project Structure

FastAPI (Python) backend for the i-am-witty exercise app. Stateless — no database. Requires `GEMINI_API_KEY` and `OPENAI_API_KEY`.

## Running

```bash
cd backend/app
python3 -m uvicorn main:app --reload --port 8000
```

## Directory Layout

```
backend/
├── .env                          # API keys (GEMINI_API_KEY, OPENAI_API_KEY)
├── .env.example
├── requirements.txt
├── scripts/
│   └── download_assets.py        # One-time script to download avatars/images from GCS
└── app/
    ├── main.py                   # FastAPI app entry point — CORS, router registration, static files
    ├── routers/
    │   ├── exercises.py          # POST /generate_question_v2, /unified_evaluation, /get_recommended_exercise
    │   └── sprint.py             # POST /generate_sprint_question, /analyze_sprint_response
    ├── agents/
    │   ├── base_agent.py         # Abstract base: wraps LLM client, builds message history
    │   ├── schemas.py            # Pydantic output schemas: EvaluationFeedback, SprintEvaluationResult
    │   ├── exercise_generator.py # Generates exercise questions via Gemini structured output
    │   ├── exercise_evaluator.py # Evaluates user text responses for regular exercises
    │   ├── push_pull_evaluator.py# Evaluates push/pull responses (multimodal — uses image few-shots)
    │   ├── image_generator.py    # Picks a random push/pull image from static/images/
    │   ├── sprint_evaluator.py   # Orchestrates sprint evaluation (text + voice)
    │   └── sprint_evaluation_agents/
    │       └── sprint_multimodal_agent.py  # Gemini multimodal agent for voice/audio analysis
    ├── prompts/
    │   └── exercise_prompts/
    │       ├── registry.py       # Maps exercise keys → prompt config dicts
    │       ├── prompt_builder.py # Builds system/user prompts from config
    │       ├── _shared_components.py  # Reusable prompt fragments
    │       ├── yes_and.py
    │       ├── misinterpretation.py
    │       ├── love_hate.py
    │       ├── if_by_x.py
    │       ├── question_answer_tease.py
    │       ├── vibing.py
    │       └── push_pull.py
    ├── llm/
    │   ├── factory.py            # Returns the right LLM client based on model name
    │   ├── gemini_client.py      # google-genai wrapper with structured output support
    │   └── openai_client.py      # OpenAI wrapper
    ├── helpers/
    │   ├── logger.py             # Configured Python logger
    │   ├── location_service.py   # IP → timezone/city lookup for context-aware prompts
    │   ├── avatar_utils.py       # Picks a random avatar from static/avatars/avatars.json
    │   ├── get_image.py          # Returns a random push/pull image from static/images/
    │   ├── question_format_converter.py  # Converts question arrays between formats
    │   ├── openai_tts.py         # OpenAI TTS: text → base64 mp3 (used in sprint questions)
    │   ├── sprint_evaluation_helpers.py  # Helpers for sprint response analysis
    │   └── unified_evaluation_helpers.py # Evaluator class selection + evaluation pipeline
    ├── constants/
    │   ├── llm_models.py         # Model name constants (Gemini, OpenAI)
    │   └── exercise_meta.json    # Exercise metadata: name, title, description, skills, examples
    ├── data/
    │   └── images/
    │       ├── girl1.py          # Base64 image used as few-shot example in PushPullEvaluator
    │       └── girl2.py          # Base64 image used as few-shot example in PushPullEvaluator
    └── static/
        ├── images/               # 169 push/pull JPGs (1.jpg … 169.jpg)
        └── avatars/              # Downloaded avatar images + avatars.json index
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/generate_question_v2` | Generate a question for a given exercise. Returns `question` array + optional `avatar_image_url`. For `pushPull`, embeds a base64 image in the question array. |
| POST | `/unified_evaluation` | Evaluate a user's text response to an exercise question. Returns HTML feedback + sample answer. |
| POST | `/get_recommended_exercise` | Returns a random ACTIVE exercise from `exercise_meta.json`. |
| POST | `/generate_sprint_question` | Generate a sprint question with TTS audio. Returns `question` array + `audio_base64` (mp3) + `speech_text`. |
| POST | `/analyze_sprint_response` | Analyze a sprint recording. Returns scores (text, voice, overall) + feedback + filler word count. |
| GET | `/static/*` | Serve static files (images, avatars). |

## Key Design Decisions

- **No database**: All endpoints are stateless. No Firestore, no SQLite.
- **Gemini for LLM**: All question generation and evaluation uses `google-genai` with structured output (Pydantic schemas).
- **OpenAI for TTS**: Sprint questions are converted to speech via `openai.audio.speech.create` (model `tts-1`).
- **Python 3.9 compatible**: No `match`/`case` statements, no `X | None` type syntax (use `from __future__ import annotations`).
- **Run from `app/` directory**: Imports are flat (`from routers import exercises`), so uvicorn must be launched from `backend/app/`.
