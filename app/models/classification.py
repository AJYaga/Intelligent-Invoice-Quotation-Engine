from dataclasses import dataclass
from enum import Enum

class DocumentType(str, Enum):
    INVOICE = "INVOICE"
    QUOTATION = "QUOTATION"
    UNKNOWN = "UNKNOWN"

@dataclass
class ClassificationEvidence:
    signal: str
    weight: float
    document_type: DocumentType

@dataclass
class ClassificationResult:
    document_type: DocumentType
    confidence: float
    invoice_score: float
    quotation_score: float
    evidence: list[ClassificationEvidence]