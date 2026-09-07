from app.rag.milvus_store import create_collection, create_indexes


print("Creating Hybrid Milvus collection...")

create_collection()

print("Creating indexes...")

create_indexes()