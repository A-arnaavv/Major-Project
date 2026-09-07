from app.resume.parser import extract_text_from_pdf
from app.resume.analyzer import analyze_resume

from app.rag.documents import create_candidate_document
from app.rag.chunker import chunk_text
from app.rag.embeddings import create_embeddings

from app.rag.milvus_store import (
    create_collection,
    create_indexes,
    insert_documents
)


# Path to your resume
RESUME_PATH = "data/raw/Tanishka latest.pdf"


print("STEP 1: Extracting resume text...")

resume_text = extract_text_from_pdf(RESUME_PATH)

print("Resume text extracted successfully!")


print("\nSTEP 2: Analyzing resume with Gemini...")

candidate_profile = analyze_resume(resume_text)

print("Resume analyzed successfully!")

print("\nCandidate Name:")
print(candidate_profile.get("name"))


print("\nSTEP 3: Creating RAG document...")

document = create_candidate_document(candidate_profile)

print("RAG document created successfully!")


print("\nSTEP 4: Chunking document...")

chunks = chunk_text(document)

print(f"Total chunks created: {len(chunks)}")


print("\nSTEP 5: Creating embeddings...")

embeddings = create_embeddings(chunks)

dense_embeddings = embeddings["dense_embeddings"]
sparse_embeddings = embeddings["sparse_embeddings"]

print("Embeddings created successfully!")


print("\nSTEP 6: Creating Milvus collection...")

create_collection()

create_indexes()


print("\nSTEP 7: Inserting documents into Milvus...")

insert_documents(
    chunks,
    dense_embeddings,
    sparse_embeddings
)


print("\nSUCCESS!")
print("Resume data has been inserted into Milvus!")