from pathlib import Path
from typing import Any

from ai_ml.integration.part1_to_part2 import build_interview_context
from ai_ml.interview_intelligence.integration_schemas import InterviewContext
from ai_ml.part1.paths import DEFAULT_RESUME_PATH
from ai_ml.part1.rag.chunker import chunk_text
from ai_ml.part1.rag.documents import create_candidate_document
from ai_ml.part1.rag.embeddings import create_embeddings
from ai_ml.part1.rag.milvus_store import (
    create_collection,
    create_indexes,
    insert_documents,
)
from ai_ml.part1.rag.retriever import hybrid_retrieve
from ai_ml.part1.resume.analyzer import analyze_resume
from ai_ml.part1.resume.parser import extract_text_from_pdf
from ai_ml.interview_intelligence.config import (
    DEFAULT_RETRIEVAL_TOP_K,
)

def process_resume(
    pdf_path: str | Path = DEFAULT_RESUME_PATH,
    *,
    candidate_id: str | None = None,
) -> dict[str, Any]:
    """
    Run the complete Part 1 resume-processing pipeline.

    When candidate_id is supplied, the candidate receives an isolated
    Milvus collection. Omitting it preserves legacy Part 1 behaviour.
    """

    resolved_path = Path(pdf_path)

    if not resolved_path.exists():
        raise FileNotFoundError(
            f"Resume PDF not found: {resolved_path}"
        )

    resume_text = extract_text_from_pdf(
        str(resolved_path)
    )

    if not resume_text.strip():
        raise ValueError(
            "Resume PDF contains no extractable text"
        )

    candidate_profile = analyze_resume(resume_text)

    if (
        not isinstance(candidate_profile, dict)
        or not candidate_profile
    ):
        raise ValueError(
            "Resume analysis returned an invalid "
            "candidate profile"
        )

    document = create_candidate_document(
        candidate_profile
    )

    if (
        not isinstance(document, str)
        or not document.strip()
    ):
        raise ValueError(
            "Candidate profile produced an empty "
            "RAG document"
        )

    chunks = chunk_text(document)

    if not chunks:
        raise ValueError(
            "Candidate profile produced no RAG chunks"
        )

    embeddings = create_embeddings(chunks)

    dense_embeddings = embeddings.get(
        "dense_embeddings"
    )
    sparse_embeddings = embeddings.get(
        "sparse_embeddings"
    )

    if (
        dense_embeddings is None
        or sparse_embeddings is None
    ):
        raise ValueError(
            "Embedding pipeline did not return dense "
            "and sparse embeddings"
        )

    if len(dense_embeddings) != len(chunks):
        raise ValueError(
            "Dense embedding count does not match "
            "chunk count"
        )

    if len(sparse_embeddings) != len(chunks):
        raise ValueError(
            "Sparse embedding count does not match "
            "chunk count"
        )

    create_collection(
        candidate_id=candidate_id,
    )

    create_indexes(
        candidate_id=candidate_id,
    )

    insert_documents(
        chunks,
        dense_embeddings,
        sparse_embeddings,
        candidate_id=candidate_id,
    )

    return candidate_profile


def retrieve_interview_context(
    query: str,
    *,
    top_k: int = DEFAULT_RETRIEVAL_TOP_K,
    candidate_id: str | None = None,
) -> list[dict[str, Any]]:
    """
    Retrieve candidate-specific resume context using Hybrid RAG.
    """

    query = query.strip()

    if not query:
        raise ValueError(
            "Retrieval query must not be empty"
        )

    if top_k < 1:
        raise ValueError(
            "top_k must be at least 1"
        )

    return hybrid_retrieve(
        query=query,
        top_k=top_k,
        candidate_id=candidate_id,
    )


def prepare_interview_context(
    *,
    candidate_profile: dict[str, Any],
    topic: str,
    difficulty: str = "medium",
    total_questions: int = 5,
    job_role: str | None = None,
    company_context: str | None = None,
    retrieval_query: str | None = None,
    top_k: int = 5,
    candidate_id: str | None = None,
) -> InterviewContext:
    """
    Convert Part 1 outputs into the InterviewContext consumed by Part 2.
    """

    if not candidate_profile:
        raise ValueError(
            "candidate_profile must not be empty"
        )

    topic = topic.strip()

    if not topic:
        raise ValueError(
            "topic must not be empty"
        )

    query = (
        retrieval_query.strip()
        if retrieval_query
        and retrieval_query.strip()
        else topic
    )

    retrieval_results = retrieve_interview_context(
        query=query,
        top_k=top_k,
        candidate_id=candidate_id,
    )

    return build_interview_context(
        candidate_profile=candidate_profile,
        retrieval_results=retrieval_results,
        topic=topic,
        difficulty=difficulty,
        total_questions=total_questions,
        job_role=job_role,
        company_context=company_context,
    )


def process_resume_for_interview(
    *,
    pdf_path: str | Path = DEFAULT_RESUME_PATH,
    topic: str,
    difficulty: str = "medium",
    total_questions: int = 5,
    job_role: str | None = None,
    company_context: str | None = None,
    retrieval_query: str | None = None,
    top_k: int = 5,
    candidate_id: str | None = None,
) -> tuple[dict[str, Any], InterviewContext]:
    """
    Run Part 1 end-to-end and produce the Part 2 InterviewContext.

    candidate_id isolates the candidate's vector collection.
    """

    candidate_profile = process_resume(
        pdf_path,
        candidate_id=candidate_id,
    )

    interview_context = prepare_interview_context(
        candidate_profile=candidate_profile,
        topic=topic,
        difficulty=difficulty,
        total_questions=total_questions,
        job_role=job_role,
        company_context=company_context,
        retrieval_query=retrieval_query,
        top_k=top_k,
        candidate_id=candidate_id,
    )

    return candidate_profile, interview_context