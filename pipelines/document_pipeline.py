from pathlib import Path

from compliance import ComplianceSummarizer, RecommendationEngine
from detection import RegexDetector, SpacyDetector
from detection.llm_validator import LLMValidator
from loaders.document_loader import DocumentLoader
from masking import Redactor
from preprocessing import TextCleaner
from risk import RiskScorer
from rag import Chunker, EmbeddingGenerator, ChromaManager
from utils import remove_duplicate_entities

class DocumentPipeline:
    def __init__(self):
        self.loader = DocumentLoader()
        self.cleaner = TextCleaner()
        self.regex = RegexDetector()
        self.spacy = SpacyDetector()
        self.llm_validator = LLMValidator()
        self.risk = RiskScorer()
        self.redactor = Redactor()
        self.recommendation = RecommendationEngine()
        self.report = ComplianceSummarizer()
        self.chunker = Chunker()
        self.embedding_generator = EmbeddingGenerator()
        self.vector_store = ChromaManager()

    def process(self, file_path: Path):
        document = self.loader.load(file_path)
        document = self.cleaner.clean(document)
        document = self.regex.detect(document)
        document = self.spacy.detect(document)
        document = self.llm_validator.detect(document)
        document = remove_duplicate_entities(document)
        document = self.risk.score(document)
        document = self.redactor.redact(document)
        document = self.recommendation.generate(document)
        document = self.report.generate(document)
        document = self.chunker.chunk(document)
        document = self.embedding_generator.generate(document)
        document = self.vector_store.store(document)
        return document