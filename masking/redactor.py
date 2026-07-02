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
            "Driving License" : "[DRIVING LICENSE REDACTED]",
            "IFSC" : "[IFSC REDACTED]",
            "Bank Account" : "[BANK ACCOUNT REDACTED]",
            "Credit Card" : "[CARD REDACTED]",
            "Debit Card" : "[CARD REDACTED]",
            "CVV" : "[CVV REDACTED]",
            "Password" : "[PASSWORD REDACTED]",
            "API Keys" : "[API KEY REDACTED]",
            "JWT" : "[JWT REDACTED]",
            "AWS Keys" : "[AWS KEY REDACTED]",
            "Employee IDs" : "[EMPLOYEE ID REDACTED]",
        }

        # Sort entities by start offset in reverse order
        sorted_entities = sorted(document.entities, key=lambda e: e.start, reverse=True)
        count = 0
        last_start = len(text) + 1

        for entity in sorted_entities:
            replacement = replacements.get(entity.category)
            if replacement and entity.start >= 0 and entity.end <= len(text):
                # Check that we are not overlapping with a previously redacted chunk
                if entity.end <= last_start:
                    text = text[:entity.start] + replacement + text[entity.end:]
                    last_start = entity.start
                    count += 1

        document.masked_text = text
        document.redaction_count = count
        return document