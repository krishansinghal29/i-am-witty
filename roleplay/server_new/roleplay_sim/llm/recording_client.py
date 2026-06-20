"""RecordingLLMClient: a per-session LLMClient decorator that captures every
call (messages, response, model, latency) for the verbose conversation log. [Layer C]

This is the *only* place raw prompts/responses are captured, and the only thing
that reads `roleplay_sim.llm.tracing`. Deleting this module (and the `full` view)
removes Layer C entirely with no effect on the transcript/detailed logs.

Each session owns its own `LLMCallBuffer`, so wrapping the API's shared client
never causes cross-session bleed: the wrapper is built fresh per session.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Sequence

from roleplay_sim.domain.interfaces import LLMClient, Message
from roleplay_sim.llm.tracing import current_stage


@dataclass
class LLMCall:
    """One captured LLM round-trip, tagged with the pipeline stage that made it."""
    stage: str                       # classify | author | act | unknown
    kind: str                        # complete | structured | stream
    model: str | None
    messages: list[Message]
    response: str
    latency_ms: float
    temperature: float | None = None
    max_tokens: int | None = None


@dataclass
class LLMCallBuffer:
    """Per-session sink. The recorder drains it once per turn."""
    calls: list[LLMCall] = field(default_factory=list)

    def add(self, call: LLMCall) -> None:
        self.calls.append(call)

    def drain(self) -> list[LLMCall]:
        out = self.calls
        self.calls = []
        return out


class RecordingLLMClient:
    """Wraps a real LLMClient; records each call into `buffer` then delegates.

    Implements the full LLMClient protocol (complete / complete_structured /
    stream) plus the model_for_* role helpers via passthrough.
    """

    def __init__(self, inner: LLMClient, buffer: LLMCallBuffer) -> None:
        self._inner = inner
        self._buffer = buffer

    async def complete(self, messages: Sequence[Message], *, model: str | None = None,
                       temperature: float = 0.7, max_tokens: int = 400) -> str:
        t0 = time.perf_counter()
        resp = await self._inner.complete(
            messages, model=model, temperature=temperature, max_tokens=max_tokens
        )
        self._buffer.add(LLMCall(
            stage=current_stage(), kind="complete", model=model,
            messages=list(messages), response=resp,
            latency_ms=(time.perf_counter() - t0) * 1000.0,
            temperature=temperature, max_tokens=max_tokens,
        ))
        return resp

    async def complete_structured(self, messages: Sequence[Message], *, schema: Any,
                                  model: str | None = None, temperature: float = 0.2,
                                  max_tokens: int = 800) -> Any:
        t0 = time.perf_counter()
        out = await self._inner.complete_structured(
            messages, schema=schema, model=model,
            temperature=temperature, max_tokens=max_tokens,
        )
        # Render the validated model back to JSON for a faithful, readable record.
        try:
            rendered = out.model_dump_json(indent=2)  # type: ignore[attr-defined]
        except Exception:
            rendered = repr(out)
        self._buffer.add(LLMCall(
            stage=current_stage(), kind="structured", model=model,
            messages=list(messages), response=rendered,
            latency_ms=(time.perf_counter() - t0) * 1000.0,
            temperature=temperature, max_tokens=max_tokens,
        ))
        return out

    async def stream(self, messages: Sequence[Message], *, model: str | None = None,
                     temperature: float = 0.9, max_tokens: int = 300) -> AsyncIterator[str]:
        t0 = time.perf_counter()
        stage = current_stage()
        chunks: list[str] = []
        async for tok in self._inner.stream(
            messages, model=model, temperature=temperature, max_tokens=max_tokens
        ):
            chunks.append(tok)
            yield tok
        self._buffer.add(LLMCall(
            stage=stage, kind="stream", model=model,
            messages=list(messages), response="".join(chunks),
            latency_ms=(time.perf_counter() - t0) * 1000.0,
            temperature=temperature, max_tokens=max_tokens,
        ))

    # role-model passthroughs (components call these to pick a per-role model)
    def model_for_classify(self) -> str | None:
        return getattr(self._inner, "model_for_classify", lambda: None)()

    def model_for_author(self) -> str | None:
        return getattr(self._inner, "model_for_author", lambda: None)()

    def model_for_act(self) -> str | None:
        return getattr(self._inner, "model_for_act", lambda: None)()
