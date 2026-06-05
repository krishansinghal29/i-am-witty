from __future__ import annotations

from app.ports.task_runtime_engine import (
    CompleteTaskRuntimeInput,
    GeneratedPrompt,
    GeneratedTaskPayload,
    GenerateTaskInput,
    PromptMessage,
    TaskRuntimeResult,
)

_SCAFFOLD_KEYS = ("scaffold", "stages", "prompts")


class FakeTaskRuntimeEngine:
    """Deterministic stand-in for an LLM-backed task runtime engine.

    Builds prompts and evaluations purely from the input task/task type so the
    app can be exercised end-to-end without an LLM, network, or SDK.
    """

    async def generate(
        self, input: GenerateTaskInput
    ) -> GeneratedTaskPayload:
        """Build a deterministic prompt payload from the task definition."""
        task = input.task
        prompt = GeneratedPrompt(
            messages=(
                PromptMessage(
                    role="system",
                    content=f"You are running '{task.title}'.",
                ),
                PromptMessage(
                    role="user",
                    content=task.description or task.title,
                ),
            ),
            speech_text=task.title,
        )
        return GeneratedTaskPayload(
            prompt=prompt,
            assigned_technique=None,
            scaffold_stages=self._extract_scaffold_stages(task.content),
            audio_base64=None,
            audio_content_type=None,
            avatar_image_url=None,
        )

    async def complete(
        self, input: CompleteTaskRuntimeInput
    ) -> TaskRuntimeResult:
        """Return deterministic four-section feedback for the transcript."""
        feedback_html = (
            "<section><h3>What Landed</h3>"
            "<p>You showed up and committed to a response.</p></section>"
            "<section><h3>The Trap</h3>"
            "<p>You played it safe instead of taking the risk.</p></section>"
            "<section><h3>Level Up</h3>"
            "<p>Add one specific, vivid detail next time.</p></section>"
            "<section><h3>Mindset Shift</h3>"
            "<p>Wit is a muscle; reps beat perfection.</p></section>"
        )
        sample_answer_html = (
            "<section><h3>Other ways to play it</h3>"
            "<ul><li>Lean into the absurd and escalate.</li>"
            "<li>Undercut with a dry, deadpan callback.</li></ul></section>"
        )
        return TaskRuntimeResult(
            style_label="The Smooth Operator",
            feedback_html=feedback_html,
            sample_answer_html=sample_answer_html,
            completion_metadata={
                "evaluator": "fake",
                "transcript_chars": len(input.transcript),
                "task_type_id": input.task_type.id,
            },
        )

    @staticmethod
    def _extract_scaffold_stages(content: object) -> tuple[dict, ...]:
        """Pull scaffold stages from task content if present, else empty."""
        if not isinstance(content, dict):
            return ()
        for key in _SCAFFOLD_KEYS:
            value = content.get(key)
            if isinstance(value, list):
                return tuple(value)
        return ()
