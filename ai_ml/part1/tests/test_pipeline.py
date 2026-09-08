import pytest

from ai_ml.part1 import pipeline


def test_process_resume_runs_complete_pipeline(
    monkeypatch,
    tmp_path,
):
    resume_path = tmp_path / "resume.pdf"
    resume_path.write_bytes(b"fake pdf")

    candidate_profile = {
        "name": "Test Candidate",
        "technical_skills": ["Python"],
    }

    chunks = [
        "Candidate knows Python.",
        "Candidate built ML projects.",
    ]

    dense_embeddings = [
        [0.1, 0.2],
        [0.3, 0.4],
    ]

    sparse_embeddings = [
        {1: 0.5},
        {2: 0.7},
    ]

    calls = []

    monkeypatch.setattr(
        pipeline,
        "extract_text_from_pdf",
        lambda path: "Resume text",
    )

    monkeypatch.setattr(
        pipeline,
        "analyze_resume",
        lambda text: candidate_profile,
    )

    monkeypatch.setattr(
        pipeline,
        "create_candidate_document",
        lambda profile: "Candidate document",
    )

    monkeypatch.setattr(
        pipeline,
        "chunk_text",
        lambda document: chunks,
    )

    monkeypatch.setattr(
        pipeline,
        "create_embeddings",
        lambda values: {
            "dense_embeddings": dense_embeddings,
            "sparse_embeddings": sparse_embeddings,
        },
    )

    def fake_create_collection(candidate_id=None):
        calls.append(
            ("collection", candidate_id)
        )

    def fake_create_indexes(candidate_id=None):
        calls.append(
            ("indexes", candidate_id)
        )

    def fake_insert(
        inserted_chunks,
        inserted_dense,
        inserted_sparse,
        candidate_id=None,
    ):
        assert inserted_chunks == chunks
        assert inserted_dense == dense_embeddings
        assert inserted_sparse == sparse_embeddings

        calls.append(
            ("insert", candidate_id)
        )

    monkeypatch.setattr(
        pipeline,
        "create_collection",
        fake_create_collection,
    )

    monkeypatch.setattr(
        pipeline,
        "create_indexes",
        fake_create_indexes,
    )

    monkeypatch.setattr(
        pipeline,
        "insert_documents",
        fake_insert,
    )

    result = pipeline.process_resume(
        resume_path,
        candidate_id="candidate-123",
    )

    assert result == candidate_profile

    assert calls == [
        ("collection", "candidate-123"),
        ("indexes", "candidate-123"),
        ("insert", "candidate-123"),
    ]


def test_process_resume_rejects_missing_file(
    tmp_path,
):
    missing_path = tmp_path / "missing.pdf"

    with pytest.raises(
        FileNotFoundError,
        match="Resume PDF not found",
    ):
        pipeline.process_resume(missing_path)


def test_process_resume_rejects_empty_resume(
    monkeypatch,
    tmp_path,
):
    resume_path = tmp_path / "resume.pdf"
    resume_path.write_bytes(b"fake pdf")

    monkeypatch.setattr(
        pipeline,
        "extract_text_from_pdf",
        lambda path: "   ",
    )

    with pytest.raises(
        ValueError,
        match="no extractable text",
    ):
        pipeline.process_resume(resume_path)


def test_retrieve_interview_context(
    monkeypatch,
):
    expected = [
        {
            "id": 1,
            "score": 0.9,
            "text": "Python project experience",
        }
    ]

    captured = {}

    def fake_hybrid_retrieve(
        query,
        top_k,
        candidate_id=None,
    ):
        captured["query"] = query
        captured["top_k"] = top_k
        captured["candidate_id"] = candidate_id

        return expected

    monkeypatch.setattr(
        pipeline,
        "hybrid_retrieve",
        fake_hybrid_retrieve,
    )

    result = pipeline.retrieve_interview_context(
        "Python",
        top_k=5,
        candidate_id="candidate-123",
    )

    assert result == expected
    assert captured == {
        "query": "Python",
        "top_k": 5,
        "candidate_id": "candidate-123",
    }


def test_prepare_interview_context_uses_part1_retrieval(
    monkeypatch,
):
    candidate_profile = {
        "name": "Test Candidate",
        "technical_skills": ["Python"],
    }

    retrieval_results = [
        {
            "id": 1,
            "score": 0.9,
            "text": (
                "Candidate has Python experience."
            ),
        }
    ]

    captured = {}

    def fake_retrieve_interview_context(
        query,
        top_k,
        candidate_id=None,
    ):
        captured["query"] = query
        captured["top_k"] = top_k
        captured["candidate_id"] = candidate_id

        return retrieval_results

    monkeypatch.setattr(
        pipeline,
        "retrieve_interview_context",
        fake_retrieve_interview_context,
    )

    context = pipeline.prepare_interview_context(
        candidate_profile=candidate_profile,
        topic="Python",
        difficulty="medium",
        total_questions=5,
        job_role="Backend Engineer",
        candidate_id="candidate-123",
    )

    assert context.topic == "Python"
    assert context.difficulty == "medium"
    assert context.total_questions == 5
    assert context.job_role == "Backend Engineer"

    assert "Test Candidate" in context.resume_context

    assert (
        "Candidate has Python experience."
        in context.retrieved_context
    )

    assert captured == {
        "query": "Python",
        "top_k": 5,
        "candidate_id": "candidate-123",
    }


def test_process_resume_for_interview(
    monkeypatch,
):
    candidate_profile = {
        "name": "Test Candidate",
    }

    expected_context = object()

    captured = {
        "process_candidate_id": None,
        "context_candidate_id": None,
    }

    def fake_process_resume(
        pdf_path,
        *,
        candidate_id=None,
    ):
        captured["process_candidate_id"] = (
            candidate_id
        )

        return candidate_profile

    def fake_prepare_interview_context(
        **kwargs,
    ):
        captured["context_candidate_id"] = (
            kwargs.get("candidate_id")
        )

        return expected_context

    monkeypatch.setattr(
        pipeline,
        "process_resume",
        fake_process_resume,
    )

    monkeypatch.setattr(
        pipeline,
        "prepare_interview_context",
        fake_prepare_interview_context,
    )

    profile, context = (
        pipeline.process_resume_for_interview(
            pdf_path="resume.pdf",
            topic="Machine Learning",
            candidate_id="candidate-123",
        )
    )

    assert profile == candidate_profile
    assert context is expected_context

    assert (
        captured["process_candidate_id"]
        == "candidate-123"
    )

    assert (
        captured["context_candidate_id"]
        == "candidate-123"
    )