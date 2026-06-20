"""Env -> typed ChatProvider resolution (adapted from the old server). [P6]

The `.env` selects the provider; litellm is the multi-vendor adapter. Per-role
model overrides let the classifier/author run cheap+cold and the actor run warm.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any


def _env(name: str, default: str = "") -> str:
    val = (os.environ.get(name) or "").strip()
    return default if (not val or val.startswith("#")) else val


@dataclass(frozen=True)
class ChatProvider:
    name: str                       # openai | sarvam
    model: str                      # litellm model string
    api_base: str | None = None
    api_key: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)
    # per-role overrides (fall back to `model` when empty)
    classify_model: str = ""
    author_model: str = ""
    act_model: str = ""


def load_chat_provider() -> ChatProvider:
    name = _env("ROLEPLAY_CHAT", "openai").lower()
    if name == "sarvam":
        model = _env("ROLEPLAY_SARVAM_CHAT_MODEL", "sarvam-30b")
        if "/" not in model:
            model = f"openai/{model}"
        return ChatProvider(
            name="sarvam",
            model=model,
            api_base=_env("ROLEPLAY_SARVAM_API_BASE", "https://api.sarvam.ai/v1"),
            api_key=os.environ.get("SARVAM_API_KEY"),
            extra={"extra_body": {"reasoning_effort": None}},
            act_model=_env("ROLEPLAY_ACT_MODEL"),
            classify_model=_env("ROLEPLAY_CLASSIFY_MODEL"),
            author_model=_env("ROLEPLAY_AUTHOR_MODEL"),
        )
    return ChatProvider(
        name="openai",
        model=_env("ROLEPLAY_OPENAI_CHAT_MODEL", "gpt-5.3-chat-latest"),
        api_base=None,
        api_key=None,  # litellm reads OPENAI_API_KEY from env
        classify_model=_env("ROLEPLAY_CLASSIFY_MODEL"),
        author_model=_env("ROLEPLAY_AUTHOR_MODEL"),
        act_model=_env("ROLEPLAY_ACT_MODEL"),
    )
