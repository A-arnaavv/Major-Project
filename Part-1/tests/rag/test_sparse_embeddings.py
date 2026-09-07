from app.resume.parser import extract_text_from_pdf
from app.resume.analyzer import analyze_resume
from app.rag.documents import create_candidate_document
from app.rag.chunker import chunk_text

from FlagEmbedding import BGEM3FlagModel


print("Loading BGE-M3 model...")

model = BGEM3FlagModel(
    "BAAI/bge-m3",
    use_fp16=True
)


# Step 1: Extract resume
print("\nExtracting resume text...")

resume_text = extract_text_from_pdf(
    "data/raw/Tanishka latest.pdf"
)


# Step 2: Analyze resume
print("Analyzing resume...")

candidate_profile = analyze_resume(resume_text)


# Step 3: Create RAG document
print("Creating RAG document...")



# Step 4: Chunk document
print("Chunking document...")

document = create_candidate_document(candidate_profile)

chunks = chunk_text(document)

print(f"Total chunks: {len(chunks)}")


# Step 5: Create sparse embeddings
print("\nCreating sparse embeddings...")

output = model.encode(
    chunks,
    return_dense=False,
    return_sparse=True
)


sparse_embeddings = output["lexical_weights"]


print("\n----- SPARSE EMBEDDING INFO -----")

print(f"Sparse embeddings created: {len(sparse_embeddings)}")


print("\nFirst sparse embedding:")

print(sparse_embeddings[0])


print("\nSparse embeddings created successfully!")