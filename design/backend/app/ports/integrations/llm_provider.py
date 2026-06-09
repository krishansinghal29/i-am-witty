from __future__ import annotations

from typing import Protocol, TypeVar

from pydantic import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)


class LlmProvider(Protocol):
    """Swappable chat-completion provider for prompt generation and evaluation.

    The concrete adapter (litellm today) hides the vendor SDK and model routing.
    `complete_structured` returns a validated Pydantic instance using the
    provider's JSON-schema/structured-output support; `complete_text` returns
    raw text. `model` overrides the adapter's default per call so the generator
    and evaluator can use different models.
    """

    async def complete_structured(
        self,
        *,
        messages: list[dict],
        response_model: type[ModelT],
        temperature: float | None = None,
        max_tokens: int | None = None,
        model: str | None = None,
    ) -> ModelT:
        ...

    async def complete_text(
        self,
        *,
        messages: list[dict],
        temperature: float | None = None,
        max_tokens: int | None = None,
        model: str | None = None,
    ) -> str:
        ...
