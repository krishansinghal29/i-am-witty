# Riffy — Google Play Console Setup Answers

A running record of every answer entered (or decided) for the Riffy Play Console
listing, so the setup can be resumed/audited without re-deriving anything.
Each question is an expandable dropdown — click to view the answer.

**Last updated:** 2026-06-12

### Legend
- ✅ **Entered & saved** in Play Console
- 📝 **Decided** — answer locked in, not yet entered in the console
- ⏳ **Pending** — needs your input / blocked

---

## Account & app identity

| Item | Value |
|---|---|
| Developer account | **curator09** (Personal) · Account ID `7752674511981103164` |
| App | **Riffy** · Play app ID `4972597653430815032` |
| Package name | `com.iamwitty.app` *(permanent — cannot change)* |
| RevenueCat entitlement | `riffy_plus` (set up separately) |

<details>
<summary>Account type — <b>Yourself (Personal)</b> ✅</summary>

Chose **Personal** (not Organisation). Consequence: as a new personal account,
Riffy must run **closed testing with 12+ testers for 14 consecutive days**
before it can apply for production access.
</details>

---

## Create app

<details>
<summary>App name — <b>Riffy</b> ✅</summary>

How it appears on Google Play. Max 30 chars.
</details>

<details>
<summary>Package name — <b>com.iamwitty.app</b> ✅</summary>

Showed "Package name available". **Locks permanently** once the app is created.
Matches the signed `.aab` build.
</details>

<details>
<summary>Default language — <b>set during creation (en-US / en-GB)</b> ✅</summary>

Console defaulted to English (United Kingdom) — en-GB. Editable later. Minor;
en-US is the more common global default.
</details>

<details>
<summary>App or game — <b>App</b> ✅</summary>
</details>

<details>
<summary>Free or paid — <b>Free</b> ✅</summary>

"Free" = free to download. Riffy still monetises via in-app subscriptions
(`riffy_plus`, $9.99/mo, $59.99/yr) — those are separate from the download price.
⚠️ A free app **cannot be switched to paid** after publishing.
</details>

<details>
<summary>Declarations — <b>accepted</b> ✅</summary>

Developer Programme Policies, Play App Signing Terms of Service, and US export
laws — all confirmed by you during app creation.
</details>

---

## App content declarations

<details>
<summary>Privacy policy — <b>https://riffy.pro/legal#privacy</b> ✅ saved</summary>

Entered on the Privacy policy page. "Change saved." (Page must be publicly live
at review time — web deploy is a separate pending item.)
</details>

<details>
<summary>Ads — <b>No, my app does not contain ads</b> ✅ saved</summary>

Riffy has no ad SDK. "Change saved."
</details>

<details>
<summary>Advertising ID — <b>No</b> ✅ saved</summary>

Verified in code: the merged release manifest contains **no
`com.google.android.gms.permission.AD_ID`** permission, so no SDK uses the
advertising ID. "Change saved."
</details>

<details>
<summary>Sign-in details (App access) — <b>Yes, restricted</b> ✅ saved</summary>

- **Is any part restricted?** → **Yes** (Google Sign-In required + subscriptions).
- **Entry name:** `Reviewer access (Google Sign-In)`
- **Username:** `test@riffy.pro` (Google Workspace account; works with "Continue
  with Google"). **Password:** entered by the user (NOT stored here).
- **Instructions:** "Riffy uses social login (Google Sign-In) only. Tap 'Continue
  with Google' and sign in with the reviewer account (test@riffy.pro). 2SV disabled.
  Complete the short onboarding to reach Home. This account has full Riffy+ premium
  access, so all features and premium content are available."
- **"Full access incl. premium" checkbox:** ✅ checked (test account has premium).
- ⚠️ Ensure **2-Step Verification stays OFF** on test@riffy.pro or reviewers get
  challenged. "Change saved."
</details>

<details>
<summary>Health apps — <b>No health features</b> ✅ saved</summary>

Classifying Riffy as a **communication / social-skills practice app**, not a
health app. Checked "My app does not have any health features" (left all
health-feature boxes incl. "Stress management, relaxation, mental acuity"
unchecked). No regional requirements. Avoids Google's Health Apps policy. "Change saved."
</details>

<details>
<summary>Target audience — <b>18 and over + restrict minors ON</b> ✅ saved</summary>

**Age groups:** ☑ 18 and over (only — 5&under/6-8/9-12/13-15/16-17 all unchecked;
under-13 buckets were greyed out because ESRB rating is Teen).
**☑ "Restrict users that Google has determined to be minors from my app"** → **ENABLED**
(updated 2026-06-12). This actively blocks Google-determined under-18 accounts from
searching/downloading/purchasing — the real enforcement of the 18+ intent, appropriate
for the sexual-innuendo/dating content. Summary reads "Your app restricted users who
are determined to be minors." Selecting 18+ auto-skips the child-related steps. "Change saved."

> **How the 3 age controls relate** (for reference):
> - **Content rating** (Teen/12+) = the *content label*; feeds parental controls (Family Link); not freely chosen.
> - **Target audience** (18+) = *who you design for*; declaration that drives which Google policies apply.
> - **Restrict-minors toggle** (ON) = the *hard block* of Google-determined under-18s. Only meaningful for 18+ apps.
</details>

<details>
<summary>Government apps — <b>No</b> ✅ saved</summary>

Riffy is not a government app. "Change saved."
</details>

<details>
<summary>Financial features — <b>No</b> ✅ saved</summary>

Checked "My app doesn't provide any financial features." (In-app subscriptions
are billing, not a "financial feature".) No documentation required. "Change saved."
</details>

<details>
<summary>Content rating — <b>SUBMITTED</b> ✅ Teen / 12+ / 14 (IARC)</summary>

Submitted 2026-06-12 with email **krishan@riffy.pro**. IARC ToS accepted.
**Result: Teen (ESRB) / IARC 12+ / PEGI 14 / USK 12 / ClassInd 12.**

Answers (honest — Riffy is flirting/dating/charisma practice with sexual innuendo,
deliberately suggestive NOT graphic; exercises `sex_with_me`, `sexual_misinterpretation`,
`shit_test`):
- Category: **All other app types**
- Downloaded app has ratings-relevant content → **Yes**
- Sexuality → **Yes → "Suggestive references and innuendo in text"** only
  (no overt/visual/explicit, no nudity, no sexual violence, nothing under-18)
- Language → **Yes → minor profanities, Rarely** (no moderate/discriminatory/sexual expletives)
- Violence / Fear / Gambling / Controlled substance / Crude humour (bodily) → **No**
- User content sharing → No · Online content → No (AI content is first-party, declared
  under Downloaded app) · Promotion of age-restricted → No
- Miscellaneous: digital purchases → **Yes** (subscriptions; not loot boxes) · everything else No

NB: rating is **Teen/12+, not Mature 17+** — suggestive (non-explicit) content rates Teen.
This means the *content rating* permits 13+, even though **Target audience is set to 18+**.
</details>

<details>
<summary>Data safety — <b>submitted</b> ✅ saved</summary>

Whole questionnaire completed and **submitted** ("Change saved"). Store-listing
preview shows "No data shared with third parties" + Name/Email/Voice collected.

Step answers:
- Collects/shares required data types? → **Yes**
- Encrypted in transit? → **Yes** · Account-deletion URL → `riffy.pro/legal#account-deletion`
- Account creation method → **OAuth** · partial-deletion-without-account → **No**

| Data type | Collected (not shared) | Ephemeral? | Required? | Purposes |
|---|---|---|---|---|
| Name | Yes | No (stored) | Required | App functionality, Account management |
| Email address | Yes | No (stored) | Required | App functionality, Account management |
| Voice/sound recordings | Yes | **Yes (ephemeral, not stored)** | Required | App functionality |

App activity/analytics → not selected (PostHog parked/off in prod).
*To add once Firebase push is wired: **Device or other IDs → push token**.*
</details>

---

## Store presence — 📝 assets ready (in `extra/play_store_listing/`), not yet entered

All publishable content + images are prepared under
**`extra/play_store_listing/`** (`listing.md` has the copy; `icon-512.png`,
`feature-graphic-1024x500.png`, and `screenshots/01..06-*.png` are the images).

<details>
<summary>Select app category & contact details — ✅ saved in console (2026-06-12)</summary>

Store settings → saved ("Change saved"):
- **App type:** App · **Category:** Lifestyle (self-improvement / social-skills practice).
- **Contact email:** support@riffy.pro (working Workspace alias; public on listing).
- **Website:** https://riffy.pro · **Phone:** left blank (optional).
- External marketing: left at default (on).
</details>

<details>
<summary>Main store listing — ✅ text saved as draft / ⏳ images need manual upload</summary>

Default store listing (en-US) created; **Save as draft** done ("Change saved. Send for review
in Publishing overview"):
- **Short description (73 chars):** "A little gym for your social spark. Quick voice reps to sharpen your wit." ✅ entered
- **Full description:** the Read→Respond→Reflect writeup (1502 chars, no Riffy+ line) ✅ entered

⏳ **Graphics still to upload (manual — drag & drop):** the Play Console upload tool can't be
driven by automation here (the controller no longer accepts host file paths), so these must be
dragged in from `extra/play_store_listing/`:
- **App icon** → `icon-512.png` (512×512) — *required*
- **Feature graphic** → `feature-graphic-1024x500.png` (1024×500)
- **Phone screenshots** (≥2 required) → `screenshots/01..06-*.png` (1120×1760)

All files are ready and validated; just open Store listings → Graphics → "Add assets" for each.
</details>

---

## Release / testing (later)

<details>
<summary>Closed testing — Alpha track ready · AAB rebuilt w/ Firebase ✅ · ⏳ needs manual upload + 12 testers</summary>

Track **"Closed testing – Alpha"** exists (Test and release → Testing → Closed testing), no release yet.
Personal account ⇒ need **12+ testers for 14 consecutive days**, then apply for production access.

✅ **Firebase sign-in fix done (2026-06-12).** `frontend/android/app/google-services.json` added (project
`i-am-witty`, package `com.iamwitty.app`, `oauth_client` types `[1,3]` → Android Sign-In client present).
Signed AAB **rebuilt** — `processReleaseGoogleServices` embedded `1:756792002130:android`; "jar verified".
Fresh AAB at `frontend/android/app/build/outputs/bundle/release/app-release.aab` (17:06).
SHA fingerprints registered in Firebase — upload key SHA-1 `04:B7:A5:83:5F:AA:1D:E8:42:0F:97:3A:BD:DD:29:9B:FF:9F:BB:08`,
SHA-256 `E6:3A:C6:A6:D6:EF:22:23:3E:DD:CF:B6:CA:16:4B:94:54:B0:96:9E:AA:39:3B:20:A1:B3:43:89:72:F8:D5:64`
(+ Play App Signing key SHA from Play Console → App integrity).

**Remaining (manual — needs you):**
1. **Upload the AAB** — Closed testing – Alpha → Create release → drag in `app-release.aab`
   (automation can't upload bundles here). App signing key choice (Play App Signing) offered at
   first release — **irreversible**.
2. Add release name + notes.
3. Add **12 tester emails** (Closed testing → Testers → create email list), have them opt in,
   keep them for **14 consecutive days**, then apply for production.
</details>

---

## Resolved decisions
- **Age / who can use it → 18+ adults only, minors actively blocked.** Decided to keep
  Target audience at 18 and over and **enable the "restrict minors" toggle** (the hard
  under-18 block), the coherent adults-only config for the sexual-innuendo/dating content.
  (Content rating Teen/12+ stays as the honest content label.)

## Waiting on you (for store listing + launch)
1. ~~Store listing assets~~ — ✅ **done**, all in `extra/play_store_listing/` (copy + icon +
   feature graphic + 6 screenshots + category/contact decided). Just needs your OK on the copy,
   then entering into Play Console.
2. **Firebase config files** — `google-services.json` (Android) + `GoogleService-Info.plist`
   (iOS) needed for Google sign-in + push to actually work; then rebuild AAB.
3. **riffy.pro** must be publicly live (privacy/terms/account-deletion) at review time.
4. **Keep 2-Step Verification OFF** on test@riffy.pro (reviewer account).

### Declaration completion status — ✅ 11 of 11 ACTIONED (App content done!)
✅ Privacy policy · Ads · Advertising ID · Government apps · Financial features · Health
✅ Sign-in details (App access) · Target audience (18+) · Data safety
✅ **Content rating — submitted (Teen/12+)**
✅ Store: app category (Lifestyle) + contact details (support@riffy.pro, riffy.pro) **saved**
✅ Main store listing: short + full description **saved as draft**
⏳ Main store listing graphics: icon + feature graphic + 6 screenshots — **drag-drop manually**
   from `extra/play_store_listing/` (automation can't upload files here).
