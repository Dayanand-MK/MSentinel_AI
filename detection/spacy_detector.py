import spacy
from config.logging_config import get_logger
from models import Document, Entity

logger = get_logger(__name__)

# Try to load model, download automatically if missing
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logger.info("Downloading spaCy model 'en_core_web_sm'...")
    from spacy.cli import download
    try:
        download("en_core_web_sm")
        nlp = spacy.load("en_core_web_sm")
    except Exception as e:
        logger.error(f"Failed to download spaCy model: {e}")
        # Create a dummy model or placeholder to avoid crash
        nlp = None

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
        if nlp is None:
            logger.warning("spaCy model is not loaded. Skipping spaCy detection.")
            return document

        doc = nlp(document.cleaned_text)
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

        for ent in doc.ents:
            if ent.label_ not in SPACY_ENTITY_MAP:
                continue

            category, risk = SPACY_ENTITY_MAP[ent.label_]
            start_offset = ent.start_char
            end_offset = ent.end_char

            entities.append(
                Entity(
                    category=category,
                    value=ent.text,
                    confidence=0.95,
                    method="spaCy",
                    risk_weight=risk,
                    start=start_offset,
                    end=end_offset,
                    page=get_page_number(start_offset),
                    filename=filename,
                )
            )

        document.entities.extend(entities)
        logger.info("%d spaCy entities detected in %s", len(entities), document.original_name)
        return document