"""Classifier prompt + JSON schema (co-located with the classifier). [P6]

The classifier tags the MAN's turn against the verbal-game taxonomy. It does NOT
judge timing or the woman's state — only what he did. Timing/gates are derived
downstream from the ladder + outcome rules.
"""
from __future__ import annotations

from typing import Any, Literal, Optional, get_args

from pydantic import BaseModel, ConfigDict, Field

from roleplay_sim.domain.enums import (
    ActionType,
    LMH,
    MoveType,
    Quality,
    Register,
    Supplication,
    ValuePosture,
)
from roleplay_sim.domain.models import GameState


# ---------------------------------------------------------------------------
# Structured-output schema (bare — field meaning lives in SYSTEM, refined later)
# ---------------------------------------------------------------------------
class MoveOut(BaseModel):
    type: MoveType
    quality: Quality = Quality.MEDIOCRE
    intensity: LMH = LMH.MED
    softener: bool = False
    target: str = "none"
    target_level: Optional[int] = None


class FrameOut(BaseModel):
    value_posture: ValuePosture = ValuePosture.NEUTRAL
    supplication: Supplication = Supplication.NONE
    reaction_seeking: bool = False
    congruence: bool = True


class ActionOut(BaseModel):
    type: ActionType
    target_level: Optional[int] = None
    intended_step: Optional[int] = None


class ShitTestOut(BaseModel):
    outcome: Literal["passed", "partial", "failed"]
    method: str = "unreactive"


class ClassificationOut(BaseModel):
    # `register` collides with BaseModel's inherited ABCMeta.register, so the
    # Python attribute is renamed while the wire/schema key stays "register".
    model_config = ConfigDict(populate_by_name=True)

    speech_register: Register = Field(default=Register.BASELINE, alias="register")
    moves: list[MoveOut] = Field(default_factory=list)
    frame: FrameOut = Field(default_factory=FrameOut)
    action: Optional[ActionOut] = None
    shit_test_response: Optional[ShitTestOut] = None


# Enum/value lists interpolated into the prompt so the prose can never drift from
# the schema. The two free-text fields (move `target`, shit-test `method`) have no
# enum, so their allowed values mirror the domain model docstrings by hand.
_REGISTERS = "/".join(r.value for r in Register)
_QUALITY = "/".join(q.value for q in Quality)
_INTENSITY = "/".join(i.value for i in LMH)
_VALUE_POSTURE = "/".join(v.value for v in ValuePosture)
_SUPPLICATION = "/".join(s.value for s in Supplication)
_TEST_OUTCOMES = "/".join(get_args(ShitTestOut.model_fields["outcome"].annotation))
_MOVE_TARGETS = "looks, personality, situation, group, self, none"   # Move.target
_TEST_METHODS = "misinterpret, agree_exaggerate, unreactive, defensive, supplicated"  # ShitTestResponse.method


