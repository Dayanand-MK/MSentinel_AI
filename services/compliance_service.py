from models import Document
from compliance import RecommendationEngine, ComplianceSummarizer

class ComplianceService:
    def __init__(self):
        self.recommendation = RecommendationEngine()
        self.summarizer = ComplianceSummarizer()

    def analyze_compliance(self, document: Document) -> Document:
        document = self.recommendation.generate(document)
        document = self.summarizer.generate(document)
        return document
