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
from roleplay_sim.domain.enums import ActionType
from roleplay_sim.domain.models import ActionMove, PlayerTurn
from roleplay_sim.engine.registry import ACTION_LADDER
from roleplay_sim.factory import build_llm_simulation
from roleplay_sim.generator.session import generate_session
from roleplay_sim.orchestrator.conversation_log import build_recorder_from_env
from roleplay_sim.llm.client import LiteLLMClient
from roleplay_sim.media import dictation, speech
from roleplay_sim.media.providers import load_dictation, load_speech

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


def _build_action(name: str | None) -> ActionMove | None:
    """Map a dropdown action value to a structured ActionMove (ladder + level)."""
    if not name:
        return None
    try:
        at = ActionType(name)
    except ValueError:
        return None
    lad, level = ACTION_LADDER.get(at, (None, 1))
    if lad is None:
        return None
    step = -1 if at is ActionType.STEP_BACK else 1
    return ActionMove(type=at, ladder=lad, target_level=level, intended_step=step)


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
        # Every session is rolled + synthesized — a fresh woman, scene, and voice.
        cfg = await generate_session(llm, seed=body.seed, goal=body.goal)
        sid = str(uuid.uuid4())
        recorder = build_recorder_from_env(sid, cfg.persona, cfg.scene, cfg.initial_state)
        sessions[sid] = {
            "sim": build_llm_simulation(cfg, llm, recorder=recorder),
            "opening_sent": False,
            "first_impression": cfg.scene.first_impression,
        }
        return {"session_id": sid}

    @app.post("/api/chat/stream")
    async def chat_stream(body: ChatStreamIn):
        entry = sessions.get(body.session_id)
        if entry is None:
            raise HTTPException(status_code=404, detail="session_not_found")
        sim = entry["sim"]
        message = (body.message or "").strip()
        action = _build_action(body.action)

        # Opening turn: the web client kicks off with an empty message. Stream the
        # firewalled first impression once, before any real exchange — it sets the
        # scene without advancing the simulation.
        if not message and action is None:
            if entry["opening_sent"] or sim.state.flags.turn_count > 0:
                raise HTTPException(status_code=400, detail="message_required")
            entry["opening_sent"] = True
            opening = entry["first_impression"] or ""

            async def opener():
                for word in opening.split(" "):
                    yield _sse({"type": "token", "text": word + " "})
                yield _sse({"type": "done", "reply": opening, "status": sim.status.value})

            return StreamingResponse(opener(), media_type="text/event-stream",
                                     headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

        async def generator():
            try:
                actor_turn, status = await sim.submit(PlayerTurn(text=message, action=action))
                reply = actor_turn.text
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
