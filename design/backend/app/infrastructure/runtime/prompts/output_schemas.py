"""Structured output schemas used by prompt specs."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class SheQuestionMessage(BaseModel):
    role: Literal["She"]
    content: str = Field(..., min_length=1)


class TopicQuestionMessage(BaseModel):
    role: Literal["Topic"]
    content: str = Field(..., min_length=1)


class StorytellerQuestionMessage(BaseModel):
    role: Literal["Storyteller"]
    content: str = Field(..., min_length=1)


class QuestionAnswerTeaseMessage(BaseModel):
    role: Literal["You", "She"]
    content: str = Field(..., min_length=1)


class SingleSheQuestion(BaseModel):
    messages: list[SheQuestionMessage] = Field(
        ...,
        min_length=1,
        max_length=1,
        description='Exactly one generated prompt message with role "She".',
    )


class SingleTopicQuestion(BaseModel):
    messages: list[TopicQuestionMessage] = Field(
        ...,
        min_length=1,
        max_length=1,
        description='Exactly one generated topic message with role "Topic".',
    )


class SingleStorytellerQuestion(BaseModel):
    messages: list[StorytellerQuestionMessage] = Field(
        ...,
        min_length=1,
        max_length=1,
        description='Exactly one generated story message with role "Storyteller".',
    )


class QuestionAnswerTeaseQuestion(BaseModel):
    messages: list[QuestionAnswerTeaseMessage] = Field(
        ...,
        min_length=2,
        max_length=2,
        description='Exactly two generated messages in order: first role "You", then role "She".',
    )

    @model_validator(mode="after")
    def validate_message_order(self) -> "QuestionAnswerTeaseQuestion":
        if [message.role for message in self.messages] != ["You", "She"]:
            raise ValueError('QuestionAnswerTease messages must be ordered as "You", then "She"')
        return self


class RenderedCharacter(BaseModel):
    persona: str = Field(
        ...,
        min_length=1,
        description="Who she is: personality, background, interests, what she's looking for, and the scenario woven into a natural description.",
    )
    appearance: str = Field(
        ...,
        min_length=1,
        description="How she looks right now: physical features and what she's wearing.",
    )


class EvaluationResult(BaseModel):
    feedback: str = Field(
        ...,
        min_length=1,
        description="HTML feedback using the exercise's required feedback structure.",
    )
    sample_answer: str = Field(
        ...,
        min_length=1,
        description="Sample answer text formatted according to the exercise instructions.",
    )
