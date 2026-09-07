from app.rag.embeddings import create_embeddings
from app.rag.milvus_store import client, COLLECTION_NAME


def retrieve_resume(query, top_k=5):

    print("Creating query embedding...")

    embeddings = create_embeddings([query])

    query_dense = embeddings["dense_embeddings"][0]

    print("Loading collection...")

    client.load_collection(
        collection_name=COLLECTION_NAME
    )

    print("Searching Milvus...")

    results = client.search(
        collection_name=COLLECTION_NAME,
        data=[query_dense],
        anns_field="dense_vector",
        limit=top_k,
        output_fields=["text"]
    )

    return results


query = "What programming languages does the candidate know?"


results = retrieve_resume(query)


print("\nRetrieved Resume Context:\n")

for result in results[0]:

    print("Score:", result["distance"])
    print("Text:", result["entity"]["text"])
    print("-" * 50)