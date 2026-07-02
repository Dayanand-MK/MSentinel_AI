from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Document:

    original_name : str
    saved_path : Path
    extension : str

    raw_text : str = ""
    cleaned_text : str = ""

    metadata : dict[str, Any] = field(default_factory=dict)

    entities : list["Entity"] = field(default_factory = list)

    risk_score : float = 0.0

    compliance_score : float = 100.0

    processing_time : float = 0.0

    ocr_used : bool = False

    page_count : int = 0

    character_count : int = 0

    word_count : int = 0

    line_count : int = 0

    risk_level : str = "Low"

    risk_explanation : str = ""

    compliance_summary : str = ""

    masked_text : str = ""

    redaction_count : int = 0

    report_markdown : str = ""

    recommendations : list[str] = field(default_factory = list)

    chunks : list[str] = field(default_factory = list)

    chunk_embeddings : list = field(default_factory = list)

    vector_ids : list[str] = field(default_factory = list)