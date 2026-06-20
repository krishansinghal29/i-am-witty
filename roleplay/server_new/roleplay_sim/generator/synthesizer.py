"""LLM expansion of a roll into the text the engine consumes.

Two firewalled calls:

- `synthesize_persona` sees the WHOLE roll (incl. latent backstory) and writes the
  character bible, speaking style, attracts/repels, mood, and band-keyed few-shot
  lines — all consistent with the rolled behavioral disposition.
- `synthesize_first_impression` sees ONLY the observable subset (+ scene), so it
  physically cannot leak her name/age/job/home into the opening snapshot.

Message-builders are pure (`*_messages`) so tests can assert the firewall without
an LLM. The few-shot the synthesizer writes uses the same combined format the
Actor must emit: spoken words in double quotes, a short third-person beat outside.
"""
from __future__ import annotations

from pydantic import BaseModel, Field

from roleplay_sim.domain.interfaces import LLMClient
from roleplay_sim.generator.rolls import Observable, RolledPersona, SceneRoll

# The five few-shot bands the Actor selects by beat (see actor/bible.py BAND).
FEWSHOT_BANDS = ["cold", "neutral", "testing", "qualifying", "warm"]

_FORMAT_NOTE = (
    "FORMAT for every line: put her spoken words in double quotes and write any "
    "action/expression as a short plain phrase outside the quotes, third person — "
    "e.g.  She barely glances up from her drink. \"Do I know you?\"  — no asterisks, "
    "no markdown, no stage directions in brackets."
)


# ---------------------------------------------------------------------------
# Persona
# ---------------------------------------------------------------------------
class FewShotOut(BaseModel):
    """Closed (fixed-key) few-shot bands. An open dict[str, list[str]] is rejected
    by OpenAI strict structured-output mode, so each band is its own field."""
    cold: list[str] = Field(default_factory=list)
    neutral: list[str] = Field(default_factory=list)
    testing: list[str] = Field(default_factory=list)
    qualifying: list[str] = Field(default_factory=list)
    warm: list[str] = Field(default_factory=list)


class PersonaSynth(BaseModel):
    bible: str
    speaking_style: str
    attracts: list[str] = Field(default_factory=list)
    repels: list[str] = Field(default_factory=list)
    mood_tonight: str = ""
    fewshot: FewShotOut = Field(default_factory=FewShotOut)

    def fewshot_dict(self) -> dict[str, list[str]]:
        """Band -> example lines (empties dropped) for PersonaConfig.fewshot."""
        raw = self.fewshot.model_dump()
        return {b: [ln for ln in raw.get(b, []) if ln.strip()] for b in FEWSHOT_BANDS}


_PERSONA_SYSTEM = (
    "You are a casting director. Given one woman's facts, her behavioral disposition, "
    "and a few seed words, write a tight character brief an actress can perform from. "
    "Make her one specific, believable person — never a stereotype. Output JSON with: "
    "bible (second person, 'You are <name>...', 6-10 sentences: who she is, what gets "
    "her attention, what kills it, how she tests, how she speaks — consistent with the "
    "disposition given, no numbers); speaking_style (one phrase); attracts (3-5 short "
    "items); repels (3-5 short items); mood_tonight (one phrase, fits the scene); "
    "fewshot (an object keyed EXACTLY by " + ", ".join(FEWSHOT_BANDS) + ", each a list "
    "of 3-4 example lines showing how she'd sound at that warmth level). "
    "The seed words are loose inspiration for her IMAGERY and word-choice only — weave "
    "in at most one or two where natural, never force them, never let them change her "
    "register. " + _FORMAT_NOTE
)


