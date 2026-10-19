from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.composition.container import Integrations, RequestContainer
from app.domain.models.app_user import AppUser
from app.infrastructure.db.session import get_session
from app.ports.integrations.auth_token_verifier import VerifiedToken
from app.settings import get_settings

_BEARER_PREFIX = "Bearer "
_RECALL_LEARNER_HEADER = "X-Recall-Learner"


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
    """Resolve the caller from a Firebase Bearer token (the only auth scheme)."""
    authorization = request.headers.get("Authorization")
    if authorization and authorization.startswith(_BEARER_PREFIX):
        token = authorization[len(_BEARER_PREFIX) :]
        try:
            verified = await container.integrations.auth_verifier.verify(token)
        except Exception as exc:  # noqa: BLE001 - any verify failure is unauthenticated
            raise HTTPException(status_code=401, detail="unauthenticated") from exc
        return await container.identity_service.resolve_authenticated(verified.uid)

    return None


async def get_current_user(
    request: Request,
    container: RequestContainer = Depends(get_container),
) -> AppUser:
    user = await _resolve_user(request, container)
    if user is None:
        raise HTTPException(status_code=401, detail="unauthenticated")
    return user


def _bearer_token(request: Request) -> str | None:
    authorization = request.headers.get("Authorization")
    if authorization and authorization.startswith(_BEARER_PREFIX):
        return authorization[len(_BEARER_PREFIX) :]
    return None


def _is_recall_admin(verified: VerifiedToken) -> bool:
    email = verified.email
    return (
        email is not None
        and verified.claims.get("email_verified") is True
        and email.lower() in get_settings().admin_email_set
    )


async def get_recall_admin(
    request: Request,
    container: RequestContainer = Depends(get_container),
) -> VerifiedToken:
    """Gate the recall admin: a verified Firebase token from an allowlisted email.

    Unlike app routes this never touches ``app_users``; the admin needs no app
    account, only a Google sign-in on the allowlist.
    """
    token = _bearer_token(request)
    if token is None:
        raise HTTPException(status_code=401, detail="unauthenticated")
    try:
        verified = await container.integrations.auth_verifier.verify(token)
    except Exception as exc:  # noqa: BLE001 - any verify failure is unauthenticated
        raise HTTPException(status_code=401, detail="unauthenticated") from exc
    if not _is_recall_admin(verified):
        raise HTTPException(status_code=403, detail="forbidden")
    return verified


async def get_recall_learner_key(
    request: Request,
    container: RequestContainer = Depends(get_container),
) -> str:
    """Identify who is practising on the public recall routes.

    The admin (valid allowlisted token) practises as ``uid:<firebase uid>`` so
    progress follows them across devices. Everyone else is the anonymous id
    their browser keeps in ``X-Recall-Learner``; a bad or non-admin token is
    ignored rather than rejected, so practice never breaks over sign-in state.
    """
    token = _bearer_token(request)
    if token is not None:
        try:
            verified = await container.integrations.auth_verifier.verify(token)
        except Exception:  # noqa: BLE001 - fall back to the anonymous id
            verified = None
        if verified is not None and _is_recall_admin(verified):
            return f"uid:{verified.uid}"

    try:
        learner_id = uuid.UUID(request.headers.get(_RECALL_LEARNER_HEADER, ""))
    except ValueError as exc:
        raise HTTPException(
            status_code=400, detail="missing or invalid X-Recall-Learner"
        ) from exc
    return f"anon:{learner_id}"


ContainerDep = Annotated[RequestContainer, Depends(get_container)]
CurrentUser = Annotated[AppUser, Depends(get_current_user)]
RecallAdmin = Annotated[VerifiedToken, Depends(get_recall_admin)]
RecallLearnerKey = Annotated[str, Depends(get_recall_learner_key)]
