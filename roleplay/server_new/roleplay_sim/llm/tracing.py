"""Lightweight LLM-stage tracing. [logging support]

A single contextvar names the pipeline stage currently issuing an LLM call
("classify" | "author" | "act"). The LLM-backed components set it around their
own call so a recording client can attribute a captured call to its stage —
without those components depending on the (optional, deletable) recording layer.

This module is always present and dependency-free: when no recording client is
installed, `llm_stage` is a cheap no-op contextvar set/reset.
"""
from __future__ import annotations

import contextvars
from contextlib import contextmanager
from typing import Iterator

_active_stage: contextvars.ContextVar[str] = contextvars.ContextVar(
    "llm_stage", default="unknown"
)


def current_stage() -> str:
    """The stage of the LLM call in flight, or 'unknown' outside any stage."""
    return _active_stage.get()


@contextmanager
def llm_stage(name: str) -> Iterator[None]:
    """Tag every LLM call made inside this block as belonging to `name`."""
    token = _active_stage.set(name)
    try:
        yield
    finally:
        _active_stage.reset(token)
