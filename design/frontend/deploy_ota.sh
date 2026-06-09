#!/usr/bin/env bash
#
# Publish a self-hosted Capgo OTA bundle: build the web layer, zip it, hash it,
# upload to public GCS, and repoint production.json. No app-store release, no
# Capgo cloud, no fee.
#
# OTA updates the WEB LAYER ONLY. If you changed native surface (Capacitor
# plugins, permissions, icons, capacitor.config.ts, ios/, android/) this script
# REFUSES — cut a store release instead, because the installed binary can't run
# a bundle that needs native code it doesn't have.
#
# One-time setup (bucket + public read) and the full flow: frontend/README.md
#
# Usage: ./deploy_ota.sh
set -euo pipefail

# gcloud installed via Homebrew cask is not on PATH by default.
if ! command -v gcloud >/dev/null 2>&1; then
  export PATH="/opt/homebrew/share/google-cloud-sdk/bin:$PATH"
fi

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

BUCKET="${OTA_BUCKET:-gs://riffy-ota}"
PREFIX="ota"
# Minimum native binary build (iOS CFBundleVersion / Android versionCode) this
# web bundle is compatible with. Bump ONLY when you ship a new native binary
# that a future web bundle will require; the backend withholds this bundle from
# any device older than this.
MIN_VERSION_BUILD="${OTA_MIN_VERSION_BUILD:-1}"
# Git tag marking the last native store release; native-surface diffs are
# measured against it.
NATIVE_TAG="${OTA_NATIVE_TAG:-native-release}"

# --- 1. Native guard -------------------------------------------------------
NATIVE_PATHS=(package.json package-lock.json capacitor.config.ts ios android)
if git rev-parse -q --verify "refs/tags/${NATIVE_TAG}" >/dev/null 2>&1; then
  if ! git diff --quiet "${NATIVE_TAG}" -- "${NATIVE_PATHS[@]}"; then
    echo "ERROR: native surface changed since tag '${NATIVE_TAG}':" >&2
    git diff --name-only "${NATIVE_TAG}" -- "${NATIVE_PATHS[@]}" >&2
    echo "OTA can only update the web layer — cut a store release instead." >&2
    exit 1
  fi
else
  echo "WARN: tag '${NATIVE_TAG}' not found; skipping native-surface guard." >&2
  echo "      Tag your last store build: git tag ${NATIVE_TAG} && git push --tags" >&2
fi

# --- 2. Build --------------------------------------------------------------
VERSION="$(node -p "require('./package.json').version")-$(git rev-parse --short HEAD)"
echo "Building OTA bundle ${VERSION} ..."
VITE_RELEASE_CHANNEL=production VITE_CAPGO_ENABLED=true npm run build

# --- 3. Zip (index.html MUST sit at the zip root, not under dist/) ----------
ZIP="bundle-${VERSION}.zip"
rm -f "$ZIP"
( cd dist && zip -qr "../${ZIP}" . )

# --- 4. Checksum (sha256 of the exact zip the device downloads) ------------
CHECKSUM="$(shasum -a 256 "$ZIP" | awk '{print $1}')"

# --- 5. Upload the bundle (public-read object) -----------------------------
HTTP_BASE="https://storage.googleapis.com/${BUCKET#gs://}/${PREFIX}"
BUNDLE_URL="${HTTP_BASE}/${ZIP}"
gcloud storage cp "$ZIP" "${BUCKET}/${PREFIX}/${ZIP}"

# --- 6. Repoint production.json (this is the "release") --------------------
POINTER="production.json"
cat > "$POINTER" <<EOF
{
  "version": "${VERSION}",
  "url": "${BUNDLE_URL}",
  "checksum": "${CHECKSUM}",
  "min_version_build": ${MIN_VERSION_BUILD}
}
EOF
# no-cache so a repoint (e.g. rollback) propagates immediately to the backend.
gcloud storage cp --cache-control="no-cache, max-age=0" "$POINTER" \
  "${BUCKET}/${PREFIX}/production.json"

rm -f "$ZIP" "$POINTER"

echo ""
echo "Published OTA bundle ${VERSION}"
echo "  bundle:  ${BUNDLE_URL}"
echo "  pointer: ${HTTP_BASE}/production.json"
echo ""
echo "Backend OTA_POINTER_URL must be: ${HTTP_BASE}/production.json"
