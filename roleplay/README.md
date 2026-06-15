# Roleplay coach (prototype)

A standalone, latency-first prototype that turns the 3-stage push-pull exercise
into a spoken **AI roleplay coach**. It does **not** touch the core app — it
reuses the real production prompt bundle and the existing keys, but runs as its
own thin proxy + single HTML page.

```
roleplay/
  .env             ELEVENLABS_API_KEY (+ optional ROLEPLAY_VOICE_ID / *_MODEL)
  run.sh           launcher (uses design/backend/.venv)
  server/main.py   FastAPI proxy: /api/token /api/question /api/evaluate /api/tts
  web/             index.html · styles.css · app.js (state machine + streaming)
```

## Run

```bash
cd roleplay
./run.sh                 # -> http://localhost:8030
```

Keys are read from:

- `design/backend/.env` → `DEEPGRAM_API_KEY`, `OPENAI_API_KEY` / `GEMINI_API_KEY`,
  `LLM_GENERATOR_MODEL`, `LLM_EVALUATOR_MODEL`
- `roleplay/.env` → `ELEVENLABS_API_KEY` (+ optional overrides below)

Open `/api/health` to confirm what's wired.

## The flow

`GREET → EXPLAIN → EXAMPLE → ASK(question) → 30s soft think → LISTEN
→ ≥2s silence → EVALUATE → 1–2 line spoken feedback → retry / new / scaffold`

- **Question** = the real `pushPull` generator (`design/backend` prompt bundle).
- **Evaluator** = same production criteria, but a compact, *speakable* output
  (`{verdict, spoken_feedback, struggle, suggest}`).
- **Turn-taking** = Deepgram streaming. The 30s window only matters until you
  start talking; once you do, it waits for you to finish. End-of-turn = ≥2s of
  silence (`utterance_end_ms`), which is also the deliberate "pause before I
  reply" beat. `I'm done` forces the turn if needed.
- **Scaffolding** = if you struggle on the full thing, the coach drops to
  **push only**, then **pull only**, then recombines on a fresh scenario.

## Latency design

- Static coach lines are synthesized once and cached server-side (`/api/tts`),
  so they replay instantly.
- The first question is generated *while the coach explains*; the next one is
  generated *while you answer* — so the question audio is ready when needed.
- The evaluator fires the instant your turn ends; its latency hides under the
  ≥2s end-of-turn silence. Feedback is spoken via ElevenLabs Flash.

## Config (roleplay/.env, all optional except the key)

| var | default | notes |
|---|---|---|
| `ELEVENLABS_API_KEY` | — | required |
| `ROLEPLAY_VOICE_ID` | `21m00Tcm4TlvDq8ikWAM` (Rachel) | any ElevenLabs voice id |
| `ROLEPLAY_TTS_MODEL` | `eleven_flash_v2_5` | `eleven_turbo_v2_5` for richer voice |
| `ROLEPLAY_GEN_MODEL` | `LLM_GENERATOR_MODEL` | override generation model |
| `ROLEPLAY_EVAL_MODEL` | `LLM_EVALUATOR_MODEL` | e.g. a faster model for lower eval latency |

## Known prototype limits

- No barge-in: the mic is gated while the coach speaks (avoids self-transcription).
- A >2s pause mid-answer ends the turn early — use `I'm done` / `Try again`.
- Push/pull only · single coach voice · in-memory TTS cache (resets on restart).
