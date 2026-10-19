from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, timedelta

# Days until a card is due again after its 1st, 2nd, ... 6th+ view. There are
# no ratings, so spacing grows with exposure alone.
LADDER_DAYS: tuple[int, ...] = (1, 2, 4, 7, 14, 30)


@dataclass(frozen=True)
class RecallSchedule:
    seen_count: int
    first_seen_on: date | None
    last_seen_on: date | None
    due_on: date | None


def apply_seen(current: RecallSchedule | None, local_date: date) -> RecallSchedule:
    """Advance a card's schedule for one "Next" tap (pure, no I/O).

    Rules:
    - Already seen on ``local_date`` (or a later date): idempotent no-op, so a
      double tap or a replayed request never counts twice.
    - Otherwise ``seen_count`` grows by one and the card is due again after the
      ladder step for that count (capped at the last step).
    """
    if current is None:
        current = RecallSchedule(
            seen_count=0, first_seen_on=None, last_seen_on=None, due_on=None
        )
    if current.last_seen_on is not None and local_date <= current.last_seen_on:
        return current

    seen_count = current.seen_count + 1
    step = LADDER_DAYS[min(seen_count, len(LADDER_DAYS)) - 1]
    return RecallSchedule(
        seen_count=seen_count,
        first_seen_on=current.first_seen_on or local_date,
        last_seen_on=local_date,
        due_on=local_date + timedelta(days=step),
    )


def compute_focus_streak(done_by_date: Mapping[date, bool], local_date: date) -> int:
    """Consecutive "yes" days for one focus item (pure, no I/O).

    A "no" today breaks the streak to 0. If today is still unanswered, the
    streak counts back from yesterday so it doesn't reset before you check in.
    """
    today = done_by_date.get(local_date)
    if today is False:
        return 0

    cursor = local_date if today is True else local_date - timedelta(days=1)
    streak = 0
    while done_by_date.get(cursor) is True:
        streak += 1
        cursor -= timedelta(days=1)
    return streak
