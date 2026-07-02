from pathlib import Path

from pipelines import DocumentPipeline


class DocumentService:

    def __init__(self):

        self.pipeline = DocumentPipeline()

    def process_document(self, path: Path, *args, **kwargs):
        original_name = kwargs.get("original_name", None)
        if not original_name and len(args) > 0:
            original_name = args[0]
        return self.pipeline.process(path, original_name)