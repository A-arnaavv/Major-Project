from ai_ml.interview_intelligence.question_generator import generate_question


def test_generate_question_returns_structured_question():
    question = generate_question(
        topic="Machine Learning",
        difficulty="medium",
        previous_questions=[
            "What is overfitting in machine learning?"
        ],
    )

    assert question is not None
    assert question.question.strip()
    assert question.topic == "Machine Learning"
    assert question.difficulty == "medium"
