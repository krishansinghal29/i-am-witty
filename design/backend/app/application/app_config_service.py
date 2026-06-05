from __future__ import annotations

from app.ports.repositories.config_repository import (
    ConfigRepository,
    PublicConfig,
)


class AppConfigService:
    def __init__(self, config: ConfigRepository) -> None:
        self._config = config

    async def get_public_config(self) -> PublicConfig:
        return await self._config.get_public_config()
