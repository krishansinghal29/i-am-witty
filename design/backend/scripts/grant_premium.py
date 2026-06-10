from __future__ import annotations

import argparse
import asyncio
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.application.entitlement_service import EntitlementService
from app.infrastructure.db.engine import get_engine, get_session_factory
from app.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork
from app.infrastructure.repositories.pg_entitlement_repository import (
    PgEntitlementRepository,
)
from app.infrastructure.repositories.pg_user_repository import PgUserRepository


class _UnusedSubscriptionProvider:
    async def get_entitlements(self, app_user_id: str):
        raise RuntimeError("subscription provider is not used by this script")

    def parse_webhook(self, headers: dict[str, str], body: bytes):
        raise RuntimeError("subscription provider is not used by this script")


def _parse_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Grant manual Riffy+ access to an app user."
    )
    parser.add_argument("--app-user-id", required=True, type=uuid.UUID)
    parser.add_argument(
        "--expires-at",
        required=True,
        help="ISO-8601 timestamp, e.g. 2026-07-10T23:59:59Z",
    )
    parser.add_argument(
        "--starts-at",
        default=None,
        help="ISO-8601 timestamp. Defaults to now.",
    )
    parser.add_argument("--entitlement-key", default="riffy_plus")
    parser.add_argument("--granted-by", default="ops")
    parser.add_argument("--reason", default=None)
    return parser.parse_args()


async def _main() -> None:
    args = _parse_args()
    factory = get_session_factory()

    async with factory() as session:
        users = PgUserRepository(session)
        entitlements = PgEntitlementRepository(session)
        uow = SqlAlchemyUnitOfWork(session)
        service = EntitlementService(
            entitlements,
            users,
            _UnusedSubscriptionProvider(),
            uow,
        )
        grant = await service.grant_manual_premium(
            app_user_id=args.app_user_id,
            entitlement_key=args.entitlement_key,
            starts_at=(
                _parse_datetime(args.starts_at) if args.starts_at is not None else None
            ),
            expires_at=_parse_datetime(args.expires_at),
            granted_by=args.granted_by,
            reason=args.reason,
            metadata={"source": "scripts/grant_premium.py"},
        )

    await get_engine().dispose()
    print(
        "created manual premium grant "
        f"id={grant.id} "
        f"app_user_id={args.app_user_id} "
        f"entitlement_key={grant.entitlement_key} "
        f"starts_at={grant.starts_at.isoformat()} "
        f"expires_at={grant.expires_at.isoformat()} "
        f"reason={grant.reason!r}"
    )


if __name__ == "__main__":
    asyncio.run(_main())
