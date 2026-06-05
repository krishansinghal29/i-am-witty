"""Idempotent reference/config data seeder.

Run with::

    uv run python -m app.infrastructure.db.seed

Upserts the canonical task types, representative tasks, and product config
rows using Postgres ``INSERT ... ON CONFLICT DO UPDATE`` so repeated runs never
create duplicates or error. Everything happens inside a single transaction via
the async session factory.

Security: this script never reads, prints, or echoes the database URL,
credentials, or any connection string. Configuration and the engine are loaded
through the existing application wiring (``app.settings`` /
``app.infrastructure.db.engine``). Output is limited to row counts and the
seeded identifiers.
"""

from __future__ import annotations

import asyncio

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.engine import get_session_factory
from app.infrastructure.db.orm.config import AppConfig, FeatureGateDefault
from app.infrastructure.db.orm.tasks import (
    Task,
    TaskAccessTier,
    TaskStatus,
    TaskType,
)

# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------
# task_types: transcribed faithfully from design/tasks_trimmed.md
# ("## `task_types` Seed"). The doc's "metadata" object maps to the ORM
# attribute `type_metadata` (DB column "metadata").
TASK_TYPES: list[dict] = [
    {
        "id": "voice_single_prompt",
        "display_name": "Voice Single Prompt",
        "description": "One generated prompt, one spoken response, one feedback result.",
        "ui_schema_key": "voice_single_prompt_v1",
        "runtime_engine_key": "voice_prompt_v1",
        "default_duration_seconds": 30,
        "is_active": True,
        "sort_order": 10,
        "type_metadata": {
            "supports_tts": True,
            "supports_avatar": True,
            "supports_assigned_technique": True,
            "supports_scaffold_stages": False,
        },
    },
    {
        "id": "voice_dialogue_prompt",
        "display_name": "Voice Dialogue Prompt",
        "description": "Two or more generated speaker messages, one spoken response, one feedback result.",
        "ui_schema_key": "voice_dialogue_prompt_v1",
        "runtime_engine_key": "voice_prompt_v1",
        "default_duration_seconds": 30,
        "is_active": True,
        "sort_order": 20,
        "type_metadata": {
            "supports_tts": True,
            "supports_avatar": True,
            "supports_assigned_technique": False,
            "supports_scaffold_stages": False,
        },
    },
    {
        "id": "voice_scaffolded_prompt",
        "display_name": "Voice Scaffolded Prompt",
        "description": "One generated prompt with guided rehearsal stages before the final evaluated response.",
        "ui_schema_key": "voice_scaffolded_prompt_v1",
        "runtime_engine_key": "voice_prompt_v1",
        "default_duration_seconds": 30,
        "is_active": True,
        "sort_order": 30,
        "type_metadata": {
            "supports_tts": True,
            "supports_avatar": True,
            "supports_assigned_technique": False,
            "supports_scaffold_stages": True,
        },
    },
]

