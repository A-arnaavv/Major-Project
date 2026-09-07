from typing import Dict, List

from pydantic import BaseModel, Field


class InterviewContext(BaseModel):
    topic: str
    difficulty: str = "medium"
    total_questions: int = Field(default=5, ge=1)

    resume_context: str | None = None
    job_role: str | None = None
    company_context: str | None = None
    retrieved_context: str | None = None


class QuestionAnalyticsRecord(BaseModel):
    session_id: str
    question_number: int

    topic: str
    subtopic: str
    difficulty: str

    question: str
    candidate_answer: str

    technical_accuracy: float
    relevance: float
    clarity: float
    completeness: float
    overall_score: float

    strengths: List[str]
    weaknesses: List[str]

    feedback: str
    improved_answer: str

    next_difficulty: str


class LearningPlanItem(BaseModel):
    priority: int
    subtopic: str
    current_score: float
    performance_level: str
    recommended_action: str


class InterviewSummaryAnalytics(BaseModel):
    session_id: str

    total_questions: int

    average_score: float
    average_technical_accuracy: float
    average_relevance: float
    average_clarity: float
    average_completeness: float

    subtopic_performance: Dict[str, float]

    overall_performance: str

    strong_areas: List[str]
    weak_areas: List[str]
    recommended_topics: List[str]

    learning_plan: List[LearningPlanItem]