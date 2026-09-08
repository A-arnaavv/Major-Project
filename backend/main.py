from pathlib import Path
import tempfile
from typing import Literal

from fastapi import (
    FastAPI,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from pydantic import (
    BaseModel,
    Field,
    field_validator,
)

from ai_ml.interview_intelligence.analytics_exporter import (
    export_interview_summary,
    export_question_records,
)
from ai_ml.interview_intelligence.config import (
    LLM_MODE,
    MAX_INTERVIEW_QUESTIONS,
    MAX_RESUME_SIZE_BYTES,
    MAX_RESUME_SIZE_MB,
)
from ai_ml.interview_intelligence.session import (
    InterviewSession,
)
from ai_ml.part1.pipeline import (
    process_resume_for_interview,
)
from backend.session_store import (
    session_store,
)
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="InterviewGPT - Interview Intelligence API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StartInterviewRequest(BaseModel):
    session_id: str = Field(
        min_length=1
    )

    topic: str = Field(
        min_length=1
    )

    difficulty: Literal[
        "easy",
        "medium",
        "hard",
    ] = "medium"

    total_questions: int = Field(
        default=5,
        ge=1,
        le=MAX_INTERVIEW_QUESTIONS,
    )

    resume_context: str | None = None
    job_role: str | None = None
    company_context: str | None = None
    retrieved_context: str | None = None

    @field_validator(
        "session_id",
        "topic",
    )
    @classmethod
    def validate_required_text(
        cls,
        value: str,
    ) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "must not be empty or whitespace"
            )

        return value


class SubmitAnswerRequest(BaseModel):
    session_id: str = Field(
        min_length=1
    )

    candidate_answer: str

    @field_validator("session_id")
    @classmethod
    def validate_session_id(
        cls,
        value: str,
    ) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "must not be empty or whitespace"
            )

        return value


@app.get("/")
def root():
    return {
        "status": "running",
        "service": (
            "Interview Intelligence API"
        ),
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": (
            "Interview Intelligence API"
        ),
        "version": "0.1.0",
        "llm_mode": LLM_MODE,
    }


@app.post(
    "/interview/start-from-resume"
)
def start_interview_from_resume(
    session_id: str = Form(...),
    topic: str = Form(...),
    resume: UploadFile = File(...),
    difficulty: Literal[
        "easy",
        "medium",
        "hard",
    ] = Form("medium"),
    total_questions: int = Form(5),
    job_role: str | None = Form(None),
    company_context: str | None = Form(
        None
    ),
):
    session_id = session_id.strip()
    topic = topic.strip()

    if not session_id:
        raise HTTPException(
            status_code=422,
            detail=(
                "session_id must not be empty"
            ),
        )

    if not topic:
        raise HTTPException(
            status_code=422,
            detail=(
                "topic must not be empty"
            ),
        )

    if (
        total_questions < 1
        or total_questions > MAX_INTERVIEW_QUESTIONS
    ):
        raise HTTPException(
            status_code=422,
            detail=(
                "total_questions must be between "
                f"1 and {MAX_INTERVIEW_QUESTIONS}"
            ),
        )

    if session_store.exists(
        session_id
    ):
        raise HTTPException(
            status_code=400,
            detail="Session already exists",
        )

    filename = resume.filename or ""

    if not filename.lower().endswith(
        ".pdf"
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Resume must be a PDF file"
            ),
        )

    temporary_path: Path | None = None

    try:
        uploaded_bytes = 0

        with tempfile.NamedTemporaryFile(
            suffix=".pdf",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(
                temporary_file.name
            )

            while chunk := resume.file.read(
                1024 * 1024
            ):
                uploaded_bytes += len(chunk)

                if uploaded_bytes > MAX_RESUME_SIZE_BYTES:
                    raise HTTPException(
                        status_code=413,
                        detail=(
                            "Resume PDF exceeds maximum "
                            f"size of {MAX_RESUME_SIZE_MB} MB"
                        ),
                    )

                temporary_file.write(
                    chunk
                )

        candidate_profile, context = (
            process_resume_for_interview(
                pdf_path=temporary_path,
                topic=topic,
                difficulty=difficulty,
                total_questions=(
                    total_questions
                ),
                job_role=job_role,
                company_context=(
                    company_context
                ),
                candidate_id=session_id,
            )
        )

        session = InterviewSession(
            topic=context.topic,
            difficulty=context.difficulty,
            total_questions=(
                context.total_questions
            ),
            resume_context=(
                context.resume_context
            ),
            job_role=context.job_role,
            company_context=(
                context.company_context
            ),
            retrieved_context=(
                context.retrieved_context
            ),
        )

        session_store.create(
            session_id=session_id,
            session=session,
        )

        question = (
            session.generate_next_question()
        )

        # Persist the generated pending
        # question so it survives restart.
        session_store.save(
            session_id,
            session,
        )

    except HTTPException:
        session_store.delete(
            session_id
        )
        raise

    except FileNotFoundError as exc:
        session_store.delete(
            session_id
        )

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except ValueError as exc:
        session_store.delete(
            session_id
        )

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except RuntimeError as exc:
        session_store.delete(
            session_id
        )

        raise HTTPException(
            status_code=503,
            detail=str(exc),
        )

    except Exception:
        session_store.delete(
            session_id
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Resume processing failed"
            ),
        )

    finally:
        resume.file.close()

        if temporary_path is not None:
            temporary_path.unlink(
                missing_ok=True
            )

    return {
        "session_id": session_id,
        "status": "started",
        "candidate_profile": (
            candidate_profile
        ),
        "question": question.question,
        "difficulty": question.difficulty,
        "topic": question.topic,
        "subtopic": question.subtopic,
    }


