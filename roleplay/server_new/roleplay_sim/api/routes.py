"""FastAPI surface wiring the simulation + media to the existing web client. [P10]

Endpoints mirror the old server's contract so the web client (../web) needs no
changes:  /api/config, /api/session/new, /api/chat/stream (SSE), /api/transcribe,
/api/tts/stream.  /api/chat/stream drives the Simulation and streams the Actor's
reply word-by-word as SSE tokens.
"""
from __future__ import annotations

import json
import logging
import os
import uuid
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response, StreamingResponse
from fastapi.staticfiles import StaticFiles

from roleplay_sim.api.schemas import ChatStreamIn, NewSessionIn, TtsIn
from roleplay_sim.domain.config import SceneConfig, SessionConfig
from roleplay_sim.domain.models import GameState, PlayerTurn
from roleplay_sim.factory import build_llm_simulation
from roleplay_sim.llm.client import LiteLLMClient
from roleplay_sim.media import dictation, speech
from roleplay_sim.media.providers import load_dictation, load_speech
from roleplay_sim.personas.loader import load_persona

logger = logging.getLogger("roleplay")
_ROLEPLAY_DIR = Path(__file__).resolve().parents[3]   # .../roleplay
WEB_DIR = _ROLEPLAY_DIR / "web"


def _load_env() -> None:
    """Load roleplay/.env so keys come from a file, not `export`. It holds the
    ROLEPLAY_* config and all provider keys (OPENAI_API_KEY included). No-op if
    python-dotenv is absent."""
    try:
        from dotenv import load_dotenv
    except Exception:
        return
    load_dotenv(_ROLEPLAY_DIR / ".env")


def _sse(payload: dict[str, Any]) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


def create_app() -> FastAPI:
    _load_env()   # before LiteLLMClient() reads the environment
    app = FastAPI(title="roleplay-sim")
    http = httpx.AsyncClient(timeout=60.0)
    llm = LiteLLMClient()
    sessions: dict[str, Any] = {}

    @app.get("/api/config")
    async def get_config():
        d = load_dictation()
        s = load_speech()
        return {
            "utterance_end_ms": int(os.environ.get("ROLEPLAY_UTTERANCE_END_MS", "2000")),
            "no_speech_end_ms": int(os.environ.get("ROLEPLAY_NO_SPEECH_END_MS", "6000")),
            "dictation": {"provider": d.name, "model": d.model, "language": d.language},
            "chat_model": llm.provider.model,
            "voice": s.voice,
        }

    @app.post("/api/session/new")
    async def new_session(body: NewSessionIn | None = None):
        body = body or NewSessionIn()
        try:
            persona = load_persona(body.persona)
        except Exception:
            raise HTTPException(status_code=400, detail="unknown_persona")
        cfg = SessionConfig(
            persona=persona,
            scene=SceneConfig(venue="rooftop bar", approach_context="cold approach",
                              present_company="two friends", goal=body.goal),
            initial_state=GameState.fresh(),
        )
        sid = str(uuid.uuid4())
        sessions[sid] = build_llm_simulation(cfg, llm)
        return {"session_id": sid}

    @app.post("/api/chat/stream")
    async def chat_stream(body: ChatStreamIn):
        sim = sessions.get(body.session_id)
        if sim is None:
            raise HTTPException(status_code=404, detail="session_not_found")
        message = (body.message or "").strip()
        if not message:
            raise HTTPException(status_code=400, detail="message_required")

        async def generator():
            try:
                actor_turn, status = await sim.submit(PlayerTurn(text=message))
                reply = actor_turn.text
                if actor_turn.action:
                    reply = f"{reply} *[{actor_turn.action}]*"
                for word in reply.split(" "):
                    yield _sse({"type": "token", "text": word + " "})
                yield _sse({"type": "done", "reply": reply, "status": status.value})
            except Exception as exc:  # noqa: BLE001
                logger.exception("chat stream failed")
                yield _sse({"type": "error", "message": str(exc)})

        return StreamingResponse(generator(), media_type="text/event-stream",
                                 headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

    @app.post("/api/transcribe")
    async def transcribe(request: Request):
        audio = await request.body()
        if not audio:
            raise HTTPException(status_code=400, detail="empty_audio")
        provider = load_dictation()
        try:
            text = await dictation.transcribe(provider, audio, http)
        except dictation.TranscriptionError as exc:
            raise HTTPException(status_code=502, detail=str(exc))
        if os.environ.get("ROLEPLAY_ROMANIZE", "").lower() in {"1", "true", "yes", "on"}:
            text = await dictation.romanize(text, os.environ.get("SARVAM_API_KEY"), http)
        return {"transcript": text}

    @app.post("/api/tts/stream")
    async def tts_stream(body: TtsIn):
        provider = load_speech()
        if not provider.api_key:
            return Response(f"{provider.name}_not_configured", status_code=500)
        text = body.text.strip()
        if not text:
            return Response("empty_text", status_code=400)
        if provider.name == "sarvam":
            try:
                wav = await speech.synthesize_sarvam(provider, text, http)
            except speech.SpeechError as exc:
                return Response(str(exc), status_code=502)
            return Response(content=wav, media_type="audio/wav")

        url, headers, payload = speech.elevenlabs_stream_request(provider, text)

        async def streamer():
            async with http.stream("POST", url, headers=headers, json=payload) as r:
                if r.status_code != 200:
                    logger.error("elevenlabs %s", r.status_code)
                    return
                async for chunk in r.aiter_bytes():
                    yield chunk

        return StreamingResponse(streamer(), media_type="audio/mpeg")

    @app.get("/api/health")
    async def health():
        return {"ok": True, "sessions": len(sessions), "chat_model": llm.provider.model}

    if WEB_DIR.is_dir():
        app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="web")
    return app


app = create_app()
