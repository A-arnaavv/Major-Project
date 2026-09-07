import pytest

from ai_ml.part1.rag.qa import answer_resume_question


pytestmark = pytest.mark.live_gemini

def test_resume_question_answering_returns_text():
    answer = answer_resume_question(
        "What are the candidate's strongest technical skills?"
    )

    assert isinstance(answer, str)
    assert answer.strip()
