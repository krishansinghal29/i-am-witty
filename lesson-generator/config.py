import os
from dotenv import load_dotenv

load_dotenv()


def get(key: str, required: bool = True) -> str:
    val = os.getenv(key)
    if required and not val:
        raise EnvironmentError(f"Missing required env var: {key}")
    return val or ""


OPENAI_API_KEY = get("OPENAI_API_KEY")
ANTHROPIC_API_KEY = get("ANTHROPIC_API_KEY")
ELEVENLABS_API_KEY = get("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = get("ELEVENLABS_VOICE_ID", required=False) or "pNInz6obpgDQGcFmaJgB"
