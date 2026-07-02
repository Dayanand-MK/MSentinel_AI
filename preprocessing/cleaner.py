import re
import unicodedata
from config.logging_config import get_logger
from models import Document

logger = get_logger(__name__)

class TextCleaner:
    def clean(self, document : Document) -> Document:
        if "page_texts" in document.metadata and document.metadata["page_texts"]:
            cleaned_pages = []
            for page_text in document.metadata["page_texts"]:
                cleaned_pages.append(self._clean_text(page_text))
            document.metadata["cleaned_pages"] = cleaned_pages
            text = "\n".join(cleaned_pages)
        else:
            text = self._clean_text(document.raw_text)
            document.metadata["cleaned_pages"] = [text]

        document.cleaned_text = text
        document.character_count = len(text)
        document.word_count = len(text.split())
        document.line_count = len(text.splitlines())

        logger.info("Text Cleaned for %s", document.original_name)

        return document

    def _clean_text(self, text: str) -> str:
        if not text:
            return ""
        text = unicodedata.normalize("NFKC", text)
        text = text.replace("\x00", "")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"\r", "", text)
        return text.strip()