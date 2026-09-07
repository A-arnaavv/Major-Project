from pymilvus import MilvusClient

from ai_ml.part1.paths import MILVUS_DB_PATH


def test_milvus_database_is_accessible():
    assert MILVUS_DB_PATH.exists()

    client = MilvusClient(
        str(MILVUS_DB_PATH)
    )

    collections = client.list_collections()

    assert isinstance(collections, list)
    assert "candidate_profiles" in collections
