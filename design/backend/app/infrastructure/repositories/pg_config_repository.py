from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.orm.config import AppConfig as OrmAppConfig
from app.infrastructure.db.orm.config import (
    FeatureGateDefault as OrmFeatureGateDefault,
)
from app.ports.repositories.config_repository import (
    ConfigRepository,
    FeatureGate,
    PublicConfig,
)

_FREE_TASK_LIMIT_KEY = "free_task_limit"


class PgConfigRepository(ConfigRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_public_config(self) -> PublicConfig:
        public_rows = (
            await self._session.execute(
                select(OrmAppConfig).where(OrmAppConfig.is_public.is_(True))
            )
        ).scalars()
        values = {row.key: row.value for row in public_rows}
        gates = await self.get_feature_gates()
        return PublicConfig(
            values=values,
            free_task_limit=await self.get_free_task_limit(),
            feature_gates=tuple(gates),
        )

    async def get_value(self, key: str) -> Any | None:
        row = await self._session.get(OrmAppConfig, key)
        if row is None:
            return None
        return row.value

    async def get_free_task_limit(self) -> int:
        value = await self.get_value(_FREE_TASK_LIMIT_KEY)
        if value is None:
            return 0
        return int(value)

    async def get_feature_gates(self) -> list[FeatureGate]:
        rows = (
            await self._session.execute(select(OrmFeatureGateDefault))
        ).scalars()
        return [self._to_gate(row) for row in rows]

    @staticmethod
    def _to_gate(row: OrmFeatureGateDefault) -> FeatureGate:
        return FeatureGate(
            feature_key=row.feature_key,
            default_enabled=row.default_enabled,
            requires_entitlement=row.requires_entitlement,
            min_app_version=row.min_app_version,
        )
