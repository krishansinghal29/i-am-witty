from __future__ import annotations

import ssl

from sqlalchemy.engine import URL, make_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from app.settings import Settings, get_settings

_ASYNC_DRIVER = "postgresql+asyncpg"
# Query params that libpq/Neon include in connection strings but asyncpg's
# connect() does not accept. SSL is handled explicitly via connect_args below.
_INCOMPATIBLE_QUERY_KEYS = ("sslmode", "channel_binding", "options")
_LOCAL_HOSTS = ("", "localhost", "127.0.0.1")


def normalize_async_dsn(raw_url: str) -> URL:
    """Coerce any Postgres DSN into an asyncpg-compatible SQLAlchemy URL.

    Accepts the raw string Neon hands out (``postgresql://...?sslmode=require&
    channel_binding=require``) and returns a URL that uses the ``postgresql+asyncpg``
    driver with the asyncpg-incompatible libpq query params stripped (SSL is
    re-applied through ``build_connect_args``). Shared by the runtime engine and
    the Alembic env so both connect identically.
    """
    url = make_url(raw_url)
    if url.get_backend_name() == "postgresql":
        url = url.set(drivername=_ASYNC_DRIVER)
    if url.query:
        cleaned = {k: v for k, v in url.query.items() if k not in _INCOMPATIBLE_QUERY_KEYS}
        url = url.set(query=cleaned)
    return url


def build_connect_args(url: URL) -> dict:
    """asyncpg connect args: disable prepared-statement cache (PgBouncer) and
    require TLS for non-local hosts (Neon mandates SSL)."""
    connect_args: dict = {"statement_cache_size": 0}
    if (url.host or "").lower() not in _LOCAL_HOSTS:
        connect_args["ssl"] = ssl.create_default_context()
    return connect_args


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
