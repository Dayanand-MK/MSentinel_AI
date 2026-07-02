from models import Document


class RiskScorer:

    MAX_SCORE = 100

    def score(self, document: Document) -> Document:

        total = sum(entity.risk_weight for entity in document.entities)

        score = min(total, self.MAX_SCORE)

        document.risk_score = score
        document.compliance_score = max(0, 100 - score)

        if score < 20:
            document.risk_level = "Low"
        elif score < 50:
            document.risk_level = "Medium"
        else:
            document.risk_level = "High"

        document.risk_explanation = (
            f"{len(document.entities)} sensitive item(s) detected "
            f"with a cumulative risk score of {score}."
        )

        return document