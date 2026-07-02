from pathlib import Path

import pytesseract
from pdf2image import convert_from_path

from config.logging_config import get_logger

logger = get_logger(__name__)


class OCRLoader:
    """Extract text from scanned PDFs using Tesseract OCR."""

    def extract_text(self, pdf_path: Path) -> list[str]:
        try:
            # pdf2image might fail if poppler is not installed
            images = convert_from_path(pdf_path)
            pages = []

            for idx, image in enumerate(images, start=1):
                try:
                    text = pytesseract.image_to_string(image)
                    pages.append(text or "")
                except Exception as e:
                    logger.warning(f"Tesseract OCR failed for page {idx} in {pdf_path.name}. Is Tesseract installed? Detail: {e}")
                    pages.append(f"[OCR Failed: Tesseract not configured. Page content not extracted.]")

            logger.info("OCR completed for %s (%d pages)", pdf_path.name, len(pages))
            return pages

        except Exception as e:
            logger.error(f"OCR conversion failed completely for {pdf_path.name}. Detail: {e}")
            # Return a fallback indicating failure so the pipeline continues
            return [f"[OCR Failed completely: {e}]"]