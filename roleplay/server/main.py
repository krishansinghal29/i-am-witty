"""Roleplay prototype proxy.

A thin, latency-first proxy that powers the standalone roleplay coach in
``roleplay/web``. It deliberately stays *outside* the core app: it never imports
the DB / auth / HTTP stack. It only:

  * mints short-lived Deepgram tokens (so the browser can stream mic audio),
  * generates a push-pull scenario using the **real** production prompt bundle
    (imported from ``design/backend``), so questions match production exactly,
  * runs a *compact* roleplay evaluator (reuses the production criteria, but
    returns 1-2 speakable lines instead of long HTML), and
  * proxies ElevenLabs streaming TTS (with an in-memory cache for the static
    coach lines, which are spoken on every session).

Run it with the backend venv so the prompt bundle + litellm are importable::

    ./run.sh        # from roleplay/
"""

from __future__ import annotations

import hashlib
import logging
import os
import sys
from pathlib import Path
from typing import Literal

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

logger = logging.getLogger("roleplay")
logging.basicConfig(level=logging.INFO)

# --- paths -----------------------------------------------------------------
ROLEPLAY_DIR = Path(__file__).resolve().parent.parent          # .../roleplay
REPO_DIR = ROLEPLAY_DIR.parent                                 # .../i-am-witty
BACKEND_DIR = REPO_DIR / "design" / "backend"                  # holds prompt bundle + .env
WEB_DIR = ROLEPLAY_DIR / "web"

# --- env: backend keys first, then roleplay-local ELEVENLABS ----------------
load_dotenv(BACKEND_DIR / ".env")
load_dotenv(ROLEPLAY_DIR / ".env", override=False)

# Make the real prompt bundle importable without pulling in the core app.
sys.path.insert(0, str(BACKEND_DIR))
from app.infrastructure.runtime.prompts.push_pull import (  # noqa: E402
    PROMPT_TEXT,
    SPEC,
)

