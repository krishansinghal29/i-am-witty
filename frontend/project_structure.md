# Frontend Project Structure

React + Vite + TypeScript frontend for the i-am-witty exercise app. Uses Deepgram WebSocket for STT (browser-side) and talks to the FastAPI backend at `VITE_API_URL`.

## Running

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Directory Layout

```
frontend/
├── .env                          # VITE_API_URL, VITE_DEEPGRAM_API_KEY
├── .env.example
├── index.html
├── vite.config.ts                # Path alias: @ → src/
├── tsconfig.app.json             # verbatimModuleSyntax — use `import type` for type-only imports
├── tailwind.config.js
├── package.json
└── src/
    ├── main.tsx                  # Entry: QueryClientProvider, UserProvider, BrowserRouter
    ├── App.tsx                   # Tab bar (7 exercises) + Regular/Sprint toggle + React Router routes
    ├── App.css
    ├── index.css                 # Tailwind base styles
    ├── api/
    │   ├── api.ts                # All fetch calls to backend (BASE_URL from VITE_API_URL)
    │   └── fetchWithHeaders.ts   # Thin fetch wrapper (sets Content-Type)
    ├── contexts/
    │   └── UserContext.tsx       # Provides sessionUid (localStorage UUID) + isAnonymous=true
    ├── hooks/
    │   ├── index.ts              # Re-exports all hooks
    │   ├── queryKeys.ts          # TanStack Query key factories
    │   ├── useDeepgramSTT.ts     # Deepgram WebSocket STT hook — manages recording, transcript, audioBase64
    │   ├── useExerciseMeta.ts    # Fetches exercise list from /get_recommended_exercise
    │   ├── useGenerateQuestion.ts# Fetches question from /generate_question_v2
    │   ├── useEvaluateResponse.ts# Mutation: POST /unified_evaluation
    │   └── useSprintPractice.ts  # useGenerateSprintQuestion + useAnalyzeSprintResponse + prefetch helper
    ├── types/
    │   ├── exercise.ts           # Exercise, ExerciseStep types
    │   ├── evaluation.ts         # EvaluationResponse, UnifiedEvaluationResponse types
    │   └── question.ts           # QuestionMessage type (role + content)
    ├── utils/
    │   ├── getRandomExercisePages.ts  # Maps raw exercise data → ExerciseMeta (intro/examples)
    │   ├── sprintConstants.ts    # RECORDING_LIMIT_SECONDS, SprintStep type
    │   └── sprintHelpers.ts      # extractDisplayText — collapses question array to display string
    ├── components/
    │   ├── QuestionDisplay.tsx   # Renders a QuestionMessage array (role + content rows)
    │   ├── exercise/
    │   │   └── ExerciseHeader.tsx# Top bar: exercise name + step indicator (intro/practice/feedback)
    │   └── sprint/
    │       ├── StepLoading.tsx   # Spinner shown while fetching sprint question
    │       ├── StepListening.tsx # Shows avatar + word-by-word text reveal while audio plays
    │       ├── StepRecording.tsx # Microphone UI + countdown timer + live transcript
    │       ├── StepAnalyzing.tsx # Spinner shown while analyzing sprint response
    │       └── StepFeedback.tsx  # Sprint results: scores (text/voice/overall) + feedback
    ├── pages/
    │   ├── exercise/
    │   │   ├── ExerciseFlow.tsx        # Orchestrates intro→example→practice→feedback for regular exercises
    │   │   ├── ExerciseIntroductionPage.tsx  # Intro slide with exercise name, description, skills
    │   │   ├── ExerciseExamplePage.tsx       # Example conversation display
    │   │   ├── ExercisePracticePage.tsx      # Shows AI question, records user response, triggers evaluation
    │   │   └── ExerciseFeedbackPage.tsx      # Shows AI feedback + sample answer; retry / next buttons
    │   └── practice/
    │       └── SprintExercise.tsx      # Full sprint flow: loading→listening→recording→analyzing→feedback
    └── assets/
        ├── hero.png
        ├── react.svg
        └── vite.svg
```

## Routing

| Path | Component | Description |
|------|-----------|-------------|
| `/` | redirect | Redirects to `/exercise/yesAnd` |
| `/exercise/:exerciseId/:count?` | `ExerciseFlow` | Regular exercise (text response + AI feedback) |
| `/sprint/:exerciseId/:count?` | `SprintExercise` | Sprint mode (voice response + delivery analysis) |

The tab bar in `App.tsx` (`AppShell`) reads `exerciseId` from `useParams` to highlight the active tab, and the Regular/Sprint toggle switches between `/exercise/` and `/sprint/` prefixes.

## Data Flow

### Regular Exercise
1. `ExerciseFlow` (step: `intro`) → user clicks Next
2. Step: `example` → shows sample conversation
3. Step: `practice` → `useGenerateQuestion` fetches question from `/generate_question_v2`
4. User records response via `useDeepgramSTT`
5. `useEvaluateResponse` POSTs to `/unified_evaluation`
6. Step: `feedback` → shows AI feedback + sample answer

### Sprint Exercise
1. `SprintExercise` (step: `intro`) → user clicks Next
2. Step: `example` → shows sample conversation
3. Step: `loading` → `useGenerateSprintQuestion` fetches from `/generate_sprint_question`
4. Step: `listening` → plays base64 mp3 audio, reveals text word-by-word; transitions to `recording` on audio end or fallback timer
5. Step: `recording` → user records via `useDeepgramSTT`; countdown timer auto-stops
6. Step: `analyzing` → `useAnalyzeSprintResponse` POSTs to `/analyze_sprint_response`
7. Step: `feedback` → shows scores (text/voice/overall) + feedback; option to refine (retry) or advance to next count

## Key Design Decisions

- **`verbatimModuleSyntax`**: All type-only imports must use `import type { X }` or `import { type X }` syntax.
- **No Firebase**: `UserContext` generates a `sessionUid` from `crypto.randomUUID()` stored in `localStorage`. No auth.
- **No `uid` in API calls**: Backend is stateless; `uid` is not sent to any endpoint.
- **Deepgram STT**: Browser-side WebSocket connection. The `useDeepgramSTT` hook manages the socket lifecycle, returns `transcript`, `audioBase64`, `durationSeconds`, `wordCount`.
- **Sprint audio fallback**: `audio.ended` event is unreliable for data URIs in Chrome. A `setTimeout` fires `goToRecording()` after `wordCount × 150ms + 2000ms` as a safety net.
- **`@` path alias**: `@/` maps to `src/` in both `vite.config.ts` and `tsconfig.app.json`.
