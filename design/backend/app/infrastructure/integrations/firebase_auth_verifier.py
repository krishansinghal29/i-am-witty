from __future__ import annotations

import asyncio
import threading

import firebase_admin
from firebase_admin import auth as firebase_auth, credentials, exceptions as firebase_exceptions

from app.ports.integrations.auth_token_verifier import VerifiedToken
from app.settings import Settings

_APP_NAME = "i-am-witty"

# Firebase apps are process-global: the SDK rejects a second `initialize_app`
# under the same name. Cache the initialized app by name so repeated instances
# (and concurrent first-use) share one app instead of racing into double-init.
_apps: dict[str, firebase_admin.App] = {}
_init_lock = threading.Lock()


class FirebaseAuthTokenVerifier:
    """Real `AuthTokenVerifier` backed by the Firebase Admin SDK.

    Credentials are loaded lazily on first verification, so importing and
    constructing this adapter never touches the filesystem or network and works
    in environments (tests, CI) where no service account is configured.
    """

    def __init__(self, settings: Settings) -> None:
        self._credentials_file = settings.firebase_credentials_file
        self._project_id = settings.firebase_project_id

    def _ensure_app(self) -> firebase_admin.App:
        """Initialize the dedicated Firebase app once, returning the cached one."""
        cached = _apps.get(_APP_NAME)
        if cached is not None:
            return cached
        with _init_lock:
            cached = _apps.get(_APP_NAME)
            if cached is not None:
                return cached
            if self._credentials_file:
                cred = credentials.Certificate(self._credentials_file)
            else:
                cred = credentials.ApplicationDefault()
            options = {"projectId": self._project_id} if self._project_id else None
            app = firebase_admin.initialize_app(cred, options, name=_APP_NAME)
            _apps[_APP_NAME] = app
            return app

    async def verify(self, id_token: str) -> VerifiedToken:
        """Verify a Firebase ID token and return the resolved identity."""
        if not id_token:
            raise ValueError("invalid_token")
        app = self._ensure_app()
        try:
            decoded = await asyncio.to_thread(
                firebase_auth.verify_id_token, id_token, app=app
            )
        except (ValueError, firebase_exceptions.FirebaseError) as exc:
            raise ValueError("invalid_token") from exc
        return VerifiedToken(
            uid=decoded["uid"],
            email=decoded.get("email"),
            claims=dict(decoded),
        )
