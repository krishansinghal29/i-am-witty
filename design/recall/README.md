# Riffy Recall (web)

The owner-only Recall admin at **recall.riffy.pro/admin**: add lines, concepts,
routines and focus check-ins (by hand or with Quick add), and manage cues. It
talks to the existing backend (`design/backend`, `/v1/admin/recall/*`) and signs
the owner in with Firebase Auth (same Firebase project as the app).

Practice lives in the Riffy app's Recall tab (riffy.pro/app/recall). Hosting
redirects recall.riffy.pro/ there (see `firebase.json`).

Approved design: `design/ux_existing/mockups/html/recall.html`.

## Develop

```bash
cp .env.example .env   # fill in VITE_API_BASE_URL and VITE_FIREBASE_*
npm install
npm run dev            # http://localhost:5174
```

The backend must allow the `http://localhost:5174` origin (CORS) for local dev.

## Build

```bash
npm run build          # type-check + production build into dist/
```

`.env.production` points production builds at the Cloud Run backend.

## Deploy

Hosting target `recall` maps to the Firebase Hosting site `riffy-recall`
(see `.firebaserc`).

```bash
npm run build
firebase deploy --only hosting:recall
```

## Access

The backend allows only the emails in `ADMIN_EMAILS` (verified Google sign-in).
Any other account sees "This account can't edit Recall."
