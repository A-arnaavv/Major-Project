from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

from ai_ml.interview_intelligence.session import InterviewSession
from ai_ml.interview_intelligence.analytics_exporter import (
    export_question_records,
    export_interview_summary,
)
from ai_ml.interview_intelligence.config import LLM_MODE
from backend.session_store import session_store


app = FastAPI(
    title="InterviewGPT - Interview Intelligence API",
    version="0.1.0",
)


class StartInterviewRequest(BaseModel):
    session_id: str = Field(min_length=1)
    topic: str = Field(min_length=1)

    difficulty: Literal["easy", "medium", "hard"] = "medium"

    total_questions: int = Field(
        default=5,
        ge=1,
        le=20,
    )

    resume_context: str | None = None
    job_role: str | None = None
    company_context: str | None = None
    retrieved_context: str | None = None

    @field_validator("session_id", "topic")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("must not be empty or whitespace")

        return value


class SubmitAnswerRequest(BaseModel):
    session_id: str = Field(min_length=1)
    candidate_answer: str


@app.get("/")
def root():
    return {
        "status": "running",
        "service": "Interview Intelligence API",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "Interview Intelligence API",
        "version": "0.1.0",
        "llm_mode": LLM_MODE,
    }


@app.post("/interview/start")
def start_interview(data: StartInterviewRequest):
    if session_store.exists(data.session_id):
        raise HTTPException(
            status_code=400,
            detail="Session already exists",
        )

    session = InterviewSession(
        topic=data.topic,
        difficulty=data.difficulty,
        total_questions=data.total_questions,
        resume_context=data.resume_context,
        job_role=data.job_role,
        company_context=data.company_context,
        retrieved_context=data.retrieved_context,
    )

    try:
        session_store.create(
            session_id=data.session_id,
            session=session,
        )

        question = session.generate_next_question()

    except ValueError as exc:
        session_store.delete(data.session_id)

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except RuntimeError as exc:
        session_store.delete(data.session_id)

        raise HTTPException(
            status_code=503,
            detail=str(exc),
        )

    return {
        "session_id": data.session_id,
        "status": "started",
        "question": question.question,
        "difficulty": question.difficulty,
        "topic": question.topic,
        "subtopic": question.subtopic,
    }


@app.post("/interview/answer")
def submit_answer(data: SubmitAnswerRequest):
    session = session_store.get(data.session_id)

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    try:
        result = session.submit_answer(
            candidate_answer=data.candidate_answer
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        )

    if session.is_complete():
        try:
            numerical_report = session.get_final_report()
            ai_summary = session.get_ai_performance_summary()
            learning_plan = session.get_learning_plan()

        except RuntimeError as exc:
            raise HTTPException(
                status_code=503,
                detail=str(exc),
            )

        return {
            "session_id": data.session_id,
            "status": "completed",
            "evaluation": result["evaluation"],
            "next_difficulty": result["next_difficulty"],
            "final_report": {
                "numerical_report": numerical_report,
                "ai_summary": ai_summary.model_dump(),
                "learning_plan": learning_plan,
            },
        }

    try:
        next_question = session.generate_next_question()

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        )

    return {
        "session_id": data.session_id,
        "status": "in_progress",
        "evaluation": result["evaluation"],
        "next_difficulty": result["next_difficulty"],
        "next_question": {
            "question": next_question.question,
            "difficulty": next_question.difficulty,
            "topic": next_question.topic,
            "subtopic": next_question.subtopic,
        },
    }


@app.get("/interview/{session_id}/next")
def next_question(session_id: str):
    session = session_store.get(session_id)

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    if session.is_complete():
        raise HTTPException(
            status_code=400,
            detail="Interview is already complete",
        )

    # A question is normally already generated by either:
    # - POST /interview/start
    # - POST /interview/answer
    #
    # Return that pending question instead of generating another one.
    question = session.current_question

    if question is None:
        try:
            question = session.generate_next_question()

        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail=str(exc),
            )

        except RuntimeError as exc:
            raise HTTPException(
                status_code=503,
                detail=str(exc),
            )

    return {
        "session_id": session_id,
        "question": question.question,
        "difficulty": question.difficulty,
        "topic": question.topic,
        "subtopic": question.subtopic,
    }


@app.get("/interview/{session_id}/report")
def get_report(session_id: str):
    session = session_store.get(session_id)

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    try:
        numerical_report = session.get_final_report()
        ai_summary = session.get_ai_performance_summary()
        learning_plan = session.get_learning_plan()

    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        )

    return {
        "session_id": session_id,
        "numerical_report": numerical_report,
        "ai_summary": ai_summary.model_dump(),
        "learning_plan": learning_plan,
    }


@app.get("/interview/{session_id}/analytics")
def get_analytics(session_id: str):
    session = session_store.get(session_id)

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    try:
        history = session.get_history()

        question_records = export_question_records(
            session_id=session_id,
            history=history,
        )

        numerical_report = session.get_final_report()
        ai_summary = session.get_ai_performance_summary()
        learning_plan = session.get_learning_plan()

        summary = export_interview_summary(
            session_id=session_id,
            numerical_report=numerical_report,
            ai_summary=ai_summary,
            learning_plan=learning_plan,
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        )

    return {
        "session_id": session_id,
        "question_records": [
            record.model_dump()
            for record in question_records
        ],
        "summary": summary.model_dump(),
    }