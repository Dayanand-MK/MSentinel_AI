from pathlib import Path
import shutil
from typing import BinaryIO
from uuid import uuid4
from config.settings import UPLOAD_DIR

UPLOAD_PATH = Path(UPLOAD_DIR)
UPLOAD_PATH.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENTIONS = {"pdf", "csv", "txt"}

def allowed_file(fileneme : str) -> bool:
    return ("." in fileneme and fileneme.rsplit(".", 1)[1].lower() in ALLOWED_EXTENTIONS)

def save_uploaded_file(uploaded_file : BinaryIO) -> Path:
    ext = uploaded_file.name.split(".")[-1]
    unique_name = f"{uuid4().hex}.{ext}"

    dest = UPLOAD_PATH / unique_name
    with open(dest, "wb") as f:
        shutil.copyfileobj(uploaded_file, f)

    return dest