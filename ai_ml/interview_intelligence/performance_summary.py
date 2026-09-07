import os
from typing import List, Dict, Any

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

MODEL_NAME = os.getenv("GEMINI_MODEL")

if not MODEL_NAME:
    raise ValueError(
        "GEMINI_MODEL not found. Add it to your .env file."
    )


class PerformanceSummary(BaseModel):
    overall_performance: str
    strong_areas: List[str]
    weak_areas: List[str]
    recommended_topics: List[str]
    final_feedback: str


def generate_performance_summary(
    history: List[Dict[str, Any]]
) -> PerformanceSummary:

    if not history:
        return PerformanceSummary(
            overall_performance="No interview data available",
            strong_areas=[],
            weak_areas=[],
            recommended_topics=[],
            final_feedback="Complete an interview to receive feedback."
        )

    interview_data = []

    for record in history:
        interview_data.append({
            "question": record["question"],
            "topic": record.get("topic", "General"),
            "subtopic": record.get("subtopic", "General"),
            "difficulty": record["difficulty"],
            "score": record["evaluation"]["overall_score"],
            "technical_accuracy": record["evaluation"]["technical_accuracy"],
            "strengths": record["evaluation"]["strengths"],
            "weaknesses": record["evaluation"]["weaknesses"]
        })

    prompt = f"""
You are an expert technical interview coach.

Analyze the candidate's complete interview performance.

Interview data:
{interview_data}

Generate a concise final performance report.

Requirements:

1. overall_performance:
Choose a short description such as:
- Beginner
- Needs Improvement
- Developing
- Good
- Strong
- Excellent

2. strong_areas:
Identify the candidate's strongest technical areas.

3. weak_areas:
Identify recurring weaknesses.
Do not repeat similar weaknesses.

4. recommended_topics:
Recommend specific topics the candidate should study next.

5. final_feedback:
Provide constructive and concise feedback.

Base the report only on the interview data provided.
"""

    interaction = client.interactions.create(
        model=MODEL_NAME,
        input=prompt,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": PerformanceSummary.model_json_schema()
        }
    )

    return PerformanceSummary.model_validate_json(
        interaction.output_text
    )