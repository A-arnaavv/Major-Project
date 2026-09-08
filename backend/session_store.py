import hashlib
import json
import os
from pathlib import Path
from typing import Dict, Optional

from ai_ml.interview_intelligence.session import (
    InterviewSession,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_SESSION_DIR = (
    PROJECT_ROOT
    / "data"
    / "sessions"
)


class SessionStore:
    """
    Interview session storage with:

    - an in-memory cache for active sessions
    - JSON persistence for restart recovery

    The persisted files contain only serializable interview state.
    Runtime objects such as orchestrators and LLM clients are rebuilt
    when a session is restored.
    """

    def __init__(
        self,
        storage_dir: str | Path | None = None,
    ):
        configured_dir = os.getenv(
            "INTERVIEWGPT_SESSION_DIR"
        )

        if storage_dir is not None:
            self.storage_dir = Path(
                storage_dir
            )
        elif configured_dir:
            self.storage_dir = Path(
                configured_dir
            )
        else:
            self.storage_dir = (
                DEFAULT_SESSION_DIR
            )

        self.storage_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._sessions: Dict[
            str,
            InterviewSession,
        ] = {}

    def _session_path(
        self,
        session_id: str,
    ) -> Path:
        """
        Build a filesystem-safe path without exposing session_id
        directly as a filename.
        """

        digest = hashlib.sha256(
            session_id.encode("utf-8")
        ).hexdigest()

        return (
            self.storage_dir
            / f"{digest}.json"
        )

    def create(
        self,
        session_id: str,
        session: InterviewSession,
    ) -> None:
        if self.exists(session_id):
            raise ValueError(
                "Session already exists"
            )

        self._sessions[
            session_id
        ] = session

        self.save(
            session_id,
            session,
        )

    def save(
        self,
        session_id: str,
        session: InterviewSession | None = None,
    ) -> None:
        """
        Persist the latest session state atomically.
        """

        if session is None:
            session = self._sessions.get(
                session_id
            )

        if session is None:
            raise ValueError(
                "Session not found"
            )

        self._sessions[
            session_id
        ] = session

        payload = {
            "session_id": session_id,
            "state": session.to_state(),
        }

        path = self._session_path(
            session_id
        )

        temporary_path = path.with_suffix(
            ".tmp"
        )

        with temporary_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                payload,
                file,
                indent=2,
                ensure_ascii=False,
            )

        temporary_path.replace(path)

    def get(
        self,
        session_id: str,
    ) -> Optional[InterviewSession]:
        cached = self._sessions.get(
            session_id
        )

        if cached is not None:
            return cached

        path = self._session_path(
            session_id
        )

        if not path.exists():
            return None

        try:
            with path.open(
                "r",
                encoding="utf-8",
            ) as file:
                payload = json.load(file)

            if (
                payload.get("session_id")
                != session_id
            ):
                raise ValueError(
                    "Persisted session ID mismatch"
                )

            state = payload.get("state")

            if not isinstance(
                state,
                dict,
            ):
                raise ValueError(
                    "Invalid persisted session state"
                )

            session = (
                InterviewSession.from_state(
                    state
                )
            )

        except (
            json.JSONDecodeError,
            KeyError,
            TypeError,
            ValueError,
        ):
            return None

        self._sessions[
            session_id
        ] = session

        return session

    def delete(
        self,
        session_id: str,
    ) -> None:
        self._sessions.pop(
            session_id,
            None,
        )

        self._session_path(
            session_id
        ).unlink(
            missing_ok=True
        )

    def exists(
        self,
        session_id: str,
    ) -> bool:
        if session_id in self._sessions:
            return True

        return self._session_path(
            session_id
        ).exists()

    def clear(
        self,
        *,
        include_persistent: bool = True,
    ) -> None:
        self._sessions.clear()

        if not include_persistent:
            return

        for path in self.storage_dir.glob(
            "*.json"
        ):
            path.unlink(
                missing_ok=True
            )

        for path in self.storage_dir.glob(
            "*.tmp"
        ):
            path.unlink(
                missing_ok=True
            )


session_store = SessionStore()