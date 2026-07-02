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
            pages = self.pdf.extract_text(file_path)
            raw_text = "\n".join(pages)

            if len(raw_text.strip()) < 20:
                pages = self.ocr.extract_text(file_path)
                raw_text = "\n".join(pages)
                document.ocr_used = True

            document.metadata["page_texts"] = pages
            document.raw_text = raw_text
            document.page_count = len(pages)

        elif extension == ".txt":
            raw_text = self.txt.extract_text(file_path)
            document.metadata["page_texts"] = [raw_text]
            document.raw_text = raw_text
            document.page_count = 1

        elif extension == ".csv":
            raw_text = self.csv.extract_text(file_path)
            document.metadata["page_texts"] = [raw_text]
            document.raw_text = raw_text
            document.page_count = 1


        else:
            raise ValueError(f"Unsupported file type: {extension}")

        return document