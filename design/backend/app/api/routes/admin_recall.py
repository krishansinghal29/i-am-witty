from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

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
Audience = Literal["everyone", "admin"]


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
    # Omitted: focus defaults to admin-only, everything else to everyone.
    audience: Audience | None = None


class UpdateItemRequest(BaseModel):
    """Partial update: only fields present in the JSON are applied (null clears)."""

    kind: ItemKind | None = None
    status: ItemStatus | None = None
    audience: Audience | None = None
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


class MergeCueRequest(BaseModel):
    into_cue_id: UUID


class SuggestRequest(BaseModel):
    text: str


class DraftCueResponse(BaseModel):
    id: UUID | None
    text: str
    type: CueType
    line_count: int


class DraftSiblingHintResponse(BaseModel):
    item_id: UUID
    body: str
    hint: str


class DraftResponse(BaseModel):
    kind: ItemKind
    cue: DraftCueResponse | None
    hint: str | None
    sibling_hint: DraftSiblingHintResponse | None
    title: str | None
    body: str | None
    delivery_note: str | None
    question: str | None
    steps: list[str] | None
    scenarios: list[str] | None


class ScenariosRequest(BaseModel):
    title: str
    body: str | None = None
    existing: list[str] = Field(default_factory=list)
    count: int = Field(3, ge=1, le=5)


class ScenariosResponse(BaseModel):
    scenarios: list[str]


class HintRequest(BaseModel):
    cue_id: UUID | None = None
    cue_text: str | None = None
    body: str


class HintResponse(BaseModel):
    hint: str


class ItemResponse(BaseModel):
    id: UUID
    kind: ItemKind
    status: ItemStatus
    audience: Audience
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
        audience=item.audience.value,
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


@router.post("/cues/{cue_id}/merge", response_model=CueWithCountResponse)
async def merge_cue(
    cue_id: UUID, body: MergeCueRequest, container: ContainerDep, admin: RecallAdmin
) -> CueWithCountResponse:
    """Move this cue's lines onto ``into_cue_id`` and delete this cue."""
    merged = await container.recall_admin_service.merge_cue(cue_id, body.into_cue_id)
    return CueWithCountResponse(
        id=merged.cue.id,
        text=merged.cue.text,
        type=merged.cue.type.value,
        line_count=merged.line_count,
    )


@router.post("/suggest", response_model=DraftResponse)
async def suggest_item(
    body: SuggestRequest, container: ContainerDep, admin: RecallAdmin
) -> DraftResponse:
    """Draft one item from a rough note; nothing is saved."""
    draft = await container.recall_assist_service.suggest(body.text)
    return DraftResponse(
        kind=draft.kind.value,
        cue=(
            DraftCueResponse(
                id=draft.cue.id,
                text=draft.cue.text,
                type=draft.cue.type.value,
                line_count=draft.cue.line_count,
            )
            if draft.cue is not None
            else None
        ),
        hint=draft.hint,
        sibling_hint=(
            DraftSiblingHintResponse(
                item_id=draft.sibling_hint.item_id,
                body=draft.sibling_hint.body,
                hint=draft.sibling_hint.hint,
            )
            if draft.sibling_hint is not None
            else None
        ),
        title=draft.title,
        body=draft.body,
        delivery_note=draft.delivery_note,
        question=draft.question,
        steps=draft.steps,
        scenarios=draft.scenarios,
    )


@router.post("/scenarios", response_model=ScenariosResponse)
async def draft_scenarios(
    body: ScenariosRequest, container: ContainerDep, admin: RecallAdmin
) -> ScenariosResponse:
    """Draft new scenarios for a concept, different from ``existing``."""
    scenarios = await container.recall_assist_service.draft_scenarios(
        body.title, body.body, body.existing, body.count
    )
    return ScenariosResponse(scenarios=scenarios)


@router.post("/hint", response_model=HintResponse)
async def draft_hint(
    body: HintRequest, container: ContainerDep, admin: RecallAdmin
) -> HintResponse:
    """Suggest a hint for a line, distinct from its cue's existing hints."""
    hint = await container.recall_assist_service.draft_hint(
        body.cue_id, body.cue_text, body.body
    )
    return HintResponse(hint=hint)


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