# tasks: the three representative task seeds, transcribed faithfully from
# "## Task Type 1/2/3". `content` and `runtime_config` are copied exactly from
# the doc. Schema-required/optional fields absent from the doc seed are filled
# per the agreed conventions (thumbnail_key/image_key = slug, access_tier=free,
# status=active, sort_order 10/20/30). `task_metadata` ("metadata" column) is
# omitted so the DB default `{}` applies.
TASKS: list[dict] = [
    {
        "slug": "misinterpretation-techniques",
        "title": "Misinterpretation: Techniques",
        "description": "Apply a specific misinterpretation technique to an ordinary sentence.",
        "task_type_id": "voice_single_prompt",
        "duration_seconds": 30,
        "thumbnail_key": "misinterpretation-techniques",
        "image_key": "misinterpretation-techniques",
        "access_tier": TaskAccessTier.free,
        "status": TaskStatus.active,
        "sort_order": 10,
        "content": {
            "exercise_key": "misinterpretationTechniques",
            "prompt_label": "Tease/Statement",
            "prompt_roles": ["She"],
            "response_instruction": "Use the assigned technique to misread the sentence.",
            "recording_limit_seconds": 30,
            "assigned_technique_mode": "runtime_generated",
            "scaffold_stages": [],
            "feedback_tabs": {
                "feedback_label": "Feedback",
                "sample_answer_label": "Better Way",
            },
        },
        "runtime_config": {
            "backend_key": "misinterpretationTechniques",
            "prompt_bundle_key": "misinterpretation_techniques_v1",
            "generator": {
                "strategy": "verb_seed",
                "output_shape": "single_message",
                "message_role": "She",
            },
            "assigned_technique": {
                "strategy": "random_choice",
                "source": "misinterpretation_techniques",
            },
            "evaluator": {
                "strategy": "transcript_feedback",
                "criteria": [
                    "technique_match",
                    "litmus_test",
                    "commitment",
                    "fit",
                    "brevity",
                ],
            },
        },
    },
    {
        "slug": "question-answer-tease",
        "title": "Question Answer Tease",
        "description": "Turn a direct answer into a playful tease.",
        "task_type_id": "voice_dialogue_prompt",
        "duration_seconds": 30,
        "thumbnail_key": "question-answer-tease",
        "image_key": "question-answer-tease",
        "access_tier": TaskAccessTier.free,
        "status": TaskStatus.active,
        "sort_order": 20,
        "content": {
            "exercise_key": "questionAnswerTease",
            "prompt_label": "Question",
            "prompt_roles": ["You", "She"],
            "response_instruction": "Tease her answer playfully without insulting or interviewing.",
            "recording_limit_seconds": 30,
            "assigned_technique_mode": "none",
            "scaffold_stages": [],
            "feedback_tabs": {
                "feedback_label": "Feedback",
                "sample_answer_label": "Better Way",
            },
        },
        "runtime_config": {
            "backend_key": "questionAnswerTease",
            "prompt_bundle_key": "question_answer_tease_v1",
            "generator": {
                "strategy": "creative_prompt",
                "output_shape": "dialogue_two_message",
                "message_roles": ["You", "She"],
            },
            "evaluator": {
                "strategy": "transcript_feedback",
                "criteria": ["frame", "tone", "specificity", "brevity"],
            },
        },
    },
    {
        "slug": "push-pull",
        "title": "Push/Pull",
        "description": "Balance genuine interest with playful challenge.",
        "task_type_id": "voice_scaffolded_prompt",
        "duration_seconds": 30,
        "thumbnail_key": "push-pull",
        "image_key": "push-pull",
        "access_tier": TaskAccessTier.free,
        "status": TaskStatus.active,
        "sort_order": 30,
        "content": {
            "exercise_key": "pushPull",
            "prompt_label": "Scenario",
            "prompt_roles": ["She"],
            "response_instruction": "Build a push, a pull, then combine them.",
            "recording_limit_seconds": 30,
            "assigned_technique_mode": "none",
            "scaffold_stages": [
                {
                    "position": 1,
                    "label": "Step 1 of 3",
                    "title": "Push",
                    "instruction": "Say just the push: one sentence, no softening.",
                    "is_final_submission": False,
                },
                {
                    "position": 2,
                    "label": "Step 2 of 3",
                    "title": "Pull",
                    "instruction": "Say just the genuine compliment: no irony.",
                    "is_final_submission": False,
                },
                {
                    "position": 3,
                    "label": "Step 3 of 3",
                    "title": "Combine",
                    "instruction": "Combine them into one push-pull line.",
                    "is_final_submission": True,
                },
            ],
            "feedback_tabs": {
                "feedback_label": "Feedback",
                "sample_answer_label": "Better Way",
            },
        },
        "runtime_config": {
            "backend_key": "pushPull",
            "prompt_bundle_key": "push_pull_v1",
            "generator": {
                "strategy": "weighted_seed",
                "output_shape": "single_message",
                "message_role": "She",
            },
            "evaluator": {
                "strategy": "transcript_feedback",
                "evaluate_stage": "final",
                "criteria": [
                    "both_sides_present",
                    "trivial_push",
                    "genuine_pull",
                    "tension",
                    "brevity",
                    "naturalness",
                ],
            },
        },
    },
]

