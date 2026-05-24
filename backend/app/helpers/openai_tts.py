from __future__ import annotations

import base64
import os
from helpers.logger import logger

import openai


def generate_tts(text: str, voice: str = "nova") -> str | None:
    """Generate TTS audio via OpenAI and return base64-encoded mp3."""
    try:
        client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text,
        )
        return base64.b64encode(response.content).decode("utf-8")
    except Exception as e:
        logger.error(f"OpenAI TTS failed: {str(e)}")
        return None


def text_to_speech_multi_role(question_parts: list) -> dict | None:
    """
    Generate TTS for a multi-role question array.
    Concatenates all non-Image parts and speaks them with a single voice.
    Returns dict matching the existing sprint question response shape.
    """
    try:
        text_parts = []
        for part in question_parts:
            if not isinstance(part, dict):
                continue
            role = part.get("role", "")
            content = part.get("content", "")
            if role == "Image" or not content:
                continue
            if role:
                text_parts.append(f"{role}: {content}")
            else:
                text_parts.append(content)

        speech_text = "\n".join(text_parts)
        if not speech_text.strip():
            return None

        audio_b64 = generate_tts(speech_text)
        if audio_b64 is None:
            return None

        return {
            "audio_content_base64": audio_b64,
            "audio_content_type": "audio/mpeg",
            "speech_text": speech_text,
        }
    except Exception as e:
        logger.error(f"text_to_speech_multi_role failed: {str(e)}")
        return None
