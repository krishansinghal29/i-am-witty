from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.app_user import AppUser, UserStatus
from app.infrastructure.db.orm.users import AppUser as OrmAppUser
from app.infrastructure.db.orm.users import UserStatus as OrmUserStatus


class PgUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, app_user_id: uuid.UUID) -> AppUser | None:
        orm = await self._session.get(OrmAppUser, app_user_id)
        return self._to_domain(orm) if orm is not None else None

    async def find_by_firebase_uid(self, firebase_uid: str) -> AppUser | None:
        stmt = select(OrmAppUser).where(OrmAppUser.firebase_uid == firebase_uid)
        orm = (await self._session.execute(stmt)).scalar_one_or_none()
        return self._to_domain(orm) if orm is not None else None

    async def create_authenticated_user(
        self, firebase_uid: str, timezone: str, locale: str | None = None
    ) -> AppUser:
        orm = OrmAppUser(
            firebase_uid=firebase_uid,
            status=OrmUserStatus(UserStatus.active.value),
            timezone=timezone,
            locale=locale,
        )
        self._session.add(orm)
        await self._session.flush()
        await self._session.refresh(orm)
        return self._to_domain(orm)

    async def touch_last_seen(self, app_user_id: uuid.UUID) -> None:
        orm = await self._session.get(OrmAppUser, app_user_id)
        if orm is not None:
            orm.last_seen_at = datetime.now(timezone.utc)
            await self._session.flush()

    @staticmethod
    def _to_domain(orm: OrmAppUser) -> AppUser:
        return AppUser(
            id=orm.id,
            firebase_uid=orm.firebase_uid,
            status=UserStatus(orm.status.value),
            timezone=orm.timezone,
            locale=orm.locale,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            last_seen_at=orm.last_seen_at,
            deleted_at=orm.deleted_at,
        )
