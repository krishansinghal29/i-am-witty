# Riffy Play Store Launch Handoff

Last updated: June 9, 2026

This file captures the current launch-prep state so the next agent can resume without reconstructing context. The next agent is expected to be Claude; for browser/manual console work, use the Claude Chrome extension, especially for Play Console, RevenueCat, Firebase Hosting/domain verification, and checking the live `riffy.pro` pages.

## Repo Context

- Repo root: `/Users/krishansinghal/i-am-witty`
- Working app/design directory: `/Users/krishansinghal/i-am-witty/design`
- Frontend: `/Users/krishansinghal/i-am-witty/design/frontend`
- Backend: `/Users/krishansinghal/i-am-witty/design/backend`
- Handoff directory: `/Users/krishansinghal/i-am-witty/design/extra`
- Canonical production web domain: `https://riffy.pro`
- Public app brand: `Riffy`
- Android package/application id: `com.iamwitty.app`
- Google Play app type: app, not game
- Business model: free app with in-app subscriptions
- Android purchases: Google Play Billing only, mediated through RevenueCat
- RevenueCat entitlement: `riffy_plus`
- Planned subscriptions:
  - Monthly: `$9.99`
  - Annual: `$59.99`

## Current Repo State

At the end of the previous Codex session:

- `http://127.0.0.1:5173/` was already running from another process and should be reused if still active.
- A temporary Vite server started on `5174` was killed.
- `5174` was confirmed not reachable.
- `5173` returned `200 OK` for `/` and `/legal`.
- `git status --short` from repo root showed an unrelated modified `backend/app/main.py`; do not revert it unless the user explicitly asks.
- The tracked change left by the last session was landing-page brand capitalization in `design/frontend/src/screens/landing/landing_page.tsx`.
- Many Play Store prep pieces are already present in `HEAD` or the working tree. Verify current file contents before assuming they are missing.

## Implemented App/Web Pieces

### Legal Page

The public legal page exists at:

- Source: `/Users/krishansinghal/i-am-witty/design/frontend/src/screens/legal/legal_page.tsx`
- Styles: `/Users/krishansinghal/i-am-witty/design/frontend/src/screens/legal/legal.css`
- Route: `/legal`

Anchors:

- `https://riffy.pro/legal#privacy`
- `https://riffy.pro/legal#terms`
- `https://riffy.pro/legal#account-deletion`

The page includes:

- Clearly labeled `Privacy Policy`
- Clearly labeled `Terms of Service`
- Prominent `Account deletion` section
- Riffy brand/developer mention
- Public, non-PDF, non-geofenced web content
- Account deletion request path
- What data is deleted
- What data may be retained
- Google Play subscription cancellation note
- Contact email currently set to `privacy@riffy.pro`
- Last updated date currently `June 9, 2026`

### Landing Page

Landing source:

- `/Users/krishansinghal/i-am-witty/design/frontend/src/screens/landing/landing_page.tsx`

The footer links visibly include:

- Privacy: `/legal#privacy`
- Terms: `/legal#terms`
- Account deletion: `/legal#account-deletion`

The visible brand copy was normalized to `Riffy` in the last session. Some internal CSS class names and comments still use lowercase `riffy`; that is intentional and not user-facing.

### Profile Account Deletion Link

Profile source:

- `/Users/krishansinghal/i-am-witty/design/frontend/src/screens/profile/profile_page.tsx`

Profile includes canonical fallback URLs:

- `https://riffy.pro/legal#terms`
- `https://riffy.pro/legal#privacy`
- `https://riffy.pro/legal#account-deletion`

Profile menu includes:

- Terms of Service
- Privacy Policy
- Account deletion

The Account deletion row opens the canonical legal anchor externally.

### Backend Public Config

Config seed source:

- `/Users/krishansinghal/i-am-witty/design/backend/app/infrastructure/db/reference_data/app_config.py`

Current intended public config values:

- `terms_url`: `https://riffy.pro/legal#terms`
- `privacy_url`: `https://riffy.pro/legal#privacy`
- `account_deletion_url`: `https://riffy.pro/legal#account-deletion`
- `android_play_store_url`: `https://play.google.com/store/apps/details?id=com.iamwitty.app`

