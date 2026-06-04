"""Fallback structured responses for prompt specs."""

from __future__ import annotations

from typing import Any

STANDARD_EVALUATOR_FALLBACK = {
    "feedback": (
        "<b>✅ What Landed</b><br>You submitted a response, which gives us something to work with."
        "<br><br><b>⚠️ The Trap</b><br>We couldn't analyse this attempt reliably, so there isn't specific coaching yet."
        "<br><br><b>🚀 Level Up</b><br>Try again with a complete response transcript."
        "<br><br><b>🧠 Mindset Shift</b><br>A clean retry gives better coaching than guessing from incomplete text."
    ),
    "sample_answer": "Please try again with a complete response transcript.",
}


def standard_evaluator_fallback() -> dict[str, Any]:
    return dict(STANDARD_EVALUATOR_FALLBACK)
