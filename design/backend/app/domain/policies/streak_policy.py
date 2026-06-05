from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class StreakUpdate:
    current_streak: int
    longest_streak: int
    last_qualified_date: date


def qualifies_for_streak(completed_task_count_today: int) -> bool:
    """A day qualifies for the streak once the user completes >=1 task."""
    return completed_task_count_today >= 1


def compute_streak_update(
    current_streak: int,
    longest_streak: int,
    last_qualified_date: date | None,
    today: date,
) -> StreakUpdate:
    """Advance the forgiving streak using only dates (pure, no I/O).

    Rules:
    - `last_qualified_date == today`: idempotent no-op (today already counted).
    - `last_qualified_date == today - 1 day`: consecutive day, current += 1.
    - `last_qualified_date is None` or any gap > 1 day: reset current to 1.

    `longest_streak` is raised to the new current whenever it grows.

    "Forgiving" note (functional req §5): this policy deliberately sees only
    dates. A day where the user hit the free-task limit can still be treated as
    streak-protected by the caller advancing `last_qualified_date` to that day
    (e.g. via `user_day_activity.streak_protected`), so the next qualifying day
    still reads as consecutive here. Whether to protect a day is the caller's
    decision; the arithmetic below stays simple and deterministic.
    """
    if last_qualified_date == today:
        return StreakUpdate(
            current_streak=current_streak,
            longest_streak=longest_streak,
            last_qualified_date=today,
        )

    if last_qualified_date is not None and (
        last_qualified_date == today - timedelta(days=1)
    ):
        new_current = current_streak + 1
    else:
        new_current = 1

    return StreakUpdate(
        current_streak=new_current,
        longest_streak=max(longest_streak, new_current),
        last_qualified_date=today,
    )
