# Capgo OTA (self-hosted) — setup & operations

We ship over-the-air updates to the **web layer** of the native iOS/Android apps
using the open-source `@capgo/capacitor-updater` plugin pointed at **our own
backend**, not Capgo's cloud. No subscription, no fee.

```
deploy_ota.sh ──► GCS (public)            FastAPI  POST /v1/ota/check
  build dist/      bundle-<ver>.zip   ◄── device downloads zip directly
  zip + sha256     production.json    ──► backend reads pointer, applies
  gcloud cp                               OTA_ENABLED + version compat
                                          and answers the plugin
```

- **Plugin** (free, on-device): download, apply-on-launch, `notifyAppReady`,
  automatic rollback. Configured in `frontend/capacitor.config.ts`.
- **Backend** `POST /v1/ota/check` (`backend/app/api/routes/ota.py`): the kill
  switch (`OTA_ENABLED`) and native-version compatibility gate.
- **Bundles**: public GCS objects. Not secret — the same JS ships in the binary.

## What can and cannot go out via OTA

| OTA ✅ (web layer) | Store release ❌ (native binary) |
|---|---|
| React/TS/CSS, copy, images, logic | New/upgraded Capacitor plugin |
| JS-only npm deps | Permissions, icon, splash, app name |
| Anything calling plugins already in the binary | `capacitor.config.ts`, `ios/`, `android/` |

`deploy_ota.sh` enforces this: it aborts if native-surface files changed since
the `native-release` git tag.

## One-time setup

1. **Create the public bucket** (project `i-am-witty`):
   ```bash
   gcloud storage buckets create gs://riffy-ota \
     --project i-am-witty --location us-east1 --uniform-bucket-level-access
   gcloud storage buckets add-iam-policy-binding gs://riffy-ota \
     --member=allUsers --role=roles/storage.objectViewer
   ```
   (Or reuse the Firebase Storage bucket and set `OTA_BUCKET` accordingly.)

2. **Backend env** (`backend/.env`, shipped to Cloud Run by `make_run_env.py`):
   ```
   OTA_ENABLED=true
   OTA_POINTER_URL=https://storage.googleapis.com/riffy-ota/ota/production.json
   ```
   Redeploy the backend (`backend/deploy.sh`) after changing these.

3. **Tag the current store build** so the native guard has a baseline:
   ```bash
   git tag native-release && git push --tags
   ```

4. **Frontend native config** is already wired (`capacitor.config.ts` reads
   `VITE_API_BASE_URL` → `updateUrl`). Set `VITE_API_BASE_URL` to the prod
   backend, `cap sync`, and build the binary you submit to the stores.

## Publishing an OTA update (the routine)

From `frontend/`:
```bash
./deploy_ota.sh
```
This builds `dist/`, zips it (index.html at the zip root), sha256s it, uploads
to GCS, and repoints `production.json`. Devices pick it up on their next
background→foreground / launch.

## Operating it

- **Kill switch (all live devices, instant, no rebuild):** set `OTA_ENABLED=false`
  in `backend/.env` and redeploy the backend. The endpoint then always reports
  "no update".
- **Roll back a bad bundle:** re-run `deploy_ota.sh` from the previous commit, or
  re-upload a `production.json` pointing `url`/`version` at the prior zip. (The
  device-side watchdog also auto-rolls-back a bundle that never calls
  `notifyAppReady`.)
- **Block a bundle from old binaries:** bump `OTA_MIN_VERSION_BUILD` (env) /
  `min_version_build` when a bundle needs a newer native build.

## Stop using Capgo entirely

There is nothing to unsubscribe from (we never use the cloud). To remove the
plugin: drop `@capgo/capacitor-updater` from `package.json`, delete
`capgo_updater.ts` + the `CapacitorUpdater` block in `capacitor.config.ts` +
`ota.py` + `deploy_ota.sh`, keep `NoOpUpdater`, `cap sync`, and cut a store
release. ~6 localized files — feature code never imports Capgo.

## Verify

- Backend: `POST /v1/ota/check` with a sample body returns the right shape
  (see the unit check in `backend`).
- End-to-end: publish a bundle, run the app on a device/emulator, background and
  reopen, confirm the new bundle loads and is not rolled back.
