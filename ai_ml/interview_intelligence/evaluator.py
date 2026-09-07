from typing import List

from google import genai

from ai_ml.interview_intelligence.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    is_mock_mode,
)
from ai_ml.interview_intelligence.schemas import EvaluationResult
from ai_ml.interview_intelligence.gemini_utils import (
    call_gemini_with_retry,
)

def evaluate_answer(
    question: str,
    candidate_answer: str,
    expected_concepts: List[str] | str,
    difficulty: str,
) -> EvaluationResult:

    # -------------------------------------------------
    # MOCK MODE
    # -------------------------------------------------
    if is_mock_mode():

        cleaned_answer = candidate_answer.strip().lower()

        no_answer_values = {
            "",
            "na",
            "n/a",
            "no",
            "idk",
            "i don't know",
            "dont know",
        }

        if cleaned_answer in no_answer_values:
            technical_accuracy = 0
            relevance = 0
            clarity = 0
            completeness = 0
            overall_score = 0.0

            strengths = []

            weaknesses = [
                "No meaningful technical answer was provided."
            ]

            feedback = (
                "Provide a complete technical response and explain "
                "the main concepts relevant to the question."
            )

            improved_answer = (
                "A stronger answer would define the core concept, "
                "explain how it works, and provide a relevant example."
            )

        else:
            technical_accuracy = 7
            relevance = 7
            clarity = 7
            completeness = 7
            overall_score = 7.0

            strengths = [
                "Attempted the technical question.",
                "Provided a relevant response.",
            ]

            weaknesses = [
                "The answer could include more technical depth."
            ]

            feedback = (
                "Good attempt. Add more technical detail, reasoning, "
                "and examples to make the answer stronger."
            )

            improved_answer = (
                "A stronger answer would clearly define the concept, "
                "explain the technical reasoning behind it, and include "
                "a practical example."
            )

        if overall_score > 7:
            next_difficulty = "harder"
        elif overall_score < 5:
            next_difficulty = "easier"
        else:
            next_difficulty = "same"

        return EvaluationResult(
            technical_accuracy=technical_accuracy,
            relevance=relevance,
            clarity=clarity,
            completeness=completeness,
            overall_score=overall_score,
            strengths=strengths,
            weaknesses=weaknesses,
            feedback=feedback,
            improved_answer=improved_answer,
            next_difficulty=next_difficulty,
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

    if isinstance(expected_concepts, list):
        expected_concepts_text = ", ".join(expected_concepts)
    else:
        expected_concepts_text = expected_concepts

    prompt = f"""
        You are an expert technical interviewer evaluating a candidate's answer.

        Interview Question:
        {question}

        Question Difficulty:
        {difficulty}

        Expected Concepts:
        {expected_concepts_text}

        Candidate Answer:
        {candidate_answer}

        Evaluate the candidate's answer carefully.

        Score each category from 0 to 10:

        1. Technical Accuracy
        - Is the technical content correct?
        - Does the answer demonstrate accurate understanding?

        2. Relevance
        - Does the answer directly address the question?
        - Does it stay focused on the requested topic?

        3. Clarity
        - Is the explanation clear and understandable?
        - Is the reasoning communicated effectively?

        4. Completeness
        - Does the answer cover the important expected concepts?
        - Are important details missing?

        Also provide:

        - An overall score from 0 to 10.
        - Key strengths in the answer.
        - Key weaknesses or missing areas.
        - Constructive feedback explaining how the candidate can improve.
        - An improved example answer that would perform better in an interview.

        Difficulty recommendation:
        - If overall score is below 5, recommend "easier".
        - If overall score is between 5 and 7 inclusive, recommend "same".
        - If overall score is above 7, recommend "harder".

        Do not penalize the candidate simply because they use different wording
        from the expected concepts. Judge whether the technical meaning is correct.

        If the candidate provides no meaningful answer, such as "na", "idk",
        or an empty response, assign very low scores appropriately.
        """

    interaction = call_gemini_with_retry(
        lambda: client.interactions.create(
            model=GEMINI_MODEL,
            input=prompt,
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": EvaluationResult.model_json_schema(),
            },
        ),
        operation_name="Answer evaluation",
    )

    try:
        return EvaluationResult.model_validate_json(
            interaction.output_text
        )

    except Exception as exc:
        raise RuntimeError(
            "Gemini returned an invalid evaluation response."
        ) from exc