import os
from typing import List

from google import genai
from pydantic import BaseModel

from ai_ml.interview_intelligence.config import (
    is_mock_mode,
    GEMINI_MODEL,
    GEMINI_API_KEY,
)
from ai_ml.interview_intelligence.gemini_utils import (
    call_gemini_with_retry,
)


class GeneratedQuestion(BaseModel):
    question: str
    expected_concepts: List[str]
    difficulty: str
    topic: str
    subtopic: str


def generate_question(
    topic: str,
    difficulty: str,
    previous_questions: List[str] | None = None
) -> GeneratedQuestion:

    previous_questions = previous_questions or []

    # -------------------------------------------------
    # MOCK MODE
    # -------------------------------------------------
    if is_mock_mode():

        mock_question_bank = {
            "easy": [
                {
                    "question": (
                        f"What is supervised learning in {topic}, "
                        "and can you give one example?"
                    ),
                    "expected_concepts": [
                        "supervised learning",
                        "labeled data",
                        "example",
                    ],
                    "subtopic": "Supervised Learning",
                },
                {
                    "question": (
                        f"What is overfitting in {topic}, "
                        "and why is it a problem?"
                    ),
                    "expected_concepts": [
                        "overfitting",
                        "training performance",
                        "generalization",
                    ],
                    "subtopic": "Overfitting",
                },
                {
                    "question": (
                        f"What is the purpose of a train-test split in {topic}?"
                    ),
                    "expected_concepts": [
                        "training data",
                        "test data",
                        "generalization",
                    ],
                    "subtopic": "Model Evaluation",
                },
            ],

            "medium": [
                {
                    "question": (
                        f"Explain the Bias-Variance Tradeoff in {topic} "
                        "and how it affects model performance."
                    ),
                    "expected_concepts": [
                        "bias",
                        "variance",
                        "underfitting",
                        "overfitting",
                        "generalization",
                    ],
                    "subtopic": "Bias-Variance Tradeoff",
                },
                {
                    "question": (
                        f"Explain Precision and Recall in {topic} "
                        "and when you would prioritize each."
                    ),
                    "expected_concepts": [
                        "precision",
                        "recall",
                        "false positives",
                        "false negatives",
                    ],
                    "subtopic": "Classification Metrics",
                },
                {
                    "question": (
                        f"How does regularization help reduce overfitting in {topic}?"
                    ),
                    "expected_concepts": [
                        "regularization",
                        "model complexity",
                        "overfitting",
                        "penalty term",
                    ],
                    "subtopic": "Regularization",
                },
            ],

            "hard": [
                {
                    "question": (
                        f"How would you diagnose and fix a model in {topic} "
                        "that performs well on training data but poorly "
                        "on unseen data?"
                    ),
                    "expected_concepts": [
                        "overfitting",
                        "validation",
                        "regularization",
                        "feature selection",
                        "generalization",
                    ],
                    "subtopic": "Model Generalization",
                },
                {
                    "question": (
                        f"How would you choose an evaluation metric for "
                        f"an imbalanced classification problem in {topic}?"
                    ),
                    "expected_concepts": [
                        "class imbalance",
                        "precision",
                        "recall",
                        "F1 score",
                        "ROC-AUC",
                    ],
                    "subtopic": "Advanced Model Evaluation",
                },
                {
                    "question": (
                        f"Explain how you would detect data leakage in a "
                        f"{topic} pipeline and prevent it."
                    ),
                    "expected_concepts": [
                        "data leakage",
                        "feature engineering",
                        "train-test separation",
                        "validation",
                    ],
                    "subtopic": "Data Leakage",
                },
            ],
        }

        difficulty_questions = mock_question_bank.get(
            difficulty,
            mock_question_bank["medium"],
        )

        # Find the first question that has not already been asked.
        selected_question = None

        for candidate in difficulty_questions:
            if candidate["question"] not in previous_questions:
                selected_question = candidate
                break

        # If every question at this difficulty has already been used,
        # fall back to the first one instead of crashing.
        if selected_question is None:
            selected_question = difficulty_questions[0]

        return GeneratedQuestion(
            question=selected_question["question"],
            expected_concepts=selected_question["expected_concepts"],
            difficulty=difficulty,
            topic=topic,
            subtopic=selected_question["subtopic"],
        )

        data = mock_questions.get(
            difficulty,
            mock_questions["medium"],
        )

        return GeneratedQuestion(
            question=data["question"],
            expected_concepts=data["expected_concepts"],
            difficulty=difficulty,
            topic=topic,
            subtopic=data["subtopic"],
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

    prompt = f"""
You are a technical interviewer.

Generate ONE interview question.

Main Topic:
{topic}

Difficulty:
{difficulty}

Previously asked questions:
{previous_questions}

Requirements:
- Do not repeat previous questions.
- The question must match the requested difficulty.
- Keep the question concise and interview-appropriate.
- Provide 3 to 6 expected concepts that a strong answer should cover.
- Keep the main topic as the provided topic.
- Identify the specific technical subtopic or skill being tested.

Examples of subtopics for Machine Learning:
- Regularization
- Classification Metrics
- Bias-Variance Tradeoff
- Overfitting and Underfitting
- Decision Trees
- Ensemble Learning
- Feature Engineering
- Model Evaluation
- Clustering
- Dimensionality Reduction
"""

    interaction = call_gemini_with_retry(
        lambda: client.interactions.create(
            model=GEMINI_MODEL,
            input=prompt,
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": GeneratedQuestion.model_json_schema(),
            },
        ),
        operation_name="Question generation",
    )

    try:
        return GeneratedQuestion.model_validate_json(
            interaction.output_text
        )

    except Exception as exc:
        raise RuntimeError(
            "Gemini returned an invalid question response."
        ) from exc