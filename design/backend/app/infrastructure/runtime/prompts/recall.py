"""Prompts and structured-output schemas for recall admin drafting.

The admin pastes or dictates a rough note; these prompts turn it into one deck
item, write concept scenarios, or label how a line answers its cue. Every field
in the schemas is required-but-nullable so strict structured output can always
be satisfied; the application layer validates the result against the database.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Literal

from pydantic import BaseModel, Field

# House-style hint labels, shown to the model as examples (not a closed list).
HINT_EXAMPLES = (
    "agree & amplify",
    "flip it",
    "misinterpret",
    "challenge",
    "tease",
    "deflect",
    "role play",
    "ambition",
    "standards",
    "adventure",
    "sound",
    "command",
)


class RecallDraftOutput(BaseModel):
    kind: Literal["line", "concept", "routine", "focus"] = Field(
        ..., description="Which kind of item the note describes."
    )
    cue_ref: str | None = Field(
        ...,
        description=(
            "Line only: the ref (e.g. 'c3') of the existing cue this line answers, "
            "or null when no existing cue is the same situation."
        ),
    )
    cue_text: str | None = Field(
        ...,
        description=(
            "Line only: the cue text. Copy the existing cue's text when cue_ref is "
            "set; otherwise write the new cue. Null for other kinds."
        ),
    )
    cue_type: Literal["reaction", "goal"] | None = Field(
        ..., description="Line only: 'reaction' or 'goal'. Null for other kinds."
    )
    hint: str | None = Field(
        ...,
        description=(
            "Line only: short lowercase technique label for how this line answers "
            "the cue. Must differ from the hints already on that cue."
        ),
    )
    sibling_hint: str | None = Field(
        ...,
        description=(
            "Line only: when the matched cue has exactly one existing line and it "
            "has no hint, a label for that existing line (different from hint). "
            "Otherwise null."
        ),
    )
    title: str | None = Field(
        ..., description="Concept name, routine name, or focus title. Null for lines."
    )
    body: str | None = Field(
        ...,
        description=(
            "Line: the line itself. Concept: one-sentence definition. Focus: one "
            "sentence on why it matters, or null. Routine: null."
        ),
    )
    delivery_note: str | None = Field(
        ...,
        description=(
            "Line only: how to say it, as a brief imperative (max 12 words), only "
            "if the note implies one. Otherwise null."
        ),
    )
    question: str | None = Field(
        ..., description="Focus only: a yes/no check-in question. Null otherwise."
    )
    steps: list[str] | None = Field(
        ..., description="Routine only: ordered steps, each a short phrase."
    )
    scenarios: list[str] | None = Field(
        ...,
        description=(
            "Concept only: exactly 3 short scenarios in second person that show "
            "the concept without naming it."
        ),
    )


class RecallScenariosOutput(BaseModel):
    scenarios: list[str] = Field(..., description="The new scenarios, in order.")


class RecallHintOutput(BaseModel):
    hint: str = Field(
        ..., min_length=1, description="Short lowercase technique label (1-3 words)."
    )


DRAFT_SYSTEM = f"""\
You help the owner of a personal recall deck for dating and social skills turn a \
rough note into exactly one practice item. They practise each item out loud from a \
prompt, so the item must stay faithful to the note.

Item kinds:
- line: something to say, including sounds ("Euuu...") and commands ("Come here."). \
Every line answers a cue:
  - reaction cue: something she says, written as her own short sentence ending in \
punctuation, without quote marks. Example: You're such a player.
  - goal cue: something he sets out to do, as a short imperative without a full \
stop. Examples: Call her over, Get her to qualify.
- concept: a named idea or technique. title = its name; body = a one-sentence \
definition; scenarios = exactly 3 short scenarios (1-2 sentences, second person \
"you", a concrete moment with her) that show the concept without naming it.
- routine: a named sequence. title = its name; steps = the ordered steps, each a \
short phrase.
- focus: a life habit to check in on every day. title = a short name; question = a \
yes/no check-in question; body = one sentence on why it matters for his energy or \
his game, or null.

Rules for a line:
- If an existing cue is the same situation, even worded differently, set cue_ref to \
its ref and copy its text exactly. Otherwise cue_ref is null and you write a new cue.
- Keep the owner's wording of the line. Fix only obvious typos, capitalisation and \
punctuation. Never rewrite the joke, add words, or explain it.
- delivery_note only if the note says how to deliver it (tone, gesture, timing), \
rewritten as a brief imperative of at most 12 words. Otherwise null.
- hint: a short lowercase label for the technique the line uses, in the deck's \
style, for example: {", ".join(HINT_EXAMPLES)}. It must differ from every hint \
already on that cue. Give a hint even for a new cue.
- sibling_hint: only when the matched cue has exactly one existing line and that \
line shows "(no hint)": a label for that existing line, different from your hint. \
Otherwise null.

Fields a kind does not use must be null. Do not invent content the note does not \
contain, except the concept definition and scenarios.\
"""


def cue_ref(index: int) -> str:
    return f"c{index + 1}"


def build_draft_prompt(
    note: str,
    cues: Sequence[tuple[str, str, str, Sequence[tuple[str | None, str]]]],
) -> str:
    """User message for drafting. ``cues`` rows are (ref, type, text, lines)."""
    if cues:
        blocks = []
        for ref, type, text, lines in cues:
            rows = [f"[{ref}] {type}: {text}"]
            for hint, body in lines:
                rows.append(f"    - {hint or '(no hint)'}: {body}")
            blocks.append("\n".join(rows))
        existing = "\n".join(blocks)
    else:
        existing = "(none yet)"
    return (
        f"Existing cues and their lines:\n{existing}\n\n"
        f"The owner's note:\n<<<\n{note}\n>>>"
    )


SCENARIOS_SYSTEM = """\
You write practice scenarios for a recall deck about dating and social skills. The \
reader sees one scenario and has to name the concept it shows.

Each scenario:
- is 1-2 sentences, in second person ("you"), describing a concrete moment with her \
(at a bar, a cafe, a party, on the street, over text...);
- shows the concept in action through what you say or do;
- never names the concept or uses its key words;
- is different in setting and move from the existing scenarios and from each other.\
"""


def build_scenarios_prompt(
    title: str, definition: str | None, existing: Sequence[str], count: int
) -> str:
    existing_block = (
        "\n".join(f"- {scenario}" for scenario in existing) if existing else "(none)"
    )
    return (
        f"Concept: {title}\n"
        f"Definition: {definition or '(not given)'}\n"
        f"Existing scenarios:\n{existing_block}\n\n"
        f"Write {count} new scenario{'s' if count != 1 else ''}."
    )


HINT_SYSTEM = f"""\
You label lines in a recall deck about dating and social skills. Given a line and \
the cue it answers, reply with a short lowercase label (1-3 words) for the technique \
the line uses, in the deck's style, for example: {", ".join(HINT_EXAMPLES)}. The \
label must not be any of the labels the user says are taken.\
"""


def build_hint_prompt(line: str, cue_text: str | None, avoid: Sequence[str]) -> str:
    taken = ", ".join(avoid) if avoid else "(none)"
    return (
        f"Cue: {cue_text or '(not given)'}\n"
        f"Line: {line}\n"
        f"Taken labels: {taken}"
    )
