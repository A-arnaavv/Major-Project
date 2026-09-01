from ai_ml.interview_intelligence.schemas import EvaluationResult


def evaluate_answer(
    question: str,
    candidate_answer: str,
    expected_concepts: str,
    difficulty: str
) -> EvaluationResult:

    # Mock evaluator for initial development.
    # This will be replaced with an actual LLM call.

    return EvaluationResult(
        technical_accuracy=7,
        relevance=8,
        clarity=8,
        completeness=6,
        overall_score=7.25,
        strengths=[
            "The candidate explained the core concept correctly."
        ],
        weaknesses=[
            "The answer could contain more technical detail."
        ],
        feedback=(
            "The answer is correct and relevant, but it should include "
            "additional technical details and an example."
        ),
        improved_answer=(
            "A stronger answer would define the concept, explain why it "
            "occurs, describe its impact, and provide an example."
        ),
        next_difficulty="harder"
    )