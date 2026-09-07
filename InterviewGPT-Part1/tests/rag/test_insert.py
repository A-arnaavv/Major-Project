from app.rag.milvus_store import insert_documents


chunks = [
    "Python is a programming language.",
    "Machine Learning is used for predictive analysis."
]


dense_embeddings = [
    [0.1] * 1024,
    [0.2] * 1024
]


sparse_embeddings = [
    {1: 0.5, 10: 0.8},
    {2: 0.4, 20: 0.9}
]


print("Inserting documents...")

insert_documents(
    chunks,
    dense_embeddings,
    sparse_embeddings
)