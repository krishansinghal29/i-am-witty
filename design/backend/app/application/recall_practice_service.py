from __future__ import annotations

import random
import uuid
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone

from app.application.exceptions import NotFoundError, ValidationError
from app.application.unit_of_work import UnitOfWork
from app.domain.models.recall import (
    RecallItem,
    RecallItemKind,
    RecallItemStatus,
    RecallProgress,
)
from app.domain.policies.recall_schedule_policy import (
    RecallSchedule,
    apply_seen,
    compute_focus_streak,
)
from app.ports.repositories.recall_repository import RecallRepository

MAX_SESSION_CARDS = 15
MAX_NEW_PER_DAY = 3
# Client dates may differ from the server's UTC date by a timezone, not more.
LOCAL_DATE_TOLERANCE = timedelta(days=2)
# Check-in history read for streaks; a streak longer than this just caps.
STREAK_LOOKBACK = timedelta(days=366)


@dataclass(frozen=True)
class SessionCard:
    item: RecallItem
    is_new: bool
    seen_count: int
    # Lines only: 1-based place among the cue's non-archived lines, and their count.
    position: int | None = None
    cue_line_count: int | None = None


@dataclass(frozen=True)
class CheckinDay:
    date: date
    done: bool | None


@dataclass(frozen=True)
class SessionCheckin:
    item: RecallItem
    today: bool | None
    streak: int
    last7: list[CheckinDay]


@dataclass(frozen=True)
class RecallSession:
    local_date: date
    checkins: list[SessionCheckin]
    cards: list[SessionCard]
    due_count: int
    new_count: int


@dataclass(frozen=True)
class RecallOutlook:
    due_tomorrow: int
    new_waiting: int


@dataclass(frozen=True)
class SelectedCard:
    item: RecallItem
    is_new: bool


def select_session_cards(
    items: Sequence[RecallItem],
    progress: Mapping[uuid.UUID, RecallProgress],
    local_date: date,
    seed: str,
) -> list[SelectedCard]:
    """Pick today's cards from active non-focus ``items`` (pure, no I/O).

    ``items`` must be oldest first; ``progress`` holds all of the learner's rows.

    - Cards already seen today are skipped, and so is every line on a cue that
      had a line seen today, so one cue's lines never blur together in a day.
    - Due cards come first, at most one line per cue (the most overdue), in an
      order shuffled by ``seed`` so a reload shows the same order.
    - Then up to ``MAX_NEW_PER_DAY`` never-seen cards (fewer if some were
      already started today), oldest first, skipping cues already in the session.
    - The whole list is capped at ``MAX_SESSION_CARDS``.
    """
    seen_today_cues = {
        item.cue_id
        for item in items
        if item.kind is RecallItemKind.line
        and (p := progress.get(item.id)) is not None
        and p.last_seen_on == local_date
    }
    candidates = [
        item
        for item in items
        if not (
            (p := progress.get(item.id)) is not None and p.last_seen_on == local_date
        )
        and not (item.kind is RecallItemKind.line and item.cue_id in seen_today_cues)
    ]

    due_sorted = sorted(
        (
            item
            for item in candidates
            if (p := progress.get(item.id)) is not None
            and p.due_on is not None
            and p.due_on <= local_date
        ),
        key=lambda item: (progress[item.id].due_on, item.created_at),
    )
    session_cues: set[uuid.UUID] = set()
    due: list[RecallItem] = []
    for item in due_sorted:
        if item.kind is RecallItemKind.line:
            if item.cue_id in session_cues:
                continue
            session_cues.add(item.cue_id)
        due.append(item)
    random.Random(seed).shuffle(due)

    started_today = sum(1 for p in progress.values() if p.first_seen_on == local_date)
    allowance = max(0, MAX_NEW_PER_DAY - started_today)
    new: list[RecallItem] = []
    for item in candidates:
        if len(new) >= allowance:
            break
        if item.id in progress:
            continue
        if item.kind is RecallItemKind.line:
            if item.cue_id in session_cues:
                continue
            session_cues.add(item.cue_id)
        new.append(item)

    selected = [SelectedCard(item=item, is_new=False) for item in due] + [
        SelectedCard(item=item, is_new=True) for item in new
    ]
    return selected[:MAX_SESSION_CARDS]


def _utc_today() -> date:
    return datetime.now(timezone.utc).date()


