from dataclasses import dataclass
from enum import Enum

class ValidationSeverity(str, Enum):
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"

class ProcessingStatus(str, Enum):
    PROCESSED = "PROCESSED"
    MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"
    INVALID = "INVALID"

@dataclass
class ValidationIssue:
    code: str
    message: str
    severity: ValidationSeverity
    field: str | None = None

@dataclass
class ValidationResult:
    issues: list[ValidationIssue]
    status: ProcessingStatus
    confidence: float