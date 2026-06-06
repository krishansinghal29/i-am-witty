from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from posthog import Posthog

    from app.settings import Settings


class PostHogAnalytics:
    """Real PostHog adapter for the `Analytics` port (product analytics + flags).

    Analytics must never break a request: every method swallows errors, and when
    no API key is configured the adapter degrades to a safe no-op.
    """

    def __init__(self, settings: Settings) -> None:
        self._api_key = settings.posthog_api_key
        self._host = settings.posthog_host
        # Lazy init keeps imports clean without a key and avoids a network client
        # until the first call that actually needs one.
        self._client: Posthog | None = None
        self._initialized = False

    def _get_client(self) -> Posthog | None:
        if self._initialized:
            return self._client
        self._initialized = True
        if not self._api_key:
            return None
        try:
            from posthog import Posthog

            self._client = Posthog(
                project_api_key=self._api_key, host=self._host
            )
        except Exception:
            self._client = None
        return self._client

    def capture(
        self, app_user_id: str, event: str, properties: dict | None = None
    ) -> None:
        client = self._get_client()
        if client is None:
            return
        try:
            client.capture(event, distinct_id=app_user_id, properties=properties)
        except Exception:
            return

    def identify(self, app_user_id: str, traits: dict | None = None) -> None:
        client = self._get_client()
        if client is None:
            return
        try:
            # `identify` was removed in posthog 7.x; `set` is the person-properties
            # equivalent for a known distinct id.
            client.set(distinct_id=app_user_id, properties=traits or {})
        except Exception:
            return

    def is_feature_enabled(self, flag: str, app_user_id: str) -> bool:
        """Experimentation flag state; defaults to False on no-op/None/error.

        Not authoritative: backend-enforced access gates live in the database
        (`feature_gate_defaults`), never here.
        """
        client = self._get_client()
        if client is None:
            return False
        try:
            return bool(client.feature_enabled(flag, app_user_id))
        except Exception:
            return False
