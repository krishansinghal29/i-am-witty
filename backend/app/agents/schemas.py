from pydantic import BaseModel


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
