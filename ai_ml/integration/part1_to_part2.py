import json
from typing import Any

from ai_ml.interview_intelligence.integration_schemas import InterviewContext


def build_resume_context(candidate_profile: dict[str, Any]) -> str:
    """
    Convert AI/ML Part 1's structured candidate profile into
    a text representation that Part 2 can safely consume.

    Part 1 remains responsible for resume analysis.
    Part 2 only consumes the resulting profile.
    """

    if not candidate_profile:
        return ""

    return json.dumps(
        candidate_profile,
        ensure_ascii=False,
        indent=2,
    )


def build_retrieved_context(
    retrieval_results: list[dict[str, Any]] | None,
) -> str:
    """
    Convert Part 1 Hybrid-RAG retrieval results into the
    retrieved_context string expected by Part 2.

    Expected Part 1 result shape:
    {
        "id": ...,
        "score": ...,
        "text": "..."
    }
    """

    if not retrieval_results:
        return ""

    chunks = []

    for result in retrieval_results:
        text = result.get("text")

        if isinstance(text, str) and text.strip():
            chunks.append(text.strip())

    return "\n\n".join(chunks)


def build_interview_context(
    *,
    candidate_profile: dict[str, Any],
    retrieval_results: list[dict[str, Any]] | None,
    topic: str,
    difficulty: str = "medium",
    total_questions: int = 5,
    job_role: str | None = None,
    company_context: str | None = None,
) -> InterviewContext:
    """
    Adapter from AI/ML Part 1 outputs to the Part 2
    InterviewContext contract.
    """

    resume_context = build_resume_context(candidate_profile)

    retrieved_context = build_retrieved_context(
        retrieval_results
    )

    return InterviewContext(
        topic=topic,
        difficulty=difficulty,
        total_questions=total_questions,
        resume_context=resume_context or None,
        job_role=job_role,
        company_context=company_context,
        retrieved_context=retrieved_context or None,
    )