# --- config ----------------------------------------------------------------
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.environ.get("ROLEPLAY_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # Rachel
ELEVENLABS_MODEL = os.environ.get("ROLEPLAY_TTS_MODEL", "eleven_flash_v2_5")

DEEPGRAM_API_KEY = os.environ.get("DEEPGRAM_API_KEY")

GEN_MODEL = os.environ.get("ROLEPLAY_GEN_MODEL") or os.environ.get(
    "LLM_GENERATOR_MODEL", "gpt-5.3-chat-latest"
)
EVAL_MODEL = os.environ.get("ROLEPLAY_EVAL_MODEL") or os.environ.get(
    "LLM_EVALUATOR_MODEL", "gpt-5.3-chat-latest"
)

_http = httpx.AsyncClient(timeout=30.0)
_tts_cache: dict[str, bytes] = {}

app = FastAPI(title="roleplay-proxy")


# --- litellm: configured lazily, exactly like the backend adapter -----------
def _ensure_litellm():
    import litellm

    litellm.drop_params = True  # tolerate temperature/etc. across providers
    return litellm


# ---------------------------------------------------------------------------
# Deepgram ephemeral token (browser streams mic audio directly to Deepgram)
# ---------------------------------------------------------------------------
@app.post("/api/token")
async def mint_token():
    if not DEEPGRAM_API_KEY:
        return Response("deepgram_not_configured", status_code=500)
    r = await _http.post(
        "https://api.deepgram.com/v1/auth/grant",
        headers={"Authorization": f"Token {DEEPGRAM_API_KEY}"},
        json={"ttl_seconds": 60},
    )
    r.raise_for_status()
    data = r.json()
    return {
        "token": data["access_token"],
        "auth_scheme": "bearer",
        "expires_in": data.get("expires_in", 60),
    }


# ---------------------------------------------------------------------------
# Question generation — the REAL production push-pull generator
# ---------------------------------------------------------------------------
@app.get("/api/question")
async def question(mode: str = "combine"):
    litellm = _ensure_litellm()
    resp = await litellm.acompletion(
        model=GEN_MODEL,
        messages=[
            {"role": "system", "content": SPEC.generator_system},
            {"role": "user", "content": SPEC.generator_prompt()},
        ],
        temperature=1.0,
        max_tokens=300,
        response_format=SPEC.generator_response_schema,
    )
    content = resp.choices[0].message.content
    obj = (
        SPEC.generator_response_schema.model_validate(content)
        if isinstance(content, (dict, list))
        else SPEC.generator_response_schema.model_validate_json(content)
    )
    scenario = obj.messages[0].content
    return {"scenario": scenario, "mode": mode}


# ---------------------------------------------------------------------------
# Compact evaluator — production criteria, speakable 1-2 line output
# ---------------------------------------------------------------------------
class RoleplayEvaluation(BaseModel):
    verdict: Literal["nailed", "close", "missed"]
    spoken_feedback: str
    struggle: bool
    suggest: Literal["retry", "new", "drop_to_push"]


class EvalIn(BaseModel):
    scenario: str
    transcript: str
    mode: str = "combine"


_COMPACT_CONTRACT = """=== YOUR OUTPUT (ROLEPLAY COACH MODE) ===
You are a warm, encouraging wit coach speaking OUT LOUD to the learner. Return JSON with exactly these fields:
- "verdict": one of "nailed", "close", "missed".
- "spoken_feedback": ONE or TWO short sentences, second person, conversational, motivational. It will be SPOKEN ALOUD, so: no markdown, no bullet points, no emoji, no headings. Name the single most useful thing. Stay kind and playful even when they missed.
- "struggle": true if the attempt badly missed the core mechanic, was empty, or off-topic; otherwise false.
- "suggest": "retry" (same scenario again), "new" (move to a fresh scenario), or "drop_to_push" (simplify to just the tease because they're clearly struggling with the full thing)."""

_MODE_NOTE = {
    "combine": "",
    "push": (
        "=== SCAFFOLD MODE: PUSH ONLY ===\n"
        "The learner is ONLY attempting the PUSH — a playful, trivial, about-her tease. "
        "Evaluate ONLY the tease: is it playful, about HER, and trivial (never hurtful)? "
        "Ignore the pull completely. Never use suggest=\"drop_to_push\" here; use \"retry\" or \"new\"."
    ),
    "pull": (
        "=== SCAFFOLD MODE: PULL ONLY ===\n"
        "The learner is ONLY attempting the PULL — a genuine, specific compliment. "
        "Evaluate ONLY the warmth: is it genuine and specific (not generic or hollow)? "
        "Ignore the push completely. Never use suggest=\"drop_to_push\" here; use \"retry\" or \"new\"."
    ),
}


def _build_eval_system(mode: str) -> str:
    ev = PROMPT_TEXT["evaluator"]
    parts = [
        ev["intro"],
        ev["what_this_exercise_is"],
        ev["push_pull_techniques"],
        ev["evaluation_criteria"],
    ]
    note = _MODE_NOTE.get(mode, "")
    if note:
        parts.append(note)
    parts.append(_COMPACT_CONTRACT)
    return "\n\n".join(p.strip("\n") for p in parts if p).strip()


@app.post("/api/evaluate")
async def evaluate(body: EvalIn) -> RoleplayEvaluation:
    litellm = _ensure_litellm()
    user_prompt = (
        f"Scenario: {body.scenario}\n"
        f'User\'s spoken attempt: "{body.transcript.strip()}"\n'
        f"Mode: {body.mode}"
    )
    try:
        resp = await litellm.acompletion(
            model=EVAL_MODEL,
            messages=[
                {"role": "system", "content": _build_eval_system(body.mode)},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=300,
            response_format=RoleplayEvaluation,
        )
        content = resp.choices[0].message.content
        return (
            RoleplayEvaluation.model_validate(content)
            if isinstance(content, (dict, list))
            else RoleplayEvaluation.model_validate_json(content)
        )
    except Exception as exc:  # never block the coach on an eval hiccup
        logger.warning("evaluate failed: %s", exc)
        return RoleplayEvaluation(
            verdict="close",
            spoken_feedback="I lost that one for a second — give it another go.",
            struggle=False,
            suggest="retry",
        )


# ---------------------------------------------------------------------------
# ElevenLabs streaming TTS (cached: static coach lines repeat every session)
# ---------------------------------------------------------------------------
@app.get("/api/tts")
async def tts(text: str):
    if not ELEVENLABS_API_KEY:
        return Response("elevenlabs_not_configured", status_code=500)

    key = hashlib.sha1(
        f"{ELEVENLABS_VOICE_ID}|{ELEVENLABS_MODEL}|{text}".encode()
    ).hexdigest()
    cached = _tts_cache.get(key)
    if cached is not None:
        return Response(cached, media_type="audio/mpeg")

    url = (
        f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}/stream"
        "?output_format=mp3_44100_128&optimize_streaming_latency=3"
    )
    payload = {
        "text": text,
        "model_id": ELEVENLABS_MODEL,
        "voice_settings": {"stability": 0.4, "similarity_boost": 0.8},
    }

    async def streamer():
        buf = bytearray()
        async with _http.stream(
            "POST",
            url,
            headers={
                "xi-api-key": ELEVENLABS_API_KEY,
                "content-type": "application/json",
            },
            json=payload,
        ) as r:
            if r.status_code != 200:
                detail = (await r.aread()).decode("utf-8", "replace")
                logger.error("elevenlabs %s: %s", r.status_code, detail[:300])
                return
            async for chunk in r.aiter_bytes():
                buf.extend(chunk)
                yield chunk
        _tts_cache[key] = bytes(buf)  # warm the cache for next time

    return StreamingResponse(streamer(), media_type="audio/mpeg")


@app.get("/api/health")
async def health():
    return {
        "elevenlabs": bool(ELEVENLABS_API_KEY),
        "deepgram": bool(DEEPGRAM_API_KEY),
        "voice_id": ELEVENLABS_VOICE_ID,
        "tts_model": ELEVENLABS_MODEL,
        "gen_model": GEN_MODEL,
        "eval_model": EVAL_MODEL,
    }


# Static web app last, so /api/* routes win.
app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="web")
