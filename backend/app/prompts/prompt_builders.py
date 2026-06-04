"""Reusable prompt assembly helpers."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any, Optional

from helpers.question_format_converter import convert_question_to_string
from prompts.prompt_contracts import EVALUATOR_OUTPUT_CONTRACT
from prompts.spec import EvaluatorPromptFactory

QuestionFormatter = Callable[[Any], str]


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
    """Build the standard 4-part HTML feedback instruction block."""
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
    """Build the standard sample-answer guidance block."""
    sample_answer_block = _render_bullets(sample_answer_instructions)

    return f'''=== SAMPLE ANSWER GUIDELINES ===
Generate 3 sample answers:
{sample_answer_block}
{closing_instruction}'''


def build_evaluator_system(
    *,
    intro: str,
    evaluation_context: str,
    sections: Iterable[str],
    feedback_style: str,
    sample_answer_guidelines: str,
    output_contract: str = EVALUATOR_OUTPUT_CONTRACT,
) -> str:
    """Assemble an evaluator system prompt in the standard order."""
    parts = [
        intro,
        evaluation_context,
        *sections,
        feedback_style,
        sample_answer_guidelines,
        output_contract,
    ]
    return "\n\n".join(part.strip("\n") for part in parts if part).strip()


def format_evaluator_question(question_data: Any) -> str:
    """Convert supported question payloads into prompt text for transcript evaluation."""
    if isinstance(question_data, list):
        parts = []
        for item in question_data:
            if isinstance(item, dict):
                role = item.get("role", "")
                content = item.get("content", "")
                if role == "Image":
                    continue
                if role and content:
                    parts.append(f"{role}: {content}")
                elif content:
                    parts.append(content)
            else:
                parts.append(str(item))
        return "\n".join(parts) if parts else ""

    return convert_question_to_string(question_data)


def standard_evaluator_prompt(
    *,
    exercise_key: str,
    sprint_question_label: str,
    instruction: Optional[str] = None,
    question_formatter: QuestionFormatter = format_evaluator_question,
) -> EvaluatorPromptFactory:
    """Create the standard evaluator user-prompt factory for an exercise."""

    def build(
        *,
        question_data: Any,
        transcription: str,
        technique_name: Optional[str] = None,
    ) -> str:
        question_text = question_formatter(question_data)
        prompt_parts = [
            f"**Exercise Type:** {exercise_key}",
            *(
                [f"**Assigned Technique:** {technique_name}"]
                if technique_name else []
            ),
            f"**{sprint_question_label}:** {question_text}",
            f"**User's Response Transcript:** {transcription.strip()}",
        ]

        if instruction:
            prompt_parts.extend(["", instruction.strip()])

        return "\n".join(prompt_parts)

    return build
