from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, status
from pydantic import BaseModel

from app.api.deps import ContainerDep, RecallAdmin
from app.domain.models.recall import (
    RecallCue,
    RecallCueType,
    RecallItem,
    RecallItemKind,
    RecallItemStatus,
)

router = APIRouter(prefix="/v1/admin/recall", tags=["admin-recall"])

CueType = Literal["reaction", "goal"]
ItemKind = Literal["line", "concept", "routine", "focus"]
ItemStatus = Literal["active", "paused", "archived"]


class AdminMeResponse(BaseModel):
    uid: str
    email: str | None


class CueResponse(BaseModel):
    id: UUID
    text: str
    type: CueType


class CueWithCountResponse(CueResponse):
    line_count: int


class CreateCueRequest(BaseModel):
    text: str
    type: CueType


class UpdateCueRequest(BaseModel):
    text: str | None = None
    type: CueType | None = None


class NewCueRequest(BaseModel):
    text: str
    type: CueType


class CreateItemRequest(BaseModel):
    kind: ItemKind
    cue_id: UUID | None = None
    new_cue: NewCueRequest | None = None
    hint: str | None = None
    title: str | None = None
    body: str | None = None
    delivery_note: str | None = None
    question: str | None = None
    steps: list[str] | None = None
    scenarios: list[str] | None = None
    source: str | None = None


class UpdateItemRequest(BaseModel):
    """Partial update: only fields present in the JSON are applied (null clears)."""

    kind: ItemKind | None = None
    status: ItemStatus | None = None
    cue_id: UUID | None = None
    new_cue: NewCueRequest | None = None
    hint: str | None = None
    title: str | None = None
    body: str | None = None
    delivery_note: str | None = None
    question: str | None = None
    steps: list[str] | None = None
    scenarios: list[str] | None = None
    source: str | None = None


class ItemResponse(BaseModel):
    id: UUID
    kind: ItemKind
    status: ItemStatus
    cue: CueResponse | None
    hint: str | None
    title: str | None
    body: str | None
    delivery_note: str | None
    question: str | None
    steps: list[str] | None
    scenarios: list[str] | None
    source: str | None
    created_at: datetime
    updated_at: datetime


def _cue_response(cue: RecallCue) -> CueResponse:
    return CueResponse(id=cue.id, text=cue.text, type=cue.type.value)


def _item_response(item: RecallItem) -> ItemResponse:
    return ItemResponse(
        id=item.id,
        kind=item.kind.value,
        status=item.status.value,
        cue=_cue_response(item.cue) if item.cue is not None else None,
        hint=item.hint,
        title=item.title,
        body=item.body,
        delivery_note=item.delivery_note,
        question=item.question,
        steps=item.steps,
        scenarios=item.scenarios,
        source=item.source,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.get("/me", response_model=AdminMeResponse)
async def get_me(admin: RecallAdmin) -> AdminMeResponse:
    """Confirm the caller is a recall admin (401/403 otherwise)."""
    return AdminMeResponse(uid=admin.uid, email=admin.email)


@router.get("/cues", response_model=list[CueWithCountResponse])
async def list_cues(
    container: ContainerDep, admin: RecallAdmin
) -> list[CueWithCountResponse]:
    """All cues, alphabetical, with their non-archived line counts."""
    cues = await container.recall_admin_service.list_cues()
    return [
        CueWithCountResponse(
            id=entry.cue.id,
            text=entry.cue.text,
            type=entry.cue.type.value,
            line_count=entry.line_count,
        )
        for entry in cues
    ]


@router.post(
    "/cues", response_model=CueResponse, status_code=status.HTTP_201_CREATED
)
async def create_cue(
    body: CreateCueRequest, container: ContainerDep, admin: RecallAdmin
) -> CueResponse:
    cue = await container.recall_admin_service.create_cue(
        body.text, RecallCueType(body.type)
    )
    return _cue_response(cue)


@router.patch("/cues/{cue_id}", response_model=CueResponse)
async def update_cue(
    cue_id: UUID, body: UpdateCueRequest, container: ContainerDep, admin: RecallAdmin
) -> CueResponse:
    cue = await container.recall_admin_service.update_cue(
        cue_id, body.model_dump(exclude_unset=True)
    )
    return _cue_response(cue)


@router.get("/items", response_model=list[ItemResponse])
async def list_items(
    container: ContainerDep,
    admin: RecallAdmin,
    kind: ItemKind | None = None,
    status: ItemStatus | None = None,
) -> list[ItemResponse]:
    """Items newest first; archived ones only when asked for by ``status``."""
    items = await container.recall_admin_service.list_items(
        kind=RecallItemKind(kind) if kind else None,
        status=RecallItemStatus(status) if status else None,
    )
    return [_item_response(item) for item in items]


@router.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: UUID, container: ContainerDep, admin: RecallAdmin
) -> ItemResponse:
    item = await container.recall_admin_service.get_item(item_id)
    return _item_response(item)


@router.post(
    "/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED
)
async def create_item(
    body: CreateItemRequest, container: ContainerDep, admin: RecallAdmin
) -> ItemResponse:
    item = await container.recall_admin_service.create_item(
        RecallItemKind(body.kind), body.model_dump(exclude={"kind"})
    )
    return _item_response(item)


@router.patch("/items/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: UUID, body: UpdateItemRequest, container: ContainerDep, admin: RecallAdmin
) -> ItemResponse:
    item = await container.recall_admin_service.update_item(
        item_id, body.model_dump(exclude_unset=True)
    )
    return _item_response(item)
