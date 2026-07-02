from models import Document


class RecommendationEngine:

    RECOMMENDATIONS = {
        "Email": "Mask or encrypt email addresses before sharing.",
        "Phone": "Remove personal phone numbers from public documents.",
        "PAN": "Redact PAN numbers unless legally required.",
        "Aadhaar": "Mask Aadhaar numbers according to UIDAI guidelines.",
        "Passport": "Avoid exposing passport details.",
        "Credit Card": "Never store or display full credit card numbers.",
        "Bank Account": "Protect bank account numbers using masking.",
        "JWT": "Rotate exposed authentication tokens immediately.",
        "IFSC": "Verify whether IFSC codes should be publicly visible.",
        "Person": "Review whether personal names should be disclosed.",
        "Organization": "Check organization names for confidentiality.",
        "Location": "Ensure location information is appropriate to share.",
    }

    def generate(self, document: Document) -> Document:

        recommendations = set()

        for entity in document.entities:
            recommendation = self.RECOMMENDATIONS.get(entity.category)
            if recommendation:
                recommendations.add(recommendation)

        document.recommendations = sorted(recommendations)

        return document