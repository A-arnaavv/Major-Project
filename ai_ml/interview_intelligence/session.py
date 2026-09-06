from ai_ml.interview_intelligence.tests.test_interview_flow import evaluation
from typing import List, Dict, Any

from ai_ml.interview_intelligence.evaluator import evaluate_answer
from ai_ml.interview_intelligence.adaptive_engine import get_next_difficulty
from ai_ml.interview_intelligence.question_generator import generate_question
from ai_ml.interview_intelligence.report_generator import (
    generate_final_report
)
from ai_ml.interview_intelligence.performance_summary import (
    generate_performance_summary
)

class InterviewSession:
    def __init__(
        self,
        topic: str,
        difficulty: str = "medium",
        total_questions: int = 5
    ):
        self.topic = topic
        self.current_difficulty = difficulty
        self.total_questions = total_questions
        self.question_number = 0
        self.history: List[Dict[str, Any]] = []
        self.current_question = None
    
    def generate_next_question(self):
        if self.is_complete():
            raise ValueError("Interview is already complete.")

        previous_questions = [
            item["question"]
            for item in self.history
        ]

        generated = generate_question(
            topic=self.topic,
            difficulty=self.current_difficulty,
            previous_questions=previous_questions
        )

        self.current_question = generated

        return generated

    def submit_answer(
        self,
        candidate_answer: str
    ):
        if self.current_question is None:
            raise ValueError(
                "No active question. Generate a question first."
            )

        self.question_number += 1

        question = self.current_question.question
        expected_concepts = self.current_question.expected_concepts

        concepts_text = ", ".join(expected_concepts)

        evaluation = evaluate_answer(
            question=question,
            candidate_answer=candidate_answer,
            expected_concepts=concepts_text,
            difficulty=self.current_difficulty
        )

        next_difficulty = get_next_difficulty(
            current_difficulty=self.current_difficulty,
            overall_score=evaluation.overall_score
        )

        record = {
            "question_number": self.question_number,
            "question": question,
            "candidate_answer": candidate_answer,
            "difficulty": self.current_difficulty,
            "topic": self.current_question.topic,
            "expected_concepts": expected_concepts,
            "evaluation": evaluation.model_dump(),
            "next_difficulty": next_difficulty
        }

        self.history.append(record)

        self.current_difficulty = next_difficulty

        # Question has now been answered.
        self.current_question = None

        return record

    def get_history(self):
        return self.history
    
    def get_final_report(self):
        return generate_final_report(self.history)

    def get_ai_performance_summary(self):
        return generate_performance_summary(self.history)

    def is_complete(self) -> bool:
        return self.question_number >= self.total_questions