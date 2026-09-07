from app.llm.gemini_client import generate_response


prompt = "Explain RAG in simple terms in three sentences."

response = generate_response(prompt)

print(response)