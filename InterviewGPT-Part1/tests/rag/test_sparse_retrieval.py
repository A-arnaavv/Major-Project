from app.rag.retriever import retrieve_sparse


query = "What programming languages does the candidate know?"

print("Searching using sparse retrieval...\n")

results = retrieve_sparse(query)

print("Retrieved Results:\n")

for result in results[0]:
    print("Score:", result["distance"])
    print("Text:", result["entity"]["text"])
    print("-" * 50)