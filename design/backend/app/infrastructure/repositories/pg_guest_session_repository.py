from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.orm.users import GuestSession as OrmGuestSession
from app.ports.repositories.guest_session_repository import GuestSessionRecord


class PgGuestSessionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_session(
        self,
        app_user_id: uuid.UUID,
        session_token_hash: str,
        expires_at: datetime | None = None,
    ) -> GuestSessionRecord:
        orm = OrmGuestSession(
            app_user_id=app_user_id,
            session_token_hash=session_token_hash,
            expires_at=expires_at,
        )
        self._session.add(orm)
        await self._session.flush()
        await self._session.refresh(orm)
        return self._to_record(orm)

    async def find_by_token_hash(
        self, session_token_hash: str
    ) -> GuestSessionRecord | None:
        stmt = select(OrmGuestSession).where(
            OrmGuestSession.session_token_hash == session_token_hash
        )
        orm = (await self._session.execute(stmt)).scalar_one_or_none()
        return self._to_record(orm) if orm is not None else None

    async def touch_last_seen(self, session_id: uuid.UUID) -> None:
        orm = await self._session.get(OrmGuestSession, session_id)
        if orm is not None:
            orm.last_seen_at = datetime.now(timezone.utc)
            await self._session.flush()

    async def mark_converted(self, session_id: uuid.UUID) -> None:
        orm = await self._session.get(OrmGuestSession, session_id)
        if orm is not None:
            orm.converted_at = datetime.now(timezone.utc)
            await self._session.flush()

    @staticmethod
    def _to_record(orm: OrmGuestSession) -> GuestSessionRecord:
        return GuestSessionRecord(
            id=orm.id,
            app_user_id=orm.app_user_id,
            session_token_hash=orm.session_token_hash,
            created_at=orm.created_at,
            last_seen_at=orm.last_seen_at,
            expires_at=orm.expires_at,
            converted_at=orm.converted_at,
        )
