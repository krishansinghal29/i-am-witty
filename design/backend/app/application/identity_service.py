from __future__ import annotations

import hashlib
import secrets
import uuid
from dataclasses import dataclass

from app.application.exceptions import ConflictError
from app.application.unit_of_work import UnitOfWork
from app.domain.models.app_user import AppUser
from app.ports.integrations.auth_token_verifier import AuthTokenVerifier
from app.ports.repositories.guest_session_repository import GuestSessionRepository
from app.ports.repositories.onboarding_repository import OnboardingRepository
from app.ports.repositories.user_repository import UserRepository


@dataclass(frozen=True)
class GuestIdentity:
    user: AppUser
    session_token: str


class IdentityService:
    """Orchestrates guest creation and guest→authenticated account linking."""

    def __init__(
        self,
        users: UserRepository,
        sessions: GuestSessionRepository,
        onboarding: OnboardingRepository,
        verifier: AuthTokenVerifier,
        uow: UnitOfWork,
    ) -> None:
        self._users = users
        self._sessions = sessions
        self._onboarding = onboarding
        self._verifier = verifier
        self._uow = uow

    @staticmethod
    def _hash_token(raw: str) -> str:
        return hashlib.sha256(raw.encode()).hexdigest()

    async def create_guest(
        self, timezone: str, locale: str | None = None
    ) -> GuestIdentity:
        raw = secrets.token_urlsafe(32)
        async with self._uow.transaction():
            user = await self._users.create_guest_user(timezone, locale)
            await self._sessions.create_session(user.id, self._hash_token(raw))
            await self._onboarding.create_initial_state(user.id)
        return GuestIdentity(user=user, session_token=raw)

    async def link_account(self, app_user_id: uuid.UUID, id_token: str) -> AppUser:
        verified = await self._verifier.verify(id_token)
        existing = await self._users.find_by_firebase_uid(verified.uid)
        if existing is not None and existing.id != app_user_id:
            raise ConflictError("account_already_linked")
        async with self._uow.transaction():
            user = await self._users.link_firebase_uid(app_user_id, verified.uid)
        return user

    async def resolve_authenticated(self, firebase_uid: str) -> AppUser | None:
        return await self._users.find_by_firebase_uid(firebase_uid)

    async def resolve_guest(self, session_token: str) -> AppUser | None:
        record = await self._sessions.find_by_token_hash(
            self._hash_token(session_token)
        )
        if record is None:
            return None
        return await self._users.find_by_id(record.app_user_id)
