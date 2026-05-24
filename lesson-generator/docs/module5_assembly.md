# Module 5 — Final Video Assembly

Composes the talking-head MP4 (Module 4) with optional slide images, B-roll, captions, and intro/outro into a final `lesson_final.mp4`.

## Input / Output

- **Input**: `output/video/lesson_avatar.mp4` (Module 4)
- **Input**: (optional) slide images in `content/slides/` (PNG/JPG)
- **Input**: (optional) Whisper transcript JSON from `output/transcripts/` → SRT subtitles
- **Output**: `output/video/lesson_final.mp4`

**Tool**: FFmpeg (local, free). Install: `brew install ffmpeg` or `apt install ffmpeg`.

---

## Step 1 — Generate SRT subtitles from Whisper transcript

The Whisper API returns word-level timestamps when called with `response_format="verbose_json"`.

Update `video_transcriber.py` to save the raw verbose response, then convert to SRT:

```python
def transcript_to_srt(verbose_json: dict, out_path: str):
    segments = verbose_json["segments"]
    lines = []
    for i, seg in enumerate(segments, 1):
        start = format_timestamp(seg["start"])
        end = format_timestamp(seg["end"])
        lines.append(f"{i}\n{start} --> {end}\n{seg['text'].strip()}\n")
    with open(out_path, "w") as f:
        f.write("\n".join(lines))

def format_timestamp(secs: float) -> str:
    h = int(secs // 3600)
    m = int((secs % 3600) // 60)
    s = int(secs % 60)
    ms = int((secs % 1) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"
```

---

## Step 2 — Burn subtitles into avatar video

```bash
ffmpeg -i output/video/lesson_avatar.mp4 \
       -vf "subtitles=output/transcripts/lesson.srt:force_style='FontSize=20,PrimaryColour=&Hffffff'" \
       -c:a copy \
       output/video/lesson_subtitled.mp4
```

---

## Step 3 — Side-by-side: avatar + slide (optional)

If you have slide images (one per segment), compose them next to the talking head:

```bash
# Scale avatar to left half, slide image to right half, stack horizontally
ffmpeg -i output/video/lesson_avatar.mp4 \
       -i content/slides/slide_01.png \
       -filter_complex "[0:v]scale=640:720[av];[1:v]scale=640:720,loop=-1:1[sl];[av][sl]hstack=inputs=2[v]" \
       -map "[v]" -map 0:a \
       -c:v libx264 -c:a copy \
       output/video/lesson_composed.mp4
```

For multiple slides timed to segments, use `ffmpeg`'s `overlay` + `setpts` filters or script it per-segment and concatenate (Step 5).

---

## Step 4 — Add intro/outro bumper (optional)

Place bumper clips at `content/bumpers/intro.mp4` and `content/bumpers/outro.mp4`.

Create a concat list:
```bash
echo "file 'content/bumpers/intro.mp4'" > /tmp/concat.txt
echo "file 'output/video/lesson_composed.mp4'" >> /tmp/concat.txt
echo "file 'content/bumpers/outro.mp4'" >> /tmp/concat.txt

ffmpeg -f concat -safe 0 -i /tmp/concat.txt -c copy output/video/lesson_final.mp4
```

All clips must share the same resolution, framerate, and codec for `-c copy` to work. Re-encode if needed:
```bash
ffmpeg -i input.mp4 -vf scale=1280:720 -r 30 -c:v libx264 -c:a aac output_normalized.mp4
```

---

## Step 5 — Full pipeline (no bumpers, no slides)

Simplest case — just burn subtitles and output:

```bash
ffmpeg -i output/video/lesson_avatar.mp4 \
       -vf "subtitles=output/transcripts/lesson.srt" \
       -c:a copy \
       output/video/lesson_final.mp4
```

---

## Implementation Notes

- Place implementation in `modules/assembler/assembler.py`
- Function signature: `assemble_video(avatar_video: str, srt_path: str | None, slides_dir: str | None, output_dir: str) -> str`
- Uses `subprocess.run(["ffmpeg", ...], check=True)` — requires FFmpeg on PATH
- Add `--module 5` support to `main.py`
- Add `AssemblyOutput` dataclass to `models.py`: `file_path: str`

## Env Vars to Add

None — FFmpeg is a local tool.

## Dependencies to Add

No new Python packages. FFmpeg must be installed system-wide.
