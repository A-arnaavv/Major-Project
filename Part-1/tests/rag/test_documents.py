from app.resume.parser import extract_text_from_pdf
from app.resume.analyzer import analyze_resume
from app.rag.documents import create_candidate_document


pdf_path = "data/raw/Tanishka latest.pdf"

print("Extracting resume text...")
resume_text = extract_text_from_pdf(pdf_path)

print("Analyzing resume...")
candidate_profile = analyze_resume(resume_text)

print("\nCreating RAG document...")
document = create_candidate_document(candidate_profile)

print("\n----- RAG DOCUMENT -----\n")
print(document)