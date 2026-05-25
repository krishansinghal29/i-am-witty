from typing import Optional

from llm.gemini_client import GeminiClient
from llm.openai_client import OpenAIClient

DEFAULT_MODEL = "gpt-4.1-mini"


def infer_provider(model_name: str) -> str:
    """Infer the LLM provider from the model name."""
    if model_name and model_name.startswith("gemini"):
        return "gemini"
    return "openai"


def create_llm_client(model_name: Optional[str] = None):
    """
    Create LLM client based on model name.

    Args:
        model_name: Model name (e.g. 'gpt-4.1-mini', 'gpt-4.1'). Defaults to gpt-4.1-mini.

    Returns:
        LLM client instance (GeminiClient or OpenAIClient).
    """
    model_name = model_name or DEFAULT_MODEL

    if infer_provider(model_name) == "gemini":
        return GeminiClient(model_name=model_name)
    else:
        return OpenAIClient(model_name=model_name)
