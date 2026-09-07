from pymilvus import MilvusClient

from ai_ml.part1.rag import milvus_store


def test_insert_documents_into_temporary_collection(
    tmp_path,
    monkeypatch,
):
    db_path = tmp_path / "test_insert.db"

    test_client = MilvusClient(str(db_path))
    test_collection = "test_candidate_profiles"

    monkeypatch.setattr(
        milvus_store,
        "client",
        test_client,
    )

    monkeypatch.setattr(
        milvus_store,
        "COLLECTION_NAME",
        test_collection,
    )

    milvus_store.create_collection()
    milvus_store.create_indexes()

    chunks = [
        "Python is a programming language.",
        "Machine learning is used for predictive analysis.",
    ]

    dense_embeddings = [
        [0.1] * 1024,
        [0.2] * 1024,
    ]

    sparse_embeddings = [
        {1: 0.5, 10: 0.8},
        {2: 0.4, 20: 0.9},
    ]

    result = milvus_store.insert_documents(
        chunks,
        dense_embeddings,
        sparse_embeddings,
    )

    assert result["insert_count"] == 2
    assert len(result["ids"]) == 2

    stats = test_client.get_collection_stats(
        collection_name=test_collection,
    )

    assert int(stats["row_count"]) == 2
