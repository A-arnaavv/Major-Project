import json

from pymilvus import MilvusClient

from ai_ml.part1.paths import CANDIDATE_PROFILE_PATH
from ai_ml.part1.rag import milvus_store
from ai_ml.part1.rag.chunker import chunk_text
from ai_ml.part1.rag.documents import create_candidate_document
from ai_ml.part1.rag.embeddings import create_embeddings


def load_candidate_profile():
    assert CANDIDATE_PROFILE_PATH.exists()

    with open(
        CANDIDATE_PROFILE_PATH,
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


def test_candidate_profile_can_be_indexed_in_milvus(
    tmp_path,
    monkeypatch,
):
    candidate_profile = load_candidate_profile()

    document = create_candidate_document(
        candidate_profile
    )

    chunks = chunk_text(document)

    assert chunks

    embeddings = create_embeddings(chunks)

    dense_embeddings = embeddings["dense_embeddings"]
    sparse_embeddings = embeddings["sparse_embeddings"]

    assert len(dense_embeddings) == len(chunks)
    assert len(sparse_embeddings) == len(chunks)

    db_path = tmp_path / "resume_index.db"

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

    result = milvus_store.insert_documents(
        chunks,
        dense_embeddings,
        sparse_embeddings,
    )

    assert result["insert_count"] == len(chunks)

    stats = test_client.get_collection_stats(
        collection_name=test_collection,
    )

    assert int(stats["row_count"]) == len(chunks)
