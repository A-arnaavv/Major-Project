from typing import List

from ai_ml.interview_intelligence.question_generator import (
    generate_question,
    GeneratedQuestion
)


class InterviewerAgent:

    def generate_question(
        self,
        topic: str,
        difficulty: str,
        previous_questions: List[str]
    ) -> GeneratedQuestion:

        return generate_question(
            topic=topic,
            difficulty=difficulty,
            previous_questions=previous_questions
        )