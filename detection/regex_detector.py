import re

from config.logging_config import get_logger
from models import Document, Entity
from detection.patterns import PATTERNS
from risk.risk_weights import RISK_WEIGHTS

logger = get_logger(__name__)

class RegexDetector:
    def detect(self, document: Document) -> Document:
        entities = []
        text = document.cleaned_text
        cleaned_pages = document.metadata.get("cleaned_pages", [text])
        filename = document.original_name

        def get_page_number(offset: int) -> int:
            curr = 0
            for idx, p in enumerate(cleaned_pages):
                p_len = len(p)
                if curr <= offset <= curr + p_len:
                    return idx + 1
                curr += p_len + 1
            return 1

        for category, pattern in PATTERNS.items():
            matches = re.finditer(pattern, text)

            for match in matches:
                start_offset = match.start()
                end_offset = match.end()
                entities.append(
                    Entity(
                        category=category,
                        value=match.group(),
                        confidence=1.0,
                        method="Regex",
                        risk_weight=RISK_WEIGHTS.get(category, 1),
                        start=start_offset,
                        end=end_offset,
                        page=get_page_number(start_offset),
                        filename=filename,
                    )
                )

        document.entities.extend(entities)
        logger.info("%d regex entities detected in %s", len(entities), document.original_name)
        return document