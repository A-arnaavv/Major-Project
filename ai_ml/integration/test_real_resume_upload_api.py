import pytest
from fastapi.testclient import TestClient

from ai_ml.part1.paths import DEFAULT_RESUME_PATH
from backend.main import app
from backend.session_store import session_store


pytestmark = [
    pytest.mark.live_rag,
    pytest.mark.live_gemini,
]

client = TestClient(app)


def test_real_resume_upload_starts_interview():
    assert DEFAULT_RESUME_PATH.exists(), (
        f"Configured resume does not exist: {DEFAULT_RESUME_PATH}"
    )

    session_id = "real-resume-upload-session"

    session_store.delete(session_id)

    try:
        with DEFAULT_RESUME_PATH.open("rb") as resume_file:
            response = client.post(
                "/interview/start-from-resume",
                data={
                    "session_id": session_id,
                    "topic": "Python",
                    "difficulty": "medium",
                    "total_questions": "2",
                    "job_role": "Software Engineer",
                },
                files={
                    "resume": (
                        "resume.pdf",
                        resume_file,
                        "application/pdf",
                    )
                },
            )

        assert response.status_code == 200, response.text

        body = response.json()

        assert body["session_id"] == session_id
        assert body["status"] == "started"
        assert body["candidate_profile"]
        assert body["question"]
        assert body["topic"] == "Python"
        assert body["difficulty"] == "medium"

    finally:
        session_store.delete(session_id)


def test_real_resume_upload_full_interview_flow():
    assert DEFAULT_RESUME_PATH.exists(), (
        f"Configured resume does not exist: {DEFAULT_RESUME_PATH}"
    )

    session_id = "real-resume-full-flow-session"

    session_store.delete(session_id)

    try:
        with DEFAULT_RESUME_PATH.open("rb") as resume_file:
            start_response = client.post(
                "/interview/start-from-resume",
                data={
                    "session_id": session_id,
                    "topic": "Python",
                    "difficulty": "medium",
                    "total_questions": "2",
                    "job_role": "Software Engineer",
                },
                files={
                    "resume": (
                        "resume.pdf",
                        resume_file,
                        "application/pdf",
                    )
                },
            )

        assert start_response.status_code == 200, start_response.text

        start_body = start_response.json()

        assert start_body["session_id"] == session_id
        assert start_body["status"] == "started"
        assert start_body["candidate_profile"]
        assert start_body["question"]
        assert start_body["topic"] == "Python"
        assert start_body["difficulty"] == "medium"

        first_answer = client.post(
            "/interview/answer",
            json={
                "session_id": session_id,
                "candidate_answer": (
                    "Python is a high-level programming language "
                    "that supports object-oriented, functional, "
                    "and procedural programming."
                ),
            },
        )

        assert first_answer.status_code == 200, first_answer.text

        first_body = first_answer.json()

        assert first_body["session_id"] == session_id
        assert first_body["status"] == "in_progress"
        assert "evaluation" in first_body
        assert "next_difficulty" in first_body
        assert "next_question" in first_body

        second_answer = client.post(
            "/interview/answer",
            json={
                "session_id": session_id,
                "candidate_answer": (
                    "I would structure the solution into reusable "
                    "functions, validate inputs, handle exceptions, "
                    "and add tests for important edge cases."
                ),
            },
        )

        assert second_answer.status_code == 200, second_answer.text

        completed_body = second_answer.json()

        assert completed_body["session_id"] == session_id
        assert completed_body["status"] == "completed"
        assert "evaluation" in completed_body
        assert "next_difficulty" in completed_body
        assert "final_report" in completed_body

        final_report = completed_body["final_report"]

        assert "numerical_report" in final_report
        assert "ai_summary" in final_report
        assert "learning_plan" in final_report

        report_response = client.get(
            f"/interview/{session_id}/report"
        )

        assert report_response.status_code == 200, report_response.text

        analytics_response = client.get(
            f"/interview/{session_id}/analytics"
        )

        assert (
            analytics_response.status_code == 200
        ), analytics_response.text

    finally:
        session_store.delete(session_id)