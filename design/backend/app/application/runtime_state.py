from __future__ import annotations

from app.ports.task_runtime_engine import GeneratedTaskPayload


def serialize_runtime_state(
    payload: GeneratedTaskPayload, total_rounds: int = 1
) -> dict:
    """Persistable prompt context for evaluation.

    Stores only what the evaluator needs to re-read the prompt later (messages,
    speech text, assigned technique) — never the generated audio, which is large
    and reproducible.

    Conversational (roleplay) tasks carry their own multi-turn state under the
    ``roleplay`` payload. Non-conversational tasks instead carry a ``rounds``
    block (``{"total", "completed"}``) so a single-shot exercise can be repeated
    ``total_rounds`` times within one attempt; ``total_rounds == 1`` keeps the
    classic single-shot behavior and the client hides the progress bar.
    """
    technique = payload.assigned_technique
    state: dict = {
        "prompt": {
            "messages": [
                {"role": m.role, "content": m.content}
                for m in payload.prompt.messages
            ],
            "speech_text": payload.prompt.speech_text,
        },
        "assigned_technique": (
            {
                "name": technique.name,
                "instruction": technique.instruction,
                "example": technique.example,
            }
            if technique is not None
            else None
        ),
    }
    if payload.roleplay is not None:
        # Roleplay owns the full turn state and its own landed/target progress.
        state.update(payload.roleplay.runtime_state)
    else:
        state["rounds"] = {"total": total_rounds, "completed": 0}
    return state


def rounds_from_state(runtime_state: dict) -> tuple[int, int]:
    """Read ``(completed, total)`` from an attempt's persisted ``rounds`` block.

    Defaults to a single round when the block is missing or malformed, so
    pre-existing single-shot attempts (no ``rounds`` key) finalize on their
    first completion exactly as before.
    """
    rounds = (runtime_state or {}).get("rounds") or {}
    total = rounds.get("total")
    total = total if isinstance(total, int) and total > 0 else 1
    completed = rounds.get("completed")
    completed = completed if isinstance(completed, int) and completed >= 0 else 0
    return completed, total
