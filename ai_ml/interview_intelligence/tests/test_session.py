from ai_ml.interview_intelligence.session import InterviewSession


def test_session_generates_question():
    session = InterviewSession(
        topic="Machine Learning",
        difficulty="medium",
        total_questions=2,
    )

    question = session.generate_next_question()

    assert question.question
    assert question.topic == "Machine Learning"
    assert question.difficulty == "medium"


def test_session_submit_answer():
    session = InterviewSession(
        topic="Machine Learning",
        difficulty="medium",
        total_questions=2,
    )

    session.generate_next_question()

    result = session.submit_answer(
        candidate_answer="na"
    )

    assert result["question_number"] == 1
    assert result["evaluation"]["overall_score"] == 0
    assert result["next_difficulty"] == "easy"


def test_session_tracks_history():
    session = InterviewSession(
        topic="Machine Learning",
        difficulty="medium",
        total_questions=2,
    )

    session.generate_next_question()
    session.submit_answer(
        candidate_answer="na"
    )

    history = session.get_history()

    assert len(history) == 1
    assert history[0]["question_number"] == 1
    assert "evaluation" in history[0]
    assert "subtopic" in history[0]


def test_session_completion():
    session = InterviewSession(
        topic="Machine Learning",
        difficulty="medium",
        total_questions=1,
    )

    session.generate_next_question()
    session.submit_answer(
        candidate_answer="na"
    )

    assert session.is_complete() is True


def test_session_report():
    session = InterviewSession(
        topic="Machine Learning",
        difficulty="medium",
        total_questions=1,
    )

    session.generate_next_question()
    session.submit_answer(
        candidate_answer="na"
    )

    report = session.get_final_report()

    assert report["total_questions"] == 1
    assert report["average_score"] == 0
    assert "subtopic_performance" in report


def test_session_learning_plan():
    session = InterviewSession(
        topic="Machine Learning",
        difficulty="medium",
        total_questions=1,
    )

    session.generate_next_question()
    session.submit_answer(
        candidate_answer="na"
    )

    plan = session.get_learning_plan()

    assert len(plan) >= 1
    assert plan[0]["performance_level"] == "Critical"