from pathlib import Path
from config.logging_config import get_logger

logger = get_logger(__name__)

class TXTLoader:
    def extract_text(self, file_path : Path) -> str:
        try:
            text = file_path.read_text(encoding="utf-8")
            logger.info("TXT file extracted : %s", file_path.name)
            return text
            
        except Exception as e:
            logger.exception("Error extracting text from TXT")
            raise RuntimeError(str(e))
            