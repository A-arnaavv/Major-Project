from typing import Dict, Optional

from ai_ml.interview_intelligence.session import InterviewSession


class SessionStore:
    """
    In-memory session storage abstraction.

    This keeps storage logic separate from the FastAPI routes so the
    implementation can later be replaced by a database-backed store.
    """

    def __init__(self):
        self._sessions: Dict[str, InterviewSession] = {}

    def create(
        self,
        session_id: str,
        session: InterviewSession,
    ) -> None:
        if session_id in self._sessions:
            raise ValueError("Session already exists")

        self._sessions[session_id] = session

    def get(
        self,
        session_id: str,
    ) -> Optional[InterviewSession]:
        return self._sessions.get(session_id)

    def delete(
        self,
        session_id: str,
    ) -> None:
        self._sessions.pop(session_id, None)

    def exists(
        self,
        session_id: str,
    ) -> bool:
        return session_id in self._sessions

    def clear(self) -> None:
        self._sessions.clear()


session_store = SessionStore()