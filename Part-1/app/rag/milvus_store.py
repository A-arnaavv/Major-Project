from pymilvus import MilvusClient, DataType


DB_PATH = "data/milvus.db"
COLLECTION_NAME = "candidate_profiles"


# Connect to Milvus
client = MilvusClient(DB_PATH)


def create_collection():
    """
    Creates the Milvus collection for storing
    dense and sparse embeddings.
    """

    # Delete collection if it already exists
    if client.has_collection(COLLECTION_NAME):
        print(f"Deleting existing collection: {COLLECTION_NAME}")
        client.drop_collection(COLLECTION_NAME)

    # Create schema
    schema = client.create_schema(
        auto_id=True,
        enable_dynamic_field=True
    )

    # Primary key
    schema.add_field(
        field_name="id",
        datatype=DataType.INT64,
        is_primary=True
    )

    # Original text chunk
    schema.add_field(
        field_name="text",
        datatype=DataType.VARCHAR,
        max_length=5000
    )

    # Dense vector from BGE-M3
    schema.add_field(
        field_name="dense_vector",
        datatype=DataType.FLOAT_VECTOR,
        dim=1024
    )

    # Sparse vector from BGE-M3
    schema.add_field(
        field_name="sparse_vector",
        datatype=DataType.SPARSE_FLOAT_VECTOR
    )

    # Create collection
    client.create_collection(
        collection_name=COLLECTION_NAME,
        schema=schema
    )

    print(
        f"Hybrid collection '{COLLECTION_NAME}' "
        f"created successfully!"
    )


def create_indexes():
    """
    Creates indexes for dense and sparse vectors.
    """

    index_params = client.prepare_index_params()

    # Dense vector index
    index_params.add_index(
        field_name="dense_vector",
        index_type="FLAT",
        metric_type="COSINE"
    )

    # Sparse vector index
    index_params.add_index(
        field_name="sparse_vector",
        index_type="SPARSE_INVERTED_INDEX",
        metric_type="IP"
    )

    # Create indexes
    client.create_index(
        collection_name=COLLECTION_NAME,
        index_params=index_params
    )

    print("Dense and sparse indexes created successfully!")


def insert_documents(chunks, dense_embeddings, sparse_embeddings):
    """
    Inserts text chunks along with dense and sparse
    embeddings into the Milvus collection.
    """

    data = []

    for i, chunk in enumerate(chunks):

        data.append({
            "text": chunk,
            "dense_vector": dense_embeddings[i],
            "sparse_vector": sparse_embeddings[i]
        })

    result = client.insert(
        collection_name=COLLECTION_NAME,
        data=data
    )

    print(f"{len(chunks)} documents inserted successfully!")

    return result