"""Summarize a transcript into an abstract + key points via OpenAI."""
from __future__ import annotations
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import json
import re

import openai
import config

_MODEL = "gpt-4o-mini"
_client = openai.OpenAI(api_key=config.OPENAI_API_KEY, max_retries=6)

_PROMPT = """You are summarizing the transcript of a single lesson video titled "{title}".

Write a faithful summary of what the video teaches. Respond with ONLY a JSON object, no prose, no code fences:
{{"abstract": "<2-4 sentence overview of the video's content>", "key_points": ["<concise takeaway>", "..."]}}

Use 3-6 key points. Keep them specific to what is actually said in the transcript.

Transcript:
{transcript}"""


def _extract_json(raw: str) -> dict:
    raw = raw.strip()
    # Strip ```json ... ``` fences if the model added them.
    fence = re.match(r"^```(?:json)?\s*(.*?)\s*```$", raw, re.DOTALL)
    if fence:
        raw = fence.group(1).strip()
    return json.loads(raw)


def summarize_transcript(text: str, title: str = "") -> dict | None:
    """Return {"abstract": str, "key_points": [str, ...]} or None on empty input."""
    text = (text or "").strip()
    if not text:
        return None

    response = _client.chat.completions.create(
        model=_MODEL,
        max_tokens=1024,
        response_format={"type": "json_object"},
        messages=[
            {"role": "user", "content": _PROMPT.format(title=title or "Untitled", transcript=text)}
        ],
    )
    raw = response.choices[0].message.content or ""

    try:
        data = _extract_json(raw)
    except (json.JSONDecodeError, ValueError):
        # Fall back to storing the raw text rather than failing the whole file.
        return {"abstract": raw.strip(), "key_points": []}

    return {
        "abstract": str(data.get("abstract", "")).strip(),
        "key_points": [str(p).strip() for p in data.get("key_points", []) if str(p).strip()],
    }
