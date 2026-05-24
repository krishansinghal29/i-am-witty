import json
from typing import List

from pydantic import BaseModel

from llm.factory import create_llm_client


class MockLLMClient:
    """Mock LLM client for testing when API is not available."""

    def get_response(self, messages: list, response_schema=None, generation_config=None):
        if isinstance(response_schema, type) and issubclass(response_schema, BaseModel):
            # Build a minimal valid instance from the schema's defaults/types
            return response_schema.model_validate_json('{"message": "Mock response for testing"}')
        return '{"message": "Mock response for testing"}'


class BaseAgent:
    def __init__(
        self,
        system_message: str,
        few_shot_examples: list[dict] = None,
        model_name: str = None,
        agent_type: str = None,
    ) -> None:
        self.system_message = {
            "role": "system",
            "content": system_message,
        }
        self.few_shot_examples = few_shot_examples if few_shot_examples is not None else []

        try:
            self.llm = create_llm_client(model_name)
        except Exception as e:
            print(f"Warning: LLM initialization failed: {e}")
            self.llm = MockLLMClient()

    def build_messages(self, message: any) -> List[dict]:
        llm_messages: List[dict] = []
        llm_messages.append(self.system_message)
        llm_messages.extend(self.few_shot_examples)

        if isinstance(message, str):
            message = {
                "role": "user",
                "content": message,
            }
        llm_messages.append(message)

        return llm_messages

    # Backward-compatible alias
    generate_llm_history = build_messages
