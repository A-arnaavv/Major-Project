from app.rag.retriever import hybrid_retrieve


query = "What programming languages and technical skills does the candidate have?"

print("Performing Hybrid Retrieval...\n")

dense_results, sparse_results = hybrid_retrieve(query)


print("----- DENSE RESULTS -----\n")

for result in dense_results[0]:
    print("Score:", result["distance"])
    print("Text:", result["entity"]["text"])
    print("-" * 50)


print("\n----- SPARSE RESULTS -----\n")

for result in sparse_results[0]:
    print("Score:", result["distance"])
    print("Text:", result["entity"]["text"])
    print("-" * 50)