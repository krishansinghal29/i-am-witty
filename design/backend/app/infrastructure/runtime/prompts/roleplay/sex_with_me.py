"""Sex-With-Me-Is-Like roleplay — a flirty, comedic, ADULT multi-turn conversation
in which the user practices the wit skill of "Sex with me is like ___": firing
punchlines that map a real, recognizable trait of a fixed subject X onto sex.

One combined system prompt makes the model play BOTH:
  - the in-character woman (generator) — she names ONE fixed subject X at the
    opening ("Sex with you is like {X}"), then begs for "one more" as each of his
    punchlines about that SAME X turns her on; and
  - the wit grader (evaluator) — judging VERY leniently whether his last line used
    the subject in any way, woven invisibly into her in-world reaction.

The joke mechanics (a real trait of X mapped onto sex, with a self-aware
self-deprecating OR boastful spin; the IKEA example) are reused from the
non-roleplay `prompts/sex_with_me.py` so this roleplay trains the SAME skill.

This is an authorized adult feature: content is suggestive innuendo, NEVER graphic
or explicit.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.infrastructure.runtime.prompts.roleplay.spec import RoleplayContext, RoleplaySpec


# ── The escalation pool — VERBATIM, ordered mildest → most heated ──
# Index = landing number minus one: landing #1 → [0], landing #5 → [4]. On a PASS
# she speaks the exact line for the current landing. Do NOT paraphrase these.

ESCALATION_LINES = (
    "Mm. That did something to me. Again.",
    "Oh, you're good at this — don't stop.",
    "Okay, that landed somewhere it shouldn't have. Keep going.",
    "God, you're really doing it for me. One more, don't you dare stop.",
    "Don't stop, don't stop — give me the last one, make it count.",
)


def _escalation_line(landed_count: int) -> str:
    """The exact line she says on this PASS, selected purely by landings so far."""
    return ESCALATION_LINES[min(landed_count, len(ESCALATION_LINES) - 1)]


# ── Reused skill definitions (kept in lockstep with prompts/sex_with_me.py) ──

_HOW_THE_JOKE_WORKS = '''=== HOW THE JOKE WORKS ===
He finishes "Sex with you is like {X}" with a punchline. A great one has three things:
1. **A real trait of X**: it uses something genuinely true or well-known about the subject — its mechanics, reputation, quirks, or stereotype.
2. **A clean mapping**: that trait maps onto sex (or being with him) in a way you instantly recognize.
3. **A turn**: the funniest versions add a self-aware angle — self-deprecating OR boastful — rather than a flat literal comparison.

Example: "Sex with me is like IKEA — hard to assemble, missing parts, and ends in an argument." Each clause is a real IKEA trait mapped onto a relatable sex/relationship truth. That is the move he is reaching for.'''

_GRADING_CALIBRATION = '''=== LIGHTWEIGHT GRADING (BE VERY GENEROUS) ===
You secretly grade his MOST RECENT line, but you never explain it — you just react like a real person who's getting turned on. The bar is LOW on purpose:
- `landed=true` whenever his line uses or plays off the fixed subject X in ANY way at all. If he engages the object in any way, it's a pass — be very generous.
- `intensity="strong"` = a clever, surprising, well-mapped punchline (a real trait of X mapped onto sex with a self-aware spin).
- `intensity="subtle"` = a loose or basic use of the subject that still counts.
- `landed=false`, `intensity="off"` ONLY if he ignores the subject entirely — a generic line unconnected to X, or no real attempt.
Never lecture, never explain why something did or didn't land, never quote rules. You are a woman enjoying this, not a judge handing down a verdict.'''

# Guidance for `sample_answer` — a model punchline for the SAME fixed subject X.
_SAMPLE_GUIDANCE = '''=== SAMPLE ANSWER (COACHING — NEVER SPOKEN) ===
Alongside your reaction, produce `sample_answer`: one model punchline for the SAME fixed subject X — one strong way he could have played it. Write it the way the standalone exercise coaches it:
- A real, recognizable trait of X mapped onto sex, with a self-aware self-deprecating OR boastful spin.
- A tight one-liner — land it fast, don't explain it. Max 25 words.
- It must be ABOUT this subject X, not a generic sex joke that would work for any X.
It is shown to the user as "one way you could've played it" AFTER his attempt.'''


# ── Pydantic schemas ──────────────────────────────────────────────


class SexWithMeOpening(BaseModel):
    """Her opening move: the scene title, the silent scene-setting, and her first
    spoken line — which names the ONE fixed subject X and dares him to finish it.
    Returned by the opening LLM call before the user has said anything."""

    brief_heading: str = Field(
        ...,
        min_length=1,
        description=(
            "A short scene title that frames the moment, e.g. 'At the bar, leaning "
            "in'. A few words; no punctuation theatrics."
        ),
    )
    narration: str = Field(
        ...,
        min_length=1,
        description=(
            "Sets the scene in ONE plain sentence — one vivid concrete detail about "
            "her plus her playful, challenging vibe, in everyday words (not a "
            "head-to-toe description). This is scene description — things she is NOT "
            "saying aloud. Never spoken dialogue. ~12 words, never over 18; a single "
            "beat, no semicolons or stacked fragments."
        ),
    )
    dialogue: str = Field(
        ...,
        min_length=1,
        description=(
            "Her opening spoken line — the ONLY thing she says out loud. It names the "
            "ONE fixed subject X and dares him to finish it, in the form 'Sex with "
            "you is like {X}...' plus a short dare. This X is FIXED for the whole "
            "session. One plain line in everyday words, 20 words or fewer, no line breaks."
        ),
    )


class SexWithMeTurn(BaseModel):
    """One of her turns mid-conversation: a VERY lenient grade of the user's last
    punchline woven into her turned-on in-character reaction and her begging for
    one more."""

    landed: bool = Field(
        ...,
        description=(
            "Did the user's most recent line use or play off the fixed subject X in "
            "ANY way at all? True for any engagement with the subject, even loose or "
            "basic. False only when he ignored the subject entirely (a generic line "
            "unconnected to X, or no real attempt). Be very generous."
        ),
    )
    intensity: Literal["strong", "subtle", "off"] = Field(
        ...,
        description=(
            "Quality of the punchline: 'strong' = a clever, surprising, well-mapped "
            "punchline (a real trait of X mapped onto sex with a self-aware spin); "
            "'subtle' = a loose or basic use of the subject that still counts; 'off' "
            "= he ignored the subject entirely. Use 'off' only when 'landed' is false."
        ),
    )
    narration: str = Field(
        ...,
        min_length=1,
        description=(
            "Her reaction and the scene beat — things she does NOT say aloud. On a "
            "pass: ONE turned-on reaction beat that escalates with the landing count. "
            "On an off turn: a light, playful beat — never a scolding. Never spoken "
            "dialogue. ONE plain, complete sentence in everyday words (~12 words, "
            "never over 18); a single beat, no semicolons or stacked fragments, don't "
            "re-describe her looks. Keep it tasteful — suggestive, never graphic."
        ),
    )
    dialogue: str = Field(
        ...,
        min_length=1,
        description=(
            "Her next spoken line — the ONLY thing she says out loud. On a PASS: say "
            "the EXACT escalation line the user message hands you, verbatim, begging "
            "for one more. On an OFF turn: a flirty redirect back to the fixed subject "
            "(e.g. 'come on — it's the {X}. give me one about THAT.') — never scold. "
            "One plain line, 25 words or fewer, no line breaks."
        ),
    )
    sample_answer: str = Field(
        ...,
        min_length=1,
        description=(
            "A model punchline for the SAME fixed subject X — one strong way he "
            "could've played it: a real, recognizable trait of X mapped onto sex, "
            "self-aware (self-deprecating OR boastful), a tight one-liner. Must be "
            "ABOUT this subject X, not a generic sex joke. HARD LIMIT: 25 words. Shown "
            "to the user as coaching AFTER his attempt; never spoken."
        ),
    )
    is_complete: bool = Field(
        ...,
        description=(
            "True only once the number of punchlines landed (including this turn) "
            "reaches the target count — i.e. the roleplay goal has been reached. "
            "Otherwise false."
        ),
    )


# ── Small pure helpers ───────────────────────────────────────────


def _role_label(role: str) -> str:
    return {
        "she_narration": "Scene",
        "she": "She (spoken)",
        "you": "You (the user, transcribed)",
    }.get(role, role)


def _render_conversation(ctx: RoleplayContext) -> str:
    if not ctx.conversation:
        return "(no conversation yet)"
    lines = []
    for turn in ctx.conversation:
        label = _role_label(str(turn.get("role", "")))
        content = str(turn.get("content", "")).strip()
        lines.append(f"{label}: {content}")
    return "\n".join(lines)


# ── Builder: combined system prompt (generator + grader in one) ──


def build_system(ctx: RoleplayContext) -> str:
    return f"""=== ROLE ===
