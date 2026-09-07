from app.rag.retriever import hybrid_retrieve


query = "What are the candidate's Machine Learning skills?"

results = hybrid_retrieve(query)


print("\n----- HYBRID RRF RESULTS -----\n")

for result in results:

    print(f"Score: {result['score']}")

    print(f"Text: {result['text']}")

    print("-" * 50)