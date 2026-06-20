"""All enumerations for the simulation. Pure types — no logic. [P1]"""
from __future__ import annotations

from enum import Enum


class Ladder(Enum):
    PHYSICAL = "physical"
    VERBAL = "verbal"
    LOGISTICAL = "logistical"


class LMH(Enum):
    """Low / Medium / High — used for dials and intensities."""
    LOW = "low"
    MED = "med"
    HIGH = "high"


class Quality(Enum):
    GOOD = "good"
    MEDIOCRE = "mediocre"
    BOTCHED = "botched"


class ValuePosture(Enum):
    HIGH = "high"
    NEUTRAL = "neutral"
    LOW = "low"


class Supplication(Enum):
    NONE = "none"
    MILD = "mild"
    STRONG = "strong"


class Register(Enum):
    BASELINE = "baseline"
    PLOTLINE = "plotline"
    MIXED = "mixed"


class MoveType(Enum):
    # --- openers ---
    OPEN_DIRECT = "open_direct"
    OPEN_INDIRECT = "open_indirect"
    OPEN_PUSH_PULL = "open_push_pull"
    OPEN_SITUATIONAL = "open_situational"
    OPEN_OBSERVATIONAL = "open_observational"
    OPEN_NONVERBAL = "open_nonverbal"
    OPEN_OPINION = "open_opinion"
    # --- attraction techniques ---
    TEASE = "tease"
    PUSH_PULL = "push_pull"
    COLD_READ = "cold_read"
    DISQUALIFY = "disqualify"
    COCKY_FRAME = "cocky_frame"
    OPEN_LOOP = "open_loop"
    EXAGGERATION = "exaggeration"
    MISINTERPRET = "misinterpret"
    SEXUALIZE = "sexualize"
    # --- premise ---
    PREMISE_SUBTLE = "premise_subtle"
    PREMISE_OVERT = "premise_overt"
    # --- evaluate (get her to qualify) ---
    QUALIFY_ASK = "qualify_ask"
    QUALIFY_TEASE = "qualify_tease"
    QUALIFY_LEAD = "qualify_lead"
    QUALIFY_HAVE_VALUE = "qualify_have_value"
    # --- narrative ---
    STORY_SHOW = "story_show"
    STORY_TELL = "story_tell"
    SELF_DISCLOSURE = "self_disclosure"
    PREFRAME = "preframe"
    REFRAME = "reframe"
    SOCIAL_PROOF = "social_proof"
    # --- comfort / baseline ---
    GENUINE_QUESTION = "genuine_question"
    ACTIVE_LISTENING = "active_listening"
    RAPPORT = "rapport"
    AGREE_EXAGGERATE = "agree_exaggerate"
    # --- frame tools ---
    SOCIAL_PRESSURE = "social_pressure"
    SEEDING = "seeding"
    BABYSTEP = "babystep"
    FALSE_TIME_CONSTRAINT = "false_time_constraint"
    ASSUME_BURDEN = "assume_burden"
    # --- close ---
    CLOSE_NUMBER = "close_number"
    CLOSE_DATE = "close_date"
    CLOSE_INSTANT_DATE = "close_instant_date"
    # --- anti-patterns ---
    SUPPLICATE = "supplicate"
    INTERVIEW_QS = "interview_qs"
    TRY_HARD = "try_hard"
    OVER_EXPLAIN = "over_explain"
    SEEK_VALIDATION = "seek_validation"


class ActionType(Enum):
    # approach
    SIT_DOWN = "sit_down"
    STOP_HER = "stop_her"
    TAP_SHOULDER = "tap_shoulder"
    PLANT_FEET = "plant_feet"
    HOLD_GAZE = "hold_gaze"
    STEP_BACK = "step_back"
    # physical escalation
    TOUCH_LIGHT = "touch_light"
    TOUCH_ESCALATE = "touch_escalate"
    LEAN_IN = "lean_in"
    KISS_ATTEMPT = "kiss_attempt"
    # logistical escalation
    SUGGEST_ISOLATE = "suggest_isolate"
    SUGGEST_VENUE_CHANGE = "suggest_venue_change"
    PULL = "pull"


class Beat(Enum):
    LEAVE = "leave"
    COOL_OFF = "cool_off"
    POLITE_BRUSHOFF = "polite_brushoff"
    NEUTRAL_ENGAGE = "neutral_engage"
    CURIOUS = "curious"
    SHIT_TEST = "shit_test"
    QUALIFY_SELF = "qualify_self"
    WARM_OPEN = "warm_open"
    BANTER = "banter"
    COMPLY = "comply"
    ESCALATE_BACK = "escalate_back"
    BRAKES = "brakes"
    FLAKE_SIGNAL = "flake_signal"


class Consequence(Enum):
    WARMS = "warms"
    COOLS = "cools"
    BORED = "bored"
    SHE_QUALIFIES = "she_qualifies"
    FEELS_INTERVIEWED = "feels_interviewed"
    TEST_TRIGGERED = "test_triggered"
    TEST_PASSED = "test_passed"
    TEST_FAILED = "test_failed"
    ESCALATION_ACCEPTED = "escalation_accepted"
    ESCALATION_RESISTED = "escalation_resisted"
    RE_ESCALATION = "re_escalation"
    LOCKED_OUT = "locked_out"
    SELF_ESCALATES = "self_escalates"
    PREMISE_SET = "premise_set"
    CLOSE_ACCEPTED = "close_accepted"
    CLOSE_FLAKY = "close_flaky"
    CLOSE_REJECTED = "close_rejected"
    LEAVES = "leaves"


class SessionStatus(Enum):
    ONGOING = "ongoing"
    WON = "won"
    LEFT = "left"
    LOCKED_OUT = "locked_out"


# Convenience numeric mapping for dials/intensities when the engine needs scalars.
LMH_VALUE: dict[LMH, float] = {LMH.LOW: 0.25, LMH.MED: 0.55, LMH.HIGH: 0.85}
