from fastapi.testclient import TestClient

from backend.main import app
from backend.session_store import session_store
from unittest.mock import patch
from ai_ml.interview_intelligence.integration_schemas import InterviewContext

client = TestClient(app)


def setup_function():
    """
    Clear in-memory sessions before every test so tests
    do not interfere with one another.
    """
    session_store.clear()


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "running"
    assert data["service"] == "Interview Intelligence API"


def test_start_interview():
    response = client.post(
        "/interview/start",
        json={
            "session_id": "test_candidate_001",
            "topic": "Machine Learning",
            "difficulty": "medium",
            "total_questions": 2,
            "resume_context": "Python and NLP experience",
            "job_role": "ML Engineer",
            "company_context": "Recommendation systems",
            "retrieved_context": "Embeddings and ranking models",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["session_id"] == "test_candidate_001"
    assert data["status"] == "started"
    assert data["question"]
    assert data["difficulty"] == "medium"
    assert data["topic"] == "Machine Learning"
    assert data["subtopic"]


def test_duplicate_session_rejected():
    payload = {
        "session_id": "duplicate_session",
        "topic": "Machine Learning",
        "difficulty": "medium",
        "total_questions": 1,
    }

    first_response = client.post(
        "/interview/start",
        json=payload,
    )

    second_response = client.post(
        "/interview/start",
        json=payload,
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Session already exists"


def test_submit_answer():
    client.post(
        "/interview/start",
        json={
            "session_id": "answer_test",
            "topic": "Machine Learning",
            "difficulty": "medium",
            "total_questions": 2,
        },
    )

    response = client.post(
        "/interview/answer",
        json={
            "session_id": "answer_test",
            "candidate_answer": "na",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["session_id"] == "answer_test"
    assert data["status"] == "in_progress"

    assert data["evaluation"]["overall_score"] == 0
    assert data["next_difficulty"] == "easy"

    assert "next_question" in data
    assert data["next_question"]["question"]
    assert data["next_question"]["difficulty"] == "easy"


def test_complete_interview():
    client.post(
        "/interview/start",
        json={
            "session_id": "complete_test",
            "topic": "Machine Learning",
            "difficulty": "medium",
            "total_questions": 1,
        },
    )

    response = client.post(
        "/interview/answer",
        json={
            "session_id": "complete_test",
            "candidate_answer": "na",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "completed"
    assert data["evaluation"]["overall_score"] == 0

    assert "final_report" in data
    assert "numerical_report" in data["final_report"]
    assert "ai_summary" in data["final_report"]
    assert "learning_plan" in data["final_report"]

    assert (
        data["final_report"]["numerical_report"]["total_questions"]
        == 1
    )


def test_missing_session_on_answer():
    response = client.post(
        "/interview/answer",
        json={
            "session_id": "does_not_exist",
            "candidate_answer": "Test answer",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"


def test_get_report():
    client.post(
        "/interview/start",
        json={
            "session_id": "report_test",
            "topic": "Machine Learning",
            "difficulty": "medium",
            "total_questions": 1,
        },
    )

    client.post(
        "/interview/answer",
        json={
            "session_id": "report_test",
            "candidate_answer": "na",
        },
    )

    response = client.get(
        "/interview/report_test/report"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["session_id"] == "report_test"

    assert "numerical_report" in data
    assert "ai_summary" in data
    assert "learning_plan" in data

    assert data["numerical_report"]["total_questions"] == 1


def test_analytics_endpoint():
    client.post(
        "/interview/start",
        json={
            "session_id": "analytics_test",
            "topic": "Machine Learning",
            "difficulty": "medium",
            "total_questions": 1,
        },
    )

    client.post(
        "/interview/answer",
        json={
            "session_id": "analytics_test",
            "candidate_answer": "na",
        },
    )

    response = client.get(
        "/interview/analytics_test/analytics"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["session_id"] == "analytics_test"

    assert "question_records" in data
    assert "summary" in data

    assert len(data["question_records"]) == 1

    record = data["question_records"][0]

    assert record["session_id"] == "analytics_test"
    assert record["question_number"] == 1
    assert record["overall_score"] == 0

    summary = data["summary"]

    assert summary["session_id"] == "analytics_test"
    assert summary["total_questions"] == 1
    assert summary["average_score"] == 0
    assert len(summary["learning_plan"]) >= 1


def test_missing_analytics_session():
    response = client.get(
        "/interview/missing_session/analytics"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"


def test_invalid_difficulty_rejected():
    response = client.post(
        "/interview/start",
        json={
            "session_id": "invalid_difficulty",
            "topic": "Machine Learning",
            "difficulty": "expert",
            "total_questions": 1,
        },
    )

    assert response.status_code == 422


def test_zero_questions_rejected():
    response = client.post(
        "/interview/start",
        json={
            "session_id": "zero_questions",
            "topic": "Machine Learning",
            "difficulty": "medium",
            "total_questions": 0,
        },
    )

    assert response.status_code == 422


def test_too_many_questions_rejected():
    response = client.post(
        "/interview/start",
        json={
            "session_id": "too_many_questions",
            "topic": "Machine Learning",
            "difficulty": "medium",
            "total_questions": 21,
        },
    )

    assert response.status_code == 422


def test_empty_topic_rejected():
    response = client.post(
        "/interview/start",
        json={
            "session_id": "empty_topic",
            "topic": "",
            "difficulty": "medium",
            "total_questions": 1,
        },
    )

    assert response.status_code == 422


def test_empty_session_id_rejected():
    response = client.post(
        "/interview/start",
        json={
            "session_id": "",
            "topic": "Machine Learning",
            "difficulty": "medium",
            "total_questions": 1,
        },
    )

    assert response.status_code == 422


def test_next_question_missing_session():
    response = client.get(
        "/interview/missing_session/next"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"


def test_next_question_after_completion():
    client.post(
        "/interview/start",
        json={
            "session_id": "completed_next_test",
            "topic": "Machine Learning",
            "difficulty": "medium",
            "total_questions": 1,
        },
    )

    client.post(
        "/interview/answer",
        json={
            "session_id": "completed_next_test",
            "candidate_answer": "na",
        },
    )

    response = client.get(
        "/interview/completed_next_test/next"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Interview is already complete"


def test_report_missing_session():
    response = client.get(
        "/interview/missing_report/report"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"


def test_answer_missing_candidate_answer():
    response = client.post(
        "/interview/answer",
        json={
            "session_id": "some_session",
        },
    )

    assert response.status_code == 422

def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["service"] == "Interview Intelligence API"
    assert data["version"] == "0.1.0"
    assert data["llm_mode"] in {"mock", "real"}

def test_next_question_returns_existing_pending_question():
    start_response = client.post(
        "/interview/start",
        json={
            "session_id": "next_pending_session",
            "topic": "Machine Learning",
            "difficulty": "medium",
            "total_questions": 2,
        },
    )

    assert start_response.status_code == 200

    first_question = start_response.json()["question"]

    session = session_store.get("next_pending_session")

    assert session is not None
    assert session.current_question is not None

    with patch.object(
        session,
        "generate_next_question",
        side_effect=AssertionError(
            "GET /next should not generate a new question "
            "when one is already pending"
        ),
    ):
        response = client.get(
            "/interview/next_pending_session/next"
        )

    assert response.status_code == 200
    assert response.json()["question"] == first_question


def test_next_question_returns_question_created_after_answer():
    start_response = client.post(
        "/interview/start",
        json={
            "session_id": "next_after_answer_session",
            "topic": "Machine Learning",
            "difficulty": "medium",
            "total_questions": 2,
        },
    )

    assert start_response.status_code == 200

    answer_response = client.post(
        "/interview/answer",
        json={
            "session_id": "next_after_answer_session",
            "candidate_answer": (
                "A meaningful technical answer explaining "
                "the relevant machine learning concept."
            ),
        },
    )

    assert answer_response.status_code == 200
    assert answer_response.json()["status"] == "in_progress"

    expected_next_question = (
        answer_response.json()["next_question"]["question"]
    )

    session = session_store.get("next_after_answer_session")

    assert session is not None
    assert session.current_question is not None

    with patch.object(
        session,
        "generate_next_question",
        side_effect=AssertionError(
            "GET /next should return the question already "
            "generated after answer submission"
        ),
    ):
        response = client.get(
            "/interview/next_after_answer_session/next"
        )

    assert response.status_code == 200
    assert response.json()["question"] == expected_next_question

def test_whitespace_only_session_id_rejected():
    response = client.post(
        "/interview/start",
        json={
            "session_id": "   ",
            "topic": "Machine Learning",
            "difficulty": "medium",
            "total_questions": 2,
        },
    )

    assert response.status_code == 422


def test_whitespace_only_topic_rejected():
    response = client.post(
        "/interview/start",
        json={
            "session_id": "whitespace_topic_session",
            "topic": "   ",
            "difficulty": "medium",
            "total_questions": 2,
        },
    )

    assert response.status_code == 422


def test_start_interview_strips_session_id_and_topic():
    response = client.post(
        "/interview/start",
        json={
            "session_id": "  normalized_session  ",
            "topic": "  Machine Learning  ",
            "difficulty": "medium",
            "total_questions": 2,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["session_id"] == "normalized_session"
    assert data["topic"] == "Machine Learning"

    assert session_store.exists("normalized_session")
    assert not session_store.exists("  normalized_session  ")

def test_start_interview_from_resume(monkeypatch):
    candidate_profile = {
        "name": "Test Candidate",
        "technical_skills": ["Python"],
    }

    context = InterviewContext(
        topic="Python",
        difficulty="medium",
        total_questions=2,
        resume_context='{"name": "Test Candidate"}',
        job_role="Backend Engineer",
        company_context="Example Company",
        retrieved_context="Candidate has Python experience.",
    )

    monkeypatch.setattr(
        "backend.main.process_resume_for_interview",
        lambda **kwargs: (candidate_profile, context),
    )

    response = client.post(
        "/interview/start-from-resume",
        data={
            "session_id": "resume-session",
            "topic": "Python",
            "difficulty": "medium",
            "total_questions": "2",
            "job_role": "Backend Engineer",
            "company_context": "Example Company",
        },
        files={
            "resume": (
                "resume.pdf",
                b"%PDF-1.4 fake resume",
                "application/pdf",
            )
        },
    )
    assert response.status_code == 200

    body = response.json()

    assert body["session_id"] == "resume-session"
    assert body["status"] == "started"
    assert body["candidate_profile"] == candidate_profile
    assert body["topic"] == "Python"
    assert body["difficulty"] == "medium"
    assert "question" in body


def test_start_interview_from_resume_rejects_non_pdf():
    response = client.post(
        "/interview/start-from-resume",
        data={
            "session_id": "bad-resume-session",
            "topic": "Python",
        },
        files={
            "resume": (
                "resume.txt",
                b"not a pdf",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Resume must be a PDF file"


def test_start_interview_from_resume_rejects_duplicate_session(
    monkeypatch,
):
    candidate_profile = {
        "name": "Test Candidate",
    }

    context = InterviewContext(
        topic="Python",
        difficulty="medium",
        total_questions=1,
        resume_context="{}",
    )

    monkeypatch.setattr(
        "backend.main.process_resume_for_interview",
        lambda **kwargs: (candidate_profile, context),
    )

    files = {
        "resume": (
            "resume.pdf",
            b"%PDF-1.4 fake resume",
            "application/pdf",
        )
    }

    data = {
        "session_id": "duplicate-resume-session",
        "topic": "Python",
        "total_questions": "1",
    }

    first = client.post(
        "/interview/start-from-resume",
        data=data,
        files=files,
    )

    assert first.status_code == 200

    second = client.post(
        "/interview/start-from-resume",
        data=data,
        files={
            "resume": (
                "resume.pdf",
                b"%PDF-1.4 fake resume",
                "application/pdf",
            )
        },
    )

    assert second.status_code == 400
    assert second.json()["detail"] == "Session already exists"


def test_start_from_resume_then_answer(monkeypatch):
    candidate_profile = {
        "name": "Test Candidate",
        "technical_skills": ["Python"],
    }

    context = InterviewContext(
        topic="Python",
        difficulty="medium",
        total_questions=2,
        resume_context='{"name": "Test Candidate"}',
        retrieved_context="Python project experience.",
    )

    monkeypatch.setattr(
        "backend.main.process_resume_for_interview",
        lambda **kwargs: (candidate_profile, context),
    )

    start_response = client.post(
        "/interview/start-from-resume",
        data={
            "session_id": "resume-flow-session",
            "topic": "Python",
            "total_questions": "2",
        },
        files={
            "resume": (
                "resume.pdf",
                b"%PDF-1.4 fake resume",
                "application/pdf",
            )
        },
    )

    assert start_response.status_code == 200
    assert start_response.json()["status"] == "started"

    answer_response = client.post(
        "/interview/answer",
        json={
            "session_id": "resume-flow-session",
            "candidate_answer": (
                "Python is a high-level programming language "
                "used for backend systems, automation, and data work."
            ),
        },
    )

    assert answer_response.status_code == 200

    body = answer_response.json()

    assert body["session_id"] == "resume-flow-session"
    assert body["status"] == "in_progress"
    assert "evaluation" in body
    assert "next_question" in body

def test_start_from_resume_rejects_oversized_pdf(
    monkeypatch,
):
    from backend import main

    monkeypatch.setattr(
        main,
        "MAX_RESUME_SIZE_BYTES",
        10,
    )

    response = client.post(
        "/interview/start-from-resume",
        data={
            "session_id": "oversized-resume-test",
            "topic": "Machine Learning",
            "difficulty": "medium",
            "total_questions": "2",
        },
        files={
            "resume": (
                "resume.pdf",
                b"x" * 11,
                "application/pdf",
            )
        },
    )

    assert response.status_code == 413

    assert (
        "exceeds maximum size"
        in response.json()["detail"]
    )

    session_store.delete(
        "oversized-resume-test"
    )


def test_answer_whitespace_session_id_rejected():
    response = client.post(
        "/interview/answer",
        json={
            "session_id": "   ",
            "candidate_answer": "Some answer",
        },
    )

    assert response.status_code == 422