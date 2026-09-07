from typing import List

from ai_ml.interview_intelligence.integration_schemas import (
    QuestionAnalyticsRecord,
    InterviewSummaryAnalytics,
)


def export_question_records(
    session_id: str,
    history: list[dict],
) -> List[QuestionAnalyticsRecord]:
    records = []

    for item in history:
        evaluation = item["evaluation"]

        records.append(
            QuestionAnalyticsRecord(
                session_id=session_id,
                question_number=item["question_number"],
                topic=item["topic"],
                subtopic=item["subtopic"],
                difficulty=item["difficulty"],
                question=item["question"],
                candidate_answer=item["candidate_answer"],
                technical_accuracy=evaluation["technical_accuracy"],
                relevance=evaluation["relevance"],
                clarity=evaluation["clarity"],
                completeness=evaluation["completeness"],
                overall_score=evaluation["overall_score"],
                strengths=evaluation["strengths"],
                weaknesses=evaluation["weaknesses"],
                feedback=evaluation["feedback"],
                improved_answer=evaluation["improved_answer"],
                next_difficulty=item["next_difficulty"],
            )
        )

    return records


def export_interview_summary(
    session_id: str,
    numerical_report: dict,
    ai_summary,
    learning_plan: list[dict],
) -> InterviewSummaryAnalytics:
    return InterviewSummaryAnalytics(
        session_id=session_id,
        total_questions=numerical_report["total_questions"],
        average_score=numerical_report["average_score"],
        average_technical_accuracy=numerical_report["average_technical_accuracy"],
        average_relevance=numerical_report["average_relevance"],
        average_clarity=numerical_report["average_clarity"],
        average_completeness=numerical_report["average_completeness"],
        subtopic_performance=numerical_report["subtopic_performance"],
        overall_performance=ai_summary.overall_performance,
        strong_areas=ai_summary.strong_areas,
        weak_areas=ai_summary.weak_areas,
        recommended_topics=ai_summary.recommended_topics,
        learning_plan=learning_plan,
    )