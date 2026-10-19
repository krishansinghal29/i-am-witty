# Riffy Recall (web)

Public daily recall practice at **recall.riffy.pro**, plus an owner-only admin at
**/admin** for adding lines, concepts, routines and focus check-ins. It talks to
the existing backend (`design/backend`, `/v1/recall/*` and `/v1/admin/recall/*`)
and signs the owner in with Firebase Auth (same Firebase project as the app).

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

## How identity works

- Visitors get a random learner id kept in this browser (`riffy_recall_learner`
  in localStorage), sent as `X-Recall-Learner` on every practice call.
- When the owner has signed in on this browser (via /admin), practice calls also
  send their Firebase ID token so progress follows them across devices.
  Firebase only loads for /admin or when this browser has signed in before.
