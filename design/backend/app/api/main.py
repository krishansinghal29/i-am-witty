from __future__ import annotations

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.session import get_session

app = FastAPI(title="i-am-witty backend")


@app.get("/health")
async def health(session: AsyncSession = Depends(get_session)) -> dict[str, str]:
    """Liveness/readiness probe that pings the database with `SELECT 1`.

    Never crashes the app when the DB is unreachable; the DB error is reported
    in the response body instead.
    """
    try:
        await session.execute(text("SELECT 1"))
        return {"status": "ok", "db": "ok"}
    except Exception as exc:  # noqa: BLE001 - surface any DB error as a body field
        return {"status": "ok", "db": "error", "detail": str(exc)}
