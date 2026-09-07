from fastapi.testclient import TestClient

from backend.main import app
from backend.session_store import session_store


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