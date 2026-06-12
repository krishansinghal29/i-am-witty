from __future__ import annotations

from app.application.exceptions import ValidationError
from app.application.unit_of_work import UnitOfWork
from app.domain.models.app_user import AppUser
from app.ports.integrations.auth_token_verifier import AuthTokenVerifier
from app.ports.repositories.onboarding_repository import OnboardingRepository
from app.ports.repositories.user_repository import UserRepository

# Allowed onboarding triggers (mirrors OnboardingTrigger.value strings); kept
# inline so the application layer stays free of infrastructure imports. The
# legacy "teased" value is still accepted so older app builds keep working.
_ALLOWED_TRIGGERS = frozenset(
    {"group_chats", "dates", "work", "friends", "stage", "other", "teased"}
)


class IdentityService:
    """Resolves authenticated users and finalizes onboarding in one transaction.

    Onboarding runs entirely client-side until the user finishes; completion is
    the first (and only) write: it creates the Firebase-authenticated user (if
    new) and the onboarding row together. There are no guests.
    """

    def __init__(
        self,
        users: UserRepository,
        onboarding: OnboardingRepository,
        verifier: AuthTokenVerifier,
        uow: UnitOfWork,
    ) -> None:
        self._users = users
        self._onboarding = onboarding
        self._verifier = verifier
        self._uow = uow

    async def resolve_authenticated(self, firebase_uid: str) -> AppUser | None:
        return await self._users.find_by_firebase_uid(firebase_uid)

    async def complete_onboarding(
        self,
        *,
        timezone: str,
        trigger: str,
        id_token: str,
        locale: str | None = None,
    ) -> AppUser:
        """Verify the Firebase token, then create the user + onboarding row.

        Idempotent: re-running with the same token reuses the existing user and
        refreshes the onboarding row rather than creating a duplicate.
        """
        if trigger not in _ALLOWED_TRIGGERS:
            raise ValidationError("invalid_trigger")
        verified = await self._verifier.verify(id_token)
        async with self._uow.transaction():
            user = await self._users.find_by_firebase_uid(verified.uid)
            if user is None:
                user = await self._users.create_authenticated_user(
                    verified.uid, timezone, locale
                )
            await self._onboarding.create_completed_state(user.id, trigger)
        return user
