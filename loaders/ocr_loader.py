from pathlib import Path

import pytesseract
from pdf2image import convert_from_path

from config.logging_config import get_logger

logger = get_logger(__name__)


class OCRLoader:
    """Extract text from scanned PDFs using Tesseract OCR."""

    def extract_text(self, pdf_path: Path) -> str:
        try:
            images = convert_from_path(pdf_path)

            pages = []

            for image in images:
                text = pytesseract.image_to_string(image)
                pages.append(text)

            logger.info("OCR completed for %s", pdf_path.name)

            return "\n".join(pages)

        except Exception:
            logger.exception("OCR failed.")
            raise