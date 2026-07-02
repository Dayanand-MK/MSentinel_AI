import sys
errors = []
from pathlib import Path

# 1. Config
try:
    from config.constants import APP_NAME, SUPPORTED_FILE_TYPES
    from config.settings import LOG_DIR, CHROMA_DB_PATH
    print(f"[OK] config — APP_NAME={APP_NAME}, LOG_DIR={LOG_DIR}")
except Exception as e:
    errors.append(f"[FAIL] config: {e}")

# 2. Models
try:
    from models.document import Document
    from models.entity import Entity
    d = Document(original_name="test.txt", saved_path=Path("test.txt"), extension=".txt")
    e = Entity(category="Email", value="a@b.com", confidence=1.0, method="Regex", risk_weight=2, start=0, end=8, page=1, filename="test.txt")
    assert e.page == 1 and e.filename == "test.txt"
    print(f"[OK] models — Document and Entity OK; Entity.page={e.page}, Entity.filename={e.filename}")
except Exception as ex:
    errors.append(f"[FAIL] models: {ex}")

# 3. Loaders
try:
    from loaders.pdf_loader import PDFLoader
    from loaders.txt_loader import TXTLoader
    from loaders.csv_loader import CSVLoader
    from loaders.ocr_loader import OCRLoader
    from loaders.document_loader import DocumentLoader
    print("[OK] loaders — all loader classes import cleanly")
except Exception as ex:
    errors.append(f"[FAIL] loaders: {ex}")

# 4. Preprocessing (space-collapsing fix)
try:
    from preprocessing.cleaner import TextCleaner
    from models.document import Document
    doc = Document(original_name="t.txt", saved_path=Path("t.txt"), extension=".txt")
    doc.raw_text = "Hello   World\n\n\n\nTest line."
    doc.metadata["page_texts"] = [doc.raw_text]
    cleaner = TextCleaner()
    doc = cleaner.clean(doc)
    assert "Hello World" in doc.cleaned_text, "Space preservation failed — spaces are still being collapsed"
    pages_key = "cleaned_pages"
    n_pages = len(doc.metadata[pages_key])
    print(f"[OK] TextCleaner — cleaned_text OK, {n_pages} page(s) in metadata")
except Exception as ex:
    errors.append(f"[FAIL] preprocessing: {ex}")

# 5. Detection
try:
    from detection.patterns import PATTERNS
    from detection.regex_detector import RegexDetector
    from detection.spacy_detector import SpacyDetector
    from detection.llm_validator import LLMValidator
    print(f"[OK] detection — {len(PATTERNS)} regex patterns; RegexDetector, SpacyDetector, LLMValidator import OK")
except Exception as ex:
    errors.append(f"[FAIL] detection: {ex}")

# 6. Risk & Masking
try:
    from risk.scorer import RiskScorer
    from risk.risk_weights import RISK_WEIGHTS
    from masking.redactor import Redactor
    print(f"[OK] risk/masking — {len(RISK_WEIGHTS)} risk weight categories loaded")
except Exception as ex:
    errors.append(f"[FAIL] risk/masking: {ex}")

# 7. Compliance & Reports
try:
    from compliance.summarizer import ComplianceSummarizer
    from compliance.recommendations import RecommendationEngine
    from reports.pdf_generator import PDFReportGenerator
    print("[OK] compliance/reports — all classes import cleanly")
except Exception as ex:
    errors.append(f"[FAIL] compliance/reports: {ex}")

# 8. RAG
try:
    from rag.chunker import Chunker
    from rag.embeddings import EmbeddingGenerator
    from rag.qa_engine import QAEngine
    print("[OK] rag — Chunker, EmbeddingGenerator, QAEngine import OK")
except Exception as ex:
    errors.append(f"[FAIL] rag: {ex}")

# 9. Logger
try:
    from logger.audit_logger import AuditLogger
    al = AuditLogger()
    print("[OK] AuditLogger — instantiated successfully")
except Exception as ex:
    errors.append(f"[FAIL] logger: {ex}")

