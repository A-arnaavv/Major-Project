from backend.session_store import SessionStore
from ai_ml.interview_intelligence.session import InterviewSession


def test_session_survives_store_restart(
    tmp_path,
):
    storage_dir = tmp_path / "sessions"

    first_store = SessionStore(
        storage_dir=storage_dir
    )

    session = InterviewSession(
        topic="Machine Learning",
        difficulty="medium",
        total_questions=2,
        resume_context="Candidate knows Python.",
        job_role="ML Engineer",
        company_context="AI company",
        retrieved_context=(
            "Candidate built an ML project."
        ),
    )

    question = session.generate_next_question()

    first_store.create(
        "restart-test",
        session,
    )

    first_store.save(
        "restart-test",
        session,
    )

    # Simulate application restart.
    second_store = SessionStore(
        storage_dir=storage_dir
    )

    restored = second_store.get(
        "restart-test"
    )

    assert restored is not None
    assert restored.topic == "Machine Learning"
    assert restored.current_difficulty == "medium"
    assert restored.total_questions == 2
    assert restored.question_number == 0

    assert restored.resume_context == (
        "Candidate knows Python."
    )

    assert restored.job_role == "ML Engineer"
    assert restored.company_context == "AI company"

    assert restored.retrieved_context == (
        "Candidate built an ML project."
    )

    assert restored.current_question is not None

    assert (
        restored.current_question.question
        == question.question
    )

    assert (
        restored.current_question.expected_concepts
        == question.expected_concepts
    )

    assert (
        restored.current_question.subtopic
        == question.subtopic
    )


def test_answer_history_survives_restart(
    tmp_path,
):
    storage_dir = tmp_path / "sessions"

    first_store = SessionStore(
        storage_dir=storage_dir
    )

    session = InterviewSession(
        topic="Machine Learning",
        difficulty="medium",
        total_questions=2,
    )

    session.generate_next_question()

    first_store.create(
        "history-test",
        session,
    )

    result = session.submit_answer(
        "Bias is error from overly simple assumptions, "
        "while variance measures sensitivity to training "
        "data. The tradeoff affects generalization."
    )

    first_store.save(
        "history-test",
        session,
    )

    # Simulate restart.
    second_store = SessionStore(
        storage_dir=storage_dir
    )

    restored = second_store.get(
        "history-test"
    )

    assert restored is not None
    assert restored.question_number == 1
    assert len(restored.history) == 1

    assert (
        restored.history[0]["question"]
        == result["question"]
    )

    assert (
        restored.history[0]["candidate_answer"]
        == result["candidate_answer"]
    )

    assert restored.current_question is None


def test_delete_removes_persistent_session(
    tmp_path,
):
    storage_dir = tmp_path / "sessions"

    store = SessionStore(
        storage_dir=storage_dir
    )

    session = InterviewSession(
        topic="Python"
    )

    store.create(
        "delete-test",
        session,
    )

    assert store.exists(
        "delete-test"
    )

    store.delete(
        "delete-test"
    )

    assert not store.exists(
        "delete-test"
    )

    restarted_store = SessionStore(
        storage_dir=storage_dir
    )

    assert (
        restarted_store.get(
            "delete-test"
        )
        is None
    )