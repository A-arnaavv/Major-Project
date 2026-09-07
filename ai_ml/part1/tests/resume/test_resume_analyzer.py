import pytest

from ai_ml.part1.paths import DEFAULT_RESUME_PATH
from ai_ml.part1.resume.analyzer import analyze_resume
from ai_ml.part1.resume.parser import extract_text_from_pdf


pytestmark = pytest.mark.live_gemini

def test_analyze_resume_returns_candidate_profile():
    assert DEFAULT_RESUME_PATH.exists()

    resume_text = extract_text_from_pdf(
        str(DEFAULT_RESUME_PATH)
    )

    candidate_profile = analyze_resume(
        resume_text
    )

    assert isinstance(candidate_profile, dict)
    assert candidate_profile

    expected_keys = {
        "name",
        "summary",
        "education",
        "technical_skills",
        "programming_languages",
        "libraries_tools",
        "databases",
        "projects",
        "experience",
        "certifications",
        "strengths",
        "improvement_areas",
    }

    assert expected_keys.issubset(
        candidate_profile.keys()
    )
