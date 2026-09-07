import json

from fastapi.testclient import TestClient

from ai_ml.integration.part1_to_part2 import build_interview_context
from ai_ml.part1.paths import CANDIDATE_PROFILE_PATH
from ai_ml.part1.rag.retriever import hybrid_retrieve
from backend.main import app
from backend.session_store import session_store


client = TestClient(app)


def load_candidate_profile():
    assert CANDIDATE_PROFILE_PATH.exists(), (
        f"Missing Part 1 output: {CANDIDATE_PROFILE_PATH}"
    )

    with open(CANDIDATE_PROFILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_real_part1_retrieval_results():
    """
    Run the actual Part 1 Hybrid-RAG pipeline.

    This performs:
    query embedding
    -> dense Milvus retrieval
    -> sparse Milvus retrieval
    -> reciprocal rank fusion
    """

    results = hybrid_retrieve(
        "What machine learning projects and technical skills "
        "does the candidate have?",
        top_k=5,
    )

    assert results
    assert len(results) <= 5

    for result in results:
        assert "id" in result
        assert "score" in result
        assert "text" in result
        assert result["text"]

    return results


def setup_function():
    session_store.clear()


def test_real_part1_rag_to_part2_context():
    candidate_profile = load_candidate_profile()
    retrieval_results = get_real_part1_retrieval_results()

    context = build_interview_context(
        candidate_profile=candidate_profile,
        retrieval_results=retrieval_results,
        topic="Machine Learning",
        difficulty="medium",
        total_questions=2,
        job_role="Machine Learning Engineer",
        company_context="Recommendation Systems Company",
    )

    assert context.resume_context is not None
    assert len(context.resume_context) > 100

    assert context.retrieved_context is not None
    assert len(context.retrieved_context) > 100

    # Make sure actual Part 1 retrieval text reached Part 2.
    assert any(
        result["text"] in context.retrieved_context
        for result in retrieval_results
    )


def test_real_part1_rag_starts_part2_interview():
    candidate_profile = load_candidate_profile()
    retrieval_results = get_real_part1_retrieval_results()

    context = build_interview_context(
        candidate_profile=candidate_profile,
        retrieval_results=retrieval_results,
        topic="Machine Learning",
        difficulty="medium",
        total_questions=2,
        job_role="Machine Learning Engineer",
        company_context="Recommendation Systems Company",
    )

    response = client.post(
        "/interview/start",
        json={
            "session_id": "real_part1_rag_start",
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

    assert data["session_id"] == "real_part1_rag_start"
    assert data["status"] == "started"
    assert data["question"]
    assert data["topic"] == "Machine Learning"


def test_real_part1_rag_full_interview_flow():
    candidate_profile = load_candidate_profile()
    retrieval_results = get_real_part1_retrieval_results()

    context = build_interview_context(
        candidate_profile=candidate_profile,
        retrieval_results=retrieval_results,
        topic="Machine Learning",
        difficulty="medium",
        total_questions=2,
        job_role="Machine Learning Engineer",
        company_context="Recommendation Systems Company",
    )

    session_id = "real_part1_rag_full_flow"

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
    assert start.json()["status"] == "started"

    first = client.post(
        "/interview/answer",
        json={
            "session_id": session_id,
            "candidate_answer": (
                "Regularization reduces overfitting by adding a penalty "
                "to the objective function and discouraging overly "
                "complex model parameters."
            ),
        },
    )

    assert first.status_code == 200

    first_data = first.json()

    assert first_data["status"] == "in_progress"
    assert "evaluation" in first_data
    assert first_data["next_question"]

    second = client.post(
        "/interview/answer",
        json={
            "session_id": session_id,
            "candidate_answer": (
                "Cross-validation estimates generalization performance "
                "by training and validating the model across multiple "
                "different splits of the available dataset."
            ),
        },
    )

    assert second.status_code == 200

    second_data = second.json()

    assert second_data["status"] == "completed"
    assert "evaluation" in second_data
    assert "final_report" in second_data

    report = client.get(
        f"/interview/{session_id}/report"
    )

    assert report.status_code == 200

    report_data = report.json()

    assert "numerical_report" in report_data
    assert "ai_summary" in report_data
    assert "learning_plan" in report_data

    analytics = client.get(
        f"/interview/{session_id}/analytics"
    )

    assert analytics.status_code == 200

    analytics_data = analytics.json()

    assert analytics_data["session_id"] == session_id
    assert len(analytics_data["question_records"]) == 2
    assert "summary" in analytics_data