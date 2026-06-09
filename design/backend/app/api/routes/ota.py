"""Self-hosted Capgo OTA update endpoint.

The app's `@capgo/capacitor-updater` plugin (auto-update mode) POSTs here to ask
"is there a newer web-layer bundle?". We answer in the shape Capgo's plugin
expects (`LatestVersion`): `{version, url, checksum}` when an update is available,
`{version, message}` otherwise. Bundles themselves live on public GCS and are
downloaded directly by the device — this endpoint never proxies them.

Being in the loop earns its keep two ways: `ota_enabled` is an instant kill
switch for every installed device (no rebuild), and `min_version_build` lets us
withhold a bundle from a native binary too old to run it (which would otherwise
crash on a missing plugin method). Everything fails safe to "no update": a
missing pointer, a fetch error, or a disabled flag never serves a bad bundle and
never raises.
"""

from __future__ import annotations

import time
from typing import Any

import httpx
from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict

from app.settings import Settings, get_settings

router = APIRouter(prefix="/v1", tags=["ota"])

# The pointer changes only on a deploy, and devices poll on their own cadence, so
# a short in-process cache spares GCS without making the kill switch feel sticky.
_POINTER_TTL_SECONDS = 60.0
_pointer_cache: dict[str, Any] = {"at": 0.0, "data": None}


class UpdateCheckRequest(BaseModel):
    """Subset of Capgo's `AppInfos` body we actually use; the rest is ignored."""

    model_config = ConfigDict(extra="ignore")

    platform: str | None = None
    # Native binary build (iOS CFBundleVersion / Android versionCode). Drives the
    # compatibility gate.
    version_build: str | None = None
    # The web bundle the device is currently running ("builtin" before any OTA).
    version_name: str | None = None
    plugin_version: str | None = None


class UpdateCheckResponse(BaseModel):
    """Capgo `LatestVersion` shape. `url` present ⇒ download; absent ⇒ no-op."""

    version: str
    message: str | None = None
    url: str | None = None
    checksum: str | None = None


async def _load_pointer(url: str) -> dict | None:
    """Fetch `production.json` with a short TTL cache; serve stale on failure."""
    now = time.monotonic()
    cached = _pointer_cache["data"]
    if cached is not None and now - _pointer_cache["at"] < _POINTER_TTL_SECONDS:
        return cached
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
    except Exception:
        # Never let a GCS hiccup break update checks — keep the last good pointer.
        return cached
    _pointer_cache["at"] = now
    _pointer_cache["data"] = data
    return data


@router.post("/ota/check", response_model=UpdateCheckResponse)
async def ota_check(
    body: UpdateCheckRequest,
    settings: Settings = Depends(get_settings),
) -> UpdateCheckResponse:
    no_update = UpdateCheckResponse(
        version=body.version_name or "builtin",
        message="No new version available",
    )

    if not settings.ota_enabled or not settings.ota_pointer_url:
        return no_update

    pointer = await _load_pointer(settings.ota_pointer_url)
    if not pointer or not pointer.get("url") or not pointer.get("version"):
        return no_update

    # Compatibility gate: never serve a bundle to a native binary older than the
    # bundle requires. Unparseable values don't block (the gate only filters out
    # provably-too-old binaries, never ambiguous ones).
    min_build = pointer.get("min_version_build")
    if min_build is not None and body.version_build is not None:
        try:
            if int(body.version_build) < int(min_build):
                return no_update
        except (TypeError, ValueError):
            pass

    # Device already runs this bundle — nothing to download.
    if body.version_name and body.version_name == str(pointer["version"]):
        return no_update

    return UpdateCheckResponse(
        version=str(pointer["version"]),
        url=str(pointer["url"]),
        checksum=pointer.get("checksum"),
    )
