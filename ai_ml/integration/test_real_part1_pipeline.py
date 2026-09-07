import json
from pathlib import Path

from fastapi.testclient import TestClient

from ai_ml.integration.part1_to_part2 import build_interview_context
from backend.main import app
from backend.session_store import session_store

client = TestClient(app)

PROFILE_PATH = (
    Path(__file__).parent
    / "sample_part1_output"
    / "candidate_profile.json"
)


def load_candidate_profile():
    assert PROFILE_PATH.exists(), (
        f"Missing Part 1 output: {PROFILE_PATH}"
    )

    with open(PROFILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def sample_retrieval_results():
    """
    Temporary replacement until we directly call Part 1 Hybrid-RAG.
    Uses realistic retrieved resume snippets.
    """

    return [
        {
            "id": 1,
            "score": 0.94,
            "text": "Candidate built an NLP fake-news classification system using BERT.",
        },
        {
            "id": 2,
            "score": 0.91,
            "text": "Candidate has Python, TensorFlow, PyTorch and scikit-learn experience.",
        },
        {
            "id": 3,
            "score": 0.87,
            "text": "Projects include recommendation systems and speech emotion recognition.",
        },
    ]


def setup_function():
    session_store.clear()


def test_real_part1_candidate_profile_to_part2():
    candidate_profile = load_candidate_profile()

    context = build_interview_context(
        candidate_profile=candidate_profile,
        retrieval_results=sample_retrieval_results(),
        topic="Machine Learning",
        difficulty="medium",
        total_questions=2,
        job_role="Machine Learning Engineer",
        company_context="Recommendation Systems Company",
    )

    assert context.resume_context is not None
    assert len(context.resume_context) > 100

    response = client.post(
        "/interview/start",
        json={
            "session_id": "real_part1_profile_test",
            "topic": context.topic,
            "difficulty": context.difficulty,
            "total_questions": context.total_questions,
            "resume_context": context.resume_context,
            "job_role": context.job_role,
            "company_context": context.company_context,
            "retrieved_context": context.retrieved_context,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "started"
    assert data["question"]
    assert data["topic"] == "Machine Learning"


def test_real_part1_profile_full_interview():
    candidate_profile = load_candidate_profile()

    context = build_interview_context(
        candidate_profile=candidate_profile,
        retrieval_results=sample_retrieval_results(),
        topic="Machine Learning",
        difficulty="medium",
        total_questions=2,
        job_role="Machine Learning Engineer",
        company_context="Recommendation Systems Company",
    )

    session_id = "real_part1_full_flow"

    start = client.post(
        "/interview/start",
        json={
            "session_id": session_id,
            "topic": context.topic,
            "difficulty": context.difficulty,
            "total_questions": context.total_questions,
            "resume_context": context.resume_context,
            "job_role": context.job_role,
            "company_context": context.company_context,
            "retrieved_context": context.retrieved_context,
        },
    )

    assert start.status_code == 200

    first = client.post(
        "/interview/answer",
        json={
            "session_id": session_id,
            "candidate_answer": (
                "Regularization helps reduce overfitting by adding "
                "a penalty term to the loss function."
            ),
        },
    )

    assert first.status_code == 200

    first_data = first.json()

    assert first_data["status"] == "in_progress"
    assert "evaluation" in first_data
    assert "next_question" in first_data

    second = client.post(
        "/interview/answer",
        json={
            "session_id": session_id,
            "candidate_answer": (
                "Cross-validation evaluates model performance across "
                "multiple train-validation splits."
            ),
        },
    )

    assert second.status_code == 200

    second_data = second.json()

    assert second_data["status"] == "completed"
    assert "final_report" in second_data

    analytics = client.get(
        f"/interview/{session_id}/analytics"
    )

    assert analytics.status_code == 200

    analytics_data = analytics.json()

    assert len(analytics_data["question_records"]) == 2