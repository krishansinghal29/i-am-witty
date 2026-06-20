#!/usr/bin/env bash
# Launch a roleplay server. Both use the shared backend venv (design/backend/.venv).
#   ./run.sh old   # legacy server (server/main.py)        -> :8030
#   ./run.sh new   # roleplay_sim simulator (server_new)   -> :8031
# Keys: old reads design/backend/.env + roleplay/.env; new reads roleplay/.env.
# Override the interpreter/port with PY=... PORT=...
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="${PY:-$HERE/../design/backend/.venv/bin/python}"
TARGET="${1:-}"

case "$TARGET" in
  old) APP="server.main:app";             APP_DIR="$HERE";            PORT="${PORT:-8030}";;
  new) APP="roleplay_sim.api.routes:app"; APP_DIR="$HERE/server_new"; PORT="${PORT:-8031}";;
  *)   echo "usage: ./run.sh [old|new]" >&2; exit 2;;
esac

if [[ ! -x "$PY" ]]; then
  echo "python not found at: $PY" >&2
  exit 1
fi

echo "roleplay ($TARGET) -> http://localhost:$PORT"
exec "$PY" -m uvicorn "$APP" --reload --port "$PORT" --app-dir "$APP_DIR"
