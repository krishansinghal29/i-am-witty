from __future__ import annotations

import ssl

from sqlalchemy.engine import URL, make_url

_ASYNC_DRIVER = "postgresql+asyncpg"
# Query params that libpq/Neon include in connection strings but asyncpg's
# connect() does not accept. SSL is handled explicitly via connect_args below.
_INCOMPATIBLE_QUERY_KEYS = ("sslmode", "channel_binding", "options")
_LOCAL_HOSTS = ("", "localhost", "127.0.0.1")


def normalize_async_dsn(raw_url: str) -> URL:
    """Coerce any Postgres DSN into an asyncpg-compatible SQLAlchemy URL."""
    url = make_url(raw_url)
    if url.get_backend_name() == "postgresql":
        url = url.set(drivername=_ASYNC_DRIVER)
    if url.query:
        cleaned = {
            k: v
            for k, v in url.query.items()
            if k not in _INCOMPATIBLE_QUERY_KEYS
        }
        url = url.set(query=cleaned)
    return url


def build_connect_args(url: URL) -> dict:
    """asyncpg connect args for local Postgres and Neon."""
    connect_args: dict = {"statement_cache_size": 0}
    if (url.host or "").lower() not in _LOCAL_HOSTS:
        connect_args["ssl"] = ssl.create_default_context()
    return connect_args
