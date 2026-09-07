import pytest

from ai_ml.part1.llm.gemini_client import generate_response


pytestmark = pytest.mark.live_gemini

def test_generate_response_returns_text():
    response = generate_response(
        "Explain RAG in simple terms in three sentences."
    )

    assert isinstance(response, str)
    assert response.strip()
