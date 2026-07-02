from pathlib import Path

from pipelines import DocumentPipeline


class DocumentService:

    def __init__(self):

        self.pipeline = DocumentPipeline()

    def process_document(self, path: Path):

        return self.pipeline.process(path)