# ---------------------------------------------------------------------------
# Move glossary — one line per move (definition · field-tested example) so the
# classifier knows what each taxonomy term *means*, not just that it exists.
# Definitions/examples distilled from the Verbal Game Academy conceptual lessons.
# Keep verbatim move keys; the asserts below fail fast if a MoveType is added
# without a glossary entry or a group placement.
# ---------------------------------------------------------------------------
MOVE_GLOSSARY: dict[MoveType, str] = {
    # openers
    MoveType.OPEN_DIRECT: "states interest/compliment up front · \"You're cute, I had to come say hi.\"",
    MoveType.OPEN_INDIRECT: "starts talk without stating interest or asking a verdict · \"Hey, what do you think about…\"",
    MoveType.OPEN_PUSH_PULL: "opens with a positive + negative spike together · \"You're cute, but I'm not sure about you.\" / \"You're trouble.\"",
    MoveType.OPEN_SITUATIONAL: "bland, safe comment on the shared environment · \"This line is insane today.\"",
    MoveType.OPEN_OBSERVATIONAL: "teases something she just did/wore, in the moment · \"Do NOT give me that look.\"",
    MoveType.OPEN_NONVERBAL: "a gesture/expression instead of words · wink + smile; high-five; offering a hand to pull her over.",
    MoveType.OPEN_OPINION: "asks her opinion as a pretext to launch a story · \"Quick, settle a debate for me…\"",
    # attraction techniques
    MoveType.TEASE: "playful jab mixing positive + negative; never a flat insult · \"You're such a dork… kind of cute though.\"",
    MoveType.PUSH_PULL: "one line with both a positive and a negative spike (negative often implies the positive) · \"I love you but I hate you.\" / \"I thought I loved you until you said that.\"",
    MoveType.COLD_READ: "tells her something about herself instead of asking, playful/exaggerated · \"You're definitely not from around here.\"",
    MoveType.DISQUALIFY: "states an incompatibility/obstacle so she proves you two fit · \"You and I would never get along.\"",
    MoveType.COCKY_FRAME: "asserts a frame where she should be impressed by you, tongue-in-cheek · \"You looked bored, so I came to amuse myself.\"",
    MoveType.OPEN_LOOP: "dangles an unfinished thread so she chases it · \"I just noticed something… never mind.\"",
    MoveType.EXAGGERATION: "takes an idea to a ridiculous extreme for humor (incl. agree & exaggerate) · \"Yeah, I've said that 758 times today.\"",
    MoveType.MISINTERPRET: "deliberately reads a neutral line as her hitting on you / a compliment · \"Easy — we're not getting any closer no matter how hard you try.\" (verbal-ladder move; set target_level ≈4)",
    MoveType.SEXUALIZE: "brings sexual innuendo into otherwise platonic talk · (she: \"it's so hard\") \"That's what she said.\" (verbal-ladder move; set target_level ≈6)",
    # premise
    MoveType.PREMISE_SUBTLE: "implies the dating/sexual frame without stating it · \"Don't think you get away with that just because you're cute.\"",
    MoveType.PREMISE_OVERT: "states the dating premise plainly · \"I really don't think we should date.\" / \"I think we should go on a date.\"",
    # evaluate / qualify (get HER to prove value)
    MoveType.QUALIFY_ASK: "directly asks her to prove she's more than her looks · \"Beauty's common — what else have you got going for you?\"",
    MoveType.QUALIFY_TEASE: "teases/challenges her into qualifying · \"You're not one of those girls who schedules everything, are you?\"",
    MoveType.QUALIFY_LEAD: "declares a value and lets it hang so she relates/proves she fits · \"I'm really into people with drive…\"",
    MoveType.QUALIFY_HAVE_VALUE: "signals he's selective, so his approval is worth earning · \"I'm pretty picky about who I actually let in.\"",
    # narrative
    MoveType.STORY_SHOW: "conveys a trait via a vivid story that shows it (don't tell) · a story that lets her conclude \"you travel a lot.\"",
    MoveType.STORY_TELL: "an engaging story with setup/conflict/resolution · \"So my tire blows out on the way to the airport…\"",
    MoveType.SELF_DISCLOSURE: "reveals something genuine/personal about himself · \"I'm from a small town up north, moved here for work.\"",
    MoveType.PREFRAME: "sets a frame before the moment so it's read his way later · \"Fair warning, I take forever to trust people.\"",
    MoveType.REFRAME: "changes the meaning of something after it happened · (she: \"you're such a player\") \"A player wouldn't still be standing here.\"",
    MoveType.SOCIAL_PROOF: "conveys that others (esp. women) value him · \"My friends drag me out — apparently I make the night happen.\"",
    # comfort / baseline
    MoveType.GENUINE_QUESTION: "a real, warm, curious question (not interview mode) · \"What got you into that? I'm genuinely curious.\"",
    MoveType.ACTIVE_LISTENING: "reflects/acknowledges what she just said · \"So you moved cross-country alone at 19 — that's a big deal.\"",
    MoveType.RAPPORT: "finds common ground / shared experience · \"No way, I grew up two towns over from there.\"",
    MoveType.AGREE_EXAGGERATE: "agrees with her and playfully amplifies it · \"You hate cilantro? Yeah, it's basically soap, total betrayal.\"",
    # frame tools
    MoveType.SOCIAL_PRESSURE: "uses the group/onlookers/situation to nudge compliance · \"Everyone here's on my side — you're the only holdout.\"",
    MoveType.SEEDING: "plants an idea early to call back to later · (early, no ask) \"There's an insane speakeasy two minutes from here.\"",
    MoveType.BABYSTEP: "advances in a small, easy-yes increment · \"Come grab one drink at the bar, we'll be right back.\"",
    MoveType.FALSE_TIME_CONSTRAINT: "signals he can only stay a moment, lowering pressure / adding urgency · \"I've got like two minutes, but you seem cool.\"",
    MoveType.ASSUME_BURDEN: "takes on a playful burden so she chases · \"I'll allow you to keep talking, but you have to prove you're not boring.\"",
    # close
    MoveType.CLOSE_NUMBER: "gets her contact info · \"Give me your number, I'll send you the info.\"",
    MoveType.CLOSE_DATE: "locks in a specific future plan · \"Let's grab a drink Thursday, I know a place.\"",
    MoveType.CLOSE_INSTANT_DATE: "moves her to a new venue right now · \"Come on, let's get out of here — better spot two minutes away.\"",
    # anti-patterns (mistakes — low value)
    MoveType.SUPPLICATE: "bends himself or buys favor to win her · \"Whatever you want to do is fine, I'm flexible.\"",
    MoveType.INTERVIEW_QS: "rapid-fire boring fact questions (\"interview mode\") · \"What do you do? Where are you from? How long have you lived here?\"",
    MoveType.TRY_HARD: "visibly strains to be impressive/clever · \"Watch this, I've got a great story you'll love.\"",
    MoveType.OVER_EXPLAIN: "justifies/qualifies instead of letting a statement stand · \"Well yeah that's my line, but I just think it's cool when strangers meet…\"",
    MoveType.SEEK_VALIDATION: "fishes for approval/reassurance · \"That was funny, right? You think I'm funny?\"",
}

