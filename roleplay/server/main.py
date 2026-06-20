"""Conversational roleplay proxy.

Thin FastAPI server: server-side session history, streaming LLM (SSE),
streaming TTS passthrough, and batch speech-to-text. API keys stay on the
server; the browser sends a session id + either the latest user message or the
recorded audio for that turn.

Providers (chat / dictation / speech) are selected and tuned entirely through
env vars — see `server/config.py`.
"""

from __future__ import annotations

import dataclasses
import json
import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from server import character, config, dictation, speech

logger = logging.getLogger("roleplay")
logging.basicConfig(level=logging.INFO)

ROLEPLAY_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROLEPLAY_DIR.parent / "design" / "backend"
WEB_DIR = ROLEPLAY_DIR / "web"

load_dotenv(BACKEND_DIR / ".env")
load_dotenv(ROLEPLAY_DIR / ".env", override=True)

# Resolve the active providers once, after env is loaded.
CFG = config.load()

# Each session's persona + full transcript is dumped under server/tmp for debugging.
TMP_DIR = ROLEPLAY_DIR / "server" / "tmp"
CONVERSATION_DIR = Path(os.environ.get("ROLEPLAY_CONVO_DIR") or TMP_DIR / "conversations")

_http = httpx.AsyncClient(timeout=60.0)
# session_id -> {"system": <system prompt>, "history": [<turns>]}
_sessions: dict[str, dict[str, Any]] = {}

app = FastAPI(title="roleplay-conversation")

logger.info(
    "providers | chat=%s (%s) | dictation=%s (%s) | speech=%s (%s)",
    CFG.chat.name, CFG.chat.model,
    CFG.dictation.name, CFG.dictation.model,
    CFG.speech.name, CFG.speech.voice,
)


def _ensure_litellm():
    import litellm

    litellm.drop_params = True
    return litellm


def _chat_kwargs(model: str, **extra: Any) -> dict[str, Any]:
    """litellm.acompletion kwargs for the active chat provider (+ creds)."""
    kw: dict[str, Any] = {"model": model}
    if CFG.chat.api_base:
        kw["api_base"] = CFG.chat.api_base
    if CFG.chat.api_key:
        kw["api_key"] = CFG.chat.api_key
    kw.update(CFG.chat.extra)  # provider-specific tuning (e.g. Sarvam reasoning toggle)
    kw.update(extra)
    return kw


