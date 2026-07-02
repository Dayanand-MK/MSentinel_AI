from pathlib import Path
import fitz
from config.logging_config import get_logger

logger = get_logger(__name__)

class PDFLoader:
    def extract_text(self, file_path : Path) -> str:
        try:
            document = fitz.open(file_path)
            pages = []
            for page in document:
                pages.append(page.get_text())
            document.close()

            text = "\n".join(pages)

            logger.info("PDF text extracted : %s", file_path.name)
            return text

        except Exception as e:
            logger.exception("Error extracting text from PDF")
            raise RuntimeError(str(e))