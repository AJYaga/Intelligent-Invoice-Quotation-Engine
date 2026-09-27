from app.models.classification import ClassificationResult
from app.models.extraction import ExtractionResult
from app.models.ocr import OCRResult
from app.models.validation import ValidationResult
from app.services.confidence.scoring import analyze_confidence
from app.services.validation.financial import (
    validate_grand_total,
    validate_line_items,
    validate_subtotal,
)
from app.services.validation.required_fields import (
    validate_required_fields,
)
from app.services.validation.status import resolve_status

class ValidationService:
    def validate(
        self,
        ocr_result: OCRResult,
        classification: ClassificationResult,
        extraction: ExtractionResult,
    ) -> ValidationResult:
        issues = []

        issues.extend(
            validate_required_fields(
                extraction
            )
        )

        issues.extend(
            validate_line_items(
                extraction
            )
        )

        issues.extend(
            validate_subtotal(
                extraction
            )
        )

        issues.extend(
            validate_grand_total(
                extraction
            )
        )

        confidence, confidence_issues = (
            analyze_confidence(
                ocr_result,
                classification,
                extraction,
            )
        )

        issues.extend(confidence_issues)

        status = resolve_status(issues)

        return ValidationResult(
            issues=issues,
            status=status,
            confidence=confidence,
        )