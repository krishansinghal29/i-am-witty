"""Pydantic request schemas for the API. [P10]"""
from __future__ import annotations

from pydantic import BaseModel, Field


class ChatStreamIn(BaseModel):
    session_id: str
    message: str | None = None
    action: str | None = None   # ActionType value (e.g. "sit_down"); optional


class TtsIn(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


class NewSessionIn(BaseModel):
    # Persona + scene are rolled, not chosen. `goal` optionally pins the objective
    # (else it's rolled); `seed` makes a session reproducible.
    goal: str | None = None
    seed: int | None = None
