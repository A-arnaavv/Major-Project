import pytest

from ai_ml.part1.rag.qa import answer_resume_question


pytestmark = pytest.mark.live_gemini

def test_resume_question_answering_with_machine_learning_query():
    answer = answer_resume_question(
        "What are the candidate's main Machine Learning skills?"
    )

    assert isinstance(answer, str)
    assert answer.strip()

    lower_answer = answer.lower()

    assert (
        "machine learning" in lower_answer
        or "deep learning" in lower_answer
        or "nlp" in lower_answer
        or "tensorflow" in lower_answer
        or "scikit" in lower_answer
    )
