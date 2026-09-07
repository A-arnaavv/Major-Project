import json

from ai_ml.part1.paths import CANDIDATE_PROFILE_PATH
from ai_ml.part1.rag.documents import create_candidate_document
from ai_ml.part1.rag.chunker import chunk_text


def load_candidate_profile():
    assert CANDIDATE_PROFILE_PATH.exists()

    with open(CANDIDATE_PROFILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_chunk_text_creates_multiple_nonempty_chunks():
    candidate_profile = load_candidate_profile()

    document = create_candidate_document(candidate_profile)
    chunks = chunk_text(document)

    assert chunks
    assert len(chunks) > 1

    for chunk in chunks:
        assert isinstance(chunk, str)
        assert chunk.strip()


def test_chunk_text_respects_custom_chunk_size():
    text = " ".join(["machine-learning"] * 1000)

    chunks = chunk_text(
        text,
        chunk_size=200,
        overlap=50,
    )

    assert chunks
    assert len(chunks) > 1
