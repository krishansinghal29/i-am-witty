"""
Shared Pydantic schemas used across multiple agents.

Includes schemas for:
- CombinedEvaluationResult: Used by classical (text-only) combined evaluation agents.
- SprintEvaluationResult: Used by sprint evaluation agents that analyse both
  spoken audio delivery and text content quality via multimodal Gemini calls.
"""

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Combined (classical) evaluation schemas
# ---------------------------------------------------------------------------

class EvaluationFeedback(BaseModel):
    """Feedback returned by a combined evaluation agent."""
    feedback: str
    sample_answer: str


class SkillUpdate(BaseModel):
    """Single skill score delta produced by a combined evaluation agent."""
    skillKey: str
    delta: float = Field(ge=-5.0, le=5.0)
    confidenceDelta: float = Field(ge=-2.0, le=2.0)
    rationale: str
    difficultyMultiplier: float = Field(ge=0.5, le=2.0)


class ScoringResult(BaseModel):
    """Aggregated scoring result from a combined evaluation agent."""
    skills: list[SkillUpdate]
    overallRationale: str
    timeBasedAdjustment: str


class CombinedEvaluationResult(BaseModel):
    """Full response schema for combined (classical) evaluation agents."""
    evaluation: EvaluationFeedback
    scoring: ScoringResult


# ---------------------------------------------------------------------------
# Sprint evaluation schemas
# ---------------------------------------------------------------------------

class SprintEvaluationResult(BaseModel):
    """
    Response schema for sprint evaluation agents.

    Sprint agents evaluate SPOKEN responses — they receive raw audio and
    analyse both the text content quality AND vocal delivery (filler words,
    pacing, confidence, tone) via a single multimodal Gemini call.

    Note: filler_words_breakdown is a JSON-encoded string (e.g. '{"um": 2}')
    because Gemini structured output does not support dynamic object keys.
    The backend reconstructs the nested filler_words_detail dict from these
    flat fields before returning the response to the frontend.
    """
    text_score: int
    voice_score: int
    overall_score: int
    text_feedback: str
    voice_feedback: str
    sample_answer: str
    filler_words_total_count: int
    filler_words_breakdown: str
    filler_words_frequency_per_minute: float
    improvement_tips: list[str]
    pace_wpm: int
    confidence_level: str
    refinement_comparison: str
