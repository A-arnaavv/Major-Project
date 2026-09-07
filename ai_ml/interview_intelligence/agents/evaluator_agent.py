from ai_ml.interview_intelligence.evaluator import evaluate_answer
from ai_ml.interview_intelligence.schemas import EvaluationResult


class EvaluatorAgent:

    def evaluate(
        self,
        question: str,
        candidate_answer: str,
        expected_concepts: str,
        difficulty: str
    ) -> EvaluationResult:

        return evaluate_answer(
            question=question,
            candidate_answer=candidate_answer,
            expected_concepts=expected_concepts,
            difficulty=difficulty
        )