class RecallPracticeService:
    """Public practice: build the day's session, record views and check-ins."""

    def __init__(
        self,
        recall: RecallRepository,
        uow: UnitOfWork,
        today: Callable[[], date] = _utc_today,
    ) -> None:
        self._recall = recall
        self._uow = uow
        self._today = today

    async def get_session(self, learner_key: str, local_date: date) -> RecallSession:
        self._check_local_date(local_date)
        items = await self._recall.list_non_archived_items()
        progress = {p.item_id: p for p in await self._recall.list_progress(learner_key)}

        active = [item for item in items if item.status is RecallItemStatus.active]
        practicable = [item for item in active if item.kind is not RecallItemKind.focus]
        focus = [item for item in active if item.kind is RecallItemKind.focus]

        selected = select_session_cards(
            practicable, progress, local_date, seed=f"{learner_key}:{local_date}"
        )

        # Line positions count every non-archived line on the cue (paused too),
        # in creation order, matching what the admin sees.
        cue_lines: dict[uuid.UUID, list[uuid.UUID]] = {}
        for item in items:
            if item.kind is RecallItemKind.line and item.cue_id is not None:
                cue_lines.setdefault(item.cue_id, []).append(item.id)

        cards: list[SessionCard] = []
        for pick in selected:
            item = pick.item
            seen = progress.get(item.id)
            position = cue_line_count = None
            if item.kind is RecallItemKind.line and item.cue_id is not None:
                siblings = cue_lines.get(item.cue_id, [item.id])
                position = siblings.index(item.id) + 1
                cue_line_count = len(siblings)
            cards.append(
                SessionCard(
                    item=item,
                    is_new=pick.is_new,
                    seen_count=seen.seen_count if seen is not None else 0,
                    position=position,
                    cue_line_count=cue_line_count,
                )
            )

        checkins = await self._build_checkins(learner_key, focus, local_date)
        return RecallSession(
            local_date=local_date,
            checkins=checkins,
            cards=cards,
            due_count=sum(1 for card in cards if not card.is_new),
            new_count=sum(1 for card in cards if card.is_new),
        )

    async def get_outlook(self, learner_key: str, local_date: date) -> RecallOutlook:
        self._check_local_date(local_date)
        items = await self._recall.list_non_archived_items()
        progress = {p.item_id: p for p in await self._recall.list_progress(learner_key)}
        tomorrow = local_date + timedelta(days=1)

        practicable = [
            item
            for item in items
            if item.status is RecallItemStatus.active
            and item.kind is not RecallItemKind.focus
        ]
        due_tomorrow = sum(
            1
            for item in practicable
            if (p := progress.get(item.id)) is not None
            and p.due_on is not None
            and p.due_on <= tomorrow
        )
        new_waiting = sum(1 for item in practicable if item.id not in progress)
        return RecallOutlook(
            due_tomorrow=min(due_tomorrow, MAX_SESSION_CARDS), new_waiting=new_waiting
        )

    async def mark_seen(
        self, learner_key: str, item_id: uuid.UUID, local_date: date
    ) -> RecallProgress:
        self._check_local_date(local_date)
        item = await self._recall.find_item(item_id)
        if item is None or item.status is not RecallItemStatus.active:
            raise NotFoundError("item_not_found")
        if item.kind is RecallItemKind.focus:
            raise ValidationError("focus_items_use_checkins")

        async with self._uow.transaction():
            current = await self._recall.get_progress_for_update(learner_key, item_id)
            schedule = apply_seen(
                RecallSchedule(
                    seen_count=current.seen_count,
                    first_seen_on=current.first_seen_on,
                    last_seen_on=current.last_seen_on,
                    due_on=current.due_on,
                )
                if current is not None
                else None,
                local_date,
            )
            if current is not None and schedule.seen_count == current.seen_count:
                return current
            return await self._recall.save_progress(learner_key, item_id, schedule)

    async def record_checkin(
        self, learner_key: str, item_id: uuid.UUID, local_date: date, done: bool
    ) -> tuple[bool, int]:
        """Upsert today's yes/no for a focus item; returns ``(done, streak)``."""
        self._check_local_date(local_date)
        item = await self._recall.find_item(item_id)
        if (
            item is None
            or item.kind is not RecallItemKind.focus
            or item.status is not RecallItemStatus.active
        ):
            raise ValidationError("not_an_active_focus_item")

        async with self._uow.transaction():
            await self._recall.upsert_checkin(learner_key, item_id, local_date, done)

        history = await self._recall.list_checkins(
            learner_key, since=local_date - STREAK_LOOKBACK
        )
        done_by_date = {c.local_date: c.done for c in history if c.item_id == item_id}
        return done, compute_focus_streak(done_by_date, local_date)

    async def _build_checkins(
        self, learner_key: str, focus: list[RecallItem], local_date: date
    ) -> list[SessionCheckin]:
        if not focus:
            return []
        history = await self._recall.list_checkins(
            learner_key, since=local_date - STREAK_LOOKBACK
        )
        by_item: dict[uuid.UUID, dict[date, bool]] = {}
        for checkin in history:
            by_item.setdefault(checkin.item_id, {})[checkin.local_date] = checkin.done

        week = [local_date - timedelta(days=offset) for offset in range(6, -1, -1)]
        result: list[SessionCheckin] = []
        for item in focus:
            done_by_date = by_item.get(item.id, {})
            result.append(
                SessionCheckin(
                    item=item,
                    today=done_by_date.get(local_date),
                    streak=compute_focus_streak(done_by_date, local_date),
                    last7=[CheckinDay(date=d, done=done_by_date.get(d)) for d in week],
                )
            )
        return result

    def _check_local_date(self, local_date: date) -> None:
        if abs(local_date - self._today()) > LOCAL_DATE_TOLERANCE:
            raise ValidationError("local_date_out_of_range")
