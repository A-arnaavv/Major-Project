from typing import Dict, List, Any

from ai_ml.interview_intelligence.learning_recommender import (
    generate_learning_plan
)


class RecommendationAgent:

    def generate_recommendations(
        self,
        subtopic_performance: Dict[str, float]
    ) -> List[Dict[str, Any]]:

        return generate_learning_plan(
            subtopic_performance
        )