from pathlib import Path
import shutil
import hashlib
from typing import BinaryIO
from uuid import uuid4
from config.settings import UPLOAD_DIR

UPLOAD_PATH = Path(UPLOAD_DIR)
UPLOAD_PATH.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf", "csv", "txt"}

def allowed_file(filename : str) -> bool:
    return ("." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS)

def save_uploaded_file(uploaded_file : BinaryIO) -> Path:
    ext = uploaded_file.name.split(".")[-1]
    unique_name = f"{uuid4().hex}.{ext}"

    dest = UPLOAD_PATH / unique_name
    with open(dest, "wb") as f:
        shutil.copyfileobj(uploaded_file, f)

    return dest

def get_file_hash(file_path: Path) -> str:
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()