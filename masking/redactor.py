import re

from models import Document


class Redactor:

    def redact(self, document : Document) -> Document:

        text = document.cleaned_text

        replacements = {
            "Email" : "[EMAIL REDACTED]",
            "Phone" : "[PHONE REDACTED]",
            "PAN" : "[PAN REDACTED]",
            "Aadhaar" : "[AADHAAR REDACTED]",
            "Passport" : "[PASSPORT REDACTED]",
            "Credit Card" : "[CARD REDACTED]",
            "Bank Account" : "[BANK ACCOUNT REDACTED]",
            "JWT" : "[JWT REDACTED]",
            "IFSC" : "[IFSC REDACTED]",
        }

        count = 0

        for entity in document.entities:

            replacement = replacements.get(entity.category)

            if replacement:

                pattern = re.escape(entity.value)

                text, replaced = re.subn(pattern, replacement, text,)

                count += replaced

        document.masked_text = text
        document.redaction_count = count

        return document