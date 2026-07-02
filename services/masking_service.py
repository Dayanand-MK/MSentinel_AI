from models import Document
from masking import Redactor

class MaskingService:
    def __init__(self):
        self.redactor = Redactor()

    def mask_document(self, document: Document) -> Document:
        return self.redactor.redact(document)
