"""Typed exercise prompt specs."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Optional, Protocol

from pydantic import BaseModel

GeneratorPromptFactory = Callable[[], str]
TechniquePicker = Callable[[], Optional[dict[str, Any]]]
FallbackResponseFactory = Callable[[], dict[str, Any]]
ResponseSchema = type[BaseModel]


class EvaluatorPromptFactory(Protocol):
    def __call__(
        self,
        *,
        question_data: Any,
        transcription: str,
        technique_name: Optional[str] = None,
    ) -> str:
        ...


@dataclass(frozen=True)
class ExerciseSpec:
    """Everything the generator and evaluator need for one exercise."""

    key: str
    description: str
    sprint_question_label: str
    generator_system: str
    generator_prompt: GeneratorPromptFactory
    generator_response_schema: ResponseSchema
    evaluator_system: str
    evaluator_prompt: EvaluatorPromptFactory
    evaluator_response_schema: ResponseSchema
    evaluator_fallback: FallbackResponseFactory
    technique_picker: Optional[TechniquePicker] = None
