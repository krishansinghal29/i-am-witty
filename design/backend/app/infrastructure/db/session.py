from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.engine import get_session_factory


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an AsyncSession and ensure it is closed afterwards."""
    factory = get_session_factory()
    session = factory()
    try:
        yield session
    finally:
        await session.close()
