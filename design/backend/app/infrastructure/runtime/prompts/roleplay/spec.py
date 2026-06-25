"""Typed spec + context for roleplay task types."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

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
    landed_count: int           # successes landed so far (in graded phases)
    target_count: int           # goal (e.g. 5)
    conversation: list[dict]    # each: {"role": "she_narration"|"she"|"you", "content": str}, chronological
    # The phase this turn belongs to (e.g. "ask"/"tease" for question_answer_tease,
    # "misread" for misinterpretation). Single-phase roleplays can ignore it.
    phase: str = ""
    # A composed seed line produced by spec.seed_factory (e.g. the weighted scene
    # seed for first_unusual_thing). Empty for specs that use the flat verbs spark
    # instead. Builders should treat it as loose inspiration, never a constraint.
    seed: str = ""


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
    # The user's turns cycle through these phases by parity, starting with phases[0].
    # Single-phase roleplays (e.g. misinterpretation) leave this as one entry and
    # the engine emits no move hint. Multi-phase roleplays (e.g. question_answer_tease
    # = ("ask", "tease")) drive the UI's "what to do next" hint via next_user_move.
    phases: tuple[str, ...] = ("turn",)
    # Which phases count toward target_count (and get graded/coached). A landing in
    # an ungraded phase is ignored by the engine even if the model returns landed=True.
    graded_phases: frozenset[str] = field(default_factory=lambda: frozenset({"turn"}))
    # word_lists.word_list names the engine samples this roleplay's per-turn spark
    # words from (passed in via RoleplayContext.verbs). Defaults to verbs; specs
    # whose material wants a different source override it (e.g. shit_test uses
    # ("adjectives_common",), mirroring its non-roleplay generator).
    spark_lists: tuple[str, ...] = ("verbs",)
    # How many spark words to sample for the whole attempt (the cursor walks them
    # one per turn). Defaults to 10; specs that only need sparks at the opening can
    # request fewer (e.g. vibing uses 2 — a verb+adjective pair for the first story).
    spark_count: int = 10
    # Optional richer seed source: a zero-arg factory returning a composed seed line
    # (e.g. generator_strategies.scene_seed_generator_prompt(...), which rolls a
    # weighted seed TYPE — object/setting/overheard/vibe/appearance/… — not a flat
    # word). When set, the engine calls it fresh each opening/turn into ctx.seed and
    # skips the flat verbs spark. None ⇒ use the flat spark_lists/verbs path.
    seed_factory: Callable[[], str] | None = None
