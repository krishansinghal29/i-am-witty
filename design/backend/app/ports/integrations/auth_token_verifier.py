from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class VerifiedToken:
    uid: str
    email: str | None
    claims: dict


class AuthTokenVerifier(Protocol):
    """Verifies a client-supplied identity token (Firebase ID token today).

    The backend is the token-verification authority: clients send the raw ID
    token, the backend resolves the trusted identity here, and only the
    resolved `uid`/claims are used downstream. The vendor (Firebase Admin SDK)
    lives behind this port so it can be swapped without touching services.
    """

    async def verify(self, id_token: str) -> VerifiedToken:
        """Verify `id_token` and return the resolved identity.

        Raises on an invalid, expired, or untrusted token.
        """
        ...
