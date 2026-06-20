"""Pydantic request schemas for the API. [P10]"""
from __future__ import annotations

from pydantic import BaseModel, Field


class ChatStreamIn(BaseModel):
    session_id: str
    message: str | None = None


class TtsIn(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


class NewSessionIn(BaseModel):
    persona: str = "princess"
    goal: str = "number"
