from app.resume.parser import extract_text_from_pdf
from app.resume.analyzer import analyze_resume

from app.rag.documents import create_candidate_document
from app.rag.chunker import chunk_text
from app.rag.embeddings import create_embeddings
from app.rag.milvus_store import insert_documents

from app.interview.question_generator import generate_interview_questions
from app.rag.qa import answer_resume_question


# =====================================
# PROCESS RESUME
# =====================================

def process_resume():

    pdf_path = "data/raw/Tanishka latest.pdf"

    print("\n========================================")
    print("      INTERVIEWGPT - RESUME PROCESSING")
    print("========================================\n")

    # STEP 1
    print("STEP 1: Extracting resume text...")

    resume_text = extract_text_from_pdf(pdf_path)

    print("Resume text extracted successfully!")

    # STEP 2
    print("\nSTEP 2: Analyzing resume...")

    candidate_profile = analyze_resume(resume_text)

    print("Resume analyzed successfully!")

    # STEP 3
    print("\nSTEP 3: Creating RAG document...")

    document = create_candidate_document(candidate_profile)

    print("RAG document created successfully!")

    # STEP 4
    print("\nSTEP 4: Chunking document...")

    chunks = chunk_text(document)

    print(f"Total chunks created: {len(chunks)}")

    # STEP 5
    print("\nSTEP 5: Creating embeddings...")

    embeddings = create_embeddings(chunks)

    dense_embeddings = embeddings["dense_embeddings"]
    sparse_embeddings = embeddings["sparse_embeddings"]

    print("Embeddings created successfully!")

    # STEP 6
    print("\nSTEP 6: Inserting documents into Milvus...")

    insert_documents(
        chunks,
        dense_embeddings,
        sparse_embeddings
    )

    print("\n========================================")
    print("SUCCESS!")
    print("Resume data has been inserted into Milvus!")
    print("========================================\n")


# =====================================
# GENERATE INTERVIEW QUESTIONS
# =====================================

def generate_questions():

    print("\n========================================")
    print("       GENERATE INTERVIEW QUESTIONS")
    print("========================================")

    interview_type = input(
        "\nEnter interview type "
        "(technical / HR / behavioral): "
    )

    num_questions = input(
        "Enter number of questions: "
    )

    # Convert input to integer
    try:
        num_questions = int(num_questions)

    except ValueError:

        print("\nInvalid number!")

        return

    questions = generate_interview_questions(
        interview_type=interview_type,
        num_questions=num_questions
    )

    print("\n----- INTERVIEW QUESTIONS -----\n")

    print(questions)


# =====================================
# RESUME QUESTION ANSWERING
# =====================================

def ask_resume_question():

    print("\n========================================")
    print("          RESUME QUESTION ANSWERING")
    print("========================================")

    question = input(
        "\nAsk a question about the candidate's resume:\n"
    )

    answer = answer_resume_question(question)

    print("\n----- ANSWER -----\n")

    print(answer)


# =====================================
# MAIN APPLICATION
# =====================================

def main():

    while True:

        print("\n===================================")
        print("           INTERVIEWGPT")
        print("===================================")

        print("\n1. Process Resume")
        print("2. Generate Interview Questions")
        print("3. Ask Resume Question")
        print("4. Exit")

        choice = input(
            "\nEnter your choice: "
        )

        # OPTION 1
        if choice == "1":

            process_resume()

        # OPTION 2
        elif choice == "2":

            generate_questions()

        # OPTION 3
        elif choice == "3":

            ask_resume_question()

        # OPTION 4
        elif choice == "4":

            print("\nThank you for using InterviewGPT! 👋")

            break

        else:

            print("\nInvalid choice! Please try again.")


if __name__ == "__main__":
    main()