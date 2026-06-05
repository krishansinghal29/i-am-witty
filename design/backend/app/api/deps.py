from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.composition.container import Integrations, RequestContainer
from app.domain.models.app_user import AppUser
from app.infrastructure.db.session import get_session

_BEARER_PREFIX = "Bearer "
_GUEST_HEADER = "X-Guest-Token"


def get_integrations(request: Request) -> Integrations:
    return request.app.state.integrations


async def get_container(
    session: AsyncSession = Depends(get_session),
    integrations: Integrations = Depends(get_integrations),
) -> RequestContainer:
    return RequestContainer(session, integrations)


async def _resolve_user(
    request: Request, container: RequestContainer
) -> AppUser | None:
    """Resolve the caller from a Bearer token or a guest token header."""
    authorization = request.headers.get("Authorization")
    if authorization and authorization.startswith(_BEARER_PREFIX):
        token = authorization[len(_BEARER_PREFIX) :]
        try:
            verified = await container.integrations.auth_verifier.verify(token)
        except Exception as exc:  # noqa: BLE001 - any verify failure is unauthenticated
            raise HTTPException(status_code=401, detail="unauthenticated") from exc
        return await container.identity_service.resolve_authenticated(verified.uid)

    guest_token = request.headers.get(_GUEST_HEADER)
    if guest_token:
        return await container.identity_service.resolve_guest(guest_token)

    return None


async def get_current_user(
    request: Request,
    container: RequestContainer = Depends(get_container),
) -> AppUser:
    user = await _resolve_user(request, container)
    if user is None:
        raise HTTPException(status_code=401, detail="unauthenticated")
    return user


async def get_optional_user(
    request: Request,
    container: RequestContainer = Depends(get_container),
) -> AppUser | None:
    try:
        return await _resolve_user(request, container)
    except HTTPException:
        return None


ContainerDep = Annotated[RequestContainer, Depends(get_container)]
CurrentUser = Annotated[AppUser, Depends(get_current_user)]
OptionalUser = Annotated[AppUser | None, Depends(get_optional_user)]