Production DB may still need to be reseeded or manually updated so `/v1/config` returns these values in production.

### Paywall / RevenueCat Client

RevenueCat client:

- `/Users/krishansinghal/i-am-witty/design/frontend/src/integrations/revenuecat/revenuecat_subscription_gateway.ts`

Important details:

- Entitlement is hardcoded as `riffy_plus`.
- Android key env var is `VITE_REVENUECAT_ANDROID_KEY`.
- Purchases use `@revenuecat/purchases-capacitor`.
- On web, the paywall points users to app store download rather than external checkout.
- Do not add Stripe, Razorpay, web checkout, or external payment links for Android digital purchases.

RevenueCat setup note:

- `/Users/krishansinghal/i-am-witty/design/extra/revenue_cat_setup.md`

It was corrected to refer to `riffy_plus`, monthly `$9.99`, and annual `$59.99`.

### Android App Identity

Capacitor config:

- `/Users/krishansinghal/i-am-witty/design/frontend/capacitor.config.ts`

Current values:

- `appId: 'com.iamwitty.app'`
- `appName: 'Riffy'`

Android strings:

- `/Users/krishansinghal/i-am-witty/design/frontend/android/app/src/main/res/values/strings.xml`

Current app display strings:

- `app_name`: `Riffy`
- `title_activity_main`: `Riffy`
- `package_name`: `com.iamwitty.app`

Android Gradle app file:

- `/Users/krishansinghal/i-am-witty/design/frontend/android/app/build.gradle`

Current release metadata observed:

- `applicationId "com.iamwitty.app"`
- `versionCode 1`
- `versionName "1.0"`

## Verification Already Run

From `/Users/krishansinghal/i-am-witty/design/frontend`:

```bash
npm run build
```

Result:

- Passed.
- Vite produced existing large chunk warnings, but no type/build errors.

```bash
npx cap sync android
```

Result:

- Passed.
- Android assets and `capacitor.config.json` were regenerated.

From local server checks:

```bash
curl -I http://127.0.0.1:5173/
curl -I http://127.0.0.1:5173/legal
curl -I http://127.0.0.1:5174/
```

Result:

- `/` on `5173`: `200 OK`
- `/legal` on `5173`: `200 OK`
- `5174`: not reachable, as intended after killing the temporary server

Lint:

```bash
npm run lint
```

Result:

- Failed due to pre-existing unrelated issues:
  - `src/integrations/transcription/deepgram_transcription_gateway.ts`: `no-explicit-any`
  - `src/integrations/transcription/native_transcription_gateway.ts`: `no-explicit-any`
  - `src/screens/onboarding/steps/reminder_step.tsx`: unused `IonIcon`
  - Fast-refresh warnings in existing files
- No new lint failures were attributed to the Play Store/legal changes.

Android bundle:

```bash
./gradlew :app:bundleRelease
```

Result:

- Blocked.
- Initial sandbox issue was resolved with escalation, allowing Gradle to download.
- Actual failure:
  - `Unsupported class file major version 70`
- Current Java observed:
  - `java version "26.0.1"`
  - Only JDK 26 was registered by `/usr/libexec/java_home -V`.
- Next step: install/select a supported JDK, typically JDK 17 or JDK 21, then rerun the release bundle build.

## Remaining Work

### Local Build / Release

1. Install or select supported JDK 17 or 21.
2. Rerun:

```bash
cd /Users/krishansinghal/i-am-witty/design/frontend/android
./gradlew :app:bundleRelease
```

3. Configure release signing if not already configured.
4. Confirm signed `.aab` output.
5. Keep `versionCode 1` and `versionName "1.0"` unless the user wants a different first release.

### Deploy Web

1. Deploy the frontend build to `https://riffy.pro`.
2. Verify the following are public and not behind auth:
   - `https://riffy.pro`
   - `https://riffy.pro/legal#privacy`
   - `https://riffy.pro/legal#terms`
   - `https://riffy.pro/legal#account-deletion`
3. Use the Claude Chrome extension to visually verify the deployed landing footer links and legal sections.

