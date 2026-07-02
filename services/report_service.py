from pathlib import Path
from models import Document
from config.constants import OUTPUTS_DIR
from reports.pdf_generator import PDFReportGenerator

class ReportService:
    def __init__(self):
        self.pdf_generator = PDFReportGenerator()
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    def generate_pdf_report(self, document: Document) -> Path:
        output_path = OUTPUTS_DIR / f"{document.saved_path.stem}_report.pdf"
        self.pdf_generator.generate(document, output_path)
        return output_path

    def get_redacted_path(self, document: Document) -> Path:
        output_path = OUTPUTS_DIR / f"{document.saved_path.stem}_redacted.txt"
        output_path.write_text(document.masked_text, encoding="utf-8")
        return output_path
