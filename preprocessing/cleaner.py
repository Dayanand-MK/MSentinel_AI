import re
import unicodedata
from config.logging_config import get_logger
from models import Document

logger = get_logger(__name__)

class TextCleaner:
    def clean(self, document : Document) -> Document:
        text = document.raw_text
        text = unicodedata.normalize("NFKC", text)
        text = text.replace("\x00", "")
        text = re.sub(r"[ \t]+", "", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"\r", "", text)
        text = text.strip()

        document.cleaned_text = text
        document.character_count = len(text)
        document.word_count = len(text.split())
        document.line_count = len(text.splitlines())

        logger.info("Text Cleaned for %s", document.original_name)

        return document