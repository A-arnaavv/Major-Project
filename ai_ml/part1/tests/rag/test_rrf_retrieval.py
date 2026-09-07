from ai_ml.part1.rag.retriever import reciprocal_rank_fusion


def test_rrf_prioritizes_document_present_in_both_rankings():
    dense_results = [[
        {
            "id": 1,
            "distance": 0.95,
            "entity": {"text": "Machine Learning"},
        },
        {
            "id": 2,
            "distance": 0.80,
            "entity": {"text": "Databases"},
        },
    ]]

    sparse_results = [[
        {
            "id": 1,
            "distance": 0.90,
            "entity": {"text": "Machine Learning"},
        },
        {
            "id": 3,
            "distance": 0.75,
            "entity": {"text": "Computer Networks"},
        },
    ]]

    results = reciprocal_rank_fusion(
        dense_results,
        sparse_results,
    )

    assert len(results) == 3
    assert results[0]["id"] == 1
    assert results[0]["text"] == "Machine Learning"
    assert results[0]["score"] > results[1]["score"]
