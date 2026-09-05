from typing import List, Literal

from pydantic import BaseModel, Field


class EvaluationResult(BaseModel):
    technical_accuracy: int = Field(ge=0, le=10)
    relevance: int = Field(ge=0, le=10)
    clarity: int = Field(ge=0, le=10)
    completeness: int = Field(ge=0, le=10)

    overall_score: float = Field(ge=0, le=10)

    strengths: List[str]
    weaknesses: List[str]

    feedback: str
    improved_answer: str

    next_difficulty: Literal[
        "easier",
        "same",
        "harder"
    ]