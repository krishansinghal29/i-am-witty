"""
Sprint Multimodal Agent - Extension of BaseAgent that supports audio + text input.

Used by sprint evaluation agents that need to send raw audio recordings
alongside text prompts to Gemini for multimodal analysis (voice delivery,
filler words, pacing, confidence, etc.).

The key difference from BaseAgent is that `process_multimodal()` constructs
Gemini-native content parts (audio bytes + text) instead of using the
text-only message pipeline from BaseAgent.
"""

import base64
import json
from typing import Optional

from google.genai import types

from agents.base_agent import BaseAgent
from helpers.logger import logger

# Evaluators emit structured JSON feedback, so they run at a stable temperature
# rather than the high default used for creative generation.
EVALUATOR_TEMPERATURE = 1.0


class SprintMultimodalAgent(BaseAgent):
    """
    Agent that supports multimodal input (audio + text) via Gemini.

    Extends BaseAgent with a `process_multimodal()` method that sends
    raw audio bytes alongside a text prompt. The system message and
    few-shot examples from BaseAgent are preserved.
    """

    def __init__(
        self,
        system_message: str,
        few_shot_examples: list[dict] = None,
        model_name: str = None,
        agent_type: str = None,
        response_schema=None,
    ) -> None:
        super().__init__(
            system_message,
            few_shot_examples=few_shot_examples,
            model_name=model_name,
            agent_type=agent_type,
        )
        self.response_schema = response_schema

    def process_multimodal(
        self,
        text_prompt: str,
        audio_base64: Optional[str] = None,
        image_base64: Optional[str] = None,
    ) -> str:
        """
        Send a multimodal request (audio/image + text) to Gemini.

        Constructs native Gemini content parts so that audio/image data
        is processed alongside the text prompt in a single call.

        Args:
            text_prompt: The text portion of the prompt (analysis context).
            audio_base64: Optional base64-encoded audio blob (webm/opus).
            image_base64: Optional base64-encoded image (jpeg). Used for
                          pushPull exercises where the question is an image.

        Returns:
            Raw JSON string from Gemini (cleaned of markdown fences).
        """
        # Build content parts for the user message
        user_parts = []

        # Add audio part if provided
        if audio_base64:
            try:
                audio_bytes = base64.b64decode(audio_base64)
                user_parts.append(
                    types.Part.from_bytes(data=audio_bytes, mime_type="audio/webm")
                )
            except Exception as e:
                logger.warning(f"Failed to decode audio: {e}")

        # Add image part if provided (for pushPull exercises)
        if image_base64:
            try:
                # Strip data URI prefix if present
                raw_b64 = image_base64
                if raw_b64.startswith("data:"):
                    raw_b64 = raw_b64.split(",", 1)[1]
                image_bytes = base64.b64decode(raw_b64)
                user_parts.append(
                    types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
                )
            except Exception as e:
                logger.warning(f"Failed to decode image: {e}")

        # Add combined system instructions + prompt text after media parts
        full_text_prompt = f"System Instructions: {self.system_message['content']}\n\n{text_prompt}"
        user_parts.append(types.Part.from_text(text=full_text_prompt))

        # Build the full contents list as a single user message
        contents = [
            {
                "role": "user",
                "parts": user_parts,
            },
        ]

        # Configure Gemini request
        config_params = {
            "temperature": EVALUATOR_TEMPERATURE,
            "max_output_tokens": 8000,
            "response_mime_type": "application/json",
            "thinking_config": types.ThinkingConfig(thinking_budget=0),
        }
        if self.response_schema:
            config_params["response_schema"] = self.response_schema

        is_gemini = hasattr(self.llm, "_clean_json_response") and hasattr(self.llm, "client")

        if is_gemini:
            try:
                response = self.llm.client.models.generate_content(
                    model=self.llm.model_name,
                    contents=contents,
                    config=types.GenerateContentConfig(**config_params),
                )
                return self.llm._clean_json_response(response.text)
            except Exception as e:
                logger.error(f"Multimodal Gemini call failed: {e}")
                raise

        # OpenAI path — text-only using the transcript already in text_prompt
        try:
            messages = [
                self.system_message,
                {"role": "user", "content": full_text_prompt},
            ]
            result = self.llm.get_response(
                messages,
                response_schema=self.response_schema,
                generation_config={"temperature": EVALUATOR_TEMPERATURE},
            )
            if hasattr(result, "model_dump"):
                return json.dumps(result.model_dump())
            return result
        except Exception as e:
            logger.error(f"OpenAI sprint call failed: {e}")
            raise
