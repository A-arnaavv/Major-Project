from typing import Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from ai_ml.interview_intelligence.session import InterviewSession


app = FastAPI(
    title="InterviewGPT - Interview Intelligence API",
    version="0.1.0"
)

sessions: Dict[str, InterviewSession] = {}


class StartInterviewRequest(BaseModel):
    session_id: str
    topic: str
    difficulty: str = "medium"
    total_questions: int = 5

    resume_context: str | None = None
    job_role: str | None = None
    company_context: str | None = None
    retrieved_context: str | None = None


class SubmitAnswerRequest(BaseModel):
    session_id: str
    candidate_answer: str


@app.get("/")
def root():
    return {
        "status": "running",
        "service": "Interview Intelligence API"
    }


@app.post("/interview/start")
def start_interview(data: StartInterviewRequest):

    if data.session_id in sessions:
        raise HTTPException(
            status_code=400,
            detail="Session already exists"
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

    sessions[data.session_id] = session

    try:
        question = session.generate_next_question()

    except (ValueError, RuntimeError) as exc:
        sessions.pop(data.session_id, None)

        raise HTTPException(
            status_code=500,
            detail=str(exc)
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

    session = sessions.get(data.session_id)

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    try:
        result = session.submit_answer(
            candidate_answer=data.candidate_answer
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc)
        )

    if session.is_complete():

        try:
            numerical_report = session.get_final_report()
            ai_summary = session.get_ai_performance_summary()
            learning_plan = session.get_learning_plan()

        except RuntimeError as exc:
            raise HTTPException(
                status_code=503,
                detail=str(exc)
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
            }
        }

    try:
        next_question = session.generate_next_question()

    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc)
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
        }
    }


@app.get("/interview/{session_id}/next")
def next_question(session_id: str):

    session = sessions.get(session_id)

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    if session.is_complete():
        raise HTTPException(
            status_code=400,
            detail="Interview is already complete"
        )

    try:
        question = session.generate_next_question()

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc)
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

    session = sessions.get(session_id)

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    try:
        numerical_report = session.get_final_report()
        ai_summary = session.get_ai_performance_summary()
        learning_plan = session.get_learning_plan()

    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc)
        )

    return {
        "session_id": session_id,
        "numerical_report": numerical_report,
        "ai_summary": ai_summary.model_dump(),
        "learning_plan": learning_plan,
    }