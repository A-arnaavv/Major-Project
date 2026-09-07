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


def is_mock_mode() -> bool:
    return LLM_MODE == "mock"