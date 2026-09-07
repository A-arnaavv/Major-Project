from FlagEmbedding import BGEM3FlagModel


_model = None


def get_embedding_model():
    """
    Lazily loads and caches the BGE-M3 model.

    The model is loaded only when embeddings are actually required,
    rather than during module import or pytest collection.
    """
    global _model

    if _model is None:
        print("Loading BGE-M3 embedding model...")

        _model = BGEM3FlagModel(
            "BAAI/bge-m3",
            use_fp16=False,
        )

    return _model


def create_embeddings(texts):
    """
    Creates dense and sparse embeddings using BGE-M3.
    """

    model = get_embedding_model()

    output = model.encode(
        texts,
        return_dense=True,
        return_sparse=True,
    )

    return {
        "dense_embeddings": output["dense_vecs"],
        "sparse_embeddings": output["lexical_weights"],
    }