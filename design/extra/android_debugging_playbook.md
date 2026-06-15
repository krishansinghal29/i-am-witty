# Android on-device debugging playbook (Riffy / Capacitor)

A practical guide for diagnosing native Android issues in the Riffy app
(Ionic React + Capacitor, package `com.iamwitty.app`). Written after a session
that traced a "login shows an unexpected error" bug down through five distinct
layers. The point of this doc: another agent should be able to reproduce the
debug loop and read the same signals.

Last verified: 2026-06-12. Repo state at time of writing: `design/` @ `02a2ecc`.

---

## The mental model that makes this tractable

A Capacitor app is a **native Android shell** wrapping a **WebView** that runs
the React/JS bundle. Bugs live in one layer or the other, and each has its own
debugger. Knowing which layer a symptom belongs to is 80% of the battle.

| Layer | What runs there | Tool | Gives you |
|---|---|---|---|
| WebView | React/JS, Firebase **JS SDK**, `fetch` to the backend | Chrome `chrome://inspect` | Console + **Network tab** + Sources |
| Native | Java/Kotlin Capacitor plugins (Google Sign-In via Credential Manager, etc.) | `adb logcat` | native exceptions, plugin errors, GMS auth logs |

Critical consequence: **native plugin calls make no WebView network requests**,
so the Chrome Network tab is empty for "Continue with Google"/"Apple". Those
only show up in `adb logcat`. Conversely, a CORS-blocked backend `fetch` only
shows in the WebView console, not logcat (except as a `Capacitor/Console` line).

---

## Environment / toolchain (this machine)

- `adb`: `~/Library/Android/sdk/platform-tools/adb` (also on PATH via `.zshrc`).
- JDK for Gradle: **Temurin 21** at `~/jdks/jdk-21.0.11+10/Contents/Home`
  (the system JDK is too new; always pass `JAVA_HOME=` explicitly).
- Frontend: `design/frontend`. Backend (FastAPI on Cloud Run): `design/backend`.
- `gcloud` is authed as the project owner, project `i-am-witty`, service
  `iamwitty-backend` in `us-east1`. Backend deploy = `design/backend/deploy.sh`.

---

## The build → install → inspect loop

```bash
# 0. (once) make adb usable
export PATH="$HOME/Library/Android/sdk/platform-tools:$PATH"
adb devices            # phone must show as "device" (USB debugging on, screen unlocked)

# 1. build web assets + push into the native project
cd design/frontend
npm run build
npx cap sync android   # also regenerates android/app/src/main/assets/capacitor.config.json

# 2. build a DEBUG apk (debug = FLAG_DEBUGGABLE, so chrome://inspect works)
cd android
JAVA_HOME=~/jdks/jdk-21.0.11+10/Contents/Home ./gradlew assembleDebug
# -> app/build/outputs/apk/debug/app-debug.apk

# 3. install
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

### Gotchas hit during the session
- **`INSTALL_FAILED_UPDATE_INCOMPATIBLE`** when a Play-signed build is already
  on the device: the debug keystore signature differs. Fix:
  `adb uninstall com.iamwitty.app` then install. (debug→debug reinstalls are
  fine with `-r`.)
- **Phone keeps disconnecting** (empty `adb devices`, logcat stream ends):
  replug, unlock screen, set USB mode to *File Transfer*. To block until it's
  back: `adb wait-for-device`.
- **chrome://inspect shows nothing**: only **debug** builds are inspectable by
  default. A release/Play build needs `android.webContentsDebuggingEnabled:true`
  in `capacitor.config.ts` (don't ship that to prod). Use a local debug build
  instead.

### Reading logcat without drowning
Filter to the app process and to signal, drop the noise:
```bash
# app-process-only stream (run AFTER the app is launched)
adb logcat --pid=$(adb shell pidof -s com.iamwitty.app)

# targeted filter for auth debugging; drop the GMS BAD_AUTHENTICATION flood
adb logcat -c   # clear first
adb logcat | grep -iE "signInWith|BeginSignInOperation|onboarding|Access to fetch|CORS|plugin error|Capacitor/Console" \
           | grep -viE "AuthPII|RequestTokenManager|CapgoUpdater|No listeners found"
```
- `Capacitor/Console` lines = the JS `console.*` output (incl. CORS errors).
- `Sending plugin error: {...}` = a native plugin rejected a JS call — the
  single most useful line; it carries the exact `message`.
- A storm of `AuthPII ... getToken() -> BAD_AUTHENTICATION` from
  `com.google.android.gms` / `com.android.vending` is the **device's own Google
  account** being stale — background noise, NOT your app. Ignore it; the real
  sign-in result is the `BeginSignInOperation succeeded/failed` line in the
  middle of it.

---

## Verifying the backend side

The debug build talks to the **prod** backend (`.env.production` sets
`VITE_API_BASE_URL` to the Cloud Run URL). So backend-dependent steps need the
prod service. Two cheap checks:

```bash
# CORS preflight from the Android webview origin
curl -s -i -X OPTIONS \
  'https://iamwitty-backend-756792002130.us-east1.run.app/v1/onboarding/complete' \
  -H 'Origin: https://localhost' \
  -H 'Access-Control-Request-Method: POST' \
  -H 'Access-Control-Request-Headers: authorization,content-type' \
  | grep -i 'access-control-allow-origin'      # must echo https://localhost