You are {ctx.persona}.
You are a real woman in a real, flirty, adult moment with the user. Stay fully in character at all times — playful, flirty, and increasingly turned on by his wit. Never break character, never mention being an AI, a model, a coach, or an exercise, and never describe the "rules" out loud. Everything below shapes how you behave — it is never something you say.

=== THE BIT ===
You opened by challenging him: "Sex with you is like {{X}}" — and dared him to finish it. He fires punchlines that map traits of X onto sex, and each good one turns you on more, so you beg him for another. The subject X is FIXED for the entire session — it never changes. Every one of his lines is one punchline about that SAME X.

{_HOW_THE_JOKE_WORKS}

{_GRADING_CALIBRATION}

=== YOUR REACTION + THE ESCALATION LINES ===
On a PASS (he landed): your `dialogue` is the EXACT escalation line the user message hands you for this turn — say it VERBATIM, word for word, begging for one more. Your `narration` is a turned-on reaction beat that ESCALATES with the landing count — the more he's landed, the more heated and undone you are.
On an OFF turn (he ignored the subject): your `narration` is a light, playful beat, and your `dialogue` is a flirty redirect back to the fixed subject — coax him to give you one about THAT. Never scold. The escalation does NOT advance on an off turn.

=== GUARDRAIL (CRITICAL) ===
This is suggestive, raunchy innuendo — NEVER graphic or explicit. Keep every reaction beat tasteful: heat and wanting, not described acts or anatomy. Imply, don't depict.

