from typing import List

from google import genai
from pydantic import BaseModel

from ai_ml.interview_intelligence.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    is_mock_mode,
)
from ai_ml.interview_intelligence.gemini_utils import (
    call_gemini_with_retry,
)

class PerformanceSummary(BaseModel):
    overall_performance: str
    strong_areas: List[str]
    weak_areas: List[str]
    recommended_topics: List[str]
    final_feedback: str


def generate_performance_summary(
    history: list
) -> PerformanceSummary:

    # -------------------------------------------------
    # MOCK MODE
    # -------------------------------------------------
    if is_mock_mode():

        if not history:
            return PerformanceSummary(
                overall_performance="No Data",
                strong_areas=[],
                weak_areas=[],
                recommended_topics=[],
                final_feedback=(
                    "No interview responses were recorded."
                ),
            )

        scores = [
            record["evaluation"]["overall_score"]
            for record in history
        ]

        average_score = sum(scores) / len(scores)

        subtopics = []

        for record in history:
            subtopic = record.get(
                "subtopic",
                "General"
            )

            if subtopic not in subtopics:
                subtopics.append(subtopic)

        if average_score >= 8:
            overall_performance = "Excellent"

            strong_areas = [
                "Strong technical understanding",
                "Consistent interview performance",
            ]

            weak_areas = []

            final_feedback = (
                "The candidate demonstrated strong technical "
                "understanding. Continue practicing advanced "
                "questions and deeper technical scenarios."
            )

        elif average_score >= 6:
            overall_performance = "Good"

            strong_areas = [
                "Good understanding of the interview topics"
            ]

            weak_areas = [
                "Some answers could include more technical depth"
            ]

            final_feedback = (
                "The candidate demonstrated a good foundation. "
                "Continue improving technical depth, examples, "
                "and explanation clarity."
            )

        elif average_score >= 4:
            overall_performance = "Needs Improvement"

            strong_areas = [
                "Attempted the technical questions"
            ]

            weak_areas = [
                "Technical understanding requires improvement",
                "Answers need more depth and completeness",
            ]

            final_feedback = (
                "The candidate should revisit core concepts "
                "and practice explaining technical ideas using "
                "clear examples."
            )

        else:
            overall_performance = (
                "Needs Significant Improvement"
            )

            strong_areas = []

            weak_areas = [
                "Lack of sufficient technical detail",
                "Core concepts require further practice",
            ]

            final_feedback = (
                "The candidate should focus on foundational "
                "technical concepts before attempting more "
                "advanced interview questions."
            )

        return PerformanceSummary(
            overall_performance=overall_performance,
            strong_areas=strong_areas,
            weak_areas=weak_areas,
            recommended_topics=subtopics,
            final_feedback=final_feedback,
        )

    # -------------------------------------------------
    # REAL GEMINI MODE
    # -------------------------------------------------

    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY not found. Add it to your .env file."
        )

    if not GEMINI_MODEL:
        raise ValueError(
            "GEMINI_MODEL not found. Add it to your .env file."
        )

    client = genai.Client(
        api_key=GEMINI_API_KEY
    )

    interview_data = []

    for record in history:
        evaluation = record["evaluation"]

        interview_data.append({
            "question": record["question"],
            "topic": record.get(
                "topic",
                "General"
            ),
            "subtopic": record.get(
                "subtopic",
                "General"
            ),
            "difficulty": record["difficulty"],
            "score": evaluation["overall_score"],
            "technical_accuracy": (
                evaluation["technical_accuracy"]
            ),
            "strengths": evaluation["strengths"],
            "weaknesses": evaluation["weaknesses"],
        })

    prompt = f"""
You are an expert technical interview coach.

Analyze the following completed interview:

{interview_data}

Generate a concise final performance summary.

Requirements:

1. Overall performance
   Use a short label such as:
   - Excellent
   - Good
   - Needs Improvement
   - Needs Significant Improvement

2. Strong areas
   Identify technical areas where the candidate performed well.

3. Weak areas
   Identify recurring technical weaknesses.
   Avoid unnecessary duplication.

4. Recommended topics
   Recommend specific technical concepts or subtopics that
   the candidate should study next.

5. Final feedback
   Give concise and constructive advice for improving future
   technical interview performance.

Base the recommendations on the actual interview results.
"""

    interaction = call_gemini_with_retry(
        lambda: client.interactions.create(
            model=GEMINI_MODEL,
            input=prompt,
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": PerformanceSummary.model_json_schema(),
            },
        ),
        operation_name="Performance summary",
    )

    try:
        return PerformanceSummary.model_validate_json(
            interaction.output_text
        )

    except Exception as exc:
        raise RuntimeError(
            "Gemini returned an invalid performance summary."
        ) from exc