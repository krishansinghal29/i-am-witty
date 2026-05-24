# Lesson Generator — Project Structure

A CLI pipeline that converts mixed source content (text, HTML, video) into a spoken audio lesson.

## Data Flow

```
Input files (txt/html/mp4/etc.)
        │
        ▼
Module 1 — Ingestion
  → list[IngestedFile]   (cached as <name>_transcript.json next to each source file)
        │
        ▼
Module 2 — Script Generator  ← requires --topic
  → LessonScript         (saved to output/scripts/lesson_script_<topic_slug>.json/.txt)
        │
        ▼
Module 3 — Audio Generator   ← --topic optional (auto-detects if only one script exists)
  → AudioOutput          (saved to output/audio/lesson_<topic_slug>.mp3)
        │
        ▼
[Module 4 — Avatar Video] (deferred, see docs/module4_video.md)
        │
        ▼
[Module 5 — Assembly]     (deferred, see docs/module5_assembly.md)
```

## File Map

```
lesson-generator/
├── main.py                         CLI entry point; orchestrates modules 1→2→3
├── config.py                       Loads API keys from .env
├── models.py                       Shared dataclasses: IngestedFile, LessonScript, ScriptSegment, AudioOutput
├── requirements.txt
├── .env.example                    Copy to .env and fill in API keys
│
├── modules/
│   ├── ingestion/
│   │   ├── text_parser.py          Parses .txt, .md, .html → IngestedFile
│   │   ├── video_transcriber.py    OpenAI Whisper API → IngestedFile; extracts audio via ffmpeg first
│   │   └── ingestor.py             Recurses input dir; caches results as <name>_transcript.json next to source
│   │
│   ├── script_generator/
│   │   ├── generator.py            Claude API → LessonScript; filters content by topic
│   │   └── prompts/
│   │       ├── system.txt          Claude system prompt (topic filtering, lesson structure, pause markers, JSON schema)
│   │       └── user_template.txt   User prompt template with {topic} and {content} placeholders
│   │
│   └── audio_generator/
│       └── generator.py            ElevenLabs v3 → lesson_<topic_slug>.mp3
│
├── content/                        Source files + their cached transcripts live here
│   └── <topic-folder>/
│       ├── Video.mp4
│       └── Video_transcript.json   ← written by module 1, read by module 2
│
├── output/
│   ├── scripts/                    lesson_script_<topic_slug>.json + .txt
│   └── audio/                      lesson_<topic_slug>.mp3
│
└── docs/
    ├── module4_video.md            Plan: HeyGen/D-ID avatar video generation
    └── module5_assembly.md         Plan: FFmpeg final video assembly
```

## APIs Used

| Module | API | Purpose |
|--------|-----|---------|
| 1 | OpenAI Whisper (`whisper-1`) | Video/audio → transcript |
| 2 | Anthropic Claude (`claude-sonnet-4-6`) | Content → lesson script with pause markers |
| 3 | ElevenLabs (`eleven_v3`) | Script → MP3 audio |
| 4 (planned) | HeyGen or D-ID | Audio + avatar → talking-head MP4 |
| 5 (planned) | FFmpeg (local) | Compose final video with slides and captions |

## Running the Pipeline

```bash
# Setup
cp .env.example .env   # fill in your API keys
pip install -r requirements.txt

# Full pipeline
python main.py --input ./content --topic "how to close an interaction"

# Individual modules
python main.py --input ./content --module 1                                         # no --topic needed
python main.py --input ./content --module 2 --topic "how to close an interaction"
python main.py --input ./content --module 3                                         # auto-detects script if only one exists
python main.py --input ./content --module 3 --topic "how to close an interaction"   # explicit topic

# Override voice
python main.py --input ./content --topic "..." --voice <elevenlabs_voice_id>
```

Each module is independently cacheable. Delete a module's output file to force a re-run of just that stage.

## Adding a New Input File Type

1. Add the extension handling in `modules/ingestion/ingestor.py`
2. Write a parser function in `text_parser.py` (for document types) or a new file
3. Return an `IngestedFile` — the rest of the pipeline is type-agnostic

## Swapping an API Provider

- **Transcription**: replace `video_transcriber.py` internals; keep the `IngestedFile` return shape
- **Script generation**: replace `generator.py` in `script_generator/`; keep `LessonScript` return shape
- **TTS**: replace `generator.py` in `audio_generator/`; keep `AudioOutput` return shape

## Caching Behaviour

| Module | Cache location | Cache key |
|--------|---------------|-----------|
| 1 | `<source_dir>/<filename>_transcript.json` | Per file — presence of the JSON |
| 2 | `output/scripts/lesson_script_<topic_slug>.json` | Per topic slug |
| 3 | `output/audio/lesson_<topic_slug>.mp3` | Per topic slug |

Topic slug = topic string lowercased, spaces → underscores, truncated to 60 chars.

To force re-run of a stage, delete its output file.

## Default Voice

**Adam** (`pNInz6obpgDQGcFmaJgB`) — deep, authoritative American male. Good for educational narration.
Alternative: **Daniel** (`onwK4e9ZLuTAKqWW03F9`) — British authoritative.
Override per-run with `--voice <id>` or set `ELEVENLABS_VOICE_ID` in `.env`.

## Pause Marker Convention (ElevenLabs v3)

The script generator (Module 2) embeds these markers in `raw_text`:
- `[short pause]` — brief beat (~0.3s)
- `[pause]` — natural pause (~0.8s)
- `[long pause]` — section break (~1.5s)

These are passed through as-is to ElevenLabs v3, which handles them natively. Do **not** convert to SSML `<break>` tags — those are for older ElevenLabs models only.
