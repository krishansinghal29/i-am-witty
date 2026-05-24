# Module 4 — Avatar Video Generation

Converts `output/audio/lesson.mp3` into a talking-head MP4 using an AI avatar API.

## Input / Output

- **Input**: `output/audio/lesson.mp3` (produced by Module 3)
- **Input**: avatar ID (stock or custom clone)
- **Output**: `output/video/lesson_avatar.mp4`

---

## Recommended Provider: HeyGen

HeyGen produces the highest-quality lip-sync and is the most developer-friendly option as of 2026.

### Auth
All requests require `X-Api-Key: <HEYGEN_API_KEY>` header.

### Step 1 — Upload audio

```http
POST https://upload.heygen.com/v1/asset
Content-Type: <audio/mpeg or audio/wav>
X-Api-Key: ...

<binary audio data>
```

Response:
```json
{ "data": { "asset_id": "aud_abc123" } }
```

### Step 2 — Create video

```http
POST https://api.heygen.com/v2/video/generate
X-Api-Key: ...
Content-Type: application/json

{
  "video_inputs": [
    {
      "character": {
        "type": "avatar",
        "avatar_id": "<AVATAR_ID>",
        "avatar_style": "normal"
      },
      "voice": {
        "type": "audio",
        "audio_asset_id": "aud_abc123"
      },
      "background": {
        "type": "color",
        "value": "#FAFAFA"
      }
    }
  ],
  "dimension": { "width": 1280, "height": 720 }
}
```

Response:
```json
{ "data": { "video_id": "vid_xyz789" } }
```

### Step 3 — Poll for completion

```http
GET https://api.heygen.com/v1/video_status.get?video_id=vid_xyz789
X-Api-Key: ...
```

Poll every 10–15 seconds until `status == "completed"`. Then:
```json
{ "data": { "status": "completed", "video_url": "https://..." } }
```

### Step 4 — Download

```python
import requests
r = requests.get(video_url)
with open("output/video/lesson_avatar.mp4", "wb") as f:
    f.write(r.content)
```

---

## Alternative Provider: D-ID

D-ID is cheaper at entry level ($5.90/mo) but avatar quality is lower.

### Create a talk

```http
POST https://api.d-id.com/talks
Authorization: Basic <base64(api_key:)>
Content-Type: application/json

{
  "source_url": "<URL of avatar image or use a D-ID stock presenter>",
  "script": {
    "type": "audio",
    "audio_url": "<publicly accessible URL of lesson.mp3>"
  }
}
```

Note: D-ID requires the audio to be at a public URL. You'll need to upload the MP3 to S3, GCS, or similar first.

Response:
```json
{ "id": "tlk_abc123" }
```

### Poll status

```http
GET https://api.d-id.com/talks/tlk_abc123
Authorization: Basic ...
```

Poll until `"status": "done"`, then download `result_url`.

---

## Env Vars to Add

```
HEYGEN_API_KEY=...
HEYGEN_AVATAR_ID=...       # stock avatar ID from HeyGen dashboard

# or for D-ID:
DID_API_KEY=...
DID_PRESENTER_ID=...       # e.g. "amy-jcwCkr1grs" (D-ID stock presenter)
```

---

## Implementation Notes

- Place implementation in `modules/video_generator/generator.py`
- Function signature: `generate_video(audio_path: str | Path, output_video_dir: str | Path) -> VideoOutput`
- Add `VideoOutput` dataclass to `models.py`: `file_path: str, avatar_id: str, duration_secs: float`
- Add `--module 4` support to `main.py`
- HeyGen video generation typically takes 1–3 minutes; poll with exponential backoff (start at 10s, max 30s)
