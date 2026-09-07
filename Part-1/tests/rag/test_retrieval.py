from app.rag.retriever import retrieve_documents


query = "What are the candidate's strongest technical skills?"

print("Searching documents...\n")

results = retrieve_documents(query)

print("Retrieved Results:\n")

for result in results[0]:
    print("Score:", result["distance"])
    print("Text:", result["entity"]["text"])
    print("-" * 50)