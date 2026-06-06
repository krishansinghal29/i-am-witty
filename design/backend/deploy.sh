#!/usr/bin/env bash
#
# Deploy the backend to Cloud Run, using .env as the single source of truth.
#
# The Cloud Run env config is derived from .env into a temporary file at deploy
# time and deleted afterward, so there is no second env file to maintain. Edit
# .env only.
#
# Usage: ./deploy.sh
set -euo pipefail

# gcloud installed via Homebrew cask is not on PATH by default.
if ! command -v gcloud >/dev/null 2>&1; then
  export PATH="/opt/homebrew/share/google-cloud-sdk/bin:$PATH"
fi

SERVICE="iamwitty-backend"
REGION="us-east1"
PROJECT="i-am-witty"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

# Translate .env -> ephemeral env-vars file (auto-removed on exit).
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT
ENV_FILE="$TMP_DIR/run-env.yaml"
python3 scripts/make_run_env.py "$ENV_FILE"

gcloud run deploy "$SERVICE" \
  --project "$PROJECT" \
  --source . \
  --region "$REGION" \
  --allow-unauthenticated \
  --env-vars-file "$ENV_FILE" \
  --port 8080 \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 2 \
  --quiet
