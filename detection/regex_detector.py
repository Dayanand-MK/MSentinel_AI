import re

from config.logging_config import get_logger
from models import Document, Entity
from detection.patterns import PATTERNS
from risk.risk_weights import RISK_WEIGHTS

logger = get_logger(__name__)

class RegexDetector:
    def detect(self, document : Document ) -> Document:
        entities = []

        text = document.cleaned_text

        for category, pattern in PATTERNS.items():
            matches = re.finditer(pattern, text)

            for match in matches:
                entities.append(
                    Entity(
                        category = category,
                        value = match.group(),
                        confidence = 1.0,
                        method = "Regex",
                        risk_weight = RISK_WEIGHTS.get(category, 1),
                        start = match.start(),
                        end = match.end(),
                    )
                )

        document.entities.extend(entities)

        logger.info("%d regex entitie detected in %s", len(entities), document.original_name,)

        return document