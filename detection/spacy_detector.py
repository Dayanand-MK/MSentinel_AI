import spacy

from config.logging_config import get_logger
from models import Document, Entity

logger = get_logger(__name__)

nlp = spacy.load("en_core_web_sm")


SPACY_ENTITY_MAP = {
    "PERSON": ("Person", 3),
    "ORG": ("Organization", 4),
    "GPE": ("Location", 2),
    "LOC": ("Location", 2),
    "DATE": ("Date", 1),
    "MONEY": ("Money", 5),
}


class SpacyDetector:

    def detect(self, document: Document) -> Document:

        doc = nlp(document.cleaned_text)

        entities = []

        for ent in doc.ents:

            if ent.label_ not in SPACY_ENTITY_MAP:
                continue

            category, risk = SPACY_ENTITY_MAP[ent.label_]

            entities.append(
                Entity(
                    category=category,
                    value=ent.text,
                    confidence=0.95,
                    method="spaCy",
                    risk_weight=risk,
                    start=ent.start_char,
                    end=ent.end_char,
                )
            )

        document.entities.extend(entities)

        logger.info(
            "%d spaCy entities detected in %s",
            len(entities),
            document.original_name,
        )

        return document