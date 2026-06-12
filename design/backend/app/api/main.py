from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes import comms as comms_routes
from app.api.routes import identity as identity_routes
from app.api.routes import ota as ota_routes
from app.api.routes import tasks as tasks_routes
from app.application.exceptions import (
    AccessDeniedError,
    ApplicationError,
    ConflictError,
    NotFoundError,
    PaywallRequiredError,
    ValidationError,
)
from app.composition.container import build_integrations
from app.infrastructure.db.engine import get_engine
from app.infrastructure.db.session import get_session
from app.settings import get_settings

# Maps application errors to HTTP status; resolution walks the MRO so the most
# specific subclass wins and any unmapped ApplicationError falls back to 400.
EXCEPTION_STATUS_MAP: dict[type[ApplicationError], int] = {
    NotFoundError: 404,
    AccessDeniedError: 403,
    PaywallRequiredError: 402,
    ConflictError: 409,
    ValidationError: 422,
    ApplicationError: 400,
}


def _status_for(exc: ApplicationError) -> int:
    for klass in type(exc).__mro__:
        if klass in EXCEPTION_STATUS_MAP:
            return EXCEPTION_STATUS_MAP[klass]
    return 400


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    from app.infrastructure.db import orm  # noqa: F401 - registers ORM mappers

    app.state.integrations = build_integrations(get_settings())
    try:
        yield
    finally:
        await get_engine().dispose()


app = FastAPI(title="i-am-witty backend", lifespan=lifespan)

# CORS: allow the web frontend (prod + dev) and the Capacitor app to call the
# API from a browser. Native Capacitor requests are not subject to CORS; the
# capacitor:// + localhost origins cover the dev/native webview cases. With
# allow_credentials=True an explicit origin list is required (no wildcard).
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # Production web (Firebase Hosting + custom domain).
        "https://riffy.pro",
        "https://www.riffy.pro",
        "https://i-am-witty.web.app",
        "https://i-am-witty.firebaseapp.com",
        # Dev (Vite dev server) + Capacitor app origins.
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "capacitor://localhost",
        "http://localhost",
        # Android Capacitor webview uses the https scheme by default
        # (server.androidScheme), so its origin is https://localhost.
        "https://localhost",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ApplicationError)
async def handle_application_error(
    request: Request, exc: ApplicationError
) -> JSONResponse:
    return JSONResponse(
        status_code=_status_for(exc), content={"error": exc.reason}
    )


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


app.include_router(identity_routes.router)
app.include_router(tasks_routes.router)
app.include_router(comms_routes.router)
app.include_router(ota_routes.router)
