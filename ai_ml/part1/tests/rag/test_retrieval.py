from ai_ml.part1.rag.retriever import hybrid_retrieve


def test_hybrid_retrieval_returns_results():
    results = hybrid_retrieve(
        "What are the candidate's strongest technical skills?",
        top_k=3,
    )

    assert results
    assert len(results) <= 3

    for result in results:
        assert "id" in result
        assert "score" in result
        assert "text" in result

        assert isinstance(result["text"], str)
        assert result["text"].strip()
