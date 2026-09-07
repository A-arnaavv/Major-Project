import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

DEFAULT_RESUME_FILENAME = os.getenv(
    "INTERVIEWGPT_RESUME_FILENAME",
    "resume.pdf",
)

DEFAULT_RESUME_PATH = RAW_DATA_DIR / DEFAULT_RESUME_FILENAME
CANDIDATE_PROFILE_PATH = PROCESSED_DATA_DIR / "candidate_profile.json"
MILVUS_DB_PATH = DATA_DIR / "milvus.db"
