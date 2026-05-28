"""OpenAI API client for LLM calls."""

import json

from openai import OpenAI
from helpers.logger import logger
from pydantic import BaseModel


class OpenAIClient:
    """OpenAI API client with the same interface as GeminiClient."""

    def __init__(self, model_name: str = "gpt-5.3-chat-latest"):
        self.model_name = model_name
        self.client = OpenAI()

    def get_response(self, messages: list, response_schema=None, generation_config=None):
        """
        Get response from OpenAI.

        Args:
            messages: List of message dicts with 'role' and 'content'.
            response_schema: Optional schema for structured output.
                - type[BaseModel]: uses .parse() and returns a Pydantic instance.
                - dict: injects schema into prompt, returns JSON string (legacy).
                - None: returns raw text.

        Returns:
            Pydantic model instance when response_schema is a BaseModel subclass,
            otherwise a string.
        """
        use_pydantic = isinstance(response_schema, type) and issubclass(response_schema, BaseModel)
        generation_config = generation_config or {}
        temperature = generation_config.get("temperature", 1.0)
        max_tokens = generation_config.get(
            "max_tokens",
            generation_config.get("max_output_tokens", 8000),
        )

        try:
            if use_pydantic:
                response = self.client.beta.chat.completions.parse(
                    model=self.model_name,
                    messages=messages,
                    temperature=temperature,
                    max_completion_tokens=max_tokens,
                    response_format=response_schema,
                )
                parsed = response.choices[0].message.parsed
                if parsed is None:
                    raise ValueError("OpenAI returned null parsed result")
                return parsed

            params = {
                'model': self.model_name,
                'messages': messages,
                'temperature': temperature,
                'max_completion_tokens': max_tokens,
            }

            if response_schema:
                schema_str = json.dumps(response_schema, indent=2)
                json_instruction = (
                    f"\n\nRespond with valid JSON matching this schema:\n"
                    f"{schema_str}\n\n"
                    f"Do not include any text outside the JSON response."
                )
                # Append schema instruction to the last user message
                messages = [m.copy() for m in messages]
                for msg in reversed(messages):
                    if msg.get('role') == 'user':
                        msg['content'] += json_instruction
                        break
                params['messages'] = messages
                params['response_format'] = {"type": "json_object"}

            response = self.client.chat.completions.create(**params)
            return response.choices[0].message.content

        except Exception as e:
            if use_pydantic:
                raise
            logger.error(f"OpenAI API call failed: {str(e)}")
            return f"Error: {str(e)}"
