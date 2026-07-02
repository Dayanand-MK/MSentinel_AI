from pathlib import Path

# Base Dir
BASE_DIR  = Path(__file__).resolve().parent.parent

# Default Dir
UPLOADS_DIR = BASE_DIR / "uploads"
OUTPUTS_DIR = BASE_DIR / "outputs"
LOGS_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"
CHROMA_DB_DIR =  BASE_DIR / "chroma_db"

# File Types
SUPPORTED_FILE_TYPES = ["pdf", "txt", "csv"]

# Risk
LOW_RISK = "Low"
MEDIUM_RISK = "Medium"
HIGH_RISK = "High"

# Application
APP_NAME = "MSentinal AI"