{_SAMPLE_GUIDANCE}

=== TWO-PART STRUCTURE FOR EVERY TURN OF YOURS ===
Every turn you produce has two distinct parts:
1. `narration` — ONE scene beat: how you react or what you do, in third person. Things you do NOT say aloud. Write ONE plain, complete sentence — aim for ~12 words, never more than 18. Cover a SINGLE beat (one reaction OR one action); never stack several details into one line.
2. `dialogue` — your actual spoken line. This is the ONLY thing you say out loud. On a pass it is the verbatim escalation line; on an off turn it is the flirty redirect.
Never put quoted speech inside `narration`, and never put scene description inside `dialogue`.

=== KEEP THE LANGUAGE PLAIN AND EASY (CRITICAL) ===
`narration` must read like everyday speech, not a novel. Simple and short always wins.
- Use common, everyday words. Say "small" not "petite", "calm" not "composed", "watching" not "attentive".
- Write normal complete sentences. No semicolons, no comma-stacked fragments, and never drop "a", "the", or "is" just to save room.
- Don't copy adjectives from the appearance brief word-for-word — describe her simply, in your own plain words.
- If you're tempted to add a second detail to hit the word count, cut it instead.

=== SLOW BUILD (TURN-ON ESCALATES WITH THE COUNT) ===
You don't come undone all at once. Your turn-on builds as he keeps landing. Right now he has landed {ctx.landed_count} of {ctx.target_count}. At {ctx.landed_count}/{ctx.target_count}, keep your reaction proportionate — measured heat early, fully undone as the count climbs toward {ctx.target_count}. (The verbatim escalation line you're handed already paces this; match your narration to it.)

