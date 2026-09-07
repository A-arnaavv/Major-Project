from ai_ml.interview_intelligence.integration_schemas import (
    InterviewContext,
    QuestionAnalyticsRecord,
    InterviewSummaryAnalytics,
)


def test_interview_context():
    context = InterviewContext(
        topic="Machine Learning",
        job_role="ML Engineer",
        resume_context="Python and NLP experience",
    )

    assert context.topic == "Machine Learning"
    assert context.difficulty == "medium"
    assert context.total_questions == 5
    assert context.job_role == "ML Engineer"


def test_question_analytics_record():
    record = QuestionAnalyticsRecord(
        session_id="candidate_001",
        question_number=1,
        topic="Machine Learning",
        subtopic="Regularization",
        difficulty="medium",
        question="What is regularization?",
        candidate_answer="It helps reduce overfitting.",
        technical_accuracy=7,
        relevance=8,
        clarity=7,
        completeness=6,
        overall_score=7.0,
        strengths=["Relevant answer"],
        weaknesses=["Needs more detail"],
        feedback="Explain L1 and L2 regularization.",
        improved_answer="Regularization adds a penalty term...",
        next_difficulty="medium",
    )

    assert record.session_id == "candidate_001"
    assert record.overall_score == 7.0
    assert record.subtopic == "Regularization"


def test_interview_summary_analytics():
    summary = InterviewSummaryAnalytics(
        session_id="candidate_001",
        total_questions=2,
        average_score=6.5,
        average_technical_accuracy=6.0,
        average_relevance=7.0,
        average_clarity=6.5,
        average_completeness=6.0,
        subtopic_performance={
            "Regularization": 6.0,
            "Model Evaluation": 7.0,
        },
        overall_performance="Good",
        strong_areas=["Model Evaluation"],
        weak_areas=["Regularization"],
        recommended_topics=["L1 and L2 regularization"],
        learning_plan=[
            {
                "priority": 1,
                "subtopic": "Regularization",
                "current_score": 6.0,
                "performance_level": "Moderate",
                "recommended_action": (
                    "Review key concepts and practice medium-level questions."
                ),
            }
        ],
    )

    assert summary.total_questions == 2
    assert summary.overall_performance == "Good"
    assert len(summary.learning_plan) == 1