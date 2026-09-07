from app.resume.parser import extract_text_from_pdf
from app.resume.analyzer import analyze_resume
from app.rag.documents import create_candidate_document
from app.rag.chunker import chunk_text


pdf_path = "data/raw/Tanishka latest.pdf"

print("Extracting resume text...")
resume_text = extract_text_from_pdf(pdf_path)

print("Analyzing resume...")
candidate_profile = analyze_resume(resume_text)

print("Creating RAG document...")
document = create_candidate_document(candidate_profile)

print("Chunking document...")
chunks = chunk_text(document)

print("\n----- CHUNKS -----\n")

for i, chunk in enumerate(chunks):
    print(f"\nCHUNK {i + 1}")
    print("-" * 50)
    print(chunk)

print(f"\nTotal chunks created: {len(chunks)}")