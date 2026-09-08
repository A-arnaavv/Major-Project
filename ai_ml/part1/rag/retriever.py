from pymilvus import MilvusClient

from ai_ml.part1.paths import MILVUS_DB_PATH
from ai_ml.part1.rag.embeddings import create_embeddings
from ai_ml.part1.rag.milvus_store import get_collection_name


DB_PATH = str(MILVUS_DB_PATH)

client = MilvusClient(DB_PATH)


def reciprocal_rank_fusion(
    dense_results,
    sparse_results,
    k=60,
):
    """
    Combine dense and sparse retrieval results using
    Reciprocal Rank Fusion (RRF).
    """

    fused_scores = {}
    documents = {}

    for rank, result in enumerate(
        dense_results[0],
        start=1,
    ):
        doc_id = result["id"]

        fused_scores[doc_id] = (
            fused_scores.get(doc_id, 0)
            + 1 / (k + rank)
        )

        documents[doc_id] = result["entity"]["text"]

    for rank, result in enumerate(
        sparse_results[0],
        start=1,
    ):
        doc_id = result["id"]

        fused_scores[doc_id] = (
            fused_scores.get(doc_id, 0)
            + 1 / (k + rank)
        )

        documents[doc_id] = result["entity"]["text"]

    ranked_results = sorted(
        fused_scores.items(),
        key=lambda x: x[1],
        reverse=True,
    )

    results = []

    for doc_id, score in ranked_results:
        results.append(
            {
                "id": doc_id,
                "score": score,
                "text": documents[doc_id],
            }
        )

    return results


def hybrid_retrieve(
    query,
    top_k=5,
    candidate_id: str | None = None,
):
    """
    Perform hybrid dense + sparse retrieval using RRF.

    When candidate_id is provided, retrieval is isolated to that
    candidate's Milvus collection.

    Omitting candidate_id preserves legacy Part 1 behaviour.
    """

    collection_name = get_collection_name(candidate_id)

    if not client.has_collection(collection_name):
        raise ValueError(
            "Candidate retrieval collection does not exist: "
            f"{collection_name}"
        )

    print(
        f"Creating query embedding for "
        f"'{collection_name}'..."
    )

    query_embeddings = create_embeddings([query])

    dense_vector = query_embeddings[
        "dense_embeddings"
    ][0]

    sparse_vector = query_embeddings[
        "sparse_embeddings"
    ][0]

    print(
        f"Loading collection: {collection_name}"
    )

    client.load_collection(collection_name)

    print("Performing dense search...")

    dense_results = client.search(
        collection_name=collection_name,
        data=[dense_vector],
        anns_field="dense_vector",
        limit=top_k,
        output_fields=["text"],
        search_params={
            "metric_type": "COSINE",
        },
    )

    print("Performing sparse search...")

    sparse_results = client.search(
        collection_name=collection_name,
        data=[sparse_vector],
        anns_field="sparse_vector",
        limit=top_k,
        output_fields=["text"],
        search_params={
            "metric_type": "IP",
        },
    )

    print("Combining results using RRF...")

    fused_results = reciprocal_rank_fusion(
        dense_results,
        sparse_results,
    )

    return fused_results[:top_k]