# Display order + section headers for the rendered glossary (and a coverage check).
_MOVE_GROUPS: list[tuple[str, tuple[MoveType, ...]]] = [
    ("openers", (MoveType.OPEN_DIRECT, MoveType.OPEN_INDIRECT, MoveType.OPEN_PUSH_PULL,
                 MoveType.OPEN_SITUATIONAL, MoveType.OPEN_OBSERVATIONAL, MoveType.OPEN_NONVERBAL,
                 MoveType.OPEN_OPINION)),
    ("attraction techniques", (MoveType.TEASE, MoveType.PUSH_PULL, MoveType.COLD_READ,
                               MoveType.DISQUALIFY, MoveType.COCKY_FRAME, MoveType.OPEN_LOOP,
                               MoveType.EXAGGERATION, MoveType.MISINTERPRET, MoveType.SEXUALIZE)),
    ("premise", (MoveType.PREMISE_SUBTLE, MoveType.PREMISE_OVERT)),
    ("evaluate / qualify (get HER to prove value)", (MoveType.QUALIFY_ASK, MoveType.QUALIFY_TEASE,
                                                     MoveType.QUALIFY_LEAD, MoveType.QUALIFY_HAVE_VALUE)),
    ("narrative", (MoveType.STORY_SHOW, MoveType.STORY_TELL, MoveType.SELF_DISCLOSURE,
                   MoveType.PREFRAME, MoveType.REFRAME, MoveType.SOCIAL_PROOF)),
    ("comfort / baseline", (MoveType.GENUINE_QUESTION, MoveType.ACTIVE_LISTENING,
                            MoveType.RAPPORT, MoveType.AGREE_EXAGGERATE)),
    ("frame tools", (MoveType.SOCIAL_PRESSURE, MoveType.SEEDING, MoveType.BABYSTEP,
                     MoveType.FALSE_TIME_CONSTRAINT, MoveType.ASSUME_BURDEN)),
    ("close", (MoveType.CLOSE_NUMBER, MoveType.CLOSE_DATE, MoveType.CLOSE_INSTANT_DATE)),
    ("anti-patterns (mistakes — low value)", (MoveType.SUPPLICATE, MoveType.INTERVIEW_QS,
                                              MoveType.TRY_HARD, MoveType.OVER_EXPLAIN,
                                              MoveType.SEEK_VALIDATION)),
]
assert set(MOVE_GLOSSARY) == set(MoveType), "MOVE_GLOSSARY is missing/extra MoveType keys"
assert {m for _, ms in _MOVE_GROUPS for m in ms} == set(MoveType), "_MOVE_GROUPS does not cover every MoveType"

