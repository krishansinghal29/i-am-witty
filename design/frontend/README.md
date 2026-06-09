# riffy frontend

Ionic React + Vite + Capacitor app (iOS, Android, Web). For architecture,
conventions, and the API contract see [`context.md`](./context.md).

## Common commands

```bash
npm run dev          # Vite dev server (web)
npm run build        # typecheck + production build to dist/
npm run test.unit    # vitest
npx cap sync         # copy web build + native config into ios/ and android/
./deploy_ota.sh      # publish a self-hosted Capgo OTA bundle (see below)
```

## Over-the-air updates (self-hosted Capgo)

We push updates to the **web layer** of the native apps using the open-source
`@capgo/capacitor-updater` plugin pointed at **our own backend**, not Capgo's
cloud — so there's no subscription and no fee.

```
deploy_ota.sh ──► GCS (public)            backend  POST /v1/ota/check
  build dist/      bundle-<ver>.zip   ◄── device downloads the zip directly
  zip + sha256     production.json    ──► backend reads the pointer, applies
  gcloud cp                               OTA_ENABLED + version compatibility
```

The plugin (download, apply-on-launch, `notifyAppReady`, automatic rollback) is
configured in `capacitor.config.ts`, which reads `VITE_API_BASE_URL` for the
update URL and `VITE_CAPGO_ENABLED` for the on/off flag. `App.tsx` calls
`notifyAppReady()` on boot — required, or Capgo rolls every applied bundle back.

### What can go out via OTA

| OTA ✅ (web layer) | Store release ❌ (native binary) |
|---|---|
| React/TS/CSS, copy, images, logic | New/upgraded Capacitor plugin |
| JS-only npm deps | Permissions, icon, splash, app name |
| Anything calling plugins already in the binary | `capacitor.config.ts`, `ios/`, `android/` |

`deploy_ota.sh` enforces this: it aborts if native-surface files changed since
the `native-release` git tag.

### One-time setup

1. **Create the public bucket** (project `i-am-witty`):
   ```bash
   gcloud storage buckets create gs://riffy-ota \
     --project i-am-witty --location us-east1 --uniform-bucket-level-access
   gcloud storage buckets add-iam-policy-binding gs://riffy-ota \
     --member=allUsers --role=roles/storage.objectViewer
   ```
   (Reuse another bucket by setting `OTA_BUCKET=gs://...` when running the script.)

2. **Point the backend at the pointer** — set in `backend/.env` and redeploy:
   ```
   OTA_ENABLED=true
   OTA_POINTER_URL=https://storage.googleapis.com/riffy-ota/ota/production.json
   ```

3. **Tag the current store build** so the native guard has a baseline:
   ```bash
   git tag native-release && git push --tags
   ```
   This tag marks "the code that's in the binary users have installed."
   `deploy_ota.sh` refuses to publish if native-surface files changed since it
   (because OTA can't deliver native changes). **Move it forward by hand every
   time you submit a new store binary** — it's a per-store-release step, not a
   per-OTA one (auto-moving it on OTA would defeat the guard):
   ```bash
   git tag -f native-release && git push -f --tags
   ```

4. Set `VITE_API_BASE_URL` to the prod backend, `npx cap sync`, then build the
   binary you submit to the stores.

### Publishing an update

```bash
./deploy_ota.sh
```

Builds `dist/`, zips it (index.html at the zip root), sha256s it, uploads to GCS,
and repoints `production.json`. Devices pick it up on the next launch /
background→foreground.

Env knobs (all optional, with defaults):

```
OTA_BUCKET=gs://riffy-ota            # target bucket
OTA_MIN_VERSION_BUILD=1              # min native build this bundle requires
OTA_NATIVE_TAG=native-release        # baseline tag for the native-surface guard
```

### Operating it

- **Kill switch (all live devices, instant, no rebuild):** set `OTA_ENABLED=false`
  in `backend/.env` and redeploy the backend.
- **Roll back:** re-run `deploy_ota.sh` from the previous commit (re-points
  `production.json` at that bundle). The device watchdog also auto-rolls-back any
  bundle that never calls `notifyAppReady`.
- **Disable in a build (dev/web/CI):** `VITE_CAPGO_ENABLED=false`. This governs
  only the build it compiles into — it is **not** the live kill switch.

### Removing Capgo entirely

There's nothing to unsubscribe from (we never use the cloud). Drop
`@capgo/capacitor-updater` from `package.json`, delete `capgo_updater.ts`, the
`CapacitorUpdater` block in `capacitor.config.ts`, the backend `ota.py`, and
`deploy_ota.sh`; keep `NoOpUpdater`; `npx cap sync`; cut a store release. Feature
code never imports Capgo, so the change stays localized (~6 files).
