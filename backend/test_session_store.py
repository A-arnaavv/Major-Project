import pytest

from ai_ml.interview_intelligence.session import (
    InterviewSession,
)
from backend.session_store import (
    SessionStore,
)


def create_test_session():
    return InterviewSession(
        topic="Machine Learning",
        difficulty="medium",
        total_questions=3,
    )


@pytest.fixture
def store(tmp_path):
    """
    Give every test its own isolated persistent
    session directory.

    This prevents one test's persisted session
    from affecting another test.
    """
    return SessionStore(
        storage_dir=tmp_path / "sessions"
    )


def test_create_and_get_session(
    store,
):
    session = create_test_session()

    store.create(
        session_id="candidate_001",
        session=session,
    )

    stored_session = store.get(
        "candidate_001"
    )

    assert stored_session is session


def test_session_exists(
    store,
):
    session = create_test_session()

    store.create(
        session_id="candidate_001",
        session=session,
    )

    assert store.exists(
        "candidate_001"
    )

    assert not store.exists(
        "candidate_999"
    )


def test_duplicate_session_rejected(
    store,
):
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


def test_delete_session(
    store,
):
    store.create(
        session_id="candidate_001",
        session=create_test_session(),
    )

    assert store.exists(
        "candidate_001"
    )

    store.delete(
        "candidate_001"
    )

    assert not store.exists(
        "candidate_001"
    )

    assert (
        store.get(
            "candidate_001"
        )
        is None
    )


def test_delete_missing_session_is_safe(
    store,
):
    store.delete(
        "missing-session"
    )

    assert not store.exists(
        "missing-session"
    )


def test_clear_sessions(
    store,
):
    store.create(
        session_id="candidate_001",
        session=create_test_session(),
    )

    store.create(
        session_id="candidate_002",
        session=create_test_session(),
    )

    assert store.exists(
        "candidate_001"
    )

    assert store.exists(
        "candidate_002"
    )

    store.clear()

    assert not store.exists(
        "candidate_001"
    )

    assert not store.exists(
        "candidate_002"
    )

    assert (
        store.get(
            "candidate_001"
        )
        is None
    )

    assert (
        store.get(
            "candidate_002"
        )
        is None
    )


def test_session_can_be_loaded_by_new_store(
    tmp_path,
):
    """
    Explicitly verify persistence across
    SessionStore instances.
    """
    storage_dir = (
        tmp_path
        / "persistent-sessions"
    )

    first_store = SessionStore(
        storage_dir=storage_dir
    )

    session = create_test_session()

    session.generate_next_question()

    first_store.create(
        session_id="candidate_001",
        session=session,
    )

    first_store.save(
        "candidate_001",
        session,
    )

    second_store = SessionStore(
        storage_dir=storage_dir
    )

    restored = second_store.get(
        "candidate_001"
    )

    assert restored is not None

    assert restored.topic == (
        session.topic
    )

    assert (
        restored.current_difficulty
        == session.current_difficulty
    )

    assert (
        restored.total_questions
        == session.total_questions
    )

    assert (
        restored.current_question
        is not None
    )

    assert (
        restored.current_question.question
        == session.current_question.question
    )