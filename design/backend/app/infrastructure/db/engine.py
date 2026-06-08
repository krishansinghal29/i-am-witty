from __future__ import annotations

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from app.infrastructure.db.dsn import build_connect_args, normalize_async_dsn
from app.settings import Settings, get_settings


def create_engine_from_settings(settings: Settings) -> AsyncEngine:
    """Create an async engine from settings.

    The runtime uses Neon's PgBouncer pooler endpoint with asyncpg, so prepared
    statement caching is disabled for pgbouncer compatibility. Building the engine
    does not open a connection (asyncpg connects lazily on first use), so this is
    safe to call with a placeholder URL.
    """
    url = normalize_async_dsn(settings.database_url)
    return create_async_engine(
        url,
        pool_size=5,
        max_overflow=5,
        pool_pre_ping=True,
        connect_args=build_connect_args(url),
    )


# Lazily-created module-level singletons. These are created from get_settings()
# at import time, but creating the engine does NOT open a connection.
_engine: AsyncEngine = create_engine_from_settings(get_settings())
session_factory: async_sessionmaker = async_sessionmaker(
    bind=_engine,
    expire_on_commit=False,
)

# Backwards/convention-friendly alias.
SessionLocal = session_factory


def get_engine() -> AsyncEngine:
    return _engine


def get_session_factory() -> async_sessionmaker:
    return session_factory
