from FlagEmbedding import BGEM3FlagModel


# Load BGE-M3 model
model = BGEM3FlagModel(
    "BAAI/bge-m3",
    use_fp16=False
)


def create_embeddings(texts):
    """
    Creates dense and sparse embeddings
    using the BGE-M3 model.
    """

    output = model.encode(
        texts,
        return_dense=True,
        return_sparse=True
    )

    return {
        "dense_embeddings": output["dense_vecs"],
        "sparse_embeddings": output["lexical_weights"]
    }