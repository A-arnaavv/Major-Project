from ai_ml.part1.rag.embeddings import create_embeddings


def test_sparse_embeddings_are_created():
    texts = [
        "Python machine learning natural language processing",
        "TensorFlow Scikit-learn model evaluation",
    ]

    embeddings = create_embeddings(texts)

    sparse_embeddings = embeddings["sparse_embeddings"]

    assert len(sparse_embeddings) == len(texts)

    for sparse_vector in sparse_embeddings:
        assert sparse_vector is not None
        assert len(sparse_vector) > 0
