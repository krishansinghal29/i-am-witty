"""Structured-output schemas for the roleplay task type."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class RolePlayOpening(BaseModel):
    """Her opening move: the scene title, the silent scene-setting, and her first
    spoken line. Returned by the opening LLM call before the user has said anything."""

    brief_heading: str = Field(
        ...,
        min_length=1,
        description=(
            "A short scene title that frames the moment, e.g. 'At the rooftop "
            "party'. A few words; no punctuation theatrics."
        ),
    )
    narration: str = Field(
        ...,
        min_length=1,
        description=(
            "Sets the scene in ONE plain sentence — one concrete visual detail "
            "about her plus where she is, in everyday words (not a head-to-toe "
            "description). This is scene description — things she is NOT saying "
            "aloud. Never spoken dialogue. ~12 words, never over 18; a single "
            "beat, no semicolons or stacked fragments."
        ),
    )
    dialogue: str = Field(
        ...,
        min_length=1,
        description=(
            "Her opening spoken line — the only thing she actually says out loud. "
            "MUST contain the word 'I', 'you', or 'we', sound completely ordinary "
            "and everyday, and be ripe for misinterpretation. One plain line in "
            "everyday words, ~10 words (never over 15), a single sentence with no "
            "line breaks."
        ),
    )


class RolePlayTurn(BaseModel):
    """One of her turns mid-conversation: an evaluation of the user's last line
    woven into her in-character reaction and next spoken line."""

    landed: bool = Field(
        ...,
        description=(
            "Did the user's most recent line achieve a genuine misinterpretation "
            "(deliberately misreading an everyday line and committing to the "
            "alternate meaning)? True for any genuine misread, even a subtle one; "
            "false only when there was no misread at all."
        ),
    )
    intensity: Literal["strong", "subtle", "off"] = Field(
        ...,
        description=(
            "Quality of the misread: 'strong' = a clear, committed, clever "
            "misinterpretation; 'subtle' = a small but genuine misread that still "
            "counts; 'off' = no misread at all (a plain/normal reply). Use 'off' "
            "only when 'landed' is false."
        ),
    )
    narration: str = Field(
        ...,
        min_length=1,
        description=(
            "Her reaction and the scene beat — things she does NOT say aloud. "
            "When the user landed it, OPEN with a tiny, natural, in-world coach "
            "affirmation that doubles as feedback (e.g. 'she catches the misread "
            "and laughs, leaning in'). When it's off, give a gentle, subtle "
            "in-world cue (a slight cooling, she doesn't quite follow) — never an "
            "explicit scolding. Never spoken dialogue. ONE plain, complete "
            "sentence in everyday words (~12 words, never over 18); a single "
            "beat, no semicolons or stacked fragments, don't re-describe her looks."
        ),
    )
    dialogue: str = Field(
        ...,
        min_length=1,
        description=(
            "Her next spoken line — the only thing she actually says out loud. "
            "MUST contain the word 'I', 'you', or 'we', sound completely ordinary "
            "and everyday, and be ripe for misinterpretation. One plain line in "
            "everyday words, ~10 words (never over 15), a single sentence with no "
            "line breaks."
        ),
    )
    sample_answer: str = Field(
        ...,
        min_length=1,
        description=(
            "A model misinterpretation of YOUR PREVIOUS spoken line — the exact "
            "line the user just responded to (NOT your new dialogue). One short, "
            "fully committed example a sharp person could have said, following the "
            "misinterpretation techniques and failing the litmus test. HARD LIMIT: "
            "20 words. Shown to the user as coaching AFTER their attempt; never spoken."
        ),
    )
    is_complete: bool = Field(
        ...,
        description=(
            "True only once the number of misinterpretations landed (including "
            "this turn) reaches the target count — i.e. the roleplay goal has "
            "been reached. Otherwise false."
        ),
    )
