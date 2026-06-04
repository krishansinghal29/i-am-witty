"""Shared prompt text helpers for exercise specs."""

from __future__ import annotations

from collections.abc import Iterable


def _render_bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def _render_quoted_examples(items: list[str]) -> str:
    return "\n".join(f'- "{item}"' for item in items)


def build_feedback_style(
    trap_intro: str,
    common_traps: list[str],
    mindset_examples: list[str],
    *,
    level_up_instruction: str = "One specific technique from the list above. 1-2 sentences max.",
    mindset_intro: str = "One root-cause mental reframe.",
) -> str:
    """Build the shared 4-part HTML feedback instruction block."""
    traps_block = _render_bullets(common_traps)
    mindset_examples_block = _render_quoted_examples(mindset_examples)

    return f'''=== FEEDBACK FORMAT (CRITICAL — FOLLOW THIS STRUCTURE) ===

<b>✅ What Landed</b><br>
What worked. Quote their words if possible. 1-2 sentences max.
<br><br>

<b>⚠️ The Trap</b><br>
{trap_intro}
{traps_block}
1-2 sentences max.
<br><br>

<b>🚀 Level Up</b><br>
{level_up_instruction}
<br><br>

<b>🧠 Mindset Shift</b><br>
{mindset_intro}
Examples:
{mindset_examples_block}
1-2 sentences max.'''


def build_sample_answer_guidelines(
    sample_answer_instructions: list[str],
    closing_instruction: str,
) -> str:
    """Build the sample-answer guidance block shared across prompt types."""
    sample_answer_block = _render_bullets(sample_answer_instructions)

    return f'''=== SAMPLE ANSWER GUIDELINES ===
Generate 3 sample answers:
{sample_answer_block}
{closing_instruction}'''


EVALUATION_CONTEXT = '''=== EVALUATION CONTEXT ===
You are evaluating a user's transcribed response. You only have the transcript.
Focus on content quality using the exercise criteria below. Do not assess audio quality, vocal delivery, tone, pacing, or confidence.'''

EVALUATOR_JSON_OUTPUT_FORMAT = '''=== JSON OUTPUT FORMAT (CRITICAL) ===
Respond with ONLY valid JSON, no text before or after, no markdown code blocks.

{
    "feedback": "<HTML formatted feedback using the exact 4-section structure above: What Landed, The Trap, Level Up, Mindset Shift>",
    "sample_answer": "<3 short responses using different techniques, separated by <br><br>>"
}

Rules:
- feedback MUST follow the exact 4-section structure defined above.
- sample_answer must contain exactly 3 responses separated by <br><br>. Each should be short and punchy.'''


def build_evaluator_system(
    *,
    intro: str,
    sections: Iterable[str],
    feedback_style: str,
    sample_answer_guidelines: str,
    json_output_format: str = EVALUATOR_JSON_OUTPUT_FORMAT,
) -> str:
    """Assemble an evaluator system prompt in the standard order."""
    parts = [
        intro,
        EVALUATION_CONTEXT,
        *sections,
        feedback_style,
        sample_answer_guidelines,
        json_output_format,
    ]
    return "\n\n".join(part.strip("\n") for part in parts if part).strip()
