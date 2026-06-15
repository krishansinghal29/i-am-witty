"""Typed spec + context for roleplay task types."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from pydantic import BaseModel


@dataclass(frozen=True)
class RoleplayContext:
    """Everything the builders need to render one roleplay LLM call.

    The engine owns all sampling and state; the builders are pure functions of
    this context (string in, string out — no I/O, no randomness, no LLM calls).
    """

    persona: str
    appearance: str
    verbs: list[str]            # 10 random spark verbs
    verb_cursor: int            # index of the verb to lean on this turn
    landed_count: int           # misinterpretations landed so far
    target_count: int           # goal (e.g. 5)
    conversation: list[dict]    # each: {"role": "she_narration"|"she"|"you", "content": str}, chronological


@dataclass(frozen=True)
class RoleplaySpec:
    """Everything the engine needs to drive one roleplay."""

    key: str
    target_count: int
    safety_max_turns: int
    opening_schema: type[BaseModel]
    turn_schema: type[BaseModel]
    build_system: Callable[[RoleplayContext], str]       # the combined system prompt
    build_opening_user: Callable[[RoleplayContext], str] # user message for the opening LLM call
    build_turn_user: Callable[[RoleplayContext], str]    # user message for each turn LLM call
