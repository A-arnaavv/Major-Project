import os

from dotenv import load_dotenv


load_dotenv()


LLM_MODE = os.getenv(
    "LLM_MODE",
    "real",
).strip().lower()


GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL"
)


GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)


MAX_INTERVIEW_QUESTIONS = int(
    os.getenv(
        "MAX_INTERVIEW_QUESTIONS",
        "20",
    )
)


MAX_RESUME_SIZE_MB = int(
    os.getenv(
        "MAX_RESUME_SIZE_MB",
        "10",
    )
)


MAX_RESUME_SIZE_BYTES = (
    MAX_RESUME_SIZE_MB
    * 1024
    * 1024
)


DEFAULT_RETRIEVAL_TOP_K = int(
    os.getenv(
        "DEFAULT_RETRIEVAL_TOP_K",
        "5",
    )
)


def is_mock_mode() -> bool:
    return LLM_MODE == "mock"