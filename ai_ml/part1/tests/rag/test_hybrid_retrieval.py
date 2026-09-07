from ai_ml.part1.rag.retriever import hybrid_retrieve


def test_hybrid_retrieval_returns_ranked_resume_chunks():
    results = hybrid_retrieve(
        "What programming languages and technical skills "
        "does the candidate have?",
        top_k=5,
    )

    assert results
    assert len(results) <= 5

    for result in results:
        assert "id" in result
        assert "score" in result
        assert "text" in result

        assert isinstance(result["score"], float)
        assert isinstance(result["text"], str)
        assert result["text"].strip()

    scores = [
        result["score"]
        for result in results
    ]

    assert scores == sorted(
        scores,
        reverse=True,
    )
