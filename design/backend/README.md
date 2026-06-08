## Database setup

Schema and data are initialized in two separate steps:

```bash
uv run alembic upgrade head
uv run python -m app.infrastructure.db.seed_reference_data
```

Alembic migrations own schema changes only. Reference/catalog rows live under
`app/infrastructure/db/reference_data/`, and
`app.infrastructure.db.seed_reference_data` applies them idempotently with
Postgres upserts.

## Dev database initialization

Use `scripts/init_dev_db.py` for a Neon development branch. It loads
`.env.development` by default and never prints database URLs.

Create or refresh a dev branch with the same schema and data as production:

```bash
uv run python scripts/init_dev_db.py --mode prod-copy --branch development
```

Create or refresh a dev branch, then wipe app data and keep only reference/config
rows:

```bash
uv run python scripts/init_dev_db.py --mode empty-config --branch development
```

For `empty-config`, the script resets the branch, fetches that branch's direct
and pooled connection strings from Neon CLI, runs migrations against the direct
URL, truncates application tables, and applies reference data. This avoids
trusting a stale `DATABASE_URL` from another env file.

Useful options:

```bash
--project-id <neon-project-id>   # optional if Neon CLI context is configured
--database-name neondb           # needed if the branch has multiple databases
--role-name <role>               # needed if the branch has multiple roles
--create-if-missing              # create the dev branch from --parent first
--parent production              # branch parent used with --create-if-missing
--skip-neon-reset                # use after manually preparing the branch
--use-env-database-url           # required with --skip-neon-reset for empty-config
--yes                            # skip interactive confirmation
```