### Backend / Production Config

1. Ensure backend production config returns:
   - `terms_url = https://riffy.pro/legal#terms`
   - `privacy_url = https://riffy.pro/legal#privacy`
   - `account_deletion_url = https://riffy.pro/legal#account-deletion`
2. Reseed or manually update production `app_config`.
3. Ensure backend production env contains:
   - `REVENUECAT_API_KEY`
   - `REVENUECAT_WEBHOOK_AUTH`

### RevenueCat

Use RevenueCat dashboard, ideally through Claude Chrome extension for manual steps:

1. Create or confirm RevenueCat project/app for Android.
2. Create entitlement exactly:
   - `riffy_plus`
3. In Google Play Console, create subscription products/base plans:
   - Monthly: `$9.99`
   - Annual: `$59.99`
4. Import Play products into RevenueCat.
5. Attach monthly and annual products/packages to `riffy_plus`.
6. Configure current Offering with monthly and annual packages.
7. Copy Android public SDK key into frontend production env:
   - `VITE_REVENUECAT_ANDROID_KEY`
8. Create Google Play service account and grant required Play permissions.
9. Upload service account credentials JSON to RevenueCat.
10. Configure RevenueCat webhook:
    - URL: `https://<production-backend>/v1/webhooks/revenuecat`
    - Authorization header value must match backend `REVENUECAT_WEBHOOK_AUTH`.
11. Test purchase, restore, webhook delivery, and backend entitlement sync.

### Google Play Console

Use the Claude Chrome extension for Play Console manual work.

1. Create/finish Google Play developer account.
2. Complete payments profile, tax, and banking setup.
3. Create app:
   - App name: `Riffy`
   - Package: `com.iamwitty.app`
   - Website: `https://riffy.pro`
   - Availability: worldwide
   - App type: app, not game
   - Price: free app with in-app subscriptions
4. Enroll developer account in Google 15% service fee tier where applicable.
5. If Google classifies the account as a new personal developer account, plan closed testing:
   - At least 12 opted-in testers
   - 14 consecutive days
   - Then apply for production access
6. Complete App Content:
   - Data Safety
   - Privacy Policy URL: `https://riffy.pro/legal#privacy`
   - Account deletion URL: `https://riffy.pro/legal#account-deletion`
   - Target audience and content
   - Content rating
   - Ads declaration
   - App access declaration
7. App access declaration for first submission:
   - No special credentials required.
   - Reviewers can use guest flow or tap `Continue with Google`.
   - Fallback if Google flags access: create reusable reviewer Google account and manually grant Riffy+.

### Play Store Assets

Use existing Riffy assets:

- `/Users/krishansinghal/i-am-witty/design/ux_existing/logo/png`
- App icon sources are already also present under frontend public/assets/native resources.

Capture Android screenshots for:

- Onboarding
- Home
- Practice
- Task runtime
- Profile
- Paywall

### QA Checklist

Before Play submission, verify:

- `riffy.pro` loads publicly.
- `/legal#privacy`, `/legal#terms`, `/legal#account-deletion` load publicly.
- Landing page visibly links to Privacy, Terms, and Account deletion.
- App launches on Android.
- Guest/onboarding flow works.
- Google-only sign-in works.
- Core practice flow is accessible without reviewer-provided credentials.
- Profile links open legal sections.
- Account deletion request path is discoverable in app and on web.
- Paywall loads live monthly/annual RevenueCat packages.
- Play Billing purchase grants `riffy_plus`.
- Restore purchase works.
- RevenueCat webhook reaches backend.
- Backend `/v1/me/access` reflects entitlement after purchase/restore.
- Free limit triggers paywall for non-subscribers.

## Important Cautions

- Do not revert unrelated local changes. There was an unrelated modified `backend/app/main.py` at handoff.
- Do not introduce external checkout links for Android digital purchases.
- Do not rename `riffy_plus`; both client and backend expect that entitlement key.
- Do not change Android package `com.iamwitty.app` after creating the Play app.
- Browser automation in the previous Codex environment reported `iab` unavailable; the next agent should use Claude Chrome extension for browser/manual UI tasks.
