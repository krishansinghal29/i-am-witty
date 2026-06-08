"""Initialize a Neon development database.

Usage examples:

    uv run python scripts/init_dev_db.py --mode prod-copy --branch development
    uv run python scripts/init_dev_db.py --mode empty-config --branch development

Modes:
    prod-copy
        Reset the Neon branch to its parent and stop. This leaves the dev
        branch with the same schema and data as production.

    empty-config
        Reset the Neon branch to its parent, run Alembic migrations, truncate
        all application tables, then seed reference/config data only.

The script never prints database URLs or credentials. Neon authentication is
delegated to neonctl/neon, either through prior CLI auth or NEON_API_KEY.
It loads `.env.development` by default.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ENV_FILE = ROOT / ".env.development"
PROTECTED_BRANCH_NAMES = {"main", "master", "prod", "production"}
POSTGRES_URL_RE = re.compile(r"postgres(?:ql)?://[^\s'\"]+")


def _parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        values[key] = value
    return values


def _load_env_file(path: Path) -> bool:
    values = _parse_env_file(path)
    for key, value in values.items():
        os.environ[key] = value
    return bool(values)


def _redact(text: str) -> str:
    return POSTGRES_URL_RE.sub("postgresql://***", text)


def _run_quiet(cmd: list[str], *, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        cmd,
        cwd=cwd,
        env=os.environ.copy(),
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        detail = _redact((result.stderr or result.stdout or "").strip())
        raise RuntimeError(
            f"Command failed ({cmd[0]} exited {result.returncode})."
            + (f"\n{detail}" if detail else "")
        )
    return result


def _neon_executable() -> str:
    exe = shutil.which("neonctl") or shutil.which("neon")
    if exe is None:
        raise RuntimeError(
            "Neon CLI not found. Install neonctl/neon, authenticate it, or run "
            "with --skip-neon-reset after creating/resetting the branch manually."
        )
    return exe


def _append_neon_project(cmd: list[str], project_id: str | None) -> list[str]:
    if project_id:
        cmd.extend(["--project-id", project_id])
    return cmd


def _load_neon_branches(exe: str, project_id: str | None) -> list[dict[str, Any]]:
    cmd = _append_neon_project([exe, "branches", "list", "--output", "json"], project_id)
    result = _run_quiet(cmd)
    try:
        payload = __import__("json").loads(result.stdout or "[]")
    except Exception as exc:  # noqa: BLE001 - CLI output shape is external.
        raise RuntimeError("Could not parse Neon branch list JSON.") from exc
    if isinstance(payload, dict):
        branches = payload.get("branches", [])
    else:
        branches = payload
    if not isinstance(branches, list):
        raise RuntimeError("Unexpected Neon branch list response.")
    return [branch for branch in branches if isinstance(branch, dict)]


def _branch_exists(exe: str, branch: str, project_id: str | None) -> bool:
    branches = _load_neon_branches(exe, project_id)
    for item in branches:
        if item.get("id") == branch or item.get("name") == branch:
            return True
    return False


def _create_neon_branch(args: argparse.Namespace, exe: str) -> None:
    cmd = [
        exe,
        "branches",
        "create",
        "--name",
        args.branch,
        "--parent",
        args.parent,
        "--output",
        "json",
    ]
    _append_neon_project(cmd, args.project_id)
    _run_quiet(cmd)
    print(f"Created Neon branch '{args.branch}' from parent '{args.parent}'.")


def _reset_neon_branch(args: argparse.Namespace) -> None:
    exe = _neon_executable()
    if args.create_if_missing and not _branch_exists(exe, args.branch, args.project_id):
        _create_neon_branch(args, exe)

    cmd = [exe, "branches", "reset", args.branch, "--parent"]
    if args.preserve_under_name:
        cmd.extend(["--preserve-under-name", args.preserve_under_name])
    _append_neon_project(cmd, args.project_id)
    _run_quiet(cmd)
    print(f"Reset Neon branch '{args.branch}' from its parent.")


def _get_branch_connection_string(
    args: argparse.Namespace, *, pooled: bool
) -> str:
    exe = _neon_executable()
    cmd = [exe, "connection-string", args.branch]
    if pooled:
        cmd.append("--pooled")
    if args.database_name:
        cmd.extend(["--database-name", args.database_name])
    if args.role_name:
        cmd.extend(["--role-name", args.role_name])
    _append_neon_project(cmd, args.project_id)
    result = _run_quiet(cmd)
    match = POSTGRES_URL_RE.search(result.stdout or "")
    if match is None:
        raise RuntimeError(
            "Neon CLI did not return a connection string. If your branch has "
            "multiple roles or databases, pass --role-name and --database-name."
        )
    return match.group(0)


def _install_branch_connection_urls(args: argparse.Namespace) -> None:
    if args.use_env_database_url:
        print("Using DATABASE_URL/DATABASE_URL_DIRECT from the loaded environment.")
        return

    os.environ["DATABASE_URL_DIRECT"] = _get_branch_connection_string(
        args, pooled=False
    )
    os.environ["DATABASE_URL"] = _get_branch_connection_string(args, pooled=True)
    print(f"Loaded direct and pooled connection strings for branch '{args.branch}'.")


def _confirm(args: argparse.Namespace) -> None:
    if args.yes:
        return
    action = (
        "reset the branch"
        if args.mode == "prod-copy"
        else "reset the branch, truncate application data, and reseed reference data"
    )
    if not sys.stdin.isatty():
        raise RuntimeError(f"Confirmation required to {action}; rerun with --yes.")
    expected = args.branch
    actual = input(f"Type '{expected}' to {action}: ").strip()
    if actual != expected:
        raise RuntimeError("Confirmation did not match; aborting.")


def _validate_target(args: argparse.Namespace) -> None:
    app_env = os.environ.get("APP_ENV", "development").strip().lower()
    if app_env == "production":
        raise RuntimeError("Refusing to initialize a database while APP_ENV=production.")
    if args.branch.strip().lower() in PROTECTED_BRANCH_NAMES:
        raise RuntimeError(
            f"Refusing to operate on protected branch name '{args.branch}'. "
            "Use a non-production branch such as 'development'."
        )
    if args.skip_neon_reset and args.mode == "prod-copy":
        raise RuntimeError("prod-copy mode has no work to do with --skip-neon-reset.")
    if (
        args.mode == "empty-config"
        and args.skip_neon_reset
        and not args.use_env_database_url
    ):
        raise RuntimeError(
            "--skip-neon-reset in empty-config mode requires "
            "--use-env-database-url so the destructive target is explicit."
        )


def _run_alembic_upgrade() -> None:
    from alembic import command
    from alembic.config import Config

    config = Config(str(ROOT / "alembic.ini"))
    command.upgrade(config, "head")
    print("Applied Alembic migrations to head.")


def _register_orm_tables() -> None:
    import app.infrastructure.db.orm.billing  # noqa: F401
    import app.infrastructure.db.orm.comms  # noqa: F401
    import app.infrastructure.db.orm.config  # noqa: F401
    import app.infrastructure.db.orm.onboarding  # noqa: F401
    import app.infrastructure.db.orm.plans  # noqa: F401
    import app.infrastructure.db.orm.tasks  # noqa: F401
    import app.infrastructure.db.orm.users  # noqa: F401


def _admin_url():
    from app.infrastructure.db.dsn import normalize_async_dsn

    raw_url = os.environ.get("DATABASE_URL_DIRECT") or os.environ.get("DATABASE_URL")
    if not raw_url:
        raise RuntimeError("DATABASE_URL_DIRECT or DATABASE_URL is required.")
    return normalize_async_dsn(raw_url)


def _connect_args(url):
    from app.infrastructure.db.dsn import build_connect_args

    return build_connect_args(url)


def _qualified_table_name(table: sa.Table, dialect) -> str:
    preparer = dialect.identifier_preparer
    name = preparer.quote(table.name)
    if table.schema:
        return f"{preparer.quote_schema(table.schema)}.{name}"
    return name


async def _create_admin_engine():
    url = _admin_url()
    return create_async_engine(
        url,
        poolclass=NullPool,
        connect_args=_connect_args(url),
    )


async def _truncate_application_tables() -> int:
    from app.infrastructure.db.orm.base import Base

    _register_orm_tables()
    tables = list(Base.metadata.sorted_tables)
    if not tables:
        return 0

    engine = await _create_admin_engine()
    try:
        dialect = engine.sync_engine.dialect
        names = [_qualified_table_name(table, dialect) for table in tables]
        sql = "TRUNCATE TABLE " + ", ".join(names) + " RESTART IDENTITY CASCADE"
        async with engine.begin() as conn:
            await conn.execute(sa.text(sql))
    finally:
        await engine.dispose()
    print(f"Truncated {len(tables)} application tables.")
    return len(tables)


async def _seed_reference_data() -> None:
    from app.infrastructure.db import seed_reference_data

    engine = await _create_admin_engine()
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    try:
        async with session_factory() as session:
            async with session.begin():
                counts = await seed_reference_data.seed_all(session)

        print("--- seed summary (rows upserted) ---")
        for table, count in counts.items():
            print(f"{table:22s}: {count}")

        async with session_factory() as session:
            await seed_reference_data.verify(session)
    finally:
        await engine.dispose()


def _build_parser(pre_parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Initialize a Neon development database branch.",
        parents=[pre_parser],
    )
    parser.add_argument("--mode", choices=("prod-copy", "empty-config"), required=True)
    parser.add_argument(
        "--branch",
        default=os.environ.get("NEON_DEV_BRANCH", "development"),
        help="Target Neon development branch name or id.",
    )
    parser.add_argument(
        "--parent",
        default=os.environ.get("NEON_PARENT_BRANCH", "production"),
        help="Parent branch used only when --create-if-missing creates the branch.",
    )
    parser.add_argument(
        "--project-id",
        default=os.environ.get("NEON_PROJECT_ID"),
        help="Neon project id. Optional if neonctl/neon context already has one.",
    )
    parser.add_argument(
        "--database-name",
        default=os.environ.get("NEON_DATABASE_NAME"),
        help="Neon database name. Required only when the branch has multiple databases.",
    )
    parser.add_argument(
        "--role-name",
        default=os.environ.get("NEON_ROLE_NAME"),
        help="Neon role name. Required only when the branch has multiple roles.",
    )
    parser.add_argument(
        "--create-if-missing",
        action="store_true",
        help="Create the target branch from --parent before resetting it if absent.",
    )
    parser.add_argument(
        "--skip-neon-reset",
        action="store_true",
        help="Do not call Neon CLI. Useful after manually preparing the target DB.",
    )
    parser.add_argument(
        "--use-env-database-url",
        action="store_true",
        help=(
            "Use DATABASE_URL/DATABASE_URL_DIRECT from env instead of fetching "
            "target-branch URLs from Neon CLI."
        ),
    )
    parser.add_argument(
        "--preserve-under-name",
        help="Pass through to Neon branch reset to preserve the previous branch state.",
    )
    parser.add_argument(
        "--skip-migrations",
        action="store_true",
        help="For empty-config only: skip Alembic upgrade before truncating/seeding.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip the interactive confirmation prompt.",
    )
    return parser


def _parse_args() -> argparse.Namespace:
    pre_parser = argparse.ArgumentParser(add_help=False)
    pre_parser.add_argument(
        "--env-file",
        default=str(DEFAULT_ENV_FILE),
        help="Env file to load before running. Defaults to .env.development.",
    )
    if any(arg in {"-h", "--help"} for arg in sys.argv[1:]):
        return _build_parser(pre_parser).parse_args()

    pre_args, remaining = pre_parser.parse_known_args()
    env_path = Path(pre_args.env_file).expanduser()
    if not env_path.is_absolute():
        env_path = ROOT / env_path
    _load_env_file(env_path)

    parser = _build_parser(pre_parser)
    return parser.parse_args(remaining)


def main() -> int:
    try:
        args = _parse_args()
        _validate_target(args)
        _confirm(args)

        if not args.skip_neon_reset:
            _reset_neon_branch(args)

        if args.mode == "prod-copy":
            print("Done. No migrations, truncation, or seed changes were applied.")
            return 0

        _install_branch_connection_urls(args)

        if not args.skip_migrations:
            _run_alembic_upgrade()

        asyncio.run(_truncate_application_tables())
        asyncio.run(_seed_reference_data())
        print("Done. Empty dev database now has reference data only.")
        return 0
    except Exception as exc:  # noqa: BLE001 - command-line failure boundary.
        print(f"ERROR: {_redact(str(exc))}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
