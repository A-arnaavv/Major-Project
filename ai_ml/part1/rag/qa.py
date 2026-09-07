from ai_ml.part1.rag.retriever import hybrid_retrieve
from ai_ml.part1.llm.gemini_client import generate_response


def answer_resume_question(question: str):
    """
    Answers a question using the candidate's resume
    through Hybrid RAG with RRF.
    """

    print("Retrieving relevant resume context...")

    # Retrieve relevant chunks using Hybrid RAG + RRF
    results = hybrid_retrieve(
        question,
        top_k=5
    )

    # Handle empty results
    if not results:
        return "No relevant resume information was found."

    # Combine retrieved chunks into context
    context = "\n\n".join(
        result["text"]
        for result in results
    )

    print("Generating answer using Gemini...")

    prompt = f"""
You are an AI interview assistant.

Answer the user's question using ONLY the candidate resume
context provided below.

If the answer is not present in the context, clearly say:

"I could not find this information in the candidate's resume."

Do not invent information.

Candidate Resume Context:

{context}


Question:

{question}


Answer:
"""

    answer = generate_response(prompt)

    return answer