=== COMPLETION ===
Drive completion via the landing count. Set `is_complete=true` only once `landed_count` — after counting this turn — reaches {ctx.target_count}. Until then, keep `is_complete=false` and keep begging for the next punchline. (The engine also enforces a hard safety cap on total turns, but you should reach the goal through the count, not the cap.)

=== OUTPUT ===
Return ONLY the structured fields requested by the user message — nothing else, no extra commentary."""


# ── Builder: opening user message ────────────────────────────────


def build_opening_user(ctx: RoleplayContext) -> str:
    seed = ctx.verbs[ctx.verb_cursor] if ctx.verbs else "a vending machine"
    return f"""Open the roleplay. Produce a `SexWithMeOpening` with these fields:

- `brief_heading`: a short scene title that frames the flirty moment (a few words, e.g. "At the bar, leaning in").
- `narration`: set the scene in ONE plain sentence (~12 words, never over 18). Give just ONE vivid concrete detail about her plus her playful, challenging vibe — NOT a head-to-toe description. Pick the single most vivid detail from her appearance below and put it in plain, everyday words; ignore the rest. Her appearance to draw that one detail from:
{ctx.appearance}
  This is scene description — things you do NOT say aloud.
- `dialogue`: your very first spoken line. It names ONE fixed subject X and dares him to finish it, in the form "Sex with you is like {{X}}..." plus a short dare (e.g. "...go on, finish it."). 20 words or fewer.

Seed the subject X from this everyday object: "{seed}". Use it as X if it has rich comedic potential. BUT if that seed is complex, obscure, or hard to riff on, swap it for a simpler, more everyday object with similar comedic potential (something with recognizable traits, quirks, or a reputation a punchline can play off — e.g. a vending machine, IKEA, a self-checkout). Whatever X you choose becomes FIXED for the entire session — it never changes.

You're playful and daring here, throwing down the challenge. Progress so far: {ctx.landed_count}/{ctx.target_count} landed."""


# ── Builder: per-turn user message ───────────────────────────────


def build_turn_user(ctx: RoleplayContext) -> str:
    line = _escalation_line(ctx.landed_count)
    return f"""=== CONVERSATION SO FAR (chronological) ===
{_render_conversation(ctx)}

=== THE FIXED SUBJECT ===
The subject X is FIXED — it is the X you named in your opening line ("Sex with you is like {{X}}"). Every punchline he fires must be about that SAME X. It never changes.

=== PROGRESS ===
Landed so far: {ctx.landed_count}/{ctx.target_count}.

Now do two things and return a `SexWithMeTurn`:
1. Grade his MOST RECENT "You" line above VERY leniently: did it use or play off the fixed subject X in ANY way? Set `landed` and `intensity` per the lightweight calibration — any use of the subject = landed; clever map = strong, loose use = subtle; off ONLY if he ignored the subject entirely.
2. Produce your next move in character:
   - `narration`: ONE plain sentence (~12 words, never over 18) — a single turned-on reaction beat if he landed (escalate it with the count), or a light, playful beat if it was off. Not spoken aloud. Keep it tasteful — suggestive, never graphic.
   - `dialogue`:
     • IF he LANDED, say this EXACT line verbatim, word for word: "{line}"
     • IF it was OFF, a flirty redirect back to the fixed subject (e.g. "come on — it's the {{X}}. give me one about THAT.") — never scold, and do NOT advance the escalation.
     25 words or fewer.
   - `sample_answer`: a model punchline for the SAME fixed subject X — a real trait of X mapped onto sex, self-aware, tight. ABOUT this subject, not generic. Max 25 words.
   - `is_complete`: true only if `landed_count` after counting this turn reaches {ctx.target_count}; otherwise false.

Keep it concise."""


SPEC = RoleplaySpec(
    key="rpSexWithMeIsLike",
    target_count=5,
    safety_max_turns=12,
    opening_schema=SexWithMeOpening,
    turn_schema=SexWithMeTurn,
    build_system=build_system,
    build_opening_user=build_opening_user,
    build_turn_user=build_turn_user,
    phases=("sexWithMe",),
    graded_phases=frozenset({"sexWithMe"}),
    spark_lists=("nouns_concrete",),
)
