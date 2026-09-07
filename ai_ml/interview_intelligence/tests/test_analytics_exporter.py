from ai_ml.interview_intelligence.session import InterviewSession
from ai_ml.interview_intelligence.analytics_exporter import (
    export_question_records,
    export_interview_summary,
)


def test_export_question_records():
    session = InterviewSession(
        topic="Machine Learning",
        difficulty="medium",
        total_questions=1,
    )

    session.generate_next_question()
    session.submit_answer(
        candidate_answer="na"
    )

    records = export_question_records(
        session_id="candidate_001",
        history=session.get_history(),
    )

    assert len(records) == 1
    assert records[0].session_id == "candidate_001"
    assert records[0].question_number == 1
    assert records[0].overall_score == 0


def test_export_interview_summary():
    session = InterviewSession(
        topic="Machine Learning",
        difficulty="medium",
        total_questions=1,
    )

    session.generate_next_question()
    session.submit_answer(
        candidate_answer="na"
    )

    numerical_report = session.get_final_report()
    ai_summary = session.get_ai_performance_summary()
    learning_plan = session.get_learning_plan()

    summary = export_interview_summary(
        session_id="candidate_001",
        numerical_report=numerical_report,
        ai_summary=ai_summary,
        learning_plan=learning_plan,
    )

    assert summary.session_id == "candidate_001"
    assert summary.total_questions == 1
    assert summary.average_score == 0
    assert len(summary.learning_plan) >= 1