def persona_messages(rolled: RolledPersona, scene: SceneRoll) -> list[dict[str, str]]:
    lat = rolled.latent
    obs = rolled.observable
    user = (
        f"NAME: {lat.name}\n"
        f"AGE: {lat.age}\n"
        f"OCCUPATION: {lat.occupation}\n"
        f"FROM: {lat.hometown}\n"
        f"INTO: {', '.join(lat.hobbies)}\n"
        f"LOOK: {obs.style}; {obs.body_shape}; {obs.age_hint}"
        + (f"; {obs.distinctive_feature}" if obs.distinctive_feature else "") + "\n"
        f"DISPOSITION: {rolled.axes.disposition()}\n"
        f"SCENE TONIGHT: {scene.approach_context} at {scene.venue}, {scene.time_of_day}"
        + (f", with {scene.present_company}" if scene.present_company else "") + "\n"
        f"SEED WORDS (loose imagery inspiration): {', '.join(rolled.voice_palette)}\n"
    )
    return [
        {"role": "system", "content": _PERSONA_SYSTEM},
        {"role": "user", "content": user},
    ]


async def synthesize_persona(client: LLMClient, rolled: RolledPersona,
                             scene: SceneRoll) -> PersonaSynth:
    model = getattr(client, "model_for_author", lambda: None)()
    return await client.complete_structured(
        persona_messages(rolled, scene), schema=PersonaSynth, model=model,
        temperature=0.9, max_tokens=1100,
    )


# ---------------------------------------------------------------------------
# First impression (firewalled — observable only)
# ---------------------------------------------------------------------------
class FirstImpressionOut(BaseModel):
    text: str


_FIRST_IMPRESSION_SYSTEM = (
    "You write a short, vivid FIRST IMPRESSION of a woman a man has just noticed in "
    "a public place — the snapshot he takes in at a glance, before either speaks.\n"
    "- 2 to 3 sentences. Plain, everyday words — never a fashion-magazine voice.\n"
    "- Describe ONLY what is visibly observable right now: the place, her outfit, her "
    "build, her hair, what she's doing.\n"
    "- Do NOT invent or state her name, age, job, hometown, or personality — only what "
    "the eye can see.\n"
    "- Second person, addressed to him ('You spot...', 'She's...').\n"
    "- Make her feel like one specific, real person. Output JSON: {\"text\": \"...\"}."
)


def first_impression_messages(observable: Observable, scene: SceneRoll) -> list[dict[str, str]]:
    """Observable-only — NO latent fields are ever placed in this prompt."""
    lines = [
        f"Place: {scene.venue}, {scene.time_of_day}.",
        f"Overall style: {observable.style}.",
        f"Main outfit: {observable.outfit}.",
        f"Build: {observable.body_shape}.",
        f"Apparent age: {observable.age_hint}.",
    ]
    if scene.present_company:
        lines.append(f"She's there with {scene.present_company}.")
    if observable.toggles:
        lines.append(
            "Work in these details — invent something specific and natural for each: "
            + "; ".join(observable.toggles) + "."
        )
    if observable.distinctive_feature:
        lines.append(f"One distinctive feature: {observable.distinctive_feature}.")
    lines.append(
        f'Spark word: "{observable.spark_word}" — loose inspiration only; ignore it if '
        "it doesn't fit naturally."
    )
    return [
        {"role": "system", "content": _FIRST_IMPRESSION_SYSTEM},
        {"role": "user", "content": "\n".join(lines)},
    ]


def fallback_first_impression(observable: Observable, scene: SceneRoll) -> str:
    """Deterministic snapshot if the synthesizer call is unavailable (offline path)."""
    bits = [
        f"You spot her at {scene.venue}.",
        f"She's {observable.body_shape}, wearing {observable.outfit}, and {observable.age_hint}.",
    ]
    if observable.distinctive_feature:
        bits.append(f"You notice {observable.distinctive_feature}.")
    return " ".join(bits)


async def synthesize_first_impression(client: LLMClient, observable: Observable,
                                      scene: SceneRoll) -> str:
    model = getattr(client, "model_for_author", lambda: None)()
    out = await client.complete_structured(
        first_impression_messages(observable, scene), schema=FirstImpressionOut,
        model=model, temperature=0.9, max_tokens=200,
    )
    return out.text.strip() or fallback_first_impression(observable, scene)
