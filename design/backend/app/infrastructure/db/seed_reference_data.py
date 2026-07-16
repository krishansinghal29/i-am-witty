"""Idempotent reference/config data seeder.

Run with:

    uv run python -m app.infrastructure.db.seed_reference_data

This module contains the write methods for canonical reference data. The row
definitions live in ``app.infrastructure.db.reference_data`` so product data is
kept separate from database write behavior.
"""

from __future__ import annotations

import asyncio
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.orm.config import (
    AppConfig,
    AppReleaseChannel,
    FeatureGateDefault,
)
from app.infrastructure.db.orm.tasks import (
    Task,
    TaskAccessTier,
    TaskStatus,
    TaskType,
)
from app.infrastructure.db.reference_data.app_config import (
    APP_CONFIG,
    APP_RELEASE_CHANNELS,
    FEATURE_GATES,
)
from app.infrastructure.db.reference_data.task_catalog import TASK_TYPES, TASKS


def _task_values() -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    for row in TASKS:
        values.append(
            {
                **row,
                "access_tier": TaskAccessTier(row["access_tier"]),
                "status": TaskStatus(row["status"]),
            }
        )
    return values


async def seed_task_types(session: AsyncSession) -> int:
    """Upsert task_types on conflict of the text PK `id`."""
    stmt = pg_insert(TaskType).values(TASK_TYPES)
    stmt = stmt.on_conflict_do_update(
        index_elements=[TaskType.id],
        set_={
            "display_name": stmt.excluded.display_name,
            "description": stmt.excluded.description,
            "ui_schema_key": stmt.excluded.ui_schema_key,
            "runtime_engine_key": stmt.excluded.runtime_engine_key,
            "default_duration_seconds": stmt.excluded.default_duration_seconds,
            "is_active": stmt.excluded.is_active,
            "sort_order": stmt.excluded.sort_order,
            "metadata": stmt.excluded["metadata"],
            "updated_at": func.now(),
        },
    )
    await session.execute(stmt)
    return len(TASK_TYPES)


async def seed_tasks(session: AsyncSession) -> int:
    """Upsert tasks on conflict of the unique `slug`."""
    stmt = pg_insert(Task).values(_task_values())
    stmt = stmt.on_conflict_do_update(
        index_elements=[Task.slug],
        set_={
            "title": stmt.excluded.title,
            "description": stmt.excluded.description,
            "task_type_id": stmt.excluded.task_type_id,
            "duration_seconds": stmt.excluded.duration_seconds,
            "thumbnail_key": stmt.excluded.thumbnail_key,
            "image_key": stmt.excluded.image_key,
            "content": stmt.excluded.content,
            "runtime_config": stmt.excluded.runtime_config,
            "access_tier": stmt.excluded.access_tier,
            "status": stmt.excluded.status,
            "sort_order": stmt.excluded.sort_order,
            "updated_at": func.now(),
        },
    )
    await session.execute(stmt)
    return len(TASKS)


async def seed_app_config(session: AsyncSession) -> int:
    """Upsert app_config on conflict of the PK `key`."""
    stmt = pg_insert(AppConfig).values(APP_CONFIG)
    stmt = stmt.on_conflict_do_update(
        index_elements=[AppConfig.key],
        set_={
            "value": stmt.excluded.value,
            "is_public": stmt.excluded.is_public,
            "description": stmt.excluded.description,
            "updated_at": func.now(),
        },
    )
    await session.execute(stmt)
    return len(APP_CONFIG)


async def seed_feature_gates(session: AsyncSession) -> int:
    """Upsert feature_gate_defaults on conflict of the PK `feature_key`."""
    stmt = pg_insert(FeatureGateDefault).values(FEATURE_GATES)
    stmt = stmt.on_conflict_do_update(
        index_elements=[FeatureGateDefault.feature_key],
        set_={
            "default_enabled": stmt.excluded.default_enabled,
            "requires_entitlement": stmt.excluded.requires_entitlement,
            "min_app_version": stmt.excluded.min_app_version,
            "updated_at": func.now(),
        },
    )
    await session.execute(stmt)
    return len(FEATURE_GATES)


async def seed_app_release_channels(session: AsyncSession) -> int:
    """Upsert app_release_channels on conflict of the PK `channel_key`."""
    stmt = pg_insert(AppReleaseChannel).values(APP_RELEASE_CHANNELS)
    stmt = stmt.on_conflict_do_update(
        index_elements=[AppReleaseChannel.channel_key],
        set_={
            "min_supported_version": stmt.excluded.min_supported_version,
            "latest_version": stmt.excluded.latest_version,
            "is_active": stmt.excluded.is_active,
            "metadata": stmt.excluded["metadata"],
            "updated_at": func.now(),
        },
    )
    await session.execute(stmt)
    return len(APP_RELEASE_CHANNELS)


async def seed_all(session: AsyncSession) -> dict[str, int]:
    return {
        "task_types": await seed_task_types(session),
        "tasks": await seed_tasks(session),
        "app_config": await seed_app_config(session),
        "feature_gate_defaults": await seed_feature_gates(session),
        "app_release_channels": await seed_app_release_channels(session),
    }


async def verify(session: AsyncSession) -> None:
    task_type_count = await session.scalar(
        select(func.count()).select_from(TaskType)
    )
    task_count = await session.scalar(select(func.count()).select_from(Task))
    app_config_count = await session.scalar(
        select(func.count()).select_from(AppConfig)
    )
    feature_gate_count = await session.scalar(
        select(func.count()).select_from(FeatureGateDefault)
    )
    app_release_channel_count = await session.scalar(
        select(func.count()).select_from(AppReleaseChannel)
    )

    print("--- verification ---")
    print(f"task_types rows           : {task_type_count} (expected {len(TASK_TYPES)})")
    print(f"tasks rows                : {task_count} (expected {len(TASKS)})")
    print(f"app_config rows           : {app_config_count} (expected {len(APP_CONFIG)})")
    print(
        "feature_gate_defaults rows: "
        f"{feature_gate_count} (expected {len(FEATURE_GATES)})"
    )
    print(
        "app_release_channels rows : "
        f"{app_release_channel_count} (expected {len(APP_RELEASE_CHANNELS)})"
    )

    print("tasks (slug -> task_type_id | content/runtime_config non-empty):")
    rows = (
        await session.execute(
            select(
                Task.slug,
                Task.task_type_id,
                Task.content,
                Task.runtime_config,
            ).order_by(Task.sort_order)
        )
    ).all()
    for slug, task_type_id, content, runtime_config in rows:
        print(
            f"  {slug:30s} -> {task_type_id:25s} | "
            f"content={'non-empty' if content else 'EMPTY'}, "
            f"runtime_config={'non-empty' if runtime_config else 'EMPTY'}"
        )

    free_task_limit = await session.scalar(
        select(AppConfig.value).where(AppConfig.key == "free_task_limit")
    )
    expected_limit = next(
        r["value"] for r in APP_CONFIG if r["key"] == "free_task_limit"
    )
    print(
        f"app_config.free_task_limit value == {expected_limit}: "
        f"{free_task_limit == expected_limit} (value={free_task_limit!r})"
    )


async def main() -> None:
    from app.infrastructure.db.engine import get_session_factory

    session_factory = get_session_factory()

    async with session_factory() as session:
        async with session.begin():
            counts = await seed_all(session)

    print("--- seed summary (rows upserted) ---")
    for table, count in counts.items():
        print(f"{table:22s}: {count}")

    async with session_factory() as session:
        await verify(session)


if __name__ == "__main__":
    asyncio.run(main())
