from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.orm.users import UserProfile as OrmUserProfile
from app.ports.repositories.profile_repository import UserProfileRecord


class PgProfileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_profile(self, app_user_id: uuid.UUID) -> UserProfileRecord | None:
        orm = await self._session.get(OrmUserProfile, app_user_id)
        return self._to_record(orm) if orm is not None else None

    async def upsert_profile(
        self, app_user_id: uuid.UUID, display_name: str | None
    ) -> UserProfileRecord:
        orm = await self._session.get(OrmUserProfile, app_user_id)
        if orm is None:
            orm = OrmUserProfile(app_user_id=app_user_id, display_name=display_name)
            self._session.add(orm)
        else:
            orm.display_name = display_name
        await self._session.flush()
        await self._session.refresh(orm)
        return self._to_record(orm)

    @staticmethod
    def _to_record(orm: OrmUserProfile) -> UserProfileRecord:
        return UserProfileRecord(
            app_user_id=orm.app_user_id,
            display_name=orm.display_name,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )
