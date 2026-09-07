from ai_ml.interview_intelligence.agents.interviewer_agent import (
    InterviewerAgent
)
from ai_ml.interview_intelligence.agents.evaluator_agent import (
    EvaluatorAgent
)
from ai_ml.interview_intelligence.agents.recommendation_agent import (
    RecommendationAgent
)


class InterviewOrchestrator:

    def __init__(self):
        self.interviewer = InterviewerAgent()
        self.evaluator = EvaluatorAgent()
        self.recommender = RecommendationAgent()

    def generate_learning_plan(
        self,
        subtopic_performance
    ):
        return self.recommender.generate_recommendations(
            subtopic_performance
        )