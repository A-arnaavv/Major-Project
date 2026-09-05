from typing import List, Dict, Any

from ai_ml.interview_intelligence.evaluator import evaluate_answer
from ai_ml.interview_intelligence.adaptive_engine import get_next_difficulty
from ai_ml.interview_intelligence.question_generator import generate_question
from ai_ml.interview_intelligence.report_generator import (
    generate_final_report
)

class InterviewSession:
    def __init__(self, topic: str, difficulty: str = "medium"):
        self.topic = topic
        self.current_difficulty = difficulty
        self.question_number = 0
        self.history: List[Dict[str, Any]] = []

    def generate_next_question(self):
        previous_questions = [
            item["question"]
            for item in self.history
        ]

        return generate_question(
            topic=self.topic,
            difficulty=self.current_difficulty,
            previous_questions=previous_questions
        )

    def submit_answer(
        self,
        question: str,
        candidate_answer: str,
        expected_concepts: List[str]
    ):
        self.question_number += 1

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
            "expected_concepts": expected_concepts,
            "evaluation": evaluation.model_dump(),
            "next_difficulty": next_difficulty
        }

        self.history.append(record)

        self.current_difficulty = next_difficulty

        return record

    def get_history(self):
        return self.history
    
    def get_final_report(self):
        return generate_final_report(self.history)