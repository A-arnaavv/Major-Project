from typing import List

from ai_ml.interview_intelligence.question_generator import (
    generate_question,
    GeneratedQuestion,
)


class InterviewerAgent:

    def generate_question(
        self,
        topic: str,
        difficulty: str,
        previous_questions: List[str],
        resume_context: str | None = None,
        job_role: str | None = None,
        company_context: str | None = None,
        retrieved_context: str | None = None,
    ) -> GeneratedQuestion:

        return generate_question(
            topic=topic,
            difficulty=difficulty,
            previous_questions=previous_questions,
            resume_context=resume_context,
            job_role=job_role,
            company_context=company_context,
            retrieved_context=retrieved_context,
        )