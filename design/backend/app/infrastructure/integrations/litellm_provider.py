from __future__ import annotations

import os
from typing import TYPE_CHECKING, TypeVar

from pydantic import BaseModel

if TYPE_CHECKING:
    from app.settings import Settings

ModelT = TypeVar("ModelT", bound=BaseModel)

_DEFAULT_MAX_TOKENS = 8000


class LiteLlmProvider:
    """litellm-backed `LlmProvider` adapter.

    One adapter routes to any litellm-supported vendor (OpenAI, Gemini,
    Anthropic, …) by model string, so the generator and evaluator can target
    different models without separate clients. The module imports without the
    SDK or credentials present: litellm is imported lazily and provider keys are
    pushed into the environment (where litellm reads them) on first use.
    """

    def __init__(
        self,
        settings: Settings,
        *,
        default_model: str | None = None,
    ) -> None:
        self._settings = settings
        self._default_model = default_model or settings.llm_generator_model
        self._timeout = settings.llm_request_timeout_seconds
        self._num_retries = settings.llm_num_retries
        self._configured = False

    def _ensure_configured(self) -> None:
        """Lazily import litellm and seed provider keys from settings."""
        if self._configured:
            return
        import litellm

        # Unsupported params (e.g. temperature on some models) are dropped
        # rather than raising, so one call shape works across providers.
        litellm.drop_params = True

        if self._settings.openai_api_key and not os.environ.get("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = self._settings.openai_api_key
        if self._settings.gemini_api_key and not os.environ.get("GEMINI_API_KEY"):
            os.environ["GEMINI_API_KEY"] = self._settings.gemini_api_key
        self._configured = True

    async def complete_structured(
        self,
        *,
        messages: list[dict],
        response_model: type[ModelT],
        temperature: float | None = None,
        max_tokens: int | None = None,
        model: str | None = None,
    ) -> ModelT:
        self._ensure_configured()
        import litellm

        response = await litellm.acompletion(
            model=model or self._default_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens or _DEFAULT_MAX_TOKENS,
            response_format=response_model,
            timeout=self._timeout,
            num_retries=self._num_retries,
        )
        content = response.choices[0].message.content
        if content is None:
            raise ValueError("LLM returned empty structured content")
        if isinstance(content, (dict, list)):
            return response_model.model_validate(content)
        return response_model.model_validate_json(content)

    async def complete_text(
        self,
        *,
        messages: list[dict],
        temperature: float | None = None,
        max_tokens: int | None = None,
        model: str | None = None,
    ) -> str:
        self._ensure_configured()
        import litellm

        response = await litellm.acompletion(
            model=model or self._default_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens or _DEFAULT_MAX_TOKENS,
            timeout=self._timeout,
            num_retries=self._num_retries,
        )
        return response.choices[0].message.content or ""
