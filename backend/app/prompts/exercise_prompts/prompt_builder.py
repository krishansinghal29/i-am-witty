"""Shared helpers for exercise prompt component assembly."""

from __future__ import annotations

def build_system_prompts(
    prompt_components: dict[str, dict[str, str]],
    prompt_sequences: dict[str, list[str]],
) -> dict[str, str]:
    """Build concrete system prompts from component references."""
    system_prompts: dict[str, str] = {}

    for prompt_type, sequence in prompt_sequences.items():
        parts: list[str] = []
        for component_ref in sequence:
            scope, component_key = component_ref.split(".", 1)
            component_text = prompt_components.get(scope, {}).get(component_key)
            if component_text is None:
                raise ValueError(
                    f"Missing prompt component '{component_ref}' "
                    f"for prompt type '{prompt_type}'"
                )
            parts.append(component_text.strip("\n"))

        system_prompts[prompt_type] = "\n\n".join(parts).strip()

    return system_prompts
