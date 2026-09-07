import pytest

from ai_ml.part1.interview.question_generator import (
    generate_interview_questions,
)


pytestmark = pytest.mark.live_gemini


def test_generate_personalized_interview_questions():
    questions = generate_interview_questions(
        interview_type="technical",
        num_questions=5,
    )

    assert isinstance(questions, str)
    assert questions.strip()

    questions_lower = questions.lower()
    assert any(
        keyword in questions_lower
        for keyword in [
            "machine learning",
            "python",
            "project",
            "technical",
            "experience",
        ]
    )
