import os
from typing import List

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, Field

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found.")

client = genai.Client(api_key=api_key)


class GeneratedQuestion(BaseModel):
    question: str
    expected_concepts: List[str]
    difficulty: str
    topic: str


def generate_question(
    topic: str,
    difficulty: str,
    previous_questions: List[str] | None = None
) -> GeneratedQuestion:

    previous_questions = previous_questions or []

    prompt = f"""
You are a technical interviewer.

Generate ONE interview question.

Topic:
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
"""

    interaction = client.interactions.create(
        model="gemini-3.1-flash-lite",
        input=prompt,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": GeneratedQuestion.model_json_schema()
        }
    )

    return GeneratedQuestion.model_validate_json(
        interaction.output_text
    )