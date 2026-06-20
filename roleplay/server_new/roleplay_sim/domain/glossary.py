"""Plain-language glosses for Beats and Dials. [P6]

Shared by the Director (brief author) and Actor prompts so neither LLM has to
guess what a raw enum value like `qualify_self` or `testiness=high` means.
The asserts fail fast if a Beat is added without a gloss.
"""
from __future__ import annotations

from roleplay_sim.domain.enums import Beat

# What each beat asks the actress to DO this turn (one in-character intent).
BEAT_GLOSS: dict[Beat, str] = {
    Beat.LEAVE: "disengage and leave — you're done here",
    Beat.COOL_OFF: "pull back, go cooler/shorter — he lost ground",
    Beat.POLITE_BRUSHOFF: "politely wind it down — you're bored, not hostile",
    Beat.NEUTRAL_ENGAGE: "engage politely but unimpressed — he hasn't earned warmth yet",
    Beat.CURIOUS: "mildly intrigued but reserved — let him keep working",
    Beat.SHIT_TEST: "challenge/tease him to test his reaction — bust his balls a little",
    Beat.QUALIFY_SELF: "try to impress him / prove you're interesting — you want his approval",
    Beat.WARM_OPEN: "warm up and open up — show real, growing interest",
    Beat.BANTER: "play back — tease, volley, match his energy",
    Beat.COMPLY: "go along with his lead (escalation/close) — you're into it",
    Beat.ESCALATE_BACK: "ramp it up yourself — you're turned on and pushing it forward",
    Beat.BRAKES: "slow the physical/logistical escalation — not yet, ease off",
    Beat.FLAKE_SIGNAL: "agree on the surface but stay non-committal — you might flake",
}
assert set(BEAT_GLOSS) == set(Beat), "BEAT_GLOSS missing/extra Beat keys"

# What low→high means on each performance dial (each dial value is low/med/high).
DIAL_GLOSS: dict[str, str] = {
    "warmth": "how affectionate/friendly you are (low = cool, closed; high = warm, touchy)",
    "investment": "how much effort you put into the talk (low = one-word, minimal; high = ask questions, carry it)",
    "testiness": "how much you challenge/tease/test him (low = compliant; high = busting, probing)",
    "openness": "how much you share/open up (low = guarded; high = candid, personal)",
    "receptiveness": "how open you are to his leading/escalation (low = resist his moves; high = follow, encourage)",
}

DIAL_DOC = "\n".join(f"- {k}: {v}" for k, v in DIAL_GLOSS.items())


def beat_line(beat: Beat, secondary: "Beat | None" = None) -> str:
    """`beat (gloss)` [, then secondary (gloss)] — for prompt interpolation."""
    line = f"{beat.value} ({BEAT_GLOSS[beat]})"
    if secondary is not None:
        line += f", then {secondary.value} ({BEAT_GLOSS[secondary]})"
    return line
