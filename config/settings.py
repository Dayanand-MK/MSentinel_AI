from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

APP_NAME = os.getenv("APP_NAME", "MSentinal AI")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

UPLOAD_DIR = os.getenv("UPLOAD_DIR", str(BASE_DIR / "uploads"))

OUTPUT_DIR = os.getenv("OUTPUT_DIR", str(BASE_DIR / "outputs"))

LOG_DIR = os.getenv("LOG_DIR", str(BASE_DIR / "logs"))

CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", str(BASE_DIR / "data/chroma_db"))

HF_API_TOKEN = os.getenv("HF_API_TOKEN", "")