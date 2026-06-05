from __future__ import annotations

from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo


def local_today(tz_name: str, now: datetime | None = None) -> date:
    """Calendar date in the user's timezone (daily-boundary logic depends on it).

    ``now`` is injectable so callers/tests can pin the instant; when omitted the
    current UTC instant is used. A bad ``tz_name`` falls back to UTC so a single
    malformed profile can never break streak/limit math.
    """
    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        tz = timezone.utc
    moment = now if now is not None else datetime.now(timezone.utc)
    return moment.astimezone(tz).date()


def week_start(day: date) -> date:
    """Monday of the week containing ``day`` (used for week activity grids)."""
    from datetime import timedelta

    return day - timedelta(days=day.weekday())
