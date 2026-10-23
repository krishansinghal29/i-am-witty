from __future__ import annotations

from datetime import date
from typing import Literal
from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel

from app.api.deps import ContainerDep, RecallLearnerDep
from app.application.recall_practice_service import SessionCard, SessionCheckin
from app.domain.models.recall import RecallItemKind

router = APIRouter(prefix="/v1/recall", tags=["recall"])


class CheckinDayResponse(BaseModel):
    date: date
    done: bool | None


class SessionCheckinResponse(BaseModel):
    item_id: UUID
    title: str
    question: str
    why: str | None
    today: bool | None
    streak: int
    last7: list[CheckinDayResponse]


class LineCardResponse(BaseModel):
    cue_text: str
    cue_type: Literal["reaction", "goal"]
    hint: str | None
    text: str
    delivery_note: str | None
    position: int
    cue_line_count: int


class ConceptCardResponse(BaseModel):
    name: str
    definition: str
    scenario: str
    scenario_number: int
    scenario_count: int


class RoutineCardResponse(BaseModel):
    name: str
    steps: list[str]


class SessionCardResponse(BaseModel):
    item_id: UUID
    kind: Literal["line", "concept", "routine"]
    is_new: bool
    # Exactly one of these is set, matching `kind`; the others are null.
    line: LineCardResponse | None = None
    concept: ConceptCardResponse | None = None
    routine: RoutineCardResponse | None = None


class SessionCountsResponse(BaseModel):
    due: int
    new: int
    line: int
    concept: int
    routine: int


class SessionResponse(BaseModel):
    local_date: date
    checkins: list[SessionCheckinResponse]
    cards: list[SessionCardResponse]
    counts: SessionCountsResponse


class SeenRequest(BaseModel):
    item_id: UUID
    local_date: date


class SeenResponse(BaseModel):
    item_id: UUID
    seen_count: int
    due_on: date | None


class CheckinRequest(BaseModel):
    item_id: UUID
    local_date: date
    done: bool


class CheckinResponse(BaseModel):
    item_id: UUID
    done: bool
    streak: int


class OutlookResponse(BaseModel):
    due_tomorrow: int
    new_waiting: int


def _card_response(card: SessionCard) -> SessionCardResponse:
    item = card.item
    if item.kind is RecallItemKind.line:
        return SessionCardResponse(
            item_id=item.id,
            kind="line",
            is_new=card.is_new,
            line=LineCardResponse(
                cue_text=item.cue.text if item.cue is not None else "",
                cue_type=item.cue.type.value if item.cue is not None else "reaction",
                hint=item.hint,
                text=item.body or "",
                delivery_note=item.delivery_note,
                position=card.position or 1,
                cue_line_count=card.cue_line_count or 1,
            ),
        )
    if item.kind is RecallItemKind.concept:
        scenarios = item.scenarios or [""]
        index = card.seen_count % len(scenarios)
        return SessionCardResponse(
            item_id=item.id,
            kind="concept",
            is_new=card.is_new,
            concept=ConceptCardResponse(
                name=item.title or "",
                definition=item.body or "",
                scenario=scenarios[index],
                scenario_number=index + 1,
                scenario_count=len(scenarios),
            ),
        )
    return SessionCardResponse(
        item_id=item.id,
        kind="routine",
        is_new=card.is_new,
        routine=RoutineCardResponse(name=item.title or "", steps=item.steps or []),
    )


def _checkin_response(checkin: SessionCheckin) -> SessionCheckinResponse:
    return SessionCheckinResponse(
        item_id=checkin.item.id,
        title=checkin.item.title or "",
        question=checkin.item.question or "",
        why=checkin.item.body,
        today=checkin.today,
        streak=checkin.streak,
        last7=[CheckinDayResponse(date=d.date, done=d.done) for d in checkin.last7],
    )


@router.get("/session", response_model=SessionResponse)
async def get_session(
    local_date: date, container: ContainerDep, learner: RecallLearnerDep
) -> SessionResponse:
    """Today's check-ins and cards for the signed-in caller."""
    session = await container.recall_practice_service.get_session(
        learner.key, local_date, include_admin_only=learner.is_admin
    )
    cards = [_card_response(card) for card in session.cards]
    return SessionResponse(
        local_date=session.local_date,
        checkins=[_checkin_response(c) for c in session.checkins],
        cards=cards,
        counts=SessionCountsResponse(
            due=session.due_count,
            new=session.new_count,
            line=sum(1 for c in cards if c.kind == "line"),
            concept=sum(1 for c in cards if c.kind == "concept"),
            routine=sum(1 for c in cards if c.kind == "routine"),
        ),
    )


@router.post("/seen", response_model=SeenResponse)
async def mark_seen(
    body: SeenRequest, container: ContainerDep, learner: RecallLearnerDep
) -> SeenResponse:
    """Record a "Next" tap; repeat taps on the same day count once."""
    progress = await container.recall_practice_service.mark_seen(
        learner.key, body.item_id, body.local_date, include_admin_only=learner.is_admin
    )
    return SeenResponse(
        item_id=progress.item_id,
        seen_count=progress.seen_count,
        due_on=progress.due_on,
    )


@router.post("/checkins", response_model=CheckinResponse)
async def record_checkin(
    body: CheckinRequest, container: ContainerDep, learner: RecallLearnerDep
) -> CheckinResponse:
    """Save today's yes/no for a focus item and return its streak."""
    done, streak = await container.recall_practice_service.record_checkin(
        learner.key,
        body.item_id,
        body.local_date,
        body.done,
        include_admin_only=learner.is_admin,
    )
    return CheckinResponse(item_id=body.item_id, done=done, streak=streak)


@router.get("/outlook", response_model=OutlookResponse)
async def get_outlook(
    local_date: date, container: ContainerDep, learner: RecallLearnerDep
) -> OutlookResponse:
    """What's waiting tomorrow, for the end-of-session screen."""
    outlook = await container.recall_practice_service.get_outlook(
        learner.key, local_date, include_admin_only=learner.is_admin
    )
    return OutlookResponse(
        due_tomorrow=outlook.due_tomorrow, new_waiting=outlook.new_waiting
    )