_MOVES_DOC = "\n".join(
    f"  [{header}]\n" + "\n".join(f"  - {m.value}: {MOVE_GLOSSARY[m]}" for m in members)
    for header, members in _MOVE_GROUPS
)

# Action types with their canonical 0-10 rung (mirrors engine.registry.ACTION_LADDER).
_ACTION_GROUPS: list[tuple[str, tuple[tuple[str, int], ...]]] = [
    ("approach", (("sit_down", 1), ("stop_her", 0), ("tap_shoulder", 1), ("plant_feet", 0),
                  ("hold_gaze", 1), ("step_back", 0))),
    ("physical escalation", (("touch_light", 2), ("touch_escalate", 4), ("lean_in", 4),
                             ("kiss_attempt", 5))),
    ("logistical escalation", (("suggest_isolate", 3), ("suggest_venue_change", 5), ("pull", 7))),
]
assert {n for _, rows in _ACTION_GROUPS for n, _ in rows} == {a.value for a in ActionType}, \
    "_ACTION_GROUPS does not cover every ActionType"
_ACTIONS_DOC = "; ".join(
    f"{header}: " + ", ".join(f"{name}({lvl})" for name, lvl in rows)
    for header, rows in _ACTION_GROUPS
)

# Worked examples (turn -> label). Plain string (literal JSON braces), appended to SYSTEM.
_FEWSHOT = """Examples (turn → label):

1) turn=0; he said: "Hey — you've got a cool vibe, I had to come say hi."
{"register":"baseline","moves":[{"type":"open_direct","quality":"good","intensity":"low","softener":false,"target":"personality","target_level":null}],"frame":{"value_posture":"neutral","supplication":"none","reaction_seeking":false,"congruence":true},"action":null,"shit_test_response":null}

2) he said: "You're honestly adorable… which is exactly why you're dangerous. I should probably get out of here."
{"register":"plotline","moves":[{"type":"push_pull","quality":"good","intensity":"med","softener":false,"target":"looks","target_level":null},{"type":"false_time_constraint","quality":"mediocre","intensity":"low","softener":false,"target":"none","target_level":null}],"frame":{"value_posture":"high","supplication":"none","reaction_seeking":false,"congruence":true},"action":null,"shit_test_response":null}

3) her_last="You're so full of yourself."; he said: "Oh completely — I'm basically a national monument, people take photos."
{"register":"plotline","moves":[{"type":"agree_exaggerate","quality":"good","intensity":"med","softener":false,"target":"self","target_level":null}],"frame":{"value_posture":"high","supplication":"none","reaction_seeking":false,"congruence":true},"action":null,"shit_test_response":{"outcome":"passed","method":"agree_exaggerate"}}

4) he said: "Sorry if this is weird — um, so what do you do? where are you from? do you like it here?"
{"register":"baseline","moves":[{"type":"supplicate","quality":"botched","intensity":"low","softener":true,"target":"self","target_level":null},{"type":"interview_qs","quality":"botched","intensity":"low","softener":false,"target":"none","target_level":null}],"frame":{"value_posture":"low","supplication":"mild","reaction_seeking":true,"congruence":false},"action":null,"shit_test_response":null}

5) action: lean_in; she just said the music is loud; he said: "Mm, perfect excuse to get closer. Don't get any ideas though."
{"register":"plotline","moves":[{"type":"sexualize","quality":"good","intensity":"med","softener":false,"target":"situation","target_level":6}],"frame":{"value_posture":"high","supplication":"none","reaction_seeking":false,"congruence":true},"action":{"type":"lean_in","target_level":4,"intended_step":1},"shit_test_response":null}"""

