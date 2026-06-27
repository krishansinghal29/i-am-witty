# Lesson caption resources

One JSON file per lesson, named `<audio_key>.json` (e.g. `pushPull.json`,
`intro.json`) — the same stem as the hosted `<audio_key>.mp3`.

Shape:

```json
{
  "transcript": "Push-pull. This really is the core idea ...",
  "cues": [
    { "start": 0.00, "end": 0.42, "text": "Push-pull." },
    { "start": 0.42, "end": 0.71, "text": "This" }
  ]
}
```

`cues` are word-level, time-aligned to the **final** (sped-up) mp3 we ship, and
are produced offline by the forced-alignment pass in `audio-content/`
(see `align.py`). `LessonTaskEngine` reads these at generate time and returns
them in the task runtime payload; a missing file degrades gracefully to audio
with no synced captions (the seeded `content.transcript` is then used as a
plain-text fallback).
