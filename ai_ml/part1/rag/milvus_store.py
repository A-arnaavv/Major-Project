import hashlib
import re

from pymilvus import DataType, MilvusClient

from ai_ml.part1.paths import MILVUS_DB_PATH


DB_PATH = str(MILVUS_DB_PATH)
COLLECTION_NAME = "candidate_profiles"

client = MilvusClient(DB_PATH)


def get_collection_name(candidate_id: str | None = None) -> str:
    """
    Return the Milvus collection used for a candidate.

    When candidate_id is omitted, the legacy collection name is returned
    for backward compatibility with existing Part 1 tests and utilities.
    """

    if candidate_id is None:
        return COLLECTION_NAME

    candidate_id = candidate_id.strip()

    if not candidate_id:
        raise ValueError("candidate_id must not be empty")

    safe_id = re.sub(
        r"[^A-Za-z0-9_]",
        "_",
        candidate_id,
    ).strip("_")

    if not safe_id:
        safe_id = "candidate"

    digest = hashlib.sha256(
        candidate_id.encode("utf-8")
    ).hexdigest()[:12]

    # Keep collection names bounded and collision-resistant.
    safe_id = safe_id[:40]

    return f"{COLLECTION_NAME}_{safe_id}_{digest}"


def create_collection(
    candidate_id: str | None = None,
) -> str:
    """
    Create a dense + sparse Milvus collection.

    Candidate-specific calls rebuild only that candidate's collection.
    They never drop another candidate's collection.

    Omitting candidate_id preserves the original Part 1 behaviour.
    """

    collection_name = get_collection_name(candidate_id)

    if client.has_collection(collection_name):
        print(
            f"Deleting existing collection: "
            f"{collection_name}"
        )
        client.drop_collection(collection_name)

    schema = client.create_schema(
        auto_id=True,
        enable_dynamic_field=True,
    )

    schema.add_field(
        field_name="id",
        datatype=DataType.INT64,
        is_primary=True,
    )

    schema.add_field(
        field_name="text",
        datatype=DataType.VARCHAR,
        max_length=5000,
    )

    schema.add_field(
        field_name="dense_vector",
        datatype=DataType.FLOAT_VECTOR,
        dim=1024,
    )

    schema.add_field(
        field_name="sparse_vector",
        datatype=DataType.SPARSE_FLOAT_VECTOR,
    )

    client.create_collection(
        collection_name=collection_name,
        schema=schema,
    )

    print(
        f"Hybrid collection '{collection_name}' "
        f"created successfully!"
    )

    return collection_name


def create_indexes(
    candidate_id: str | None = None,
) -> None:
    """
    Create dense and sparse indexes for a candidate collection.
    """

    collection_name = get_collection_name(candidate_id)

    index_params = client.prepare_index_params()

    index_params.add_index(
        field_name="dense_vector",
        index_type="FLAT",
        metric_type="COSINE",
    )

    index_params.add_index(
        field_name="sparse_vector",
        index_type="SPARSE_INVERTED_INDEX",
        metric_type="IP",
    )

    client.create_index(
        collection_name=collection_name,
        index_params=index_params,
    )

    print(
        f"Dense and sparse indexes created successfully "
        f"for '{collection_name}'!"
    )


def insert_documents(
    chunks,
    dense_embeddings,
    sparse_embeddings,
    candidate_id: str | None = None,
):
    """
    Insert text chunks and embeddings into a candidate collection.
    """

    collection_name = get_collection_name(candidate_id)

    data = []

    for i, chunk in enumerate(chunks):
        data.append(
            {
                "text": chunk,
                "dense_vector": dense_embeddings[i],
                "sparse_vector": sparse_embeddings[i],
            }
        )

    result = client.insert(
        collection_name=collection_name,
        data=data,
    )

    print(
        f"{len(chunks)} documents inserted successfully "
        f"into '{collection_name}'!"
    )

    return result