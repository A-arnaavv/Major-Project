from pymilvus import MilvusClient


print("Connecting to Milvus...")

client = MilvusClient(
    "data/milvus.db"
)


print("Milvus connected successfully!")

print("\nCollections:")

collections = client.list_collections()

print(collections)