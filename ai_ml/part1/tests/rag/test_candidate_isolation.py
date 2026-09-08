from ai_ml.part1.rag.milvus_store import (
    client,
    create_collection,
    get_collection_name,
)


def test_candidate_collections_are_isolated():
    candidate_a = "candidate-A"
    candidate_b = "candidate-B"

    collection_a = get_collection_name(candidate_a)
    collection_b = get_collection_name(candidate_b)

    assert collection_a != collection_b

    if client.has_collection(collection_a):
        client.drop_collection(collection_a)

    if client.has_collection(collection_b):
        client.drop_collection(collection_b)

    try:
        create_collection(candidate_id=candidate_a)

        assert client.has_collection(collection_a)
        assert not client.has_collection(collection_b)

        create_collection(candidate_id=candidate_b)

        assert client.has_collection(collection_a)
        assert client.has_collection(collection_b)

    finally:
        if client.has_collection(collection_a):
            client.drop_collection(collection_a)

        if client.has_collection(collection_b):
            client.drop_collection(collection_b)