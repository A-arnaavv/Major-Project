import json

from app.llm.gemini_client import generate_response


def analyze_resume(resume_text: str) -> dict:
    """
    Analyzes resume text using Gemini and returns
    a structured candidate profile.
    """

    prompt = f"""
You are an expert resume analyzer.

Analyze the following resume and extract the information.

Return ONLY valid JSON.
Do not include markdown formatting or explanations.

Use exactly this structure:

{{
    "name": "",
    "summary": "",
    "education": [],
    "technical_skills": [],
    "programming_languages": [],
    "libraries_tools": [],
    "databases": [],
    "projects": [],
    "experience": [],
    "certifications": [],
    "strengths": [],
    "improvement_areas": []
}}

Resume:
{resume_text}
"""

    response = generate_response(prompt)

    return json.loads(response)