SYSTEM = f"""You label a man's single conversational turn while he flirts with a woman, using a \
fixed taxonomy. Output JSON only. Tag only what is actually present — do not invent moves. \
A turn may contain several moves; tag each one.

register — which mode the turn is in ({_REGISTERS}):
- baseline: normal, grounded talk (real life, calm getting-to-know-you, straight answers). e.g. "I work in design, grew up in Chicago."
- plotline: heightened flirty spike — teasing, roleplay, push-pull, takeaways. e.g. "You're trouble — we'd be a disaster together."
- mixed: one turn doing both. e.g. "Just got back from a month in Japan — though you don't seem cultured enough for my travel stories."

move types (definition · example) — put each move you find in `moves`:
{_MOVES_DOC}

For each move give:
- type: one of the move types above.
- quality: {_QUALITY} — how well it landed (good = clean, got the reaction; botched = fell flat or backfired).
- intensity: {_INTENSITY} — how strong/explicit (same tease dials up: "…then we cuddle" low → "…then we fuck" high).
- softener: bool — true if hedged: "just kidding", nervous laugh, qualifiers ("kind of", "I guess"), or offloading to a third party.
- target: what it's aimed at — {_MOVE_TARGETS} (self = aimed at himself, e.g. self-deprecation; group = her friends).
- target_level: integer 0-10 — ONLY for the two verbal-escalation moves (sexualize ≈6, misinterpret ≈4): the rung the innuendo reaches. null for every other move.

action (non-verbal/logistical, optional — physical/logistical escalation, never speech). Canonical rung in parens:
{_ACTIONS_DOC}.
0-10 rung anchor: 0 talk only · 1-2 incidental touch · 3-4 sustained touch / isolate · 5-6 intimate touch, venue change, kiss-attempt · 7-8 kissing / overtly sexual · 9-10 pull home / sex.
If he takes one, set `action` with:
- type: one of the action types above.
- target_level: integer 0-10 — the rung it reaches; use the canonical rung unless the turn clearly reaches higher/lower; null if unclear.
- intended_step: relative intent vs the current rung — -1 (back off), 0 (hold), +1 (step up), +2 (jump); null if unclear.

frame (always present — how he comes across this turn):
- value_posture: {_VALUE_POSTURE} — high = the prize/chooser, unreactive ("you'll have to win me over"); low = chasing, easily won, bends to her frame.
- supplication: {_SUPPLICATION} — mild = over-agreeing to please ("yeah totally, love that too!"); strong = changing himself / buying favor ("I'll skip my plans and carry your bags").
- reaction_seeking: bool — fishing for a laugh or approval rather than owning the line.
- congruence: bool — true = natural/owned; false = forced, canned, or undercut by hedging/justifying.

shit_test_response — set ONLY if her previous turn was a shit test (e.g. "Is that your line?", "You're so full of yourself"); otherwise null:
- outcome: {_TEST_OUTCOMES} — passed = assumes the bad frame away and clearly doesn't care; partial = escapes but looks reactive/try-hard; failed = falls into her frame (justifies, qualifies, supplicates).
- method: {_TEST_METHODS} — misinterpret / agree_exaggerate / unreactive PASS; defensive / supplicated FAIL. (Attitude — not caring — matters more than the exact words.)"""

SYSTEM = SYSTEM + "\n\n" + _FEWSHOT


def context_summary(state: GameState, history: Any) -> str:
    f = state.flags
    bits = [
        f"premise_set={f.premise_set}",
        f"pending_test={f.pending_test!r}",
        f"venue={f.venue}",
        f"turn={f.turn_count}",
    ]
    last_her = ""
    try:
        win = history.window(2)
        if win:
            last_her = win[-1][1].text
    except Exception:
        pass
    if last_her:
        bits.append(f'her_last="{last_her}"')
    return "; ".join(bits)


def build_messages(turn_text: str, action_hint: str, ctx: str) -> list[dict[str, str]]:
    user = f"Context: {ctx}\n"
    if action_hint:
        user += f"Player physical/logistical action: {action_hint}\n"
    user += f'Player said: "{turn_text}"\n\nReturn the JSON label.'
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]
