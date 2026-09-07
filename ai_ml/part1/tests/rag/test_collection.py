from pymilvus import MilvusClient

from ai_ml.part1.rag import milvus_store


def test_create_collection_and_indexes(tmp_path, monkeypatch):
    db_path = tmp_path / "test_collection.db"

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

    collections = test_client.list_collections()

    assert test_collection in collections
