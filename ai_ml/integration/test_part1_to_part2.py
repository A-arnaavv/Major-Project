from ai_ml.integration.part1_to_part2 import build_interview_context
from ai_ml.interview_intelligence.session import InterviewSession
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_build_interview_context_from_part1_outputs():
    candidate_profile = {
        "summary": "Candidate has experience in machine learning and NLP.",
        "technical_skills": [
            "Machine Learning",
            "Natural Language Processing",
        ],
        "programming_languages": [
            "Python",
        ],
        "projects": [
            {
                "name": "Fake News Detection",
                "description": "Built an NLP classification system.",
            }
        ],
        "strengths": [
            "Python",
            "NLP",
        ],
        "improvement_areas": [
            "System design",
        ],
    }

    retrieval_results = [
        {
            "id": 1,
            "score": 0.92,
            "text": "Candidate worked on NLP classification projects.",
        },
        {
            "id": 2,
            "score": 0.84,
            "text": "Candidate has experience with Python and machine learning.",
        },
    ]

    context = build_interview_context(
        candidate_profile=candidate_profile,
        retrieval_results=retrieval_results,
        topic="Machine Learning",
        difficulty="medium",
        total_questions=5,
        job_role="Machine Learning Engineer",
        company_context="Company works on recommendation systems.",
    )

    assert context.topic == "Machine Learning"
    assert context.difficulty == "medium"
    assert context.total_questions == 5

    assert context.resume_context is not None
    assert "Natural Language Processing" in context.resume_context
    assert "Fake News Detection" in context.resume_context

    assert context.retrieved_context is not None
    assert "NLP classification projects" in context.retrieved_context
    assert "Python and machine learning" in context.retrieved_context

    assert context.job_role == "Machine Learning Engineer"
    assert context.company_context == "Company works on recommendation systems."

def test_part1_context_starts_part2_interview():
    candidate_profile = {
        "summary": "Candidate has experience in machine learning and NLP.",
        "technical_skills": [
            "Machine Learning",
            "Natural Language Processing",
        ],
        "programming_languages": [
            "Python",
        ],
        "projects": [
            {
                "name": "Fake News Detection",
                "description": "Built an NLP classification system.",
            }
        ],
        "strengths": [
            "Python",
            "NLP",
        ],
        "improvement_areas": [
            "System design",
        ],
    }

    retrieval_results = [
        {
            "id": 1,
            "score": 0.92,
            "text": "Candidate worked on NLP classification projects.",
        },
        {
            "id": 2,
            "score": 0.84,
            "text": "Candidate has experience with Python and machine learning.",
        },
    ]

    context = build_interview_context(
        candidate_profile=candidate_profile,
        retrieval_results=retrieval_results,
        topic="Machine Learning",
        difficulty="medium",
        total_questions=2,
        job_role="Machine Learning Engineer",
        company_context="Company works on recommendation systems.",
    )

    session = InterviewSession(
        topic=context.topic,
        difficulty=context.difficulty,
        total_questions=context.total_questions,
        resume_context=context.resume_context,
        job_role=context.job_role,
        company_context=context.company_context,
        retrieved_context=context.retrieved_context,
    )

    question = session.generate_next_question()

    assert question is not None
    assert question.question
    assert question.topic == "Machine Learning"
    assert question.difficulty == "medium"

    assert session.resume_context is not None
    assert "Natural Language Processing" in session.resume_context

    assert session.retrieved_context is not None
    assert "NLP classification projects" in session.retrieved_context

def test_part1_context_starts_interview_through_api():
    candidate_profile = {
        "summary": "Candidate has experience in machine learning and NLP.",
        "technical_skills": [
            "Machine Learning",
            "Natural Language Processing",
        ],
        "programming_languages": [
            "Python",
        ],
        "projects": [
            {
                "name": "Fake News Detection",
                "description": "Built an NLP classification system.",
            }
        ],
        "strengths": [
            "Python",
            "NLP",
        ],
        "improvement_areas": [
            "System design",
        ],
    }

    retrieval_results = [
        {
            "id": 1,
            "score": 0.92,
            "text": "Candidate worked on NLP classification projects.",
        },
        {
            "id": 2,
            "score": 0.84,
            "text": "Candidate has experience with Python and machine learning.",
        },
    ]

    context = build_interview_context(
        candidate_profile=candidate_profile,
        retrieval_results=retrieval_results,
        topic="Machine Learning",
        difficulty="medium",
        total_questions=2,
        job_role="Machine Learning Engineer",
        company_context="Company works on recommendation systems.",
    )

    response = client.post(
        "/interview/start",
        json={
            "session_id": "part1_part2_api_test",
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

    assert data["session_id"] == "part1_part2_api_test"
    assert data["status"] == "started"
    assert data["question"]
    assert data["topic"] == "Machine Learning"
    assert data["difficulty"] == "medium"

def test_part1_to_part2_full_api_flow():
    candidate_profile = {
        "summary": "Candidate has experience in machine learning and NLP.",
        "technical_skills": [
            "Machine Learning",
            "Natural Language Processing",
        ],
        "programming_languages": [
            "Python",
        ],
        "projects": [
            {
                "name": "Fake News Detection",
                "description": "Built an NLP classification system.",
            }
        ],
        "strengths": [
            "Python",
            "NLP",
        ],
        "improvement_areas": [
            "System design",
        ],
    }

    retrieval_results = [
        {
            "id": 1,
            "score": 0.92,
            "text": "Candidate worked on NLP classification projects.",
        },
        {
            "id": 2,
            "score": 0.84,
            "text": "Candidate has experience with Python and machine learning.",
        },
    ]

    context = build_interview_context(
        candidate_profile=candidate_profile,
        retrieval_results=retrieval_results,
        topic="Machine Learning",
        difficulty="medium",
        total_questions=2,
        job_role="Machine Learning Engineer",
        company_context="Company works on recommendation systems.",
    )

    session_id = "part1_part2_full_flow"

    start_response = client.post(
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

    assert start_response.status_code == 200

    start_data = start_response.json()

    assert start_data["session_id"] == session_id
    assert start_data["status"] == "started"
    assert start_data["question"]

    first_answer_response = client.post(
        "/interview/answer",
        json={
            "session_id": session_id,
            "candidate_answer": (
                "Regularization helps reduce overfitting by adding "
                "a penalty to the model objective."
            ),
        },
    )

    assert first_answer_response.status_code == 200

    first_answer_data = first_answer_response.json()

    assert first_answer_data["session_id"] == session_id
    assert "evaluation" in first_answer_data
    assert "next_question" in first_answer_data
    assert first_answer_data["next_question"]

    second_answer_response = client.post(
        "/interview/answer",
        json={
            "session_id": session_id,
            "candidate_answer": (
                "Cross validation evaluates model performance across "
                "multiple train-validation splits."
            ),
        },
    )

    assert second_answer_response.status_code == 200

    second_answer_data = second_answer_response.json()

    assert second_answer_data["session_id"] == session_id
    assert "evaluation" in second_answer_data
    assert "final_report" in second_answer_data

    report_response = client.get(
        f"/interview/{session_id}/report"
    )

    assert report_response.status_code == 200

    report_data = report_response.json()

    assert "numerical_report" in report_data
    assert "ai_summary" in report_data
    assert "learning_plan" in report_data

    analytics_response = client.get(
        f"/interview/{session_id}/analytics"
    )

    assert analytics_response.status_code == 200

    analytics_data = analytics_response.json()

    assert analytics_data["session_id"] == session_id
    assert len(analytics_data["question_records"]) == 2
    assert "summary" in analytics_data