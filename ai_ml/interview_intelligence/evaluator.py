import os

from dotenv import load_dotenv
from google import genai

from ai_ml.interview_intelligence.schemas import EvaluationResult
from ai_ml.interview_intelligence.prompts import EVALUATION_PROMPT


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found. Add it to your .env file."
    )

client = genai.Client(api_key=api_key)


def evaluate_answer(
    question: str,
    candidate_answer: str,
    expected_concepts: str,
    difficulty: str
) -> EvaluationResult:

    prompt = EVALUATION_PROMPT.format(
        question=question,
        candidate_answer=candidate_answer,
        expected_concepts=expected_concepts,
        difficulty=difficulty
    )

    interaction = client.interactions.create(
        model="gemini-3.7-flash",
        input=prompt,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": EvaluationResult.model_json_schema()
        },
    )

    return EvaluationResult.model_validate_json(
        interaction.output_text
    )