# did the real request land? (Cloud Run request logs)
export PATH="/opt/homebrew/share/google-cloud-sdk/bin:$PATH"
gcloud logging read \
  'resource.type="cloud_run_revision" resource.labels.service_name="iamwitty-backend" httpRequest.requestUrl:"onboarding"' \
  --project i-am-witty --limit 5 --freshness=20m \
  --format='value(timestamp, httpRequest.requestMethod, httpRequest.status, httpRequest.requestUrl)'
# success looks like: OPTIONS 200 then POST 201
```

Backend redeploy after a code change: `cd design/backend && ./deploy.sh`
(builds from source via Cloud Build, new Cloud Run revision, rollback-able).

---

## Case study: "login shows an unexpected error" — five stacked layers

The symptom (`"An unexpected error occurred."`, which is the `unknown`-code
fallback in `frontend/src/data/errors/app_error.ts`) had FIVE independent
causes stacked on top of each other. Each was only visible once the one above
it was fixed — a good reminder to peel one layer at a time and re-test.

1. **Providers not registered.** `@capacitor-firebase/authentication` v8 loads
   zero providers by default. `signInWithGoogle` rejected with *"…provider is
   not enabled. Make sure to add the provider to the 'providers' list…"*
   → Fix: `plugins.FirebaseAuthentication.providers = ['google.com','apple.com']`
   in `frontend/capacitor.config.ts`.

2. **Native Google libs excluded from the APK.** The plugin keeps Credential
   Manager / play-services-auth / googleid as `compileOnly` unless
   `rgcfaIncludeGoogle = true`. Without it, `signInWithGoogle` would
   `NoClassDefFoundError` at runtime. (Verify with: unzip the APK and grep
   `classes*.dex` for `androidx/credentials/CredentialManager`.)
   → Fix: `rgcfaIncludeGoogle = true` in `frontend/android/variables.gradle`.

3. **Signing cert (SHA-1) not registered in Firebase.** Native Google Sign-In
   checks the app's signing cert. Symptom in logcat:
   `Auth.Api.Credentials BeginSignInOperation failed [28444]` +
   `GoogleAuthUtil ... BAD_AUTHENTICATION` + `UNAUTHENTICATED`. Each build's
   signer differs:
   - debug keystore (`~/.android/debug.keystore`, pass `android`) — for dev builds
   - upload keystore (`frontend/android/riffy-upload.keystore`) — for sideloaded release
   - **Google Play App Signing key** — what Play-distributed installs are
     actually signed with (Play re-signs the AAB). Get its SHA-1/256 from Play
     Console → Test and release → Setup → App integrity → App signing key cert.
   → Fix (user-only, Firebase Console): add the relevant SHA-1s to the Android
     app in project `i-am-witty`, re-download `google-services.json` into
     `frontend/android/app/`, rebuild. Get a keystore's SHA-1 with:
     `keytool -list -v -keystore <file> -storepass <pw>`.

4. **Backend CORS missing the Android origin.** After Firebase auth succeeded,
   the app's `POST /v1/onboarding/complete` was blocked:
   *"…blocked by CORS policy … from origin 'https://localhost'."* The allowlist
   in `backend/app/api/main.py` had `capacitor://localhost` (iOS) and
   `http://localhost` but **not** `https://localhost` — and Android's default
   `server.androidScheme` is `https`, so its webview origin is `https://localhost`.
   This is what broke **email login too** (email's Firebase step always worked;
   the post-login backend call is what failed — same root cause as Google).
   → Fix: add `"https://localhost"` to `allow_origins`, then `./deploy.sh`.

5. (Not a bug, but worth knowing) the device account's `BAD_AUTHENTICATION`
   noise — ignore, see logcat section above.

**End state (verified on-device 2026-06-12):** Google sign-in + email login both
complete; Cloud Run shows `OPTIONS 200` then `POST /v1/onboarding/complete 201`;
Firebase user object logged in the WebView console.

---

## Still open / things to keep in mind

- **The fixes above are local working-tree changes + one backend deploy.** The
  CORS fix IS live in prod (shared backend, so it fixes email on *all* installs,
  including the existing Internal Testing build). But the three frontend changes
  (providers, `rgcfaIncludeGoogle`, new `google-services.json`) are NOT yet in
  any Play build — the store build still has the old broken native code. To fix
  Google/Apple for testers: rebuild the **release AAB** and upload a new version.
  Nothing is committed to git yet.
- **Apple sign-in is wired into `providers` and the UI still shows a "Continue
  with Apple" button, but Apple is not configured in Firebase/Apple Developer.**
  Tapping it will error. Either hide the button (in
  `frontend/src/screens/onboarding/steps/login_step.tsx`) or configure Apple.
  Apple on Android is a **web OAuth flow** (Custom Tab → `…firebaseapp.com/__/auth/handler`),
  needs Services ID + return URL + .p8 key/Key ID/Team ID. Apple is **required
  for the iOS App Store** (Guideline 4.8, because Google is offered) but **not**
  for Play.
- See related memory `android-firebase-signin-blocker` and `android-build-toolchain`
  for the signing/build details, and `extra/riffy_play_store_launch_handoff.md`
  for Play Console state.