# app_config: product defaults (not in tasks_trimmed.md). `value` is stored as
# jsonb; placeholders are flagged in their descriptions.
APP_CONFIG: list[dict] = [
    {
        "key": "free_task_limit",
        "value": 3,
        "is_public": True,
        "description": "Authoritative daily free-task limit for non-subscribers.",
    },
    {
        "key": "telegram_community_url",
        "value": "https://t.me/iamwitty",
        "is_public": True,
        "description": "Telegram community link (placeholder — update with real URL).",
    },
    {
        "key": "terms_url",
        "value": "https://i-am-witty.app/terms",
        "is_public": True,
        "description": "Terms of Service URL (placeholder).",
    },
    {
        "key": "privacy_url",
        "value": "https://i-am-witty.app/privacy",
        "is_public": True,
        "description": "Privacy Policy URL (placeholder).",
    },
]

# feature_gate_defaults: product defaults (not in tasks_trimmed.md).
FEATURE_GATES: list[dict] = [
    {
        "feature_key": "role_play",
        "default_enabled": False,
        "requires_entitlement": "witty_plus",
        "min_app_version": None,
    },
    {
        "feature_key": "witty_plus",
        "default_enabled": True,
        "requires_entitlement": None,
        "min_app_version": None,
    },
    {
        "feature_key": "premium_task_library",
        "default_enabled": True,
        "requires_entitlement": "witty_plus",
        "min_app_version": None,
    },
]


# ---------------------------------------------------------------------------
# Seed functions
# ---------------------------------------------------------------------------
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
            # ORM attr `type_metadata` -> DB column "metadata".
            "metadata": stmt.excluded["metadata"],
            "updated_at": func.now(),
        },
    )
    await session.execute(stmt)
    return len(TASK_TYPES)


async def seed_tasks(session: AsyncSession) -> int:
    """Upsert tasks on conflict of the unique `slug`.

    `task_metadata` ("metadata") is intentionally left untouched so the DB
    default applies on insert and any existing value is preserved on update.
    """
    stmt = pg_insert(Task).values(TASKS)
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


# ---------------------------------------------------------------------------
# Verification (read-only; prints counts/identifiers only, never secrets)
# ---------------------------------------------------------------------------
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

    print("--- verification ---")
    print(f"task_types rows           : {task_type_count} (expected 3)")
    print(f"tasks rows                : {task_count} (expected 3)")
    print(f"app_config rows           : {app_config_count} (expected 4)")
    print(f"feature_gate_defaults rows: {feature_gate_count} (expected 3)")

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
        content_ok = bool(content)
        runtime_ok = bool(runtime_config)
        print(
            f"  {slug:30s} -> {task_type_id:25s} | "
            f"content={'non-empty' if content_ok else 'EMPTY'}, "
            f"runtime_config={'non-empty' if runtime_ok else 'EMPTY'}"
        )

    free_task_limit = await session.scalar(
        select(AppConfig.value).where(AppConfig.key == "free_task_limit")
    )
    print(
        f"app_config.free_task_limit value == 3: {free_task_limit == 3} "
        f"(value={free_task_limit!r})"
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
async def main() -> None:
    session_factory = get_session_factory()

    async with session_factory() as session:
        async with session.begin():
            counts = {
                "task_types": await seed_task_types(session),
                "tasks": await seed_tasks(session),
                "app_config": await seed_app_config(session),
                "feature_gate_defaults": await seed_feature_gates(session),
            }

    print("--- seed summary (rows upserted) ---")
    for table, count in counts.items():
        print(f"{table:22s}: {count}")

    async with session_factory() as session:
        await verify(session)


if __name__ == "__main__":
    asyncio.run(main())
