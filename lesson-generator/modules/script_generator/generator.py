import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import json
from pathlib import Path

import anthropic

import config
from models import IngestedFile, LessonScript, ScriptSegment

_PROMPTS_DIR = Path(__file__).parent / "prompts"


def generate_script(ingested_files: list[IngestedFile], topic: str) -> LessonScript:
    system_prompt = (_PROMPTS_DIR / "system.txt").read_text()
    user_template = (_PROMPTS_DIR / "user_template.txt").read_text()

    combined_content = "\n\n".join(
        f"---\n{f.filename}\n---\n{f.content}" for f in ingested_files
    )
    user_message = user_template.format(topic=topic, content=combined_content)

    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=[
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_message}],
    )

    data = json.loads(response.content[0].text)

    segments = [
        ScriptSegment(
            heading=seg["heading"],
            text=seg["text"],
            speaker_notes=seg.get("speaker_notes", ""),
        )
        for seg in data["segments"]
    ]

    return LessonScript(
        title=data["title"],
        estimated_duration_secs=data["estimated_duration_secs"],
        segments=segments,
        raw_text=data["raw_text"],
    )
