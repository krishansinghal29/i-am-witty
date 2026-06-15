#!/usr/bin/env bash
# Launch the roleplay prototype using the backend venv (so the real push-pull
# prompt bundle + litellm are importable). Reads keys from design/backend/.env
# (Deepgram, OpenAI/Gemini, models) and roleplay/.env (ElevenLabs).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$HERE/../design/backend/.venv/bin/python"
PORT="${PORT:-8030}"

if [[ ! -x "$PY" ]]; then
  echo "backend venv not found at: $PY" >&2
  exit 1
fi

echo "roleplay coach -> http://localhost:$PORT"
exec "$PY" -m uvicorn server.main:app --reload --port "$PORT" --app-dir "$HERE"