@app.post("/interview/start")
def start_interview(
    data: StartInterviewRequest,
):
    if session_store.exists(
        data.session_id
    ):
        raise HTTPException(
            status_code=400,
            detail="Session already exists",
        )

    session = InterviewSession(
        topic=data.topic,
        difficulty=data.difficulty,
        total_questions=(
            data.total_questions
        ),
        resume_context=(
            data.resume_context
        ),
        job_role=data.job_role,
        company_context=(
            data.company_context
        ),
        retrieved_context=(
            data.retrieved_context
        ),
    )

    try:
        session_store.create(
            session_id=data.session_id,
            session=session,
        )

        question = (
            session.generate_next_question()
        )

        # Persist the pending question.
        session_store.save(
            data.session_id,
            session,
        )

    except ValueError as exc:
        session_store.delete(
            data.session_id
        )

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except RuntimeError as exc:
        session_store.delete(
            data.session_id
        )

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
def submit_answer(
    data: SubmitAnswerRequest,
):
    session = session_store.get(
        data.session_id
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    try:
        result = session.submit_answer(
            candidate_answer=(
                data.candidate_answer
            )
        )

        # Persist the answer immediately.
        #
        # This is done before report generation
        # or generation of the next question so
        # the submitted answer is never lost if
        # a later LLM operation fails.
        session_store.save(
            data.session_id,
            session,
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
            numerical_report = (
                session.get_final_report()
            )

            ai_summary = (
                session
                .get_ai_performance_summary()
            )

            learning_plan = (
                session.get_learning_plan()
            )

        except RuntimeError as exc:
            raise HTTPException(
                status_code=503,
                detail=str(exc),
            )

        return {
            "session_id": (
                data.session_id
            ),
            "status": "completed",
            "evaluation": (
                result["evaluation"]
            ),
            "next_difficulty": (
                result["next_difficulty"]
            ),
            "final_report": {
                "numerical_report": (
                    numerical_report
                ),
                "ai_summary": (
                    ai_summary.model_dump()
                ),
                "learning_plan": (
                    learning_plan
                ),
            },
        }

    try:
        next_question = (
            session.generate_next_question()
        )

        # Persist the newly generated
        # pending question.
        session_store.save(
            data.session_id,
            session,
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

    return {
        "session_id": data.session_id,
        "status": "in_progress",
        "evaluation": (
            result["evaluation"]
        ),
        "next_difficulty": (
            result["next_difficulty"]
        ),
        "next_question": {
            "question": (
                next_question.question
            ),
            "difficulty": (
                next_question.difficulty
            ),
            "topic": (
                next_question.topic
            ),
            "subtopic": (
                next_question.subtopic
            ),
        },
    }


@app.get(
    "/interview/{session_id}/next"
)
def next_question(
    session_id: str,
):
    session_id = session_id.strip()

    if not session_id:
        raise HTTPException(
            status_code=422,
            detail=(
                "session_id must not be empty"
            ),
        )

    session = session_store.get(
        session_id
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    if session.is_complete():
        raise HTTPException(
            status_code=400,
            detail=(
                "Interview is already complete"
            ),
        )

    # A pending question normally already
    # exists because it is created by:
    #
    # - POST /interview/start
    # - POST /interview/start-from-resume
    # - POST /interview/answer
    #
    # Return the existing question instead
    # of accidentally skipping it.
    question = (
        session.current_question
    )

    if question is None:
        try:
            question = (
                session
                .generate_next_question()
            )

            # Persist a question generated
            # through this recovery route.
            session_store.save(
                session_id,
                session,
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

    return {
        "session_id": session_id,
        "question": question.question,
        "difficulty": (
            question.difficulty
        ),
        "topic": question.topic,
        "subtopic": question.subtopic,
    }


@app.get(
    "/interview/{session_id}/report"
)
def get_report(
    session_id: str,
):
    session = session_store.get(
        session_id
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    try:
        numerical_report = (
            session.get_final_report()
        )

        ai_summary = (
            session
            .get_ai_performance_summary()
        )

        learning_plan = (
            session.get_learning_plan()
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        )

    return {
        "session_id": session_id,
        "numerical_report": (
            numerical_report
        ),
        "ai_summary": (
            ai_summary.model_dump()
        ),
        "learning_plan": (
            learning_plan
        ),
    }


@app.get(
    "/interview/{session_id}/analytics"
)
def get_analytics(
    session_id: str,
):
    session = session_store.get(
        session_id
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    try:
        history = (
            session.get_history()
        )

        question_records = (
            export_question_records(
                session_id=session_id,
                history=history,
            )
        )

        numerical_report = (
            session.get_final_report()
        )

        ai_summary = (
            session
            .get_ai_performance_summary()
        )

        learning_plan = (
            session.get_learning_plan()
        )

        summary = (
            export_interview_summary(
                session_id=session_id,
                numerical_report=(
                    numerical_report
                ),
                ai_summary=ai_summary,
                learning_plan=(
                    learning_plan
                ),
            )
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
        "summary": (
            summary.model_dump()
        ),
    }