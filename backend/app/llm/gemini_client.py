"""Gemini API client for LLM calls."""

import json
import os
import re

from constants.llm_models import DEFAULT_GEMINI_MODEL
from google import genai
from google.genai import types
from helpers.logger import logger
from pydantic import BaseModel


class GeminiClient:
    """Gemini API client with the same interface as OpenAIClient."""

    def __init__(self, model_name: str = DEFAULT_GEMINI_MODEL):
        self.model_name = model_name
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        self.client = genai.Client(api_key=api_key)

    def get_response(self, messages: list, response_schema=None, generation_config=None):
        """
        Get response from Gemini.

        Args:
            messages: List of message dicts with 'role' and 'content'.
            response_schema: Optional schema for structured output.
                - type[BaseModel]: returns a validated Pydantic instance.
                - dict: returns a JSON string (legacy behavior).
                - None: returns raw text.

        Returns:
            Pydantic model instance when response_schema is a BaseModel subclass,
            otherwise a string.
        """
        use_pydantic = isinstance(response_schema, type) and issubclass(response_schema, BaseModel)
        generation_config = generation_config or {}
        temperature = generation_config.get("temperature", 1.0)
        max_output_tokens = generation_config.get(
            "max_output_tokens",
            generation_config.get("max_tokens", 8000),
        )
        thinking_budget = generation_config.get("thinking_budget", 0)

        try:
            contents = self._convert_messages_to_contents(messages)

            config_params = {
                'temperature': temperature,
                'max_output_tokens': max_output_tokens,
            }

            if thinking_budget is not None:
                config_params['thinking_config'] = types.ThinkingConfig(thinking_budget=thinking_budget)

            if response_schema:
                config_params['response_mime_type'] = 'application/json'
                config_params['response_schema'] = response_schema

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=types.GenerateContentConfig(**config_params),
            )

            if use_pydantic:
                # Try SDK-level parsed result first
                parsed = getattr(response, 'parsed', None)
                if parsed is not None:
                    return parsed
                # Fallback: validate from raw text
                return response_schema.model_validate_json(response.text)

            if response_schema:
                return self._clean_json_response(response.text)
            return response.text

        except Exception as e:
            if use_pydantic:
                raise
            logger.error(f"Gemini API call failed: {str(e)}")
            return f"Error: {str(e)}"

    def _convert_messages_to_contents(self, messages: list) -> list:
        """Convert OpenAI message format to Gemini contents format."""
        role_map = {'system': 'user', 'user': 'user', 'assistant': 'model'}
        contents = []

        for msg in messages:
            role = msg.get('role', '')
            content = msg.get('content', '')
            gemini_role = role_map.get(role)
            if not gemini_role:
                continue

            text = f"System Instructions: {content}" if role == 'system' else content
            contents.append({"role": gemini_role, "parts": [{"text": text}]})

        return contents

    def _clean_json_response(self, response_text: str) -> str:
        """Strip markdown fences and validate JSON. Returns original text on failure."""
        cleaned = re.sub(r'^```(?:json)?\s*', '', response_text.strip(), flags=re.MULTILINE)
        cleaned = re.sub(r'```\s*$', '', cleaned, flags=re.MULTILINE).strip()

        try:
            return json.dumps(json.loads(cleaned))
        except json.JSONDecodeError:
            logger.warning(f"JSON parse failed, returning raw response")
            return response_text