class TtsIn(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


class ChatStreamIn(BaseModel):
    session_id: str
    message: str | None = None


def _sse(payload: dict[str, Any]) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


def _llm_messages(session: dict[str, Any]) -> list[dict[str, str]]:
    return [{"role": "system", "content": session["system"]}, *session["history"]]


def _session_slug(char: "character.Character | None") -> str:
    """Shared base filename for a session's character + conversation dumps."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%f")
    return f"{ts}_{char.name if char else 'fixed'}"


def _dump_conversation(session_id: str, session: dict[str, Any]) -> None:
    """Best-effort dump of the persona + full transcript so far (rewritten each turn)."""
    char = session.get("char")
    try:
        CONVERSATION_DIR.mkdir(parents=True, exist_ok=True)
        record = {
            "slug": session["slug"],
            "session_id": session_id,
            "updated": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%f"),
            "character": dataclasses.asdict(char) if char else None,
            "first_impression": session.get("first_impression"),
            "system_prompt": session["system"],
            "history": session["history"],
        }
        path = CONVERSATION_DIR / f"{session['slug']}.json"
        path.write_text(
            json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except Exception:
        logger.exception("conversation dump failed")


async def _build_persona() -> tuple[str, "character.Character | None", str]:
    """Return (system_prompt, character, first_impression) for a new session."""
    if CFG.system_prompt_override:
        return CFG.system_prompt_override, None, ""

    char = character.roll_character()
    first_impression = character.fallback_first_impression(char)
    try:
        litellm = _ensure_litellm()
        resp = await litellm.acompletion(
            **_chat_kwargs(CFG.gen_model, messages=character.synth_messages(char),
                           temperature=1.0, max_tokens=180),
        )
        text = (resp.choices[0].message.content or "").strip()
        if text:
            first_impression = text
    except Exception:
        logger.exception("first-impression synthesis failed; using fallback")

    logger.info(
        "new persona: %s, %d, %s, from %s | %s | %s",
        char.name, char.age, char.profession, char.hometown,
        char.archetype, char.setting,
    )
    return character.build_system_prompt(char, first_impression), char, first_impression


async def _iter_llm_tokens(session: dict[str, Any]):
    litellm = _ensure_litellm()
    stream = await litellm.acompletion(
        **_chat_kwargs(CFG.chat.model, messages=_llm_messages(session),
                       temperature=0.9, max_tokens=300, stream=True),
    )
    async for chunk in stream:
        delta = chunk.choices[0].delta
        text = getattr(delta, "content", None) or ""
        if text:
            yield text


@app.get("/api/config")
async def get_config():
    # The client records each turn locally and posts it to /api/transcribe;
    # utterance_end_ms is the trailing-silence it waits for before finalizing once
    # the user has started speaking; no_speech_end_ms is the longer grace period it
    # allows before giving up when the user hasn't spoken at all yet.
    return {
        "utterance_end_ms": CFG.utterance_end_ms,
        "no_speech_end_ms": CFG.no_speech_end_ms,
        "dictation": {
            "provider": CFG.dictation.name,
            "model": CFG.dictation.model,
            "language": CFG.dictation.language,
        },
        "chat_model": CFG.chat.model,
        "voice": CFG.speech.voice,
    }


@app.post("/api/session/new")
async def new_session():
    session_id = str(uuid.uuid4())
    system_prompt, char, first_impression = await _build_persona()
    session = {
        "system": system_prompt,
        "history": [],
        "char": char,
        "first_impression": first_impression,
        "slug": _session_slug(char),
    }
    _sessions[session_id] = session
    _dump_conversation(session_id, session)
    return {"session_id": session_id}


@app.post("/api/chat/stream")
async def chat_stream(body: ChatStreamIn):
    session = _sessions.get(body.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="session_not_found")

    history = session["history"]
    message = (body.message or "").strip()
    if message:
        history.append({"role": "user", "content": message})
    elif history:
        raise HTTPException(status_code=400, detail="message_required")

    async def generator():
        reply = ""
        try:
            async for token in _iter_llm_tokens(session):
                reply += token
                yield _sse({"type": "token", "text": token})
            reply = reply.strip()
            if reply:
                history.append({"role": "assistant", "content": reply})
            _dump_conversation(body.session_id, session)
            yield _sse({"type": "done", "reply": reply})
        except Exception as exc:
            logger.exception("chat stream failed")
            yield _sse({"type": "error", "message": str(exc)})

    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/api/transcribe")
async def transcribe(request: Request):
    """Batch speech-to-text: raw WAV body in, `{transcript}` out.

    The active dictation provider (Deepgram / ElevenLabs Scribe / Sarvam) is
    chosen by env; see `server/config.py`.
    """
    audio = await request.body()
    if not audio:
        raise HTTPException(status_code=400, detail="empty_audio")
    try:
        text = await dictation.transcribe(CFG.dictation, audio, _http)
    except dictation.TranscriptionError as exc:
        logger.error("transcription failed: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc))
    if CFG.romanize_post:
        text = await dictation.romanize(text, CFG.romanize_key, _http)
    return {"transcript": text}


@app.post("/api/tts/stream")
async def tts_stream(body: TtsIn):
    if not CFG.speech.api_key:
        return Response(f"{CFG.speech.name}_not_configured", status_code=500)

    text = body.text.strip()
    if not text:
        return Response("empty_text", status_code=400)

    # Sarvam Bulbul: batch JSON -> base64 WAV. Return the clip as one response;
    # the client plays each phrase as a complete blob regardless of provider.
    if CFG.speech.name == "sarvam":
        try:
            wav = await speech.synthesize_sarvam(CFG.speech, text, _http)
        except speech.SpeechError as exc:
            logger.error("sarvam tts failed: %s", exc)
            return Response(str(exc), status_code=502)
        return Response(content=wav, media_type="audio/wav")

    # ElevenLabs: streaming MP3.
    url = (
        f"https://api.elevenlabs.io/v1/text-to-speech/{CFG.speech.voice}/stream"
        "?output_format=mp3_44100_128&optimize_streaming_latency=3"
    )
    payload = {
        "text": text,
        "model_id": CFG.speech.model,
        "voice_settings": {"stability": 0.4, "similarity_boost": 0.8},
    }

    async def streamer():
        async with _http.stream(
            "POST",
            url,
            headers={
                "xi-api-key": CFG.speech.api_key,
                "content-type": "application/json",
            },
            json=payload,
        ) as r:
            if r.status_code != 200:
                detail = (await r.aread()).decode("utf-8", "replace")
                logger.error("elevenlabs %s: %s", r.status_code, detail[:300])
                return
            async for chunk in r.aiter_bytes():
                yield chunk

    return StreamingResponse(streamer(), media_type="audio/mpeg")


@app.get("/api/health")
async def health():
    return {
        "chat": {
            "provider": CFG.chat.name,
            "model": CFG.chat.model,
            "configured": CFG.chat.name == "openai" or bool(CFG.chat.api_key),
        },
        "dictation": {
            "provider": CFG.dictation.name,
            "model": CFG.dictation.model,
            "language": CFG.dictation.language,
            "configured": bool(CFG.dictation.api_key),
        },
        "speech": {
            "provider": CFG.speech.name,
            "model": CFG.speech.model,
            "voice": CFG.speech.voice,
            "configured": bool(CFG.speech.api_key),
        },
        "utterance_end_ms": CFG.utterance_end_ms,
        "no_speech_end_ms": CFG.no_speech_end_ms,
        "active_sessions": len(_sessions),
    }


app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="web")
