from pathlib import Path
from loaders import PDFLoader, TXTLoader, CSVLoader
from models import Document
from loaders.ocr_loader import OCRLoader

class DocumentLoader:
    def __init__(self):
        self.pdf = PDFLoader()
        self.txt = TXTLoader()
        self.csv = CSVLoader()
        self.ocr = OCRLoader()

    def load(self, file_path: Path) -> Document:

        extension = file_path.suffix.lower()

        document = Document(
            original_name=file_path.name,
            saved_path=file_path,
            extension=extension,
        )

        if extension == ".pdf":
            document.raw_text = self.pdf.extract_text(file_path)

            if len(document.raw_text.strip()) < 20:
                document.raw_text = self.ocr.extract_text(file_path)
                document.ocr_used = True

        elif extension == ".txt":
            document.raw_text = self.txt.extract_text(file_path)

        elif extension == ".csv":
            document.raw_text = self.csv.extract_text(file_path)

        else:
            raise ValueError(f"Unsupported file type: {extension}")

        return document