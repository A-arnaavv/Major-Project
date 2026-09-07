from ai_ml.part1.rag.embeddings import create_embeddings


def test_create_embeddings_returns_dense_and_sparse_vectors():
    texts = [
        "Machine learning and natural language processing",
        "Python TensorFlow Scikit-learn",
    ]

    embeddings = create_embeddings(texts)

    assert "dense_embeddings" in embeddings
    assert "sparse_embeddings" in embeddings

    dense_embeddings = embeddings["dense_embeddings"]
    sparse_embeddings = embeddings["sparse_embeddings"]

    assert len(dense_embeddings) == len(texts)
    assert len(sparse_embeddings) == len(texts)

    assert len(dense_embeddings[0]) == 1024
    assert len(dense_embeddings[1]) == 1024
