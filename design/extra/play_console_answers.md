# Riffy — Google Play Console Setup Answers

A running record of every answer entered (or decided) for the Riffy Play Console
listing, so the setup can be resumed/audited without re-deriving anything.
Each question is an expandable dropdown — click to view the answer.

**Last updated:** 2026-06-10

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
<summary>Target audience — <b>18 and over</b> ✅ saved</summary>

Checked **"18 and over"** only. Optional "Restrict minors (block from download/
purchase)" → **left unchecked** (that's for adult-content apps; Riffy is just
adult-targeted, rated Everyone — forcing it risks false-positives hurting reach).
Selecting 18+ auto-skipped the child-related steps. "Change saved."
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
<summary>Content rating — <b>in progress</b> ⏳ paused — answers REVISED to MATURE (sexual/crude content found)</summary>

Category selected: **"All other app types"** (still correct — content type, not theme).

⚠️ **REVISED after finding mature exercises** (`sex_with_me`, `sexual_misinterpretation`,
`shit_test`, `if_by_x`): Riffy is flirting/dating/charisma practice with **sexual
innuendo + crude humor/profanity** (deliberately suggestive, NOT graphic — code guards
against explicit). So the questionnaire is **NOT "all No"**:
- Sexual content → **Yes (suggestive/innuendo themes)**, NOT explicit/graphic/nudity
- Crude humor / profanity → **Yes (mild)**
- Violence / drugs / gambling → No · user-to-user interaction → No · digital purchases → Yes
→ Expected rating **Mature ~17+ (Teen+)**, NOT Everyone/3+. (18+ target audience is now
clearly correct.) **Submitting "all No"/Everyone would be a FALSE declaration → suspension
risk** — caught before submit. Needs your email + OK. Re-doable later.
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

## Store presence (not started — needs your assets/copy)

<details>
<summary>Select app category & contact details — ⏳ not started</summary>

Needs: app category (e.g. Education / Lifestyle / Communication), contact email,
optional phone/website (riffy.pro).
</details>

<details>
<summary>Main store listing — ⏳ not started (needs assets)</summary>

Needs from you: short description (80 chars), full description (4000 chars),
app icon (512×512), feature graphic (1024×500), and **phone screenshots**
(onboarding, home, practice, task runtime, profile, paywall).
</details>

---

## Release / testing (later)

<details>
<summary>Closed testing — ⏳ required before production</summary>

Personal account ⇒ need **12+ testers for 14 consecutive days**, then apply for
production access. Upload the signed `app-release.aab`. App signing key choice
(Play App Signing) happens at first release — **irreversible**, will confirm with you.
</details>

---

## Open blockers / waiting on you
1. **Content rating** — needs your **email** + explicit OK to submit (agrees to IARC ToS).
   Category "All other app types" already chosen; answers ready (Everyone/3+ + IAP label).
2. **Store listing assets** — short/full description, icon (512×512), feature graphic
   (1024×500), phone screenshots. + app category + contact details.
3. **Firebase config files** — `google-services.json` (Android) + `GoogleService-Info.plist`
   (iOS) needed for Google sign-in + push to actually work; then rebuild AAB.
4. **riffy.pro** must be publicly live (privacy/terms/account-deletion) at review time.
5. **Keep 2-Step Verification OFF** on test@riffy.pro (reviewer account).

### Declaration completion status (10 of 11 actioned)
✅ Privacy policy · Ads · Advertising ID · Government apps · Financial features · Health
✅ Sign-in details (App access) · Target audience (18+) · Data safety (submitted)
🟡 Content rating — category set; needs your email + OK to submit
⏳ Store: app category + contact details, Main store listing — need assets
