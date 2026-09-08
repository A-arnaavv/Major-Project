from typing import Any, Dict, List

from ai_ml.interview_intelligence.adaptive_engine import (
    get_next_difficulty,
)
from ai_ml.interview_intelligence.orchestrator import (
    InterviewOrchestrator,
)
from ai_ml.interview_intelligence.performance_summary import (
    generate_performance_summary,
)
from ai_ml.interview_intelligence.question_generator import (
    GeneratedQuestion,
)
from ai_ml.interview_intelligence.report_generator import (
    generate_final_report,
)


class InterviewSession:
    def __init__(
        self,
        topic: str,
        difficulty: str = "medium",
        total_questions: int = 5,
        resume_context: str | None = None,
        job_role: str | None = None,
        company_context: str | None = None,
        retrieved_context: str | None = None,
    ):
        self.topic = topic
        self.current_difficulty = difficulty
        self.total_questions = total_questions

        self.question_number = 0
        self.history: List[Dict[str, Any]] = []
        self.current_question: GeneratedQuestion | None = None

        self.resume_context = resume_context
        self.job_role = job_role
        self.company_context = company_context
        self.retrieved_context = retrieved_context

        # Runtime object. This is intentionally not persisted.
        self.orchestrator = InterviewOrchestrator()

    def generate_next_question(self):
        if self.is_complete():
            raise ValueError(
                "Interview is already complete."
            )

        previous_questions = [
            record["question"]
            for record in self.history
        ]

        generated = (
            self.orchestrator.interviewer.generate_question(
                topic=self.topic,
                difficulty=self.current_difficulty,
                previous_questions=previous_questions,
                resume_context=self.resume_context,
                job_role=self.job_role,
                company_context=self.company_context,
                retrieved_context=self.retrieved_context,
            )
        )

        self.current_question = generated

        return generated

    def submit_answer(
        self,
        candidate_answer: str,
    ):
        if self.current_question is None:
            raise ValueError(
                "No active question. "
                "Generate a question first."
            )

        self.question_number += 1

        question = self.current_question.question
        expected_concepts = (
            self.current_question.expected_concepts
        )

        concepts_text = ", ".join(
            expected_concepts
        )

        evaluation = (
            self.orchestrator.evaluator.evaluate(
                question=question,
                candidate_answer=candidate_answer,
                expected_concepts=concepts_text,
                difficulty=self.current_difficulty,
            )
        )

        next_difficulty = get_next_difficulty(
            current_difficulty=self.current_difficulty,
            overall_score=evaluation.overall_score,
        )

        record = {
            "question_number": self.question_number,
            "question": question,
            "candidate_answer": candidate_answer,
            "topic": self.current_question.topic,
            "subtopic": self.current_question.subtopic,
            "difficulty": self.current_difficulty,
            "expected_concepts": expected_concepts,
            "evaluation": evaluation.model_dump(),
            "next_difficulty": next_difficulty,
        }

        self.history.append(record)

        self.current_difficulty = next_difficulty

        # The current question has now been answered.
        self.current_question = None

        return record

    def get_history(self):
        return self.history

    def get_final_report(self):
        return generate_final_report(
            self.history
        )

    def get_ai_performance_summary(self):
        return generate_performance_summary(
            self.history
        )

    def is_complete(self) -> bool:
        return (
            self.question_number
            >= self.total_questions
        )

    def get_learning_plan(self):
        report = self.get_final_report()

        return (
            self.orchestrator.generate_learning_plan(
                report["subtopic_performance"]
            )
        )

    def to_state(self) -> Dict[str, Any]:
        """
        Convert the mutable interview state into JSON-safe data.

        Runtime objects such as InterviewOrchestrator and Gemini clients
        are intentionally excluded.
        """

        current_question = None

        if self.current_question is not None:
            current_question = (
                self.current_question.model_dump()
            )

        return {
            "topic": self.topic,
            "current_difficulty": (
                self.current_difficulty
            ),
            "total_questions": self.total_questions,
            "question_number": self.question_number,
            "history": self.history,
            "current_question": current_question,
            "resume_context": self.resume_context,
            "job_role": self.job_role,
            "company_context": (
                self.company_context
            ),
            "retrieved_context": (
                self.retrieved_context
            ),
        }

    @classmethod
    def from_state(
        cls,
        state: Dict[str, Any],
    ) -> "InterviewSession":
        """
        Restore an InterviewSession from persisted JSON state.

        A fresh InterviewOrchestrator is created by __init__.
        """

        session = cls(
            topic=state["topic"],
            difficulty=state.get(
                "current_difficulty",
                "medium",
            ),
            total_questions=state.get(
                "total_questions",
                5,
            ),
            resume_context=state.get(
                "resume_context"
            ),
            job_role=state.get("job_role"),
            company_context=state.get(
                "company_context"
            ),
            retrieved_context=state.get(
                "retrieved_context"
            ),
        )

        session.question_number = state.get(
            "question_number",
            0,
        )

        session.history = state.get(
            "history",
            [],
        )

        current_question = state.get(
            "current_question"
        )

        if current_question is not None:
            session.current_question = (
                GeneratedQuestion.model_validate(
                    current_question
                )
            )

        return session