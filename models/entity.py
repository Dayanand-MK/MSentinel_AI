from dataclasses import dataclass

@dataclass
class Entity:
    category: str
    value: str
    confidence: float
    method: str
    risk_weight: int
    start: int
    end: int
    page: int = 1
    filename: str = "N/A"