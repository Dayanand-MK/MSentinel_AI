import csv
import logging
from datetime import datetime
from pathlib import Path
from threading import Lock
from config.settings import LOG_DIR

# Ensure log directory exists
log_path = Path(LOG_DIR)
log_path.mkdir(parents=True, exist_ok=True)

audit_log_file = log_path / "audit.log"
audit_csv_file = log_path / "audit.csv"

# Configure audit logger
audit_formatter = logging.Formatter("%(asctime)s | %(message)s")
audit_handler = logging.FileHandler(audit_log_file, encoding="utf-8")
audit_handler.setFormatter(audit_formatter)

audit_logger = logging.getLogger("audit_log")
audit_logger.setLevel(logging.INFO)
# Avoid duplicating handler if re-initialized
if not audit_logger.handlers:
    audit_logger.addHandler(audit_handler)

csv_lock = Lock()
CSV_HEADERS = [
    "Timestamp", 
    "Filename", 
    "Hash", 
    "Processing Time", 
    "Risk", 
    "Compliance", 
    "Question", 
    "Response", 
    "Model Used"
]

def init_csv():
    with csv_lock:
        if not audit_csv_file.exists() or audit_csv_file.stat().st_size == 0:
            with open(audit_csv_file, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(CSV_HEADERS)

class AuditLogger:
    def __init__(self):
        init_csv()

    def log_document(self, filename: str, file_hash: str, proc_time: float, risk_score: float, compliance_score: float, risk_level: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"DOC_PROCESSED | Name: {filename} | Hash: {file_hash} | Time: {proc_time:.2f}s | Risk: {risk_score:.1f} ({risk_level}) | Compliance: {compliance_score:.1f}"
        audit_logger.info(log_msg)

        with csv_lock:
            with open(audit_csv_file, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    timestamp, 
                    filename, 
                    file_hash, 
                    f"{proc_time:.2f}", 
                    f"{risk_score:.1f}", 
                    f"{compliance_score:.1f}", 
                    "", 
                    "", 
                    ""
                ])

    def log_query(self, question: str, response: str, model_used: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"Q&A | Model: {model_used} | Q: {question} | A: {response[:80]}..."
        audit_logger.info(log_msg)

        with csv_lock:
            with open(audit_csv_file, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    timestamp, 
                    "", 
                    "", 
                    "", 
                    "", 
                    "", 
                    question, 
                    response, 
                    model_used
                ])
