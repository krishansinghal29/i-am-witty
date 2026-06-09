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

## Deploy

```bash
./deploy.sh
```

Deploys to Cloud Run (`iamwitty-backend`, region `us-east1`, project `i-am-witty`).
`.env` is the single source of truth: `scripts/make_run_env.py` translates its
allowlisted keys (`RUNTIME_KEYS`) into an ephemeral Cloud Run env file at deploy
time. To ship a new runtime env var, add it to both `.env` and `RUNTIME_KEYS`.

## Over-the-air updates (self-hosted Capgo)

The native app's `@capgo/capacitor-updater` polls `POST /v1/ota/check`
(`app/api/routes/ota.py`) for new web-layer bundles, so we run OTA off our own
backend + a public GCS bucket — no Capgo cloud, no subscription. Bundles are
published from `frontend/deploy_ota.sh`; the device downloads the zip directly
from GCS and this endpoint only answers "is there a newer bundle?".

Env (`.env` → Cloud Run):

```
OTA_ENABLED=true                                                  # false = instant kill switch
OTA_POINTER_URL=https://storage.googleapis.com/riffy-ota/ota/production.json
```

- **Kill switch (all live devices, no rebuild):** set `OTA_ENABLED=false` and
  `./deploy.sh`. The endpoint then always returns "no update".
- The endpoint also gates on native-binary compatibility: a bundle whose
  `min_version_build` exceeds the device's `version_build` is withheld, so an old
  binary never receives a bundle it can't run.
- Everything fails safe to "no update": a missing pointer, a fetch error, or a
  disabled flag never serves a bad bundle and never raises.

Publishing bundles and the one-time GCS setup live in `frontend/README.md`.
