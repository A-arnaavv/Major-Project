from ai_ml.interview_intelligence.question_generator import (
    generate_question,
)
from ai_ml.interview_intelligence.evaluator import (
    evaluate_answer,
)
from ai_ml.interview_intelligence.adaptive_engine import (
    get_next_difficulty,
)
from ai_ml.interview_intelligence.learning_recommender import (
    generate_learning_plan,
)


def test_mock_question_generation():
    question = generate_question(
        topic="Machine Learning",
        difficulty="medium",
        previous_questions=[],
    )

    assert question.topic == "Machine Learning"
    assert question.difficulty == "medium"
    assert question.question
    assert question.subtopic
    assert len(question.expected_concepts) > 0


def test_mock_question_does_not_repeat():
    first = generate_question(
        topic="Machine Learning",
        difficulty="easy",
        previous_questions=[],
    )

    second = generate_question(
        topic="Machine Learning",
        difficulty="easy",
        previous_questions=[
            first.question
        ],
    )

    assert second.question != first.question


def test_mock_empty_answer_scores_zero():
    result = evaluate_answer(
        question="Explain overfitting.",
        candidate_answer="na",
        expected_concepts=[
            "overfitting",
            "generalization",
        ],
        difficulty="easy",
    )

    assert result.overall_score == 0
    assert result.technical_accuracy == 0
    assert result.next_difficulty == "easier"


def test_mock_valid_answer_scores_seven():
    result = evaluate_answer(
        question="Explain overfitting.",
        candidate_answer=(
            "Overfitting happens when a model learns the "
            "training data too closely and does not generalize well."
        ),
        expected_concepts=[
            "training data",
            "generalization",
        ],
        difficulty="easy",
    )

    assert result.overall_score == 7
    assert result.next_difficulty == "same"


def test_adaptive_difficulty():
    assert get_next_difficulty(
        "medium",
        8.5,
    ) == "hard"

    assert get_next_difficulty(
        "medium",
        6,
    ) == "medium"

    assert get_next_difficulty(
        "medium",
        3,
    ) == "easy"


def test_learning_plan_prioritizes_low_scores():
    performance = {
        "Regularization": 7.0,
        "Bias-Variance Tradeoff": 2.0,
        "Classification Metrics": 5.0,
    }

    plan = generate_learning_plan(
        performance
    )

    assert len(plan) == 3

    assert (
        plan[0]["subtopic"]
        == "Bias-Variance Tradeoff"
    )

    assert (
        plan[0]["performance_level"]
        == "Critical"
    )