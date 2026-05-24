# Lesson Generator

A CLI pipeline that turns mixed source content — text files, HTML pages, and videos — into a narrated 3–4 minute audio lesson with an AI voice.

## How it works

```
Input files  →  Transcribe / parse  →  Generate script  →  Synthesize audio
(txt/html/mp4)    (OpenAI Whisper)      (Claude Sonnet)     (ElevenLabs v3)
```

1. **Ingestion** — reads `.txt`, `.md`, `.html` files and transcribes `.mp4`/audio files via OpenAI Whisper. Transcripts are cached as `<filename>_transcript.json` alongside each source file.
2. **Script generation** — Claude filters the transcript library to content relevant to your `--topic`, then synthesises a structured 3–4 minute lesson script with natural pause markers.
3. **Audio generation** — ElevenLabs v3 converts the script to an MP3.

Avatar video (Module 4) and final video assembly (Module 5) are planned — see [`docs/`](docs/).

---

## Setup

**Requirements**: Python 3.10+

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure API keys
cp .env.example .env
```

Edit `.env` and fill in your keys:

```env
OPENAI_API_KEY=sk-...          # for Whisper transcription
ANTHROPIC_API_KEY=sk-ant-...   # for lesson script generation
ELEVENLABS_API_KEY=...         # for audio synthesis
ELEVENLABS_VOICE_ID=pNInz6obpgDQGcFmaJgB   # optional, defaults to Adam (authoritative male)
```

API key sources:
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/settings/keys
- ElevenLabs: https://elevenlabs.io/app/settings/api-keys
- ElevenLabs voice IDs: https://elevenlabs.io/voice-library

---

## Usage

### Full pipeline

```bash
python main.py --input ./content --topic "how to close an interaction"
```

Runs all three modules in sequence. Outputs land in `./output/`.

### Run a specific module

```bash
python main.py --input ./content --module 1                                        # ingestion only (no --topic needed)
python main.py --input ./content --module 2 --topic "how to open a conversation"   # script only
python main.py --input ./content --module 3                                        # audio only — auto-detects script if only one exists
python main.py --input ./content --module 3 --topic "how to open a conversation"   # audio only — explicit topic
```

Each module caches its output — re-running skips already-completed work automatically:
- Module 1: skips files that already have a `<filename>_transcript.json` next to them
- Module 2: skips if `output/scripts/lesson_script_<topic>.json` already exists
- Module 3: skips if `output/audio/lesson_<topic>.mp3` already exists

Generate multiple lessons from the same content library by using different `--topic` values — each gets its own output files.

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--input` | *(required)* | Directory containing your source files |
| `--topic` | *(required for module 2)* | Lesson topic — filters all transcripts to relevant content. Optional for module 3: auto-detects if only one script exists. |
| `--output` | `./output` | Where to write generated files |
| `--voice` | from `.env` | ElevenLabs voice ID (overrides `.env`) |
| `--module` | `all` | `1`, `2`, `3`, or `all` |

---

## Supported input file types

| Extension | How it's processed |
|-----------|-------------------|
| `.txt`, `.md` | Read directly |
| `.html`, `.htm` | HTML tags stripped via BeautifulSoup |
| `.mp4`, `.mov`, `.avi`, `.mkv` | Transcribed via OpenAI Whisper |
| `.mp3`, `.wav`, `.m4a` | Transcribed via OpenAI Whisper |

Unknown extensions are skipped with a warning.

---

## Output files

Transcripts are stored **alongside their source files** in `content/`:
```
content/
└── 02. OPEN-Close Model/
    ├── Close.mp4
    ├── Close_transcript.json       ← cached by module 1
    ├── Open.mp4
    └── Open_transcript.json
```

Scripts and audio are stored in `output/`, named by topic slug:
```
output/
├── scripts/
│   ├── lesson_script_how_to_close_an_interaction.json
│   └── lesson_script_how_to_close_an_interaction.txt
└── audio/
    └── lesson_how_to_close_an_interaction.mp3
```

Edit the `.txt` script file to tweak pacing or wording, then re-run `--module 3` to regenerate audio without calling Claude again.

---

## Pause markers

The generated script uses these markers, which ElevenLabs v3 understands natively:

| Marker | Effect |
|--------|--------|
| `[short pause]` | Brief beat (~0.3s) |
| `[pause]` | Natural pause (~0.8s) |
| `[long pause]` | Section break (~1.5s) |

To adjust pacing, edit `output/scripts/lesson_script_<topic>.txt` and re-run `--module 3 --topic "<topic>"` to regenerate audio without calling Claude again.

---

## Project structure

See [`project_structure.md`](project_structure.md) for a full file map, data flow diagram, and notes on extending the pipeline.

## Planned modules

- **Module 4** — AI avatar video (HeyGen / D-ID): [`docs/module4_video.md`](docs/module4_video.md)
- **Module 5** — Final video assembly with subtitles and slides (FFmpeg): [`docs/module5_assembly.md`](docs/module5_assembly.md)
