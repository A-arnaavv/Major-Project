from pymilvus import MilvusClient
from ai_ml.part1.rag.embeddings import create_embeddings
from ai_ml.part1.paths import MILVUS_DB_PATH


DB_PATH = str(MILVUS_DB_PATH)
COLLECTION_NAME = "candidate_profiles"

client = MilvusClient(DB_PATH)


def reciprocal_rank_fusion(dense_results, sparse_results, k=60):
    """
    Combines dense and sparse retrieval results
    using Reciprocal Rank Fusion (RRF).
    """

    fused_scores = {}
    documents = {}

    # Process dense results
    for rank, result in enumerate(dense_results[0], start=1):

        doc_id = result["id"]

        fused_scores[doc_id] = fused_scores.get(doc_id, 0) + 1 / (k + rank)

        documents[doc_id] = result["entity"]["text"]


    # Process sparse results
    for rank, result in enumerate(sparse_results[0], start=1):

        doc_id = result["id"]

        fused_scores[doc_id] = fused_scores.get(doc_id, 0) + 1 / (k + rank)

        documents[doc_id] = result["entity"]["text"]


    # Sort documents by fused score
    ranked_results = sorted(
        fused_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    results = []

    for doc_id, score in ranked_results:

        results.append({
            "id": doc_id,
            "score": score,
            "text": documents[doc_id]
        })

    return results


def hybrid_retrieve(query, top_k=5):
    """
    Performs Hybrid Retrieval using
    Dense + Sparse embeddings and RRF.
    """

    print("Creating query embedding...")

    # Create query embeddings
    query_embeddings = create_embeddings([query])

    dense_vector = query_embeddings["dense_embeddings"][0]

    sparse_vector = query_embeddings["sparse_embeddings"][0]


    # Load collection
    print("Loading collection...")

    client.load_collection(COLLECTION_NAME)


    # Dense search
    print("Performing dense search...")

    dense_results = client.search(
        collection_name=COLLECTION_NAME,
        data=[dense_vector],
        anns_field="dense_vector",
        limit=top_k,
        output_fields=["text"],
        search_params={
            "metric_type": "COSINE"
        }
    )


    # Sparse search
    print("Performing sparse search...")

    sparse_results = client.search(
        collection_name=COLLECTION_NAME,
        data=[sparse_vector],
        anns_field="sparse_vector",
        limit=top_k,
        output_fields=["text"],
        search_params={
            "metric_type": "IP"
        }
    )


    # Fuse results using RRF
    print("Combining results using RRF...")

    fused_results = reciprocal_rank_fusion(
        dense_results,
        sparse_results
    )


    return fused_results[:top_k]