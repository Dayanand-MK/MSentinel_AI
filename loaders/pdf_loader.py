from pathlib import Path
import fitz
from config.logging_config import get_logger

logger = get_logger(__name__)

class PDFLoader:
    def extract_text(self, file_path : Path) -> list[str]:
        try:
            document = fitz.open(file_path)
            pages = []
            for page in document:
                pages.append(page.get_text() or "")
            document.close()

            logger.info("PDF text extracted : %s (%d pages)", file_path.name, len(pages))
            return pages

        except Exception as e:
            logger.exception("Error extracting text from PDF")
            raise RuntimeError(str(e))