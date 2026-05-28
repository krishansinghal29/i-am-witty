from pydantic import BaseModel


class EvaluationResult(BaseModel):
    feedback: str
    sample_answer: str
