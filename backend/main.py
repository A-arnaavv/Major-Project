from typing import Dict, List

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
        total_questions=data.total_questions
    )

    sessions[data.session_id] = session

    question = session.generate_next_question()

    return {
        "session_id": data.session_id,
        "question": question.question,
        "difficulty": question.difficulty,
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

    if session.is_complete():

        numerical_report = session.get_final_report()
        ai_summary = session.get_ai_performance_summary()

        return {
            "status": "completed",
            "evaluation": result["evaluation"],
            "next_difficulty": result["next_difficulty"],
            "final_report": {
                "numerical_report": numerical_report,
                "ai_summary": ai_summary.model_dump()
            }
        }

    next_question = session.generate_next_question()

    return {
        "status": "in_progress",
        "evaluation": result["evaluation"],
        "next_difficulty": result["next_difficulty"],
        "next_question": {
            "question": next_question.question,
            "difficulty": next_question.difficulty
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

    question = session.generate_next_question()

    return {
        "question": question.question,
        "difficulty": question.difficulty
    }


@app.get("/interview/{session_id}/report")
def get_report(session_id: str):

    session = sessions.get(session_id)

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    numerical_report = session.get_final_report()
    ai_summary = session.get_ai_performance_summary()

    return {
        "numerical_report": numerical_report,
        "ai_summary": ai_summary.model_dump()
    }