from ai_ml.part1.rag.retriever import hybrid_retrieve


def test_resume_retrieval_returns_relevant_context():
    results = hybrid_retrieve(
        "What programming languages does the candidate know?",
        top_k=5,
    )

    assert results

    combined_text = " ".join(
        result["text"]
        for result in results
    ).lower()

    assert (
        "python" in combined_text
        or "java" in combined_text
        or "programming" in combined_text
    )
