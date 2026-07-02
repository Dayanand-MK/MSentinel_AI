from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Document:

    original_name: str
    saved_path: Path
    extension: str

    raw_text: str = ""
    cleaned_text: str = ""

    metadata: dict[str, Any] = field(default_factory=dict)

    entities: list["Entity"] = field(default_factory = list)

    risk_score: float = 0.0

    compliance_score: float = 100.0

    processing_time: float = 0.0

    ocr_used: bool = False

    page_count: int = 0

    character_count: int = 0

    word_count: int = 0

    line_count: int = 0