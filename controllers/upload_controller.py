from pathlib import Path
from services import DocumentService

class UploadController:
    def __init__(self):
        self.document_service = DocumentService()

    def process_uploaded_file(self, path : Path):
        return self.document_service.process_document(path)