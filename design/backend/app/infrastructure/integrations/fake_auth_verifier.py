from __future__ import annotations

from app.ports.integrations.auth_token_verifier import VerifiedToken


class FakeAuthTokenVerifier:
    """Deterministic stand-in for the real (Firebase) token verifier.

    Treats the raw token string as the trusted identity so tests can pass any
    stable string and receive a stable `uid`. No network, no SDK.
    """

    async def verify(self, id_token: str) -> VerifiedToken:
        """Resolve `id_token` to a deterministic identity (uid == token)."""
        if not id_token:
            raise ValueError("invalid_token")
        return VerifiedToken(uid=id_token, email=None, claims={"fake": True})
