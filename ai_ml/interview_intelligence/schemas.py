from pydantic import BaseModel
from typing import List


class EvaluationResult(BaseModel):
    technical_accuracy: int
    relevance: int
    clarity: int
    completeness: int
    overall_score: float

    strengths: List[str]
    weaknesses: List[str]

    feedback: str
    improved_answer: str
    next_difficulty: str