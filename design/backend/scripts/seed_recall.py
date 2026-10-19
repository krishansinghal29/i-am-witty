"""Seed Recall with the starting focus check-ins and lines.

Goes through RecallAdminService so the same validation (hint rules, required
fields) applies as in the admin UI. Safe to re-run: focus items are matched by
title and lines by cue + text, and anything already present is skipped.

Usage:
    uv run python scripts/seed_recall.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.application.recall_admin_service import RecallAdminService
from app.domain.models.recall import RecallItemKind
from app.infrastructure.db.engine import get_engine, get_session_factory
from app.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork
from app.infrastructure.repositories.pg_recall_repository import PgRecallRepository

SOURCE = "seed"

FOCUS = [
    {
        "title": "Sleep 8 hours",
        "question": "Did you get 8 hours of sleep last night?",
        "body": "Sleep is the base of your mental energy. Short sleep means flat energy when you go out.",
    },
    {
        "title": "Meditate for mental energy",
        "question": "Did you meditate in the last 24 hours?",
        "body": "Mental energy is the bottleneck for game, and meditation is what refills it.",
    },
]

# (cue text, cue type, hint, line, how to say it). Order matters: practice
# introduces new items oldest first, and a cue's lines are numbered in this order.
LINES = [
    ("You're such a player.", "reaction", "agree & amplify",
     "Only on weekends. Weekdays I'm a monk.",
     "Deadpan. Hold eye contact, smile only after."),
    ("You're such a player.", "reaction", "flip it",
     "Says the girl who's been staring at me for ten minutes.",
     "Smirk, tilt your head."),
    ("You're such a player.", "reaction", "misinterpret",
     "Player? Nobody's ever called me athletic before.",
     "Act flattered, hand on chest."),
    ("I'm not here to meet anyone.", "reaction", None,
     "Good, because I'm not that easy.",
     "Mock-serious."),
    ("Do you say that to every girl?", "reaction", "agree & amplify",
     "Only on Tuesdays. You got lucky.",
     "Deadpan."),
    ("Do you say that to every girl?", "reaction", "flip it",
     "Why, did you want to be special?",
     "Playful, lean back."),
    ("You're weird.", "reaction", None,
     "Thank you. Normal people are exhausting.",
     "Proud, not defensive."),
    ("I'm a really good dancer.", "reaction", None,
     "Prove it. One move, right now.",
     "Step back to give her room."),
    ("I drink coffee at night.", "reaction", None,
     "Euuu…",
     "Long and judgy. Eyebrows up, lean back, then grin."),
    ("Get her to qualify", "goal", "ambition",
     "So what do you do that actually excites you?",
     "Curious, then wait for her answer."),
    ("Get her to qualify", "goal", "standards",
     "Okay, but are you fun, or just pretty?",
     "Teasing smile."),
    ("Get her to qualify", "goal", "adventure",
     "Where would you take me if we had a free weekend?",
     "Lean in, let her build it."),
    ("Call her over", "goal", None,
     "Come here.",
     "Low and slow. Drop the pitch at the end. Say it once, then wait."),
    ("Lead her somewhere", "goal", None,
     "Come with me. I want to show you something.",
     "Start walking before she answers."),
]


async def _main() -> None:
    factory = get_session_factory()
    created = skipped = 0

    async with factory() as session:
        service = RecallAdminService(
            PgRecallRepository(session), SqlAlchemyUnitOfWork(session)
        )

        existing_focus = {
            item.title.lower()
            for item in await service.list_items(kind=RecallItemKind.focus)
            if item.title
        }
        for focus in FOCUS:
            if focus["title"].lower() in existing_focus:
                skipped += 1
                continue
            await service.create_item(
                RecallItemKind.focus, {**focus, "source": SOURCE}
            )
            created += 1

        existing_lines = {
            (item.cue.text.lower(), (item.body or "").lower())
            for item in await service.list_items(kind=RecallItemKind.line)
            if item.cue is not None
        }
        for cue_text, cue_type, hint, line, delivery in LINES:
            if (cue_text.lower(), line.lower()) in existing_lines:
                skipped += 1
                continue
            await service.create_item(
                RecallItemKind.line,
                {
                    "new_cue": {"text": cue_text, "type": cue_type},
                    "hint": hint,
                    "body": line,
                    "delivery_note": delivery,
                    "source": SOURCE,
                },
            )
            created += 1

    await get_engine().dispose()
    print(f"recall seed: created={created} skipped={skipped}")


if __name__ == "__main__":
    asyncio.run(_main())
