import json

from ai_ml.part1.paths import CANDIDATE_PROFILE_PATH
from ai_ml.part1.rag.documents import create_candidate_document


def load_candidate_profile():
    assert CANDIDATE_PROFILE_PATH.exists()

    with open(CANDIDATE_PROFILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_create_candidate_document_returns_nonempty_text():
    candidate_profile = load_candidate_profile()

    document = create_candidate_document(candidate_profile)

    assert isinstance(document, str)
    assert document.strip()
    assert len(document) > 100


def test_create_candidate_document_contains_profile_information():
    candidate_profile = load_candidate_profile()

    document = create_candidate_document(candidate_profile)

    name = candidate_profile.get("name")

    if name:
        assert name.lower() in document.lower()

    assert (
        "technical" in document.lower()
        or "skills" in document.lower()
    )
