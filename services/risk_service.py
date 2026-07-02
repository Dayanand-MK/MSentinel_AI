from models import Document
from risk import RiskScorer

class RiskService:
    def __init__(self):
        self.scorer = RiskScorer()

    def evaluate_risk(self, document: Document) -> Document:
        return self.scorer.score(document)