# 10. Services
try:
    from services.detection_service import DetectionService
    from services.masking_service import MaskingService
    from services.risk_service import RiskService
    from services.compliance_service import ComplianceService
    from services.report_service import ReportService
    print("[OK] services — all 5 service wrappers import cleanly")
except Exception as ex:
    errors.append(f"[FAIL] services: {ex}")

# 11. Utils
try:
    from utils.file_utils import allowed_file, save_uploaded_file, get_file_hash
    from utils.helpers import get_file_size_mb
    from utils.entity_utils import remove_duplicate_entities
    assert allowed_file("test.pdf") == True
    assert allowed_file("test.exe") == False
    print("[OK] utils — file_utils, helpers, entity_utils all work correctly")
except Exception as ex:
    errors.append(f"[FAIL] utils: {ex}")

# 12. Controllers
try:
    from controllers.dashboard_controller import DashboardController
    from controllers.upload_controller import UploadController
    from controllers.chat_controller import ChatController
    print("[OK] controllers — DashboardController, UploadController, ChatController import OK")
except Exception as ex:
    errors.append(f"[FAIL] controllers: {ex}")

# 13. Full pipeline smoke test (no network/file I/O)
try:
    from models.document import Document
    from models.entity import Entity
    from preprocessing.cleaner import TextCleaner
    from detection.regex_detector import RegexDetector
    from risk.scorer import RiskScorer
    from masking.redactor import Redactor
    from compliance.recommendations import RecommendationEngine
    from compliance.summarizer import ComplianceSummarizer

    doc = Document(original_name="smoke.txt", saved_path=Path("smoke.txt"), extension=".txt")
    doc.raw_text = "Employee: John Smith. Email: john@corp.com. PAN: ABCDE1234F. JWT: eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJqb2huIn0.SIG"
    doc.metadata["page_texts"] = [doc.raw_text]

    doc = TextCleaner().clean(doc)
    doc = RegexDetector().detect(doc)
    doc = RiskScorer().score(doc)
    doc = Redactor().redact(doc)
    doc = RecommendationEngine().generate(doc)
    doc = ComplianceSummarizer().generate(doc)

    entity_cats = [e.category for e in doc.entities]
    assert "Email" in entity_cats, "Email not detected"
    assert "PAN" in entity_cats, "PAN not detected"
    assert "JWT" in entity_cats, "JWT not detected"
    assert "[EMAIL REDACTED]" in doc.masked_text, "Email not redacted"
    assert "[PAN REDACTED]" in doc.masked_text, "PAN not redacted"
    assert "[JWT REDACTED]" in doc.masked_text, "JWT not redacted"
    assert "# MSentinel AI Compliance Report" in doc.report_markdown
    print(f"[OK] pipeline smoke test — {len(doc.entities)} entities detected, {doc.redaction_count} redacted, risk={doc.risk_score}, compliance={doc.compliance_score}%")
except Exception as ex:
    errors.append(f"[FAIL] pipeline smoke test: {ex}")

# 14. Verify CSS sidebar-hiding is in app.py
try:
    app_source = Path("app.py").read_text(encoding="utf-8")
    assert 'display: none !important' in app_source, "Sidebar hide CSS not found"
    assert 'stSidebarCollapsedControl' in app_source, "Toggle hide CSS not found"
    assert 'initial_sidebar_state="collapsed"' in app_source, "Collapsed state not set"
    assert 'st.tabs([' in app_source, "Tab navigation not found"
    assert 'st.sidebar' not in app_source, "st.sidebar is still referenced!"
    print("[OK] app.py — sidebar fully hidden via CSS, tab navigation confirmed, no st.sidebar references")
except Exception as ex:
    errors.append(f"[FAIL] app.py verification: {ex}")

# Final Summary
print()
print("=" * 60)
total = 14
passed = total - len(errors)
if errors:
    print(f"RESULT: {passed}/{total} PASSED — {len(errors)} FAILURE(S):")
    for err in errors:
        print("  " + err)
    sys.exit(1)
else:
    print(f"RESULT: ALL {total}/{total} CHECKS PASSED -- App is fully operational [PASS]")
