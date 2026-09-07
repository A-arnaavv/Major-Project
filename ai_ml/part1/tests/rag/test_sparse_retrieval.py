from ai_ml.part1.rag.retriever import reciprocal_rank_fusion


def test_reciprocal_rank_fusion_combines_dense_and_sparse_results():
    dense_results = [[
        {
            "id": 1,
            "distance": 0.95,
            "entity": {"text": "Machine learning and Python"},
        },
        {
            "id": 2,
            "distance": 0.85,
            "entity": {"text": "Database systems"},
        },
    ]]

    sparse_results = [[
        {
            "id": 1,
            "distance": 0.90,
            "entity": {"text": "Machine learning and Python"},
        },
        {
            "id": 3,
            "distance": 0.80,
            "entity": {"text": "Natural language processing"},
        },
    ]]

    results = reciprocal_rank_fusion(
        dense_results,
        sparse_results,
    )

    assert len(results) == 3

    assert results[0]["id"] == 1
    assert results[0]["text"] == "Machine learning and Python"

    assert results[0]["score"] > results[1]["score"]