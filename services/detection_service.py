from models import Document
from detection import RegexDetector, SpacyDetector
from detection.llm_validator import LLMValidator
from utils import remove_duplicate_entities

class DetectionService:
    def __init__(self):
        self.regex = RegexDetector()
        self.spacy = SpacyDetector()
        self.llm = LLMValidator()

    def detect_all(self, document: Document) -> Document:
        document = self.regex.detect(document)
        document = self.spacy.detect(document)
        document = self.llm.detect(document)
        document = remove_duplicate_entities(document)
        return document
