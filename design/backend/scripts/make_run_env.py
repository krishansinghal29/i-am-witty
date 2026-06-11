"""Build a Cloud Run --env-vars-file from the local .env (the single source of truth).

Reads .env locally and writes only the runtime-relevant keys. Values are never
printed; only the key names that were written are reported, so secrets stay out
of logs/transcripts.

Usage:
    python scripts/make_run_env.py [OUTPUT_PATH]

OUTPUT_PATH defaults to ./run-env.yaml. deploy.sh passes a temp path so no env
file persists after a deploy.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Keys the running container needs. Deliberately excludes DATABASE_URL_DIRECT
# (Alembic-only) and FIREBASE_CREDENTIALS_FILE (a local path that does not exist
# inside the container; Firebase creds will be provided separately).
RUNTIME_KEYS = (
    "DATABASE_URL",
    "APP_ENV",
    "DEEPGRAM_API_KEY",
    "DEEPGRAM_PROJECT_ID",
    "REVENUECAT_API_KEY",
    "REVENUECAT_WEBHOOK_AUTH",
    "POSTHOG_API_KEY",
    "POSTHOG_HOST",
    "FIREBASE_PROJECT_ID",
    "OTA_ENABLED",
    "OTA_POINTER_URL",
    "OPENAI_API_KEY",
    "GEMINI_API_KEY",
    "LLM_GENERATOR_MODEL",
    "LLM_EVALUATOR_MODEL",
    "TTS_VOICE",
)


def _parse_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        values[key] = value
    return values


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    env_path = root / ".env"
    # Output path is configurable so deploy.sh can target an ephemeral temp file
    # and keep .env as the single source of truth.
    out_path = Path(sys.argv[1]) if len(sys.argv) > 1 else root / "run-env.yaml"
    if not env_path.exists():
        print("ERROR: .env not found at backend root", file=sys.stderr)
        return 1

    env = _parse_env(env_path)
    written: list[str] = []
    lines: list[str] = []
    for key in RUNTIME_KEYS:
        if key in env and env[key] != "":
            # JSON strings are valid YAML double-quoted scalars and handle escaping.
            lines.append(f"{key}: {json.dumps(env[key])}")
            written.append(key)

    out_path.write_text("\n".join(lines) + "\n")
    missing = [k for k in RUNTIME_KEYS if k not in written]
    print(f"Wrote {out_path.name} with {len(written)} keys: {written}")
    if missing:
        print(f"Not set (skipped): {missing}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
