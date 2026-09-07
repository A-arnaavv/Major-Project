from ai_ml.part1.rag.retriever import hybrid_retrieve
from ai_ml.part1.llm.gemini_client import generate_response


def generate_interview_questions(
    interview_type="technical",
    num_questions=5
):
    """
    Generates personalized interview questions
    based on the candidate's resume.
    """

    print("Retrieving candidate information...")

    query = (
        "Candidate technical skills, projects, "
        "experience, education and strengths"
    )

    results = hybrid_retrieve(
    query,
    top_k=10

    )

    context = "\n\n".join(
        [result["text"] for result in results]
    )

    prompt = f"""
You are an expert technical interviewer.

Generate {num_questions} {interview_type} interview
questions based ONLY on the candidate resume context.

The questions should be personalized to the candidate's:

- Technical skills
- Programming languages
- Libraries and tools
- Projects
- Experience

Rules:

1. Ask relevant questions based on the resume.
2. Do not ask generic unrelated questions.
3. Include different difficulty levels.
4. Do not provide answers.
5. Number the questions clearly.

Candidate Resume Context:

{context}
"""

    print("Generating interview questions...")

    response = generate_response(prompt)

    return response