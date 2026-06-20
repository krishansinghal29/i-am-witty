"""LLMClient: vendor-agnostic wrapper over litellm. [P6]

Three roles share one client: complete (free text), complete_structured (JSON),
and stream (token iterator for the Actor / TTS). litellm is imported lazily so
the package and the deterministic tests run with no SDK and no API keys.
Replaces the old server's inline-litellm route calls.
"""
from __future__ import annotations

import json
import re
from typing import Any, AsyncIterator, Sequence, TypeVar

from pydantic import BaseModel

from roleplay_sim.llm.providers import ChatProvider, load_chat_provider

Message = dict[str, str]
T = TypeVar("T", bound=BaseModel)

_JSON_SPAN = re.compile(r"\{.*\}", re.DOTALL)


def _loads_json(text: str) -> Any:
    """Parse a JSON object from a model response.

    Structured-output responses are pure JSON; this also tolerates a provider
    wrapping it in prose/fences by extracting the first object span. Raises if
    nothing parseable is found — a schema-conforming response is required.
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = _JSON_SPAN.search(text or "")
        if m:
            return json.loads(m.group(0))
        raise


class LiteLLMClient:
    def __init__(self, provider: ChatProvider | None = None) -> None:
        self.provider = provider or load_chat_provider()

    # -- internals ---------------------------------------------------------
    def _litellm(self):
        import litellm  # lazy
        litellm.drop_params = True
        return litellm

    def _kwargs(self, model: str | None, **extra: Any) -> dict[str, Any]:
        p = self.provider
        kw: dict[str, Any] = {"model": model or p.model}
        if p.api_base:
            kw["api_base"] = p.api_base
        if p.api_key:
            kw["api_key"] = p.api_key
        kw.update(p.extra)
        kw.update(extra)
        return kw

    def _role_model(self, override: str, fallback: str | None) -> str | None:
        return override or fallback or None

    # -- API ---------------------------------------------------------------
    async def complete(self, messages: Sequence[Message], *, model: str | None = None,
                       temperature: float = 0.7, max_tokens: int = 400) -> str:
        litellm = self._litellm()
        resp = await litellm.acompletion(
            **self._kwargs(model, messages=list(messages),
                           temperature=temperature, max_tokens=max_tokens)
        )
        return (resp.choices[0].message.content or "").strip()

    async def complete_structured(self, messages: Sequence[Message], *, schema: type[T],
                                  model: str | None = None, temperature: float = 0.2,
                                  max_tokens: int = 800) -> T:
        litellm = self._litellm()
        kw = self._kwargs(model, messages=list(messages), temperature=temperature,
                          max_tokens=max_tokens, response_format=schema)
        resp = await litellm.acompletion(**kw)
        return schema.model_validate(_loads_json(resp.choices[0].message.content or ""))

    async def stream(self, messages: Sequence[Message], *, model: str | None = None,
                     temperature: float = 0.9, max_tokens: int = 300) -> AsyncIterator[str]:
        litellm = self._litellm()
        chunks = await litellm.acompletion(
            **self._kwargs(model, messages=list(messages), temperature=temperature,
                           max_tokens=max_tokens, stream=True)
        )
        async for chunk in chunks:
            delta = chunk.choices[0].delta
            text = getattr(delta, "content", None) or ""
            if text:
                yield text

    # role-model helpers (used by components)
    def model_for_classify(self) -> str | None:
        return self._role_model(self.provider.classify_model, self.provider.model)

    def model_for_author(self) -> str | None:
        return self._role_model(self.provider.author_model, self.provider.model)

    def model_for_act(self) -> str | None:
        return self._role_model(self.provider.act_model, self.provider.model)
