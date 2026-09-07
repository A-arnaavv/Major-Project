import pytest

from ai_ml.interview_intelligence.session import InterviewSession
from backend.session_store import SessionStore


def create_test_session():
    return InterviewSession(
        topic="Machine Learning",
        difficulty="medium",
        total_questions=1,
    )


def test_create_and_get_session():
    store = SessionStore()

    session = create_test_session()

    store.create(
        session_id="candidate_001",
        session=session,
    )

    retrieved = store.get("candidate_001")

    assert retrieved is session


def test_session_exists():
    store = SessionStore()

    session = create_test_session()

    store.create(
        session_id="candidate_001",
        session=session,
    )

    assert store.exists("candidate_001") is True
    assert store.exists("missing_session") is False


def test_duplicate_session_rejected():
    store = SessionStore()

    store.create(
        session_id="candidate_001",
        session=create_test_session(),
    )

    with pytest.raises(
        ValueError,
        match="Session already exists",
    ):
        store.create(
            session_id="candidate_001",
            session=create_test_session(),
        )


def test_delete_session():
    store = SessionStore()

    store.create(
        session_id="candidate_001",
        session=create_test_session(),
    )

    store.delete("candidate_001")

    assert store.get("candidate_001") is None
    assert store.exists("candidate_001") is False


def test_delete_missing_session_is_safe():
    store = SessionStore()

    store.delete("missing_session")

    assert store.get("missing_session") is None


def test_clear_sessions():
    store = SessionStore()

    store.create(
        session_id="candidate_001",
        session=create_test_session(),
    )

    store.create(
        session_id="candidate_002",
        session=create_test_session(),
    )

    store.clear()

    assert store.get("candidate_001") is None
    assert store.get("candidate_002") is None