from app.resume.parser import extract_text_from_pdf
from app.resume.analyzer import analyze_resume
from app.rag.documents import create_candidate_document
from app.rag.chunker import chunk_text
from app.rag.embeddings import create_embeddings


pdf_path = "data/raw/Tanishka latest.pdf"


print("Extracting resume text...")
resume_text = extract_text_from_pdf(pdf_path)

print("Analyzing resume...")
candidate_profile = analyze_resume(resume_text)

print("Creating RAG document...")
document = create_candidate_document(candidate_profile)

print("Chunking document...")
chunks = chunk_text(document)

print(f"Total chunks: {len(chunks)}")

print("\nCreating embeddings...")
embeddings = create_embeddings(chunks)


print("\n----- EMBEDDING INFO -----")

dense_embeddings = embeddings["dense_embeddings"]
sparse_embeddings = embeddings["sparse_embeddings"]

print(f"Dense embeddings created: {len(dense_embeddings)}")
print(f"Dense vector dimension: {len(dense_embeddings[0])}")

print(f"Sparse embeddings created: {len(sparse_embeddings)}")

print("\nEmbeddings created successfully!")