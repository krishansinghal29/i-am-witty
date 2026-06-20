# Roleplay conversation (prototype)

A standalone, latency-first spoken conversation prototype. The user and AI take
turns talking. API keys stay on the server. The browser records each turn and
posts it to the server, which transcribes it with the configured dictation
provider; the full sentence appears once the user stops speaking.

Providers for **chat**, **dictation**, and **speech** are pluggable and selected
in `.env` (see [Config](#config-env)):

- **chat**: OpenAI (GPT-5.3) · Sarvam (sarvam-30b / 105b)
- **dictation**: Deepgram · ElevenLabs Scribe · Sarvam Saarika (Hinglish)
- **speech**: ElevenLabs · Sarvam Bulbul (Hinglish)

```
roleplay/
  .env             provider selection + keys + utterance timing (the config file)
  run.sh           launcher: ./run.sh old|new (both use design/backend/.venv)
  server/
    config.py      reads .env -> typed chat / dictation / speech providers
    dictation.py   batch speech-to-text (Deepgram / ElevenLabs / Sarvam)
    speech.py      batch text-to-speech (Sarvam Bulbul; ElevenLabs streams inline)
    main.py        FastAPI: sessions, chat stream, TTS stream, transcribe
    character.py   per-session persona generation (roll + synthesize)
    prompts.py     synthesizer + roleplay prompt templates
    data/          curated seed lists (settings, garments, names, …)
  web/             index.html · styles.css · app.js
  server_new/      roleplay_sim — verbal-game simulator (hidden-state engine; run_tests.py)
```

## Run

```bash
cd roleplay
./run.sh old             # legacy prototype  -> http://localhost:8030
./run.sh new             # roleplay_sim sim  -> http://localhost:8031
```

Both targets use the shared `design/backend/.venv`. The **new** simulator lives in
`server_new/` (package `roleplay_sim`); run its tests pytest-free with
`cd server_new && ../design/backend/.venv/bin/python run_tests.py`.

Keys:

- `roleplay/.env` → `OPENAI_API_KEY`, `DEEPGRAM_API_KEY`, `ELEVENLABS_API_KEY`, `SARVAM_API_KEY`, `ROLEPLAY_*`
- `design/backend/.env` → `OPENAI_API_KEY` / `GEMINI_API_KEY`, model fallbacks (**old** server only)

The **new** server reads keys only from `roleplay/.env` (loaded automatically — no `export`).
Check `/api/health` to confirm which providers are selected and configured.

## Flow

`Start → new persona generated → AI sets the scene (streamed) → listen → user speaks → ≥N ms silence → turn recorded & transcribed → full sentence shown → AI replies in character (streamed) → repeat`

- **History** lives on the server per `session_id`, alongside that session's generated system prompt. The client only sends the latest user message.
- **Try new conversation** creates a fresh session — a brand-new woman — and the AI opens again.
- **No barge-in** for now: mic is muted while the AI speaks.

## Character generation

Every session rolls a fresh woman (`server/character.py`). Two tiers:

- **Observable** (what he sees at first glance): where she is, her style archetype + outfit, build, an apparent-age band, plus a *bounded* handful of optional spotlight details (shoes, hair, an accessory, what she's holding, …) and a rare distinguishing mark (~15%). One "spark" word is always offered as loose inspiration the synthesizer may ignore.
- **Latent** (revealed only in conversation): name, exact age, profession, hometown (Indian state), hobbies.

Grounded facts come from curated lists in `server/data/`; optional details use *count-then-sample* (roll how many, then which) so the description never bloats or goes bare. A **synthesizer** LLM call turns the observable facts into a 2–3 sentence, plain-language first impression — it never sees the latent backstory, so it can't leak it. The first impression + latent block + roleplay rules become that session's system prompt. The roleplay model's **first turn narrates the scene**; from the second turn on it speaks in character. Age tiers: 18–22 / 23–26 / 27–30.

Set `ROLEPLAY_SYSTEM_PROMPT` to pin a fixed persona and skip generation.

## API

| endpoint | purpose |
|---|---|
| `GET /api/config` | `utterance_end_ms`, `no_speech_end_ms`, dictation provider, model info |
| `POST /api/session/new` | `{session_id}` |
| `POST /api/chat/stream` | SSE tokens + done; body `{session_id, message?}` |
| `POST /api/tts/stream` | streaming MP3 for `{text}` |
| `POST /api/transcribe` | batch STT: WAV body in → `{transcript}` out |

## Config (`roleplay/.env`)

The `.env` **is** the config file. The two main knobs select providers; the rest
tune them (sensible defaults preserve Deepgram + GPT-5.3). Secrets stay in env.

| var | default | notes |
|---|---|---|
| `ROLEPLAY_CHAT` | `openai` | chat provider: `openai` \| `sarvam` |
| `ROLEPLAY_DICTATION` | `deepgram` | STT provider: `deepgram` \| `elevenlabs` \| `sarvam` |
| `ROLEPLAY_SPEECH` | `elevenlabs` | TTS provider: `elevenlabs` \| `sarvam` |
| `DEEPGRAM_API_KEY` | — | Deepgram STT |
| `ELEVENLABS_API_KEY` | — | ElevenLabs TTS + Scribe STT |
| `SARVAM_API_KEY` | — | Sarvam chat + STT |
| `ROLEPLAY_UTTERANCE_END_MS` | `2000` | trailing silence before a turn is sent, once the user has started speaking |
| `ROLEPLAY_NO_SPEECH_END_MS` | `6000` | grace silence before giving up when the user hasn't spoken at all yet |
| `ROLEPLAY_OPENAI_CHAT_MODEL` | `gpt-5.3-chat-latest` | OpenAI chat model |
| `ROLEPLAY_SARVAM_CHAT_MODEL` | `sarvam-30b` | Sarvam chat model (or `sarvam-105b`) |
| `ROLEPLAY_SARVAM_API_BASE` | `https://api.sarvam.ai/v1` | Sarvam OpenAI-compatible base |
| `ROLEPLAY_DEEPGRAM_MODEL` / `_LANGUAGE` | `nova-3` / `en-US` | Deepgram STT |
| `ROLEPLAY_ELEVENLABS_STT_MODEL` / `_LANGUAGE` | `scribe_v1` / auto | Scribe STT |
| `ROLEPLAY_SARVAM_STT_MODEL` / `_LANGUAGE` | `saarika:v2.5` / `unknown` | Saarika STT (`unknown` = auto, handles Hinglish) |
| `ROLEPLAY_SARVAM_STT_MODE` | — | `saaras:v3` only: `translit` = native romanized Hinglish in one call |
| `ROLEPLAY_ROMANIZE` | `false` | post-transcription transliterate → Roman/Hinglish for ElevenLabs/Deepgram (no native romanization); pair ElevenLabs with `ROLEPLAY_ELEVENLABS_STT_LANGUAGE=hi`. For Sarvam prefer the native `STT_MODE=translit` above |
| `ROLEPLAY_GEN_MODEL` | chat model | model that writes the first-impression blurb |
| `ROLEPLAY_SYSTEM_PROMPT` | — | pin a fixed persona; skips per-session generation |
| `ROLEPLAY_VOICE_ID` | Rachel | ElevenLabs voice |
| `ROLEPLAY_TTS_MODEL` | `eleven_flash_v2_5` | ElevenLabs TTS model |
| `ROLEPLAY_SARVAM_TTS_MODEL` | `bulbul:v2` | Sarvam TTS model |
| `ROLEPLAY_SARVAM_TTS_SPEAKER` | `anushka` | Sarvam voice (female: anushka, manisha, vidya, arya) |
| `ROLEPLAY_SARVAM_TTS_LANGUAGE` | `hi-IN` | Sarvam locale (handles Hinglish) |

## Latency

- LLM tokens stream to the UI via SSE as they arrive.
- TTS fires per sentence chunk while the LLM is still generating.
- End-of-turn silence (`ROLEPLAY_UTTERANCE_END_MS`, or the longer `ROLEPLAY_NO_SPEECH_END_MS` grace before the user has said anything) doubles as a natural pause before the AI replies.
- Dictation is batch (one transcription round-trip per turn) rather than live streaming — the trade-off for swapping providers freely and getting the full, punctuated sentence at once.

## Limits

- In-memory sessions (lost on server restart).
- No history cap yet — long chats may hit model context limits later.